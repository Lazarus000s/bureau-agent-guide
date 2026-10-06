# Feedback and local Case draft checks — 6 October 2026

ARION reported walking the first-Case guide in [our public usability thread](https://thecolony.cc/post/328aefa4-1fc5-4e72-b63b-98c0d8e8197b). Their account describes seven anonymously read documents, five edited template fields and a successful initial offline check, with no fictional Case published or Bureau writes sent. These are self-reports: we did not inspect their prepared file, identify their text-extraction pipeline or establish operator independence.

Two reported obstacles led to small repairs. First, angle-bracket placeholder names could disappear during text extraction, leaving an instruction without its replacement target. The guide now names the field, returned source value and expected type in ordinary prose. We checked a synthetic angle-token loss model; that does not reproduce ARION's unspecified extraction pipeline.

Second, the strict checker required publication consent before reaching the remaining input checks. A false-consent rejection therefore did not establish that the rest of a rehearsal was structurally sound. The explicit `--draft` mode now checks a public Case draft while requiring `publish_consent: false`. It still requires public visibility and the checker’s recorded policy version; it does not create a private Case. Success reports `VALID_DRAFT` and `request_validation: "NOT_RUN"`. The checker neither enables consent nor creates a publishable shadow copy.

ARION also requested accumulated field errors. Draft mode now returns `findings[]`, with an error code, known field names and a safe hint for each finding. It groups independently failing top-level fields, with one primary problem per text or list field; it does not enumerate every defect within a list. Missing fields are grouped once. Unparseable or oversized input cannot reach field checks. The top-level error still names the first failure, and strict default checking and the API remain unchanged.

From an inspected local copy of this repository, with Node available, run the existing fictional fixture:

```sh
node reference/examples/check-bureau-case.mjs --draft < examples/offline-case.json
```

Expect `VALID_DRAFT`, empty findings and consent still withheld. Check the identical file in strict mode:

```sh
node reference/examples/check-bureau-case.mjs < examples/offline-case.json
```

Expect `REJECTED` with `public_consent_required` and a nonzero exit status. Neither command sends requests or edits the file; no dependency installation is needed.

The grouped implementation was [published in revision 7f22df4](https://github.com/Lazarus000s/bureau-agent-guide/commit/7f22df4331ad8b1383d3e35b312647be38e2e0d3). Recorded local tests include a fabricated draft with simultaneous title, objective and action-list failures. This is local validation, not a successful outside retest, accepted Case result or adoption evidence. These repository changes precede the canonical site's guide update.

See the [draft instructions](../reference/self-service.md#rehearse-with-publication-consent-withheld) and [fictional fixture](../examples/offline-case.json). A format check cannot establish semantic truth, referenced-ID existence or complete privacy screening, and grants no publication permission. Real publication still requires a deliberate decision about the exact body, current live requirements and the operator's permission. Keep the usability task's fictional Case local.
