# What the disagreement costs, and the three filters the tail forced

Reproduce: `python3 src/nav_wedge.py`. Code: `src/nav_wedge.py`. Tests: `tests/test_nav_wedge.py`.
Output: `data/nav_wedge.csv`, `data/nav_wedge_stats.csv`.

The reviewer's fifth point: a 12.1% between-house spread across $517.3B of booked value means
two sets of fund investors are credited with different net asset value for the same asset on
the same day, and Zitzewitz (2003) showed a NAV that is knowably wrong is exploitable. He
called it the only visible route above a measurement paper. This is that test.

It needed no new data. `NET_ASSETS` is on every row of the panel already.

## The measure

For each fund holding a company inside a comparable cell, reprice the position at the
cross-house consensus — the median of house medians, so a complex filing thirty series cannot
vote thirty times — and express the change in basis points of **that fund's own net assets**.

## The three filters, each added because the tail said so

A spread statistic survives a few contaminated cells inside a median. A NAV statistic does
not, because all of its content is in the tail. Each filter below was written after reading
the largest rows of the previous run, not before.

**One price per fund per company.** First run's largest wedge: JPMorgan on Claire's Stores,
$881 a share against a $12.50 consensus. JPMorgan files *two lines* for Claire's in each fund,
one at $10.00 and one at $1,765.66. Two prices under one issuer key are two instruments and
their value-weighted blend is not a price. Funds whose own lines disagree by more than 0.5%
are dropped.

**One series.** Second run's ten largest were all SpaceX: Baron at $1,294 against a $527
consensus, 2,227 bps of one fund's net assets. That is the multi-class structure §4.3 excludes
SpaceX for, and the 4× guard passes it at 2.5. Restricted to §3.3's cells that never name two
letters.

**Venture-backed only.** §5.2's label. The mixed-panel figure is reported beside it.

**A unit bug the first two exposed.** §5's cells are built on filing *lines*; a wedge is a
property of the *position*. Where a fund files one company twice the two units disagree, which
is precisely the Claire's case. Cell membership, the class guard and the consensus are all
rebuilt at the position unit here.

| selection | fund-positions | fund-dates | median \|wedge\| bps | max \|wedge\| bps | over 10 bps |
|---|---|---|---|---|---|
| all comparable cells | 33,886 | 13,010 | 0.06 | 402.6 | 658 |
| + one series only | 23,884 | 11,868 | 0.03 | 402.6 | 407 |
| **+ venture-backed only** | **9,631** | **3,704** | **0.21** | **91.0** | **173** |

## The answer, which is partly negative

9,631 fund-positions · 99 companies · 273 funds · 48 houses · 3,704 fund-dates · $126.9B
booked · $8.8B gross wedge.

| wedge over | fund-dates | share | distinct funds |
|---|---|---|---|
| 1 bp | 1,283 | 34.6% | 173 |
| 5 bp | 408 | 11.0% | 102 |
| **10 bp** | **173** | **4.7%** | **54** |
| 25 bp | 44 | 1.2% | 21 |
| 50 bp | 12 | 0.3% | 8 |
| 100 bp | 0 | 0.0% | 0 |

**Median fund-date: 0.21 basis points** — two *thousandths* of one percent. The largest is
91 bps and nothing reaches 100.

**Why, and the first answer was wrong.** The first draft said the reason was book size: a
private book is a median 0.21% of net assets. Its own arithmetic disagreed by twelve — 12% of
a 0.21% book is 2.5 bps, not 0.21 — and the coincidence of the two 0.21s is dimensional
(basis points against percent). The real reason is the mass at zero: **61.9%** of the 9,631
positions sit at the consensus to within a hundredth of a percent and **21.3%** of fund-dates
carry exactly zero. The median fund does not disagree at all.

**And the panel agrees more than the population does.** Median cell spread here is **4.3%**
against 10.1% for §5.2's venture cells: five funds, two houses, one series, one price per fund
and a venture label together select the widely held names, which are the herded ones. The
number is a lower bound.

What is not small is the concentration: 173 fund-dates on **54 distinct funds** exceed ten
basis points, and those funds are the ones that bought private companies in size.

So the disagreement is large as a fraction of the asset and small as a fraction of the fund.
That is the honest answer and the section says it in those words.

## Is it forecastable? Yes, weakly — and the obvious test overstates it

The naive design — does a house's deviation at *t* predict its own change from *t* to *t+1* —
is mechanically negative. Write a mark as value plus error: the house furthest above consensus
is selected partly on its error, and its next change carries that error back with a minus
sign. Regression to the mean produces "reversion" out of nothing.

So the test selects on the deviation at *t−1* and measures the change from *t* to *t+1*. Steps
where neither house re-marked are dropped, because most house-months carry no change at all
and a test full of zeros measures reporting frequency.

| design | cells | high house moves less | share | sign p (1-sided) | 2-sided |
|---|---|---|---|---|---|
| **selected on the previous date (unbiased)** | 453 | **246 of 448** | **54.9%** | **0.021** | 0.042 |
| selected on the same date (mechanically negative) | 518 | 306 of 516 | 59.3% | 1e-5 | 3e-5 |

**The naive design overstates reversion by 4.4 points.** Both are reported so the gap is a
number rather than a claim, and a test fails if they ever agree.

Against that, persistence: the slope of a house's deviation on its own lagged deviation is
**0.73** across all house-dates and **0.81** among those that have a side; **85%** of the
1,110 sided house-dates are on the same side one step later. Errors in the regressor attenuate
both slopes, so each is a floor.

**A house at the consensus has no side, and the first version counted it as agreeing with
itself.** In a cell with an odd number of houses one house IS the median, so its deviation is
exactly zero and `sign(0) == sign(0)` scored it as "same side". Those rows were half the
sample and the reported share was 70%. Corrected, it is 85% — larger, i.e. in the direction
that flatters the argument, which is why it is stated rather than quietly fixed.

**Float equality is out, and the selection needed it too.** The first version decided
`chg == 0`, `diff != 0` and `sign(a) == sign(b)` by raw equality, and a round-trip of the same
panel through the committed CSV — which loses two parts in 10^13 — moved the cell count from
498 to 481. Every such comparison now runs against `ZERO = 1e-9`. That was not enough on its
own: with 62% of positions AT the consensus, `idxmax` was breaking exact ties arbitrarily, so
cells whose houses are not distinguishable above the tolerance are skipped. A test asserts the
CSV path and the in-memory path now agree exactly.

A house above consensus is very likely still above it next quarter and slightly more likely
than not to have narrowed the gap. Persistent difference of view, weak pull to the middle.

## What is not done, and exactly what it needs

Whether anyone *acts* on the wedge. The test is whether funds carrying larger disputed private
books see different net flows or reported returns, and it needs
**`FUND_REPORTED_INFO.tsv`'s monthly total return and monthly sales, redemption and
reinvestment flow items** — the same table `src/nport_bulk.py` already opens for `NET_ASSETS`,
in the same quarterly archives, four column groups it does not currently keep.

It was not run here because `www.sec.gov` was unreachable from both the sandbox and the host
at the time of writing; no code for it is committed, because shipping an unrun harvester is
worse than naming the columns. The manuscript says the same thing in Appendix G.4.

## What the measure does not say

The consensus is not the truth. It is the middle of a set of opinions this paper spends five
sections showing to be persistently different, so a fund above consensus is not thereby
overstating its NAV. Appendix G.2 measures the *size of the disagreement expressed in NAV*, which is
what a fund board, an auditor and a regulator each need and none of them has; Appendix G.3 adds that
it does not resolve itself quickly.
