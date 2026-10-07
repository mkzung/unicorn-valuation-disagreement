# Round dates from the first appearance of a series letter

Reproduce: `python3 src/round_dates.py`. Code: `src/round_dates.py`. Tests:
`tests/test_round_dates.py`. Output: `data/round_dates.csv`.

Three sources have been tried for round dates and all three failed. Form D misses the large
rounds, which go out under Section 4(a)(2). N-CSR gives an acquisition date, but it is the
fund's entry rather than the round. The press gives a date this repository will not cite.

The fourth was already on disk. Filers name the series in the security title — "SER H PC PP",
"Class B PP" — so the first report date on which a new letter appears anywhere in the population
bounds the round from above. 32.1% of population rows carry a letter, and the proposal came from
the reviewer.

## The calibration

Against the earliest N-CSR acquisition date for the same company and series: two document types,
one structured and already downloaded, the other parsed out of an HTML schedule.

| company | series | N-CSR entry | first in N-PORT | gap (days) | funds | houses |
|---|---|---|---|---|---|---|
| Anthropic | F | 2025-08-29 | 2025-08-31 | **2** | 35 | 2 |
| Anthropic | G-1 | 2026-01-27 | 2026-01-31 | **4** | 7 | 4 |
| Databricks | F | 2019-10-22 | 2019-10-31 | **9** | 22 | 7 |
| Databricks | G | 2021-02-01 | 2021-02-26 | **25** | 61 | 13 |
| Databricks | H | 2021-08-31 | 2021-08-31 | **0** | 51 | 10 |
| Databricks | I | 2023-09-14 | 2023-09-30 | **16** | 38 | 7 |
| Databricks | J | 2024-12-17 | 2024-12-31 | **14** | 37 | 9 |
| Databricks | D | 2025-03-12 | 2025-03-31 | **19** | 4 | 3 |
| Databricks | K | 2025-09-08 | 2025-09-30 | **22** | 29 | 5 |
| Databricks | L | 2025-12-11 | 2025-12-31 | **20** | 39 | 7 |
| OpenAI | A | 2025-10-28 | 2025-11-30 | **33** | 17 | 2 |
| Stripe | B | 2019-12-17 | 2019-12-31 | **14** | 48 | 14 |
| Stripe | H | 2021-03-15 | 2021-03-31 | **16** | 30 | 3 |
| Stripe | I | 2023-03-15 | 2023-03-31 | **16** | 15 | 4 |
| Anthropic | G | 2026-03-31 | 2026-01-31 | **−59** | 37 | 3 |

**14 of 15 dated pairs land inside 35 days. Median gap 16, worst inside 33, nearest outside 59.**
The tolerance sits in that gap and is read off it, the way the listing-date threshold was read
off the 82/258 gap, rather than chosen.

## The two rules the calibration dictated

**Two houses.** Every pair that misses by months rests on a single house: Discord Series G at
+670 days, SpaceX B at +570, OpenAI A-2 at +426 and A-3 at +259, Stripe G at +62, Databricks
B, C and E at +49. A letter one fund reports is that fund's holding. A letter several houses
report in the same quarter is a round. Eight of the twenty-four calibration pairs fail this; a ninth, SpaceX Series A, is
censored rather than thin.

**Censoring.** A series first seen on the panel's own first date is not dated, it is censored.
SpaceX Series A first appears on 2019-09-30 against an N-CSR entry of 2022-06-08, which is not a
982-day error — it is a series that existed before the window.

Houses are counted with `fund_complex.confirmations`, which exists because three metrics in a
row have been built here whose first version counted registrants.

## The sign of the error is not guaranteed

The natural claim is that a fund can only report a series after it exists, so the N-PORT date is
at or after the round and the error has a known sign. **Anthropic Series G breaks it**: the
series appears in N-PORT in January 2026 and the earliest N-CSR entry for it is 31 March 2026,
a gap of −59 days on a pair with 37 funds across 3 houses. It is not censored and it is not thin.

The reason is structural. N-PORT covers every registered fund; the N-CSR harvest covers the ten
§4.3 names and the filers who happen to schedule them. So the N-CSR date is one filer's purchase
and can be later than the series' arrival in the filing system. Neither quantity is the round
close. What licenses the N-PORT date as a proxy is the agreement on the clean cases at monthly
resolution, not an argument about which side the error falls on.

## What it reaches

**425 company-series pairs on 288 companies** clear both rules — against ten companies with any
N-CSR coverage at all. That is the point of calibrating on a small set: the rule then applies
where no schedule was ever read.

## What it cannot see

Rounds that create no new class: extensions, SAFEs, secondaries, and any priced round that
reuses an existing letter. Resolution is the reporting month, not the day. And a letter can
appear because one fund bought an old series on the secondary market, which the two-house rule
removes on average and not by construction.


## Price coordination as a dating rule: tried, and it dates worse

The count rule — two houses reporting a new letter — was the obvious thing to improve on, because
it discards 88% of the letters in the panel and the event study's magnitude turned out to rest on
it. The natural replacement uses information the count rule ignores: a round creates a *price*, so
a round month should be one where two or more houses report the new series **at prices that
agree**. It is self-validating in a way a count is not, and it should date better.

It does not. Implemented as "the first month with two or more houses whose median prices lie
within 2% of each other":

| | count rule | coordination rule |
|---|---|---|
| pairs dated | 425 | 404 (331 uncensored) |
| non-first rounds | 137 | 115 |
| calibration pairs inside 35 days | **14 of 15** | **11 of 15** |
| median absolute gap to N-CSR | **16 days** | 20 days |
| step on the non-first set | −1.08, p=0.0023 | **−0.03, p=0.043** |

It fixes one case and breaks four. Anthropic Series G goes from −59 days to **0**, which is what
the rule was supposed to do. But Databricks J moves to +45, Anthropic G-1 to +63, Databricks F to
+70 and Databricks D to +80, all of which were inside 35 days under the count rule.

The reason is the same desynchronisation `split_events` measured: houses report on different
schedules, so requiring two of them to agree *in one month* pushes the date one to three months
past the round. Coordination is a property of the second reporting house's calendar, not of the
company's. The count rule takes the first house to report and is therefore closer to the event;
the coordination rule waits for the second and is systematically late.

The magnitude disappears with it — 56 events, median −0.03, 31 of 49 negative, p=0.043 — which
is what a misplaced anchor does to a size while leaving a sign behind, and is consistent with
everything else here.

These numbers were computed once by hand when this note was written, and they were wrong by the
time the event study grew a tie tolerance: the count-rule column kept p=0.0016 (the pre-tolerance
37 of 52) while every other printing of that statistic had moved to 0.0023. The rule now lives in
`round_dates.coordination_dated`, both columns are recomputed by the pipeline, and every figure in
this table is registered, so the two halves cannot drift apart again.

**So the count rule stands, and the ladder's limit stands with it.** The event study rests on a
dating bar that discards most of the data, the alternative that would have justified a looser bar
dates worse, and the honest reading of the result is unchanged: a sign that is robust and a
magnitude that is not.
