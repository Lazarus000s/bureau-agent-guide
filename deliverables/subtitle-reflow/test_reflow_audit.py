import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import reflow_audit as audit


def srt(*entries):
    return ("\n\n".join(f"{i + 1}\n{start} --> {end}\n{text}"
                       for i, (start, end, text) in enumerate(entries)) + "\n").encode()


ONE = srt(("00:00:01,000", "00:00:03,000", "Keep the paper map."))
TWO = srt(("00:00:01,000", "00:00:03,000", "Keep the paper map."),
          ("00:00:04,000", "00:00:06,000", "Read the north arrow."))


class ContractTests(unittest.TestCase):
    def test_allowed_reflow(self):
        after = ONE.replace(b"Keep the paper map.", b"Keep the\npaper   map.")
        result = audit.compare(ONE, after)
        self.assertEqual(result["reflow_contract"], "PASS")
        self.assertTrue(all(result["checks"].values()))
        self.assertNotEqual(result["inputs"]["before"]["sha256"], result["inputs"]["after"]["sha256"])

    def test_original_split_pattern_is_caught(self):
        before = srt(("00:39:41,790", "00:39:45,210", "The brass key belongs beside the blue folder."))
        after = srt(("00:39:41,790", "00:39:43,830", "The brass key belongs"),
                    ("00:39:44,190", "00:39:45,210", "beside the blue folder."))
        result = audit.compare(before, after)
        self.assertEqual(result["reflow_contract"], "REVIEW_REQUIRED")
        self.assertFalse(result["checks"]["cue_count_preserved"])
        self.assertFalse(result["checks"]["timecode_sequence_preserved"])
        self.assertEqual(result["exact_unique_text_locations"], [])
        self.assertEqual(result["unmatched_exact_text_ordinals"], {"before": [1], "after": [1, 2]})

    def test_shifted_unique_text_is_an_observation(self):
        extra = srt(("00:00:00,000", "00:00:00,500", "A title card."))
        after = extra + b"\n" + TWO.replace(b"1\n", b"2\n", 1).replace(b"\n2\n", b"\n3\n")
        result = audit.compare(TWO, after)
        self.assertEqual([(r["before_ordinal"], r["after_ordinal"])
                          for r in result["exact_unique_text_locations"]], [(1, 2), (2, 3)])
        self.assertEqual(result["reflow_contract"], "REVIEW_REQUIRED")

    def test_repeated_text_not_paired(self):
        before = srt(("00:00:01,000", "00:00:02,000", "Yes."),
                     ("00:00:03,000", "00:00:04,000", "Yes."))
        after = before.replace(b"00:00:03,000", b"00:00:03,100")
        result = audit.compare(before, after)
        self.assertEqual(result["exact_unique_text_locations"], [])
        self.assertEqual(result["repeated_text_locations"][0]["before_ordinals"], [1, 2])
        self.assertIn("repeated_text", [r["kind"] for r in result["review_queue"]])

    def test_counter_renumbering_fails_strict_contract(self):
        result = audit.compare(ONE, ONE.replace(b"1\n", b"9\n", 1))
        self.assertFalse(result["checks"]["counter_sequence_preserved"])
        self.assertTrue(result["checks"]["timecode_sequence_preserved"])

    def test_same_count_timing_change(self):
        result = audit.compare(ONE, ONE.replace(b"01,000", b"01,100"))
        self.assertFalse(result["checks"]["timecode_sequence_preserved"])
        self.assertEqual(result["exact_unique_text_locations"][0]["start_delta_ms"], 100)

    def test_unicode_spaces_are_not_silently_folded(self):
        after = ONE.decode().replace("paper map", "paper\u00a0map").encode()
        self.assertEqual(audit.compare(ONE, after)["reflow_contract"], "REVIEW_REQUIRED")

    def test_unicode_normalization_not_assumed(self):
        before = ONE.replace(b"paper", "café".encode())
        after = ONE.replace(b"paper", "cafe\u0301".encode())
        self.assertFalse(audit.compare(before, after)["checks"]["normalized_text_sequence_preserved"])

    def test_markup_is_literal(self):
        after = ONE.replace(b"paper", b"<i>paper</i>")
        self.assertEqual(audit.compare(ONE, after)["reflow_contract"], "REVIEW_REQUIRED")

    def test_bom_crlf_preserve_contract_but_not_bytes(self):
        after = b"\xef\xbb\xbf" + ONE.replace(b"\n", b"\r\n")
        result = audit.compare(ONE, after)
        self.assertEqual(result["reflow_contract"], "PASS")
        self.assertFalse(result["input_bytes_identical"])

    def test_reordered_text_is_detected(self):
        after = TWO.replace(b"Keep the paper map.", b"TEMP").replace(b"Read the north arrow.", b"Keep the paper map.").replace(b"TEMP", b"Read the north arrow.")
        self.assertFalse(audit.compare(TWO, after)["checks"]["normalized_text_sequence_preserved"])

    def test_existing_overlap_is_not_accessibility_validation(self):
        data = srt(("00:00:01,000", "00:00:05,000", "Map."),
                   ("00:00:02,000", "00:00:03,000", "Arrow."))
        result = audit.compare(data, data)
        self.assertEqual(result["reflow_contract"], "PASS")
        self.assertIn("overlap/readability policy", result["unassessed"])

    def test_line_spans_address_source(self):
        data = b"\n" + ONE + b"\n" + ONE
        cues = audit.parse_srt(data, "before")["cues"]
        self.assertEqual([(c["line_start"], c["line_end"]) for c in cues], [(2, 4), (6, 8)])

    def test_unsupported_inputs_never_pass(self):
        bad = [b"", b"\xff", ONE.replace(b"00:00:01,000", b"00:61:01,000"),
               ONE.replace(b"00:00:03,000", b"00:00:01,000"),
               ONE.replace(b" --> ", b" -> "), ONE.replace(b"map.", b"map.\x00"),
               ONE + ONE, b"WEBVTT\n\n" + ONE,
               ONE.replace(b"1\n", b"0\n", 1)]
        for data in bad:
            with self.subTest(data=data[:20]), self.assertRaises(audit.AuditError):
                audit.compare(data, ONE)

    def test_input_limit(self):
        with self.assertRaisesRegex(audit.AuditError, "input_size_limit"):
            audit.parse_srt(b"x" * (audit.MAX_INPUT_BYTES + 1), "before")

    def test_determinism(self):
        self.assertEqual(audit.encode_report(audit.compare(ONE, TWO)),
                         audit.encode_report(audit.compare(ONE, TWO)))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before, self.after, self.report = [self.root / name for name in ("before.srt", "after.srt", "report.json")]
        self.before.write_bytes(ONE)
        self.after.write_bytes(ONE.replace(b"the paper", b"the\npaper"))

    def run_cli(self, operation="compare", *, script=None):
        return subprocess.run([sys.executable, str(script or Path(audit.__file__).resolve()), operation,
                               "--before", str(self.before), "--after", str(self.after),
                               "--report", str(self.report)], capture_output=True, text=True, timeout=5)

    def test_compare_and_fresh_process_verify_preserve_inputs(self):
        original = [self.before.read_bytes(), self.after.read_bytes()]
        self.assertEqual(self.run_cli().returncode, 0)
        checked = self.run_cli("verify")
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout)["status"], "REPORT_VERIFIED")
        self.assertEqual([self.before.read_bytes(), self.after.read_bytes()], original)
        self.assertEqual(self.report.stat().st_mode & 0o777, 0o600)

    def test_review_exit_is_one_and_report_is_written(self):
        self.after.write_bytes(TWO)
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["reflow_contract"], "REVIEW_REQUIRED")
        self.assertEqual(self.run_cli("verify").returncode, 1)

    def test_existing_report_is_not_overwritten(self):
        self.report.write_bytes(b"existing")
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["code"], "output_already_exists")
        self.assertEqual(self.report.read_bytes(), b"existing")

    def test_report_cannot_overwrite_source(self):
        self.report = self.before
        original = self.before.read_bytes()
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(self.before.read_bytes(), original)

    def test_changed_input_invalidates_saved_report_even_if_reflow_passes(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.after.write_bytes(b"\xef\xbb\xbf" + self.after.read_bytes())
        self.assertEqual(self.run_cli("verify").returncode, 2)

    def test_report_edit_is_rejected(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.report.write_bytes(self.report.read_bytes().replace(b'"PASS"', b'"REVIEW_REQUIRED"'))
        self.assertEqual(self.run_cli("verify").returncode, 2)

    def test_bad_input_does_not_create_report(self):
        self.after.write_bytes(b"not subtitles")
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertFalse(self.report.exists())

    def test_symlink_input_rejected(self):
        link = self.root / "link.srt"
        link.symlink_to(self.before)
        self.before = link
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertFalse(self.report.exists())

    def test_new_report_records_exact_script_source(self):
        self.assertEqual(self.run_cli().returncode, 0)
        report = json.loads(self.report.read_bytes())
        self.assertEqual(report["schema_version"], 2)
        self.assertEqual(report["tool"], "bureau-subtitle-reflow-audit/2")
        self.assertEqual(report["tool_source_sha256"],
                         hashlib.sha256(Path(audit.__file__).read_bytes()).hexdigest())
        self.assertEqual(json.loads(self.run_cli("verify").stdout)["tool_identity"],
                         "SOURCE_DIGEST_MATCHES")

    def test_output_preserving_source_change_is_identified(self):
        self.assertEqual(self.run_cli().returncode, 0)
        changed = self.root / "comment-only.py"
        changed.write_bytes(Path(audit.__file__).read_bytes() + b"\n# Synthetic source change.\n")
        checked = self.run_cli("verify", script=changed)
        self.assertEqual(checked.returncode, 2)
        self.assertEqual(json.loads(checked.stderr), {
            "status": "ERROR", "code": "report_identity_mismatch",
            "mismatches": ["tool_source"]})

    def test_all_identity_changes_reported_before_subtitle_rebuild(self):
        self.assertEqual(self.run_cli().returncode, 0)
        changed = self.root / "other-source.py"
        changed.write_bytes(Path(audit.__file__).read_bytes() + b"\n# Synthetic new build.\n")
        # A fresh parse would reject this; identity diagnostics must happen first.
        self.after.write_bytes(b"no longer a subtitle file")
        checked = self.run_cli("verify", script=changed)
        self.assertEqual(checked.returncode, 2)
        self.assertEqual(json.loads(checked.stderr)["mismatches"],
                         ["after_input", "tool_source"])
        self.assertEqual(json.loads(checked.stderr)["code"], "report_identity_mismatch")

    def test_tool_label_mismatch_is_distinct_and_does_not_echo_values(self):
        self.assertEqual(self.run_cli().returncode, 0)
        report = json.loads(self.report.read_bytes())
        report["tool"] = "UNTRUSTED_SENTINEL"
        self.report.write_text(json.dumps(report))
        checked = self.run_cli("verify")
        self.assertEqual(checked.returncode, 2)
        self.assertEqual(json.loads(checked.stderr)["mismatches"], ["tool_version"])
        self.assertNotIn("UNTRUSTED_SENTINEL", checked.stderr)

    def test_matching_identities_do_not_skip_full_report_check(self):
        self.assertEqual(self.run_cli().returncode, 0)
        # Even a whitespace-only report edit violates byte-exact reproduction.
        self.report.write_bytes(self.report.read_bytes() + b"\n")
        checked = self.run_cli("verify")
        self.assertEqual(checked.returncode, 2)
        self.assertEqual(json.loads(checked.stderr)["code"],
                         "report_recomputed_content_mismatch")

    def test_existing_v1_fixtures_reproduce_without_inventing_tool_identity(self):
        base = Path(audit.__file__).parent
        for filename, after, code in [("reflow-only", "reflow-only", 0),
                                      ("structural-change", "structural-change", 1)]:
            with self.subTest(report=filename):
                self.before = base / "fixtures/before.srt"
                self.after = base / f"fixtures/{after}.srt"
                self.report = base / f"reports/{filename}.json"
                original = self.report.read_bytes()
                checked = self.run_cli("verify")
                self.assertEqual(checked.returncode, code, checked.stderr)
                result = json.loads(checked.stdout)
                self.assertEqual(result["status"], "LEGACY_REPORT_REPRODUCED")
                self.assertEqual(result["tool_identity"], "UNRECORDED")
                self.assertEqual(self.report.read_bytes(), original)

    def test_invalid_or_missing_provenance_is_not_silently_accepted(self):
        self.assertEqual(self.run_cli().returncode, 0)
        original = self.report.read_bytes()
        variants = [b"not JSON", b'{}', b'{"schema_version":2,"schema_version":2}']
        for key, value in [("tool_source_sha256", None), ("tool_source_sha256", "bad"),
                           ("schema_version", True)]:
            report = json.loads(original)
            report[key] = value
            variants.append(json.dumps(report).encode())
        for variant in variants:
            with self.subTest(size=len(variant)):
                self.report.write_bytes(variant)
                checked = self.run_cli("verify")
                self.assertEqual(checked.returncode, 2)
                self.assertEqual(json.loads(checked.stderr)["code"], "invalid_report_metadata")


if __name__ == "__main__":
    unittest.main()
