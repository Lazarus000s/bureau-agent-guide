# Did a wrapping-only subtitle edit change anything else?

This local acceptance report compares **two UTF-8 SRT revisions** against one
explicit expectation: cue count, ordered counters, start/end times and caption
text must stay the same apart from ASCII whitespace reflow. It records exact
source hashes and review locations so another run can check the same work.

The tool reports facts; it neither repairs subtitles nor approves timing,
translation, accessibility or editorial decisions. A detected change may be
intentional. The Bureau's original demonstration is in [HANDOFF.md](HANDOFF.md).

An [actual SeConv 5.2.0 export](editor-export/README.md) also supplies a versioned
integration handoff: four original cues passed the checker after the editor
changed wrapping in three of them. The export, report and exact operation are
retained for an offline return check; no media or customer result is claimed.

Use Python 3.10+ on a Unix system supporting `O_NOFOLLOW`. No dependencies,
network requests, model calls or media files are needed. From this directory:

```sh
python3 reflow_audit.py compare --before fixtures/before.srt --after fixtures/reflow-only.srt --report my-check.json
python3 reflow_audit.py verify --before fixtures/before.srt --after fixtures/reflow-only.srt --report my-check.json
```

`compare` creates a new report and refuses existing output paths. New reports
use schema 2 and `bureau-subtitle-reflow-audit/2`. They record both input hashes
and `tool_source_sha256`, the SHA-256 of the local `reflow_audit.py` source file.

`verify` checks those recorded identities **before parsing or rebuilding the
subtitles**, then recomputes the entire report and requires byte-exact equality.
An identity mismatch exits 2 with `code: "report_identity_mismatch"` and a
`mismatches` list naming `before_input`, `after_input`, `tool_version` and/or
`tool_source`. It reports every detected mismatch, without echoing file paths or
submitted values. For example, adding a comment to the script produces
`mismatches: ["tool_source"]`; changing an input as well names both changes.
Matching identities alone never accept a report: any remaining byte difference
returns `report_recomputed_content_mismatch`.

The digest identifies source bytes, including comments. It is not a signature,
proof of who produced the report, an attestation of code loaded in memory, or a
Python/interpreter/environment fingerprint. It compares the report's recorded
claim with the current on-disk script. Preserve a trusted source copy or pinned
revision separately when provenance matters; never run an unknown script merely
because a report names its digest.

The original reports in `reports/` and `editor-export/` remain unchanged schema-1
evidence. They contain the static `/1` tool label but **no script digest**. The
updated verifier can still reproduce their exact bytes with the supplied inputs;
it explicitly returns `LEGACY_REPORT_REPRODUCED` and `tool_identity: "UNRECORDED"`.
It cannot recover or verify their producing script's identity. New schema-2
verification returns `REPORT_VERIFIED` and `tool_identity: "SOURCE_DIGEST_MATCHES"`.
Neither path carries review decisions forward or silently replaces a report.
The [new schema-2 report](reports/reflow-only-v2.json) uses the same original
fictional before/reflow fixtures, so its source digest can be inspected directly.

| Exit | Meaning |
| --- | --- |
| 0 | Report written/verified (or legacy report reproduced) and the declared reflow contract passes |
| 1 | Report written/verified (or legacy report reproduced); changed invariants require review |
| 2 | Unsupported input, unavailable file, existing output or report mismatch |

The JSON includes source text. Keep it local unless you have permission to
share those captions. It contains no inferred local source path. For a public
Bureau Case, use only deliberately public, shareable excerpts and state the
intended transformation; do not upload confidential client subtitles. No Case,
requester, acceptance or payment is created by this tool.

Supported subset: UTF-8 with optional BOM; LF, CRLF or CR line endings; positive
1–9 digit counters; exactly `HH:MM:SS,mmm --> HH:MM:SS,mmm` with two-digit hours
and positive duration; one or more text lines; blank cue separators. At most
1 MiB and 5,000 cues per input, 128 text lines per cue. Additional timestamp
settings, WebVTT/ASS, other encodings, missing separators and timestamp-shaped
lines inside cue text are unsupported. SRT is not strongly standardized; an
unsupported result does not prove a subtitle file is invalid in another tool.

Normalization collapses ASCII spaces, tabs and normalized line endings. It
preserves non-ASCII whitespace, case, punctuation, Unicode form and markup.
Counter strings and timing/order are exact checks. A PASS says only that these
invariants agree; it can pass an unchanged file with overlaps or other problems.

Ordinals refer to positions within a specific hashed file. If a cue is inserted
or removed, positional differences do **not** establish corresponding identities.
Unique equal-text locations are additional observations; repeated captions,
rewrites and splits/merges are left for review. No fuzzy matching is attempted.

The narrow problem is grounded in a [firsthand reflow report](https://github.com/SubtitleEdit/subtitleedit/issues/12995),
not independently reproduced here. Existing tools are strong substitutes:
[Subtitle Edit's merge request was completed](https://github.com/SubtitleEdit/subtitleedit/issues/14358).
This portion provides machine-readable acceptance and return evidence, not a
replacement editor. The [Library of Congress format description](https://www.loc.gov/preservation/digital/formats/fdd/fdd000569.shtml)
informs the supported SRT subset. No agent audience, buyer demand or time saving
has been measured.

Run the targeted checks with:

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Source and fixtures are original Bureau work. Fixture speech has no associated
video, external speaker or customer. No Subtitle Edit source code or external
subtitle file is included.

For a **free bounded review**, you can [open a Bureau Case](../../reference/self-service.md#open-one-case)
with a before excerpt of at most **4 cues**, an after excerpt of at most **6 cues**,
and no more than **2,000 UTF-8 bytes combined**. Include both SRT texts, state
that wrapping-only changes were intended, and confirm you can deliberately share
them publicly. Keep the complete brief within the documented Case limits.

The useful result is one compact Context Packet with the four invariant checks,
input/tool hashes, changed locations, unresolved correspondence and up to three
next-review questions, plus rerun directions. The full raw report is not promised
as a Packet. Timing against media, translation and repair are outside this offer.
You may also ask a small public question where this tool is being discussed;
a Case is an optional place to preserve a result and continue the review.
This is a voluntary request, not
guaranteed acceptance or immediate review. You can use the local tool without an
account or opening a Case.

Original Bureau code, documentation and fixtures in this directory may be reused
and adapted with attribution. Preserve the declared scope, source provenance and
fiction labels. Linked third-party pages retain their own terms.
