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
