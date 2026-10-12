#!/usr/bin/env python3
"""Read-only acceptance evidence for a declared UTF-8 SRT reflow-only edit.

No network, media inspection, subtitle repair, fuzzy alignment or model calls.
The report contains subtitle text. Share it only with permission for that text.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

MAX_INPUT_BYTES = 1024 * 1024
MAX_CUES = 5000
MAX_REPORT_BYTES = 32 * 1024 * 1024
STAMP = r"[0-9]{2}:[0-5][0-9]:[0-5][0-9],[0-9]{3}"
TIMING = re.compile(rf"({STAMP}) --> ({STAMP})")
COUNTER = re.compile(r"[0-9]{1,9}")


class AuditError(Exception):
    """A bounded, content-free error suitable for CLI display."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_regular(path: Path, limit: int) -> bytes:
    """Explicit local file only; reject final symlink, device, FIFO and oversize."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise AuditError("input_not_regular_file")
            data = stream.read(limit + 1)
    except OSError:
        raise AuditError("input_unavailable") from None
    if len(data) > limit:
        raise AuditError("input_size_limit")
    return data


def milliseconds(value: str) -> int:
    hours, minutes, tail = value.split(":")
    seconds, fraction = tail.split(",")
    return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(fraction)


def normalized_text(value: str) -> str:
    # Only ASCII space, TAB and line boundaries are allowed reflow changes.
    # Do not fold case, Unicode, punctuation, markup or non-ASCII whitespace.
    return re.sub(r"[ \t\n]+", " ", value).strip(" ")


def parse_srt(data: bytes, role: str) -> dict:
    if len(data) > MAX_INPUT_BYTES:
        raise AuditError("input_size_limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise AuditError("unsupported_encoding_expected_utf8") from None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in text):
        raise AuditError("unsupported_control_character")
    lines = text.split("\n")
    cues = []
    position = 0
    while position < len(lines):
        if not lines[position].strip(" \t"):
            position += 1
            continue
        start = position
        while position < len(lines) and lines[position].strip(" \t"):
            position += 1
        block = lines[start:position]
        if len(block) < 3 or not COUNTER.fullmatch(block[0]) or int(block[0]) < 1:
            raise AuditError(f"unsupported_cue_structure_at_line_{start + 1}")
        match = TIMING.fullmatch(block[1])
        if not match:
            raise AuditError(f"unsupported_timestamp_at_line_{start + 2}")
        start_ms, end_ms = (milliseconds(value) for value in match.groups())
        if end_ms <= start_ms:
            raise AuditError(f"nonpositive_duration_at_line_{start + 2}")
        if any(TIMING.fullmatch(line) for line in block[2:]):
            raise AuditError(f"ambiguous_timing_inside_text_at_line_{start + 3}")
        cue_text = "\n".join(block[2:])
        if len(block) > 130:
            raise AuditError("cue_line_limit")
        cues.append({
            "ordinal": len(cues) + 1,
            "counter": block[0],
            "line_start": start + 1,
            "line_end": position,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": cue_text,
            "text_sha256": sha256(cue_text.encode("utf-8")),
            "normalized_text_sha256": sha256(normalized_text(cue_text).encode("utf-8")),
        })
        if len(cues) > MAX_CUES:
            raise AuditError("cue_count_limit")
    if not cues:
        raise AuditError("no_cues")
    return {"role": role, "sha256": sha256(data), "byte_count": len(data),
            "cue_count": len(cues), "cues": cues}


def compare(before: bytes, after: bytes) -> dict:
    left, right = parse_srt(before, "before"), parse_srt(after, "after")
    a, b = left["cues"], right["cues"]
    checks = {
        "cue_count_preserved": len(a) == len(b),
        "counter_sequence_preserved": [x["counter"] for x in a] == [x["counter"] for x in b],
        "timecode_sequence_preserved": [(x["start_ms"], x["end_ms"]) for x in a]
        == [(x["start_ms"], x["end_ms"]) for x in b],
        "normalized_text_sequence_preserved": [normalized_text(x["text"]) for x in a]
        == [normalized_text(x["text"]) for x in b],
    }
    differences = []
    for index in range(max(len(a), len(b))):
        old = a[index] if index < len(a) else None
        new = b[index] if index < len(b) else None
        if old is None or new is None:
            fields = ["position_absent_before" if old is None else "position_absent_after"]
        else:
            fields = []
            if old["counter"] != new["counter"]:
                fields.append("counter")
            if (old["start_ms"], old["end_ms"]) != (new["start_ms"], new["end_ms"]):
                fields.append("timecodes")
            if normalized_text(old["text"]) != normalized_text(new["text"]):
                fields.append("normalized_text")
        if fields:
            differences.append({"sequence_position": index + 1, "changed_fields": fields,
                                "before_ordinal": old["ordinal"] if old else None,
                                "after_ordinal": new["ordinal"] if new else None})

    # Exact text occurrences are facts about these files, not persistent cue IDs.
    # Duplicates/splits/merges are never assigned guessed counterparts.
    by_a, by_b = defaultdict(list), defaultdict(list)
    for cue in a:
        by_a[normalized_text(cue["text"])].append(cue)
    for cue in b:
        by_b[normalized_text(cue["text"])].append(cue)
    unique_locations, repeated, unmatched = [], [], {"before": [], "after": []}
    for value in sorted(set(by_a) | set(by_b)):
        old, new = by_a[value], by_b[value]
        digest = sha256(value.encode("utf-8"))
        if len(old) == len(new) == 1:
            x, y = old[0], new[0]
            unique_locations.append({
                "normalized_text_sha256": digest,
                "before_ordinal": x["ordinal"], "after_ordinal": y["ordinal"],
                "start_delta_ms": y["start_ms"] - x["start_ms"],
                "end_delta_ms": y["end_ms"] - x["end_ms"],
            })
        if len(old) > 1 or len(new) > 1:
            repeated.append({"normalized_text_sha256": digest,
                             "before_ordinals": [x["ordinal"] for x in old],
                             "after_ordinals": [x["ordinal"] for x in new]})
        if not new:
            unmatched["before"].extend(x["ordinal"] for x in old)
        if not old:
            unmatched["after"].extend(x["ordinal"] for x in new)
    unique_locations.sort(key=lambda item: item["before_ordinal"])
    for values in unmatched.values():
        values.sort()
    passed = all(checks.values())
    queue = []
    if not checks["cue_count_preserved"]:
        queue.append({"kind": "structural_change", "next_action":
                      "Review added, removed, split or merged cues against the intended edit; positional pairs are not identities."})
    if differences:
        queue.append({"kind": "changed_sequence_positions", "positions":
                      [item["sequence_position"] for item in differences], "next_action":
                      "Inspect the corresponding source line spans. Decide whether each change is intentional; this report makes no repairs."})
    if repeated and not passed:
        queue.append({"kind": "repeated_text", "next_action":
                      "Resolve repeated-text correspondence manually when investigating changes; no unique cue match is asserted."})
    return {
        "schema_version": 1,
        "tool": "bureau-subtitle-reflow-audit/1",
        "contract": {
            "id": "ordered-srt-reflow-only/1",
            "normalization": "Collapse ASCII space, TAB and normalized line endings to one space, trim ASCII boundary spaces; no other text normalization.",
            "counter_rule": "Exact original counter strings and order are retained.",
            "location_rule": "Ordinals and line spans identify positions only within the SHA256-bound file. Exact-text locations are observations, not persistent cue identity.",
        },
        "reflow_contract": "PASS" if passed else "REVIEW_REQUIRED",
        "input_bytes_identical": before == after,
        "checks": checks,
        "inputs": {"before": left, "after": right},
        "positional_differences": differences,
        "exact_unique_text_locations": unique_locations,
        "repeated_text_locations": repeated,
        "unmatched_exact_text_ordinals": unmatched,
        "review_queue": queue,
        "unassessed": ["media synchronization", "translation/content accuracy", "accessibility compliance",
                       "intentionality of changes", "caption styling/rendering", "overlap/readability policy"],
    }


def encode_report(report: dict) -> bytes:
    data = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(data) > MAX_REPORT_BYTES:
        raise AuditError("report_size_limit")
    return data


def create_output(path: Path, data: bytes) -> None:
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        raise AuditError("output_already_exists") from None
    except OSError:
        # A partial new output may remain after a write failure; it is not valid
        # until verification succeeds. Never remove or overwrite an existing file.
        raise AuditError("output_write_failed") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["compare", "verify"])
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = compare(read_regular(args.before, MAX_INPUT_BYTES), read_regular(args.after, MAX_INPUT_BYTES))
        data = encode_report(report)
        if args.operation == "compare":
            create_output(args.report, data)
            print(json.dumps({"status": "REPORT_WRITTEN", "reflow_contract": report["reflow_contract"],
                              "report_sha256": sha256(data)}))
            return 0 if report["reflow_contract"] == "PASS" else 1
        actual = read_regular(args.report, MAX_REPORT_BYTES)
        if actual != data:
            raise AuditError("report_does_not_match_current_inputs_or_tool")
        print(json.dumps({"status": "REPORT_VERIFIED", "reflow_contract": report["reflow_contract"],
                          "report_sha256": sha256(data)}))
        return 0 if report["reflow_contract"] == "PASS" else 1
    except AuditError as error:
        print(json.dumps({"status": "ERROR", "code": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
