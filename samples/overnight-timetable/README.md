# Which day owns 25:10?

A small Bureau handoff for an overnight timetable question. Every event here
is **constructed**. These files are not a transit feed, current timetable,
travel recommendation or evidence of a customer request.

Keep the service date when carrying an extended-hour value into another run.
In example T03, `20261007` and `25:10:00` produce a local display on **October 8**,
while the source service date remains **October 7**. A clock-only note loses that
distinction.

## The worked result

All calculated rows use `Europe/Berlin` and an explicitly assumed active service.
The [GTFS Time definition](https://gtfs.org/documentation/schedule/reference/#field-types)
uses a service-day noon basis. For this literal-reference illustration:

1. Express noon on the service date in the agency zone, then convert to UTC.
2. Subtract 43,200 seconds; add the original extended-hour value as seconds.
3. Convert the resulting instant to the local display. Keep both representations.

[Stop times use the agency zone](https://gtfs.org/documentation/schedule/reference/#stop_timestxt).
An unrelated stop-zone value is not substituted when the agency zone is missing.

| ID | Service date | Original time | Derived UTC | Local display |
| --- | --- | --- | --- | --- |
| T01 | 20261007 | 23:50:00 | Oct 7 21:50Z | Oct 7 23:50 +02:00 |
| T02 | 20261007 | 24:10:00 | Oct 7 22:10Z | Oct 8 00:10 +02:00 |
| T03 | 20261007 | 25:10:00 | Oct 7 23:10Z | Oct 8 01:10 +02:00 |
| T04 | 20260329 | 01:30:00 | Mar 28 23:30Z | Mar 29 00:30 +01:00 |
| T05 | 20260329 | 02:30:00 | Mar 29 00:30Z | Mar 29 01:30 +01:00 |
| T06 | 20260329 | 03:30:00 | Mar 29 01:30Z | Mar 29 03:30 +02:00 |
| T07 | 20261024 | 26:30:00 | Oct 25 00:30Z | Oct 25 02:30 +02:00 |
| T08 | 20261025 | 01:30:00 | Oct 25 00:30Z | Oct 25 02:30 +02:00 |
| T09 | 20261025 | 02:30:00 | Oct 25 01:30Z | Oct 25 02:30 +01:00 |
| T10 | 20261024 | 27:30:00 | Oct 25 01:30Z | Oct 25 02:30 +01:00 |

All dates in the table are 2026. Full ISO timestamps, anchors, second counts and
fold values are in [result.csv](result.csv). T08 and T09 show the same wall-clock
reading but are an hour apart. T07/T08 and T09/T10 instead share instants while
retaining different service dates. Equal timestamps alone do not identify a
duplicate trip.

The spring examples intentionally distinguish the original GTFS value from a
wall-clock reading. The reference calculation does not fill the missing local
02:30 with an invented observation. A real producer's convention needs its own
evidence: [GTFS issue 325](https://github.com/google/transit/issues/325) records a
historical concern about transition-day interpretation. Its open/stale label is
not a current request to the Bureau or a universal implementation guarantee.

## What stays unresolved

Five additional constructed inputs retain an explicit decision instead of an
invented scheduled instant:

| ID | Missing or different context | Decision |
| --- | --- | --- |
| U01 | No service date | Ask for the source date. |
| U02 | No agency zone; a stop zone is supplied | Ask for the agency zone. |
| U03 | Service activity unknown | Obtain the public calendar evidence. |
| U04 | A constructed calendar exception removes service | Mark inactive under that assumption. |
| U05 | Local wall-clock 02:30 with no fold/offset | Clarify field meaning and which occurrence. |

These decisions are about the supplied examples. They do not classify a real
feed or establish actual service availability.

## Carry the result forward

- [input.json](input.json) preserves the original constructed values and assumptions.
- [result-packet.json](result-packet.json) is a complete portable result body with
  all fifteen inputs/results, source map, rule, time-zone data version and limits.
- [sources.json](sources.json) identifies the reference, historical issue and
  [Python time-zone documentation](https://docs.python.org/3.12/library/zoneinfo.html).
- [request-draft.json](request-draft.json) is a fictional local Case example with
  publication consent withheld. Keep this example local.

The calculations used Python 3.12.3, tzdata 2026c, and the recorded Berlin zone-file
hash. Ten manually specified UTC expectations and a separate GNU date rendering
check agree; both implementations use the same local time-zone data. This is
local verification, not an independent transit-operator trial. The example does
not cover frequency service, fares, real-time updates, negative hours or every
time zone.

For an actual public timetable ambiguity, the bounded Bureau offer is one
source-linked conversion or an explicit unresolved result through your own
authorized [Case](../../reference/self-service.md#open-one-case). Supply the exact
public feed version, trip/stop reference, service date, agency zone, original
value and the decision you need. Preserve the calendar evidence and any producer
convention. Do not include private journeys or publish this fiction as a proxy
participant. No paid service or operator endorsement is implied.
