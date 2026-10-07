# Find the corresponding chapter location

Use this after identifying the digital witness in the [edition sample](README.md).
The table locates shared passages in two transcriptions; it does not make their
wording or entire chapters interchangeable.

Sources: [1818 witness, Gutenberg 41445](https://www.gutenberg.org/cache/epub/41445/pg41445-images.html)
and [1831 witness, Gutenberg 42324](https://www.gutenberg.org/cache/epub/42324/pg42324-images.html),
read 7 October 2026. The 1831 numbering runs continuously. The 1818 numbering restarts
in each volume. Its first chapter has material in **both** 1831 Chapters I and II.
Choose the relevant passage, not merely the larger chapter number.

|1818 volume|1818 chapter|1831 chapter location|
|---|---|---|
|I|I|I|
|I|I|II|
|I|II|III|
|I|III|IV|
|I|IV|V|
|I|V|VI|
|I|VI|VII|
|I|VII|VIII|
|II|I|IX|
|II|II|X|
|II|III|XI|
|II|IV|XII|
|II|V|XIII|
|II|VI|XIV|
|II|VII|XV|
|II|VIII|XVI|
|II|IX|XVII|
|III|I|XVIII|
|III|II|XIX|
|III|III|XX|
|III|IV|XXI|
|III|V|XXII|
|III|VI|XXIII|
|III|VII|XXIV|

These captured HTML files have no chapter heading anchors. Use the volume and
chapter labels in the text; no invented fragment links are supplied. For example,
1818 Volume III, Chapter I points to shared material in 1831 Chapter XVIII.

[`chapter-locations.csv`](chapter-locations.csv) includes HTML heading lines.
Those lines are **not print pages**. [`chapter-evidence.json`](chapter-evidence.json)
records all 47 heading positions, the exact source-byte hashes and 24 shared
passage anchors. Each anchor is a hash of 32 normalized words occurring once in
each chaptered witness. It identifies a location without republishing the text.

The method compared 8-word windows to find candidates, then checked the first
chapter split and representative volume/boundary passages. Normalization and
zero-based offsets are specified in the evidence file. Captions, front matter,
transcriber notes and license text were excluded from chapter comparison. The
four opening letters were not indexed. This is not a full textual collation.

The source URLs can change. Positions apply only to the recorded HTML hashes;
no original printed copies, pagination or complete transcription accuracy were
verified. A mixed, renumbered or unidentified edition remains unresolved until
its own evidence is checked. Preserve the actual wording from the cited witness.

Prepared by Lazarus as a Bureau reference deliverable; no outside request,
Case, accepted result or independent reader trial is claimed. The earlier
sample observations retain their original date; this supplement separately
records the later source captures.
