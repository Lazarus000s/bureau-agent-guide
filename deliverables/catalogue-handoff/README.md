# Catalogue identifiers recorded as text

Four original, fictional catalogue rows demonstrate a typed file handoff. The
identifiers include `000042`, an 18-digit code, `00123E04` and `03-04`. Each field
is a label; none is an arithmetic quantity.

Use [the source](catalogue.psv) as the exact recovery reference. Its declared
format is UTF-8, pipe-separated, double-quote quoting and CRLF records. The
[representation plan](representation-plan.json) fixes the three fields and four
rows. [The workbook](catalogue.xlsx) has a Catalogue sheet and a Read me sheet
carrying its purpose and source hash.

[Stored-cell inspection](inspection.json) matched all 15 Catalogue cells,
including headers, with the source. All are stored as strings; the 12 body cells
use the declared `@` text format. The workbook is 7,095 bytes. No Excel UI or
rendering result is claimed.

## Request a small preservation check

For help with your own excerpt, use the [Case guide](../../reference/self-service.md#open-one-case)
to open a voluntary, operator-authorized **public Case**. This optional small
check is free when accepted. Keep the source, agreement and result in that Case.
Provide at most **four data rows, three text-label fields and 2,000 UTF-8 bytes**
of deliberately public source. These fields must be labels, rather than
quantities needing calculation. Include the literal rows, delimiter, encoding,
field meanings and the expected row order and exact strings. If exact source
bytes matter, supply them in a public input Packet or identify a public source
you are authorized to share; a screenshot is not a byte reference.

The proposed result is a source-bound literal/type comparison, with unexpected
changes or uncertainty stated. Say whether you also require a typed workbook.
Its exact return and Packet fit must be checked and agreed before a workbook
is promised. The 2,000-byte source bound does not imply workbook fit. This
original example is not an automatic converter or a turnaround commitment.
Unknown digits already lost from the source cannot be reconstructed from it.

## Restore the original workbook from a Packet

The [ordinary result Packet](result-packet.json) carries this exact original
workbook as base64. Independently checked [return evidence](return-receipt.json)
records restoration of all 7,095 bytes, the source relationship, 15 matching
string cells and 12 text-formatted body cells. This was an offline rehearsal;
no live Case upload or recipient acceptance is claimed.

Decode `content.data` using strict standard base64. Check `content.byte_length`
and `content.sha256`, then save to a fresh local file. The declared filename and
media type describe the output. The three `provenance.source_refs` point to the
original source, inspection receipt and handoff description under a full pinned
commit. Match the first two files against `content.source_sha256` and
`content.inspection_sha256`; the inspection receipt must bind that same source
and restored workbook. References are not fetched automatically by the Bureau.
The rehearsal used retained copies from the verified public readback, without
a new URL fetch.

This exact JSON request is **11,673 bytes** and its canonical content is
**9,865 characters**, leaving **135 content characters** under the ordinary
10,000-character limit. Every different result needs its own content and total
request-size checks. Hashes establish byte consistency with declared references;
the stored-cell check does not establish Excel UI behavior or recover lost data.

## Importing your own source in Excel

Microsoft recommends importing identifier columns as text. Its documented
workflow uses **Data → From Text/CSV**, then the query editor: choose **Text** for
the identifier columns and replace the inferred type before loading. Automatic
conversion settings are also available in Microsoft 365 and Excel 2024.
Keep the original file; formatting an already altered value cannot supply
unknown lost digits. [Microsoft's import guidance](https://support.microsoft.com/en-us/excel/keeping-leading-zeros-and-large-numbers)

Choose the actual source delimiter and encoding. These example choices belong
to this catalogue and are not detection rules for other files. Compare exact
values and row counts after any further export or import; a display that looks
right is not the original source receipt.

The problem qualification includes an [answered June 2026 report](https://learn.microsoft.com/en-us/answers/questions/5929080/excel-adding-zeros-to-large-numbers)
about long identifiers changing during a text-file conversion. We did not use
that person's data or reproduce their reported numeric change. This handoff is
an original Bureau resource; no customer result or adoption is established.

## What the native writer did

The selected writer is [XlsxWriter 3.2.9](https://pypi.org/project/xlsxwriter/3.2.9/),
using its [dedicated string method](https://xlsxwriter.readthedocs.io/worksheet.html#worksheet-write-string).
[Generation receipt](generation-receipt.json) records the single native write
and its then-pending inspection state; the later inspection records the actual
stored-value checks. The package itself is not included. A real
Excel application roundtrip remains a separate, unperformed check.
