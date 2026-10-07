# Splits read off the panel, and what the restatement lag does and does not explain

Reproduce: `python3 src/split_events.py`. Code: `src/split_events.py`. Tests:
`tests/test_split_events.py`. Output: `data/split_events.csv`.

The event study has been blocked on two missing quantities, round dates and a split history.
This closes part of the second. The proposal came from the reviewer; the detector below differs
from his in three places, and each difference is a correction rather than a refinement.

## The signature

A share count is a count. When a company splits k for one, a holder that did not trade files
exactly k times as many shares at its next report date, so the balance ratio is k to the
precision of an integer. The price side is not exact and must not be treated as though it were:
the same filing usually carries a fresh mark, so the price falls by roughly 1/k and not by
exactly 1/k. Baron restated SpaceX at $57.41 in the same month Fidelity restated it at $56.00,
both from a tenfold share count.

So the balance is held to half a percent and the price side is asked only to rule out the
alternative: a purchase multiplies the balance and the position value together, a split
multiplies the balance and leaves the value alone. Requiring the price ratio to be 1/k within a
few percent — the rule as proposed — drops Baron from the SpaceX event and roughly halves the
sample.

## The three corrections

**Restatement is not simultaneous, so a one-month window is the wrong unit.** This is the
finding, not a detail of implementation. Across 29 confirmed events the median restatement span
is **30 days** and the longest is **92**; only **18 of 29** fit inside a single month. Fidelity
restated SpaceX across February, March and April 2022. T. Rowe restated Perplexity in March 2026
and ARK in April. Requiring one month would discard eleven events and, worse, would score the
desynchronisation as absence of a split.

**Confirmation counts houses, never registrants.** Four T. Rowe series restating Perplexity are
one confirmation. At the median event, counting registrants multiplies the count by **1.7×**;
on the Databricks event it is 47 registrants against **14 houses**, a factor of 3.4.

**Not every integer is a split ratio.** Carbon Health at k=99, Pine Private at k=127 and
Iron Horse II at k=9 are arithmetic that lands near an integer, not corporate actions.
`CANONICAL_K` flags the ratios companies actually split at; 26 of the 29 events are at one.
Delhivery at k=100 sits at the boundary and is what the reviewer independently flagged as a
probable redenomination.

One more the table shows on its own: five of the 29 events sit on a single date, 2019-12-31, all
at k=2 with a zero span. Five simultaneous two-for-one splits at the second report date of the
panel is not what that looks like; a filing-convention change is.

## What the detector finds

601 candidate fund-dates on 228 companies; **29 events confirmed by two or more houses**, 20 of
them at a canonical ratio. The largest:

| company | k | window | span (days) | funds | houses | registrants |
|---|---|---|---|---|---|---|
| Databricks | 3 | 2022-08-31 → 2022-10-31 | 61 | 72 | **14** | 47 |
| Checkr | 3 | 2022-05-31 → 2022-08-31 | 92 | 16 | 5 | 13 |
| Allbirds | 5 | 2019-12-31 → 2020-02-29 | 60 | 21 | 4 | 21 |
| Discord | 10 | 2026-02-28 → 2026-04-30 | 61 | 16 | 3 | 16 |
| SpaceX | 10 | 2022-02-28 → 2022-04-30 | 61 | 12 | 3 | 12 |
| SecurityScorecard | 3 | 2022-08-31 → 2022-09-30 | 30 | 9 | 2 | 9 |
| Seismic Software | 5 | 2021-03-31 → 2021-05-28 | 58 | 9 | 2 | 9 |
| Perplexity AI | 10 | 2026-03-31 → 2026-04-30 | 30 | 6 | 2 | 6 |

Databricks three-for-one in the autumn of 2022 is filed by fourteen independent houses inside
two months. That is an event, not an inference.

## What this adds to §4.2

§4.2 says that within a house the mark is one number. This says the same house is not one
number about the share count. Fidelity restated SpaceX across February, March and April 2022 —
one house, one corporate action, three report dates. Alger restated Databricks over two.

So the sharpened form is: **within a house the mark is one number at a date, and the share count
is not.** Houses differ not only in what they think a share is worth but in when they recognise
that the share has been redefined, and the second is visible in a field nobody reads for
disagreement.

## The consequence that did not hold

The proposal was that §5's 4× class guard is largely absorbing this — that houses which have
restated and houses which have not differ by exactly k, so the guard fires on a dating
difference and calls it a share class.

**It is real and it is small.** The guard drops 1,945 cells. **22 of them (1.1%)** sit inside a
restatement window. Conditioning on the companies that have a confirmed split at all, 21% of the
104 cells dropped there are inside a window — material for those names, and 104 cells of 1,945.
The guard is not mostly doing this, and the 31% of company-dates it discards does not shrink
appreciably if split desync is netted out.

## The validation, and why it can only run where the answer is already known

The mechanism predicts a number: at a date when one group has restated and another has not, the
price ratio between them should be exactly k. Twenty-five cells have both groups present. The
ratio lands within a tenth of k in two of them — Discord at 10.175 against k=10, and ROW:33217
at 2.040 against k=2.

The other twenty-three are not refutations, and saying so is not special pleading — it is the
same identification problem the paper has everywhere. The observed ratio is the split factor
multiplied by whatever the two groups genuinely disagree about, and on these cells the
disagreement is large: Checkr's 3.862 against k=3 is a 29% gap between houses on top of a
three-for-one. Nothing in the data separates the two. The validation confirms the mechanism
where disagreement is near zero and is uninformative where it is not.

## Where this leaves the event study

The price half is now partly sourced: for 29 company-events, a price on one side of a
restatement can be brought to the other by a factor several houses filed independently, rather
than by one taken from the press. That is a real unblocking and it is narrow — 29 events, and
the desynchronisation means the factor is dated to a window rather than to a day.

Round dates are no longer the blocker either: `src/round_dates.py` dates a round from the first
report month carrying a new series letter, calibrated against N-CSR to within 35 days on fourteen
of fifteen pairs. Both halves now come from filings. What remains is the study itself, and the
resolution it can be run at — a reporting month on each side, not a day.
