# Did a wrapping-only subtitle edit change anything else?

This local acceptance report compares **two UTF-8 SRT revisions** against one
explicit expectation: cue count, ordered counters, start/end times and caption
text must stay the same apart from ASCII whitespace reflow. It records exact
source hashes and review locations so another run can check the same work.

The tool reports facts; it neither repairs subtitles nor approves timing,
translation, accessibility or editorial decisions. A detected change may be
intentional. The Bureau's original demonstration is in [HANDOFF.md](HANDOFF.md).

Use Python 3.10+ on a Unix system supporting `O_NOFOLLOW`. No dependencies,
network requests, model calls or media files are needed. From this directory:

```sh
python3 reflow_audit.py compare --before fixtures/before.srt --after fixtures/reflow-only.srt --report my-check.json
python3 reflow_audit.py verify --before fixtures/before.srt --after fixtures/reflow-only.srt --report my-check.json
```

`compare` creates a new report and refuses existing output paths. `verify`
recomputes the entire report in a fresh process and requires byte-exact equality.
Changed source bytes invalidate a saved report even when the new comparison
would still satisfy the reflow contract. It does not carry review decisions
forward or silently replace the report.

| Exit | Meaning |
| --- | --- |
| 0 | Report written/verified and the declared reflow contract passes |
| 1 | Report written/verified; changed invariants require review |
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
Assistance and follow-up belong in that Case. This is a voluntary request, not
guaranteed acceptance or immediate review. You can use the local tool without an
account or opening a Case.

Original Bureau code, documentation and fixtures in this directory may be reused
and adapted with attribution. Preserve the declared scope, source provenance and
fiction labels. Linked third-party pages retain their own terms.
