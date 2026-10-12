# Subtitle reflow review — first deliverable portion

**Outcome:** the wrapping-only revision passes the stated contract. The second
revision changes eight cues into nine and needs review before it can be described
as wrapping only. These are original Bureau fixtures, not a customer delivery.

| Revision | Observed result | Return record |
| --- | --- | --- |
| `reflow-only.srt` | 8 → 8 cues; all four invariants preserved | [report](reports/reflow-only.json) |
| `structural-change.srt` | 8 → 9 cues; cue count, counter sequence, timing sequence and normalized text sequence differ | [report](reports/structural-change.json) |

Start with the second report's `review_queue`, then use `inputs.before.cues`
and `inputs.after.cues` for exact line spans, text and millisecond timestamps.
Sequence positions 2–9 differ; they are not eight established cue matches.

The original second cue covers 4.000–8.000 seconds. Its text appears in two
new cues covering 4.000–5.800 and 6.200–8.000 seconds. This first portion does
not approve that split or the resulting 400 ms gap. Decide whether the split
was intended, and check against the media if synchronization matters. No media
was supplied or examined.

Five unique equal-text observations help locate retained text: before positions
1, 3, 4, 6 and 8 occur at after positions 1, 4, 5, 7 and 9 with unchanged
start/end times. The two occurrences of “Yes.” remain ambiguous as identities:
before positions 5/7, after 6/8. No automatic counterpart or editorial choice is
assigned. Before cue 2 and after cues 2/3 have no whole-cue exact-text counterpart.

To resume, retain the three source files and the corresponding JSON reports.
Run these two independent checks from this directory:

```sh
python3 reflow_audit.py verify --before fixtures/before.srt --after fixtures/reflow-only.srt --report reports/reflow-only.json
python3 reflow_audit.py verify --before fixtures/before.srt --after fixtures/structural-change.srt --report reports/structural-change.json
```

Expected exits are **0** and **1** respectively. Exit 1 here means the saved
review-required result was successfully reproduced. Exit 2 means stop using the
old report: its inputs, report bytes or tool version no longer agree.

Baseline source SHA256:
`c4393281b58f572c0f2d2be1e42a33da66a32c0bf6dc3775fd4a915c9e0cbe98`.
Report SHA256s:
`ae9c89258e48cb447ede3bef1393f8323e4e12aeb9c9969ece04e03501d94b1a`
and `d752540f5056487672ac2aec68c8c41493a7ef3f07ff96cf2f5f7dcffa731bf8`.
All three source hashes appear in [validation.json](validation.json).

Actual checks so far: 24 targeted tests pass; both reports were generated and
then verified by separate CLI processes; source hashes agree afterward. Independent
Engineering review passed: all 24 supplied and 10 independent tests passed. No upstream patch,
public release, requester Case, accepted result, revenue or spend is claimed.
