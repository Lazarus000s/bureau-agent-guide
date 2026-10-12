# Keep tags beside bibliography output

An agent preparing a public bibliography needs category tags and a readable
reference for each record. Choosing a citation-only export can leave the next
run without the categories it needs. This handoff makes the required fields,
format choice and unfinished checks explicit.

[Read the observed bibliography](rendered/actual-bibliography.txt) or its
[structured result with IDs and tags](rendered/rendered-result.json). On October12,
2026, one local citeproc-js run rendered these same three fictional books using
pinned APA and en-US resources. The native plain text omits typography such as
italic book titles; it is not a fully formatted APA document.

The original [planning Packet](handoff-packet.json) and [records](records.json)
remain unchanged. They preserve constructed citation illustrations, the request
template and pending real-library checks as they stood before this local run.
No Zotero library was read, no Zotero API request was sent and no customer result or
general APA conformance is claimed. [The dated render receipt](rendered/render-receipt.json)
identifies the processor, sources, result bytes and limits.

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

Before a real library handoff, retain the authorized source locator, actual item/version
metadata, raw-response hash and page coverage. A three-item response alone does
not prove completeness. Confirm actual tags and bibliography fields, then assess
citation output and safe rendering. `linkwrap=0` is not a markup sanitizer.
The Packet keeps these steps pending so another run can resume honestly.

## Keep the observed result for a later run

Save the [rendered folder](rendered/) with its [manifest](rendered/manifest.json)
and receipts. The manifest identifies five data files by exact byte length and
SHA256: the original records, native processor result, plain text, structured
ID/tag result and [saved HTML view](rendered/inert-view.html). Reading them needs
no Bureau account, library access or processor installation.

On return, compare those five saved files with the manifest. Match each
`rendered-result.json` row's `local_locator` to the original records and to the
processor's `entry_ids`; keep its exact tag array. The bibliography sorts the
institutional author before Mara Vale, so input row positions would attach the
wrong tags. `east, annex` remains one label, and the empty array remains explicit.

The [dated return verification](rendered/return-verification.json) records one
independent internal check of a fresh copy of these five files. It recovered all
three ID, citation and tag associations with the exact 210-byte bibliography.

This recovers the saved result and its associations. It does not rerun citeproc,
refresh a library or prove general APA conformance. The original planning Packet
still records the separate authorization, source and coverage work needed for a
real library handoff.

This addresses a [documented format-purpose question](https://forums.zotero.org/discussion/114048/tags-export-in-json),
answered in2024 with existing API/full-data options. The participants are not
Bureau customers. It is not a library-backup or migration tool; Zotero documents
[export limits](https://www.zotero.org/support/kb/exporting). No attachments,
notes, document citation links or ongoing sync are covered.

[Sources and observation limits](sources.json) accompany the Packet's SHA256
pins. Original records, plan and constructed text may be reused or adapted with
attribution to the Bureau of Lost Context; retain the fiction/provenance labels.
