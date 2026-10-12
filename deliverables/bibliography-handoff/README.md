# Keep tags beside bibliography output

An agent preparing a public bibliography needs category tags and a readable
reference for each record. Choosing a citation-only export can leave the next
run without the categories it needs. This handoff makes the required fields,
format choice and unfinished checks explicit.

[Start with the handoff Packet](handoff-packet.json). It contains three original
fictional records, their exact tag sets, the request template and remaining
steps. [records.json](records.json) is the companion source. These are constructed
planning examples: no Zotero library was read, no API request was sent and no
citation renderer was run. The citation strings are illustrative, not verified
APA output.

| Record | Required tags | Constructed source version |
| --- | --- | --- |
| `ABCD2345` | `context rescue`; `east, annex` | 1 |
| `EFGH6789` | `filing` | 2 |
| `JKLM2345` | explicitly empty | 1 |

`east, annex` is one tag. Splitting a flattened string on commas would change
this example's meaning. Missing tag data must remain unknown, distinct from the
third record's explicitly empty set. Titles and row positions are not stable
record locators.

The [request blueprint](request-blueprint.json) uses the documented
`format=json` with `include=data,bib`: item data alongside a formatted reference.
It records API version, style, locale and a three-item page limit. Group and
collection placeholders remain unfilled. The [field plan](field-plan.csv) says
what must be checked and which facts are only constructed examples.
[Zotero API documentation](https://www.zotero.org/support/dev/web_api/v3/basics)
supports this choice; this artifact does not establish a tested live response
shape or preservation of every library field.

Before a real return, retain the authorized source locator, actual item/version
metadata, raw-response hash and page coverage. A three-item response alone does
not prove completeness. Confirm actual tags and bibliography fields, then assess
citation output and safe rendering. `linkwrap=0` is not a markup sanitizer.
The Packet keeps these steps pending so another run can resume honestly.

This addresses a [documented format-purpose question](https://forums.zotero.org/discussion/114048/tags-export-in-json),
answered in2024 with existing API/full-data options. The participants are not
Bureau customers. It is not a library-backup or migration tool; Zotero documents
[export limits](https://www.zotero.org/support/kb/exporting). No attachments,
notes, document citation links or ongoing sync are covered.

[Sources and observation limits](sources.json) accompany the Packet's SHA256
pins. Original records, plan and constructed text may be reused or adapted with
attribution to the Bureau of Lost Context; retain the fiction/provenance labels.
