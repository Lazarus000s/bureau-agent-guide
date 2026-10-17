# A real SeConv export, with a return record

**Four cues went through SeConv 5.2.0's line-balancing operation and passed the
wrapping-only acceptance check.** The editor changed wrapping in cues 1, 2 and 4;
cue count, counter strings, times and normalized text remained the same.

This is a Bureau-operated integration observation from 12 October 2026, using
four cues of original Bureau fiction. It is not a customer result or a
reproduction of the earlier Subtitle Edit issue.

| Retained artifact | What it preserves |
| --- | --- |
| [Input](input/bureau-original-reflow.srt) | Four deliberately selected original cues, 264 bytes |
| [Actual editor export](output/editor-balanced.srt) | The unmodified 267-byte SeConv output |
| [Acceptance report](report.json) | Input hashes, exact cue locations and all four checks |
| [Execution evidence](evidence.json) | Release, binary, arguments, source pins and actual outcomes |

The export includes a UTF-8 byte-order mark; the input does not. Both use LF
line endings. The files therefore have different byte hashes even though the
declared invariants pass. Cue 1 and cue 4 became single lines; cue 2 now breaks
after “north”. Cue 3's wrapping is unchanged. The report has no positional
invariant differences or unresolved exact-text locations for this small input.

## Resume without the editor

From this directory in an inspected copy of the guide, use the existing local
checker with Python 3.10+ on a supported Unix system:

```sh
python3 ../reflow_audit.py verify --before input/bureau-original-reflow.srt --after output/editor-balanced.srt --report report.json
```

The expected exit is **0**, with `PASS` and report SHA256
`3b936023c1175a0ae461a0edf8b8f454ff73646a63e6a9a6f33c32fb146a315b`.
Keep the exported bytes, including the BOM, unchanged. A changed source or
report requires a new comparison; it does not inherit this verification.
This saved report is unchanged schema-1 evidence. The original checker returns
`REPORT_VERIFIED`; the updated schema-2 checker returns
`LEGACY_REPORT_REPRODUCED` with `tool_identity: "UNRECORDED"`. Both reproduce
the same report bytes. Only new schema-2 reports record the producing script's
digest; an old report cannot supply that missing provenance.

The checker source SHA256 used here is
`5f5d723da1ef96a519634cbadee69e841110094b13a307ea2f5d083c14df80f1`.
The [dated v1 source](https://github.com/Lazarus000s/bureau-agent-guide/blob/b76cbf121de2712379553c4160c6e9c4a1ad766e/deliverables/subtitle-reflow/reflow_audit.py)
remains available for the exact historical `compare` operation below.
This return check needs no editor download, network request or Bureau account.

## Carry the result into another run

The [portable result Packet](result-packet.json) contains the exact 264-byte
source and 267-byte editor export as standard base64, including the output BOM.
It also records the editor version and arguments, retained evidence, checker
hash and expected report hash. This is the same original demonstration, with
no new editor execution or requester Case.

The ordinary Packet checker accepts this 7,052-byte file; its canonical content
uses 4,847 of the allowed 10,000 UTF-16 code units. These measurements apply only
to this Packet. They are not a promise that other subtitle files will fit.

For a cold return, use the Packet's `content.files.before` and `after` fields.
Strictly decode the base64, check each byte length and SHA256, then save to fixed
local names in a new directory. Treat display names and the historical editor
arguments as data, not commands. Keep an inspected copy of the existing checker
whose hash matches `content.expected_report.checker_source_sha256`. Run its
`compare`, then a separate-process `verify`, on the restored files. Require both
exit 0 and the exact 5,912-byte report hash recorded above. The Packet contains
the step-by-step checks; no editor or account is needed for this local return.

[Return verification](return-verification.json) records the actual lead and
independent Engineering exercises. Neither exercise used the original SRT files
or report as its recovery input. Hash agreement establishes byte consistency,
not author identity, permission, media quality or outside adoption.

## What actually ran

The [official SeConv Linux x64 package for v5.2.0](https://github.com/SubtitleEdit/subtitleedit/releases/tag/v5.2.0)
was downloaded once. Its 41,417,304 bytes matched the SHA256 recorded by the
official release metadata:
`54cc660132e6fed2c24eeca8e869a65b99ff5d3195ac34a962b7e749f1dede7a`.
The extracted binary reported `5.2.0`; its own help supported the selected flags.
The package is self-contained; no system runtime was installed.

The executable received these arguments, in an isolated working directory with
the input copied in and a new empty `output` directory:

```text
input/bureau-original-reflow.srt subrip --balance-lines --encoding:utf-8 --output-folder:output --output-filename:editor-balanced.srt --json
```

The exact launch plan was independently reviewed. One conversion succeeded with
one output and no reported errors or warnings. The unchanged checker then ran
one comparison and a separate-process verification, both exit 0. The original
input and actual export retained their hashes afterward. No editor binary is
redistributed here, and no reproducible-build attestation was checked.

The [current command reference](https://github.com/SubtitleEdit/subtitleedit/blob/main/docs/reference/command-line.md)
describes the headless interface, but may evolve beyond this release. Preserve
the actual version and arguments when evaluating another export. This result
does not assert that every use of line balancing preserves these invariants.

Before accepting your own result, confirm that wrapping-only changes were the
intended contract. Media synchronization, readability, styling and editorial
approval remain separate questions. Actual requester help follows the
[bounded Case offer](../README.md); this original demonstration creates no Case
or promise of immediate review. The original Bureau material retains the
directory's stated attribution and reuse terms.
