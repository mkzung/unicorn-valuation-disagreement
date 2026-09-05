# Item D: disagreement collapses at a round, once the anchor is separated from the window

Reproduce: `python3 src/round_event_study.py`. Code: `src/round_event_study.py`. Tests:
`tests/test_round_event_study.py`. Output: `data/round_event_study.csv`.

## The first design, and why its null was right

Anchored on the most recent round, looking only forward, the pooled profile ran from 0.01% at the
round month to 10.71% nine months later — and the within-company column was flat at every
horizon. A phase-randomised null reproduced it 18% of the time, so the study was reported as a
measured null.

The reason was not noise. **A company enters this panel because a fund bought it in a round**, so
for a company's FIRST round, months-since-round and months-since-entering-the-panel are the same
quantity. Any anchor early in the observation window reproduces the profile.

## Two changes, and they separate the hypotheses

**Non-first rounds only.** For a company already in the panel, the next round is not the reason it
is there. The anchor moves; the window does not.

**A symmetric window.** A mechanism that says a round resolves disagreement predicts a
discontinuity at zero. The confound predicts a monotone trend and no step. Looking only forward
cannot tell those apart; looking both ways can.

## What the symmetric profile shows

478 guarded cells on 47 companies within six months before and twelve after a non-first round;
138 cells on 31 companies before, 340 on 47 after.

| months to round | cells | pooled median | within-company |
|---|---|---|---|
| −5 | 15 | 21.94% | **+2.25** |
| −2 | 24 | 12.55% | **+1.75** |
| −1 | 30 | 8.34% | **+1.25** |
| **0** | 49 | **0.01%** | **−0.90** |
| **1** | 37 | **0.00%** | **−2.88** |
| **2** | 35 | **0.05%** | −0.00 |
| 7 | 18 | 20.03% | **+5.72** |
| 10 | 13 | 15.40% | **+8.10** |
| 11 | 15 | 17.64% | **+10.86** |

The within-company column now moves, which is the whole difference from the first design. It is
positive before the round, negative at it, and rises to eleven points a year after.

## The step, and what the null does and does not say

Months −3..−1 against 0..2, paired inside each company, 31 companies: median 5.22% before,
**0.00% after**, step **−2.52 points**, narrower after in **24 of 30 untied**. Signed-rank
p<0.001, **sign test p=0.0007**.

The phase-randomised null matches or beats the observed step in **0 of 400** draws. That number
is weaker than it looks and the reason is worth stating: with a random anchor both bands draw
from one distribution, most companies' paired difference is exactly zero, and the median across
companies is zero in nearly every draw. So "0 of 400" says the observed step is negative and the
null never is. The sign test is the statistic here whose null does not collapse.

The contrast with the first design's statistic on the same sample is the evidence: near-versus-far
gives −7.77 points at p=0.010 and is still reproduced by **28%** of random placements, while the
step at zero is not reproduced at all. Random anchors make a trend; only the round makes a jump.

## The objection that would have made it arithmetic

If a round-month cell consisted only of funds that had just bought at the round price, they would
agree because they had all paid the same, and nothing about valuation would follow. Across the 49
round-month cells the newly priced series is a **median 28%** of the rows and the whole cell in
**none** of them. The convergence is over the company's whole position, not over the security
that has just traded.

## The cell does not get wider across the round

The spread is max over min of house medians, so it rises with the number of houses compared. If a
round brought new buyers in, the cells after it would be wider by composition and part of the step
would be arithmetic. This is the first question a referee who knows what a range statistic does
will ask, and the reviewer asked it before anything else.

Median houses per cell: **4.0 before the round against 4.0 after**, Mann-Whitney **p=0.91**, and
the month-by-month medians take two distinct values across the whole nineteen-month window. The
composition does not move. (The reviewer's own run gave 3.0 and p=0.87 on a slightly different
frame — before restatement windows are dropped and with the backward rather than nearest match —
and reaches the same conclusion.)

## How fast agreement decays, and the part of it the round owns

The within-company deviation runs −2.88 at month one and +10.86 at month eleven, so there is a
rate in here. Fitted per company over months 0..12 and taken as the median across companies:
**+1.39 points a month**, rising in 26 of 38, sign test p=0.017.

A slope is a trend, and a trend is what the phase null reproduces for the near-far statistic, so
this one has to clear the same null. It does — 2% of random placements match or beat it — but the
null's own median slope is **+0.34 points a month**, which is the general within-window drift. So
the number to quote is not the raw slope:

> **A round buys house agreement for about a quarter, after which disagreement rebuilds at
> roughly 1.4 points a month, of which about one point is attributable to the round rather than
> to the drift any anchor produces.**

That is a dated, filing-sourced rate, and it is the paper's second dynamic quantity beside the
−62% drawdown and +171% recovery of Appendix C.1.

## What this does to §4.3

§4.3 reports a bimodal picture: names with a fresh believed round are herded, stale ones are
dispersed, and it reads as two kinds of company. The trough says otherwise. The same company is
herded in the month it prices a round and dispersed a year later, so the bimodality is a snapshot
of a distribution of companies over one phase variable rather than two populations.

That is worth more than either observation alone: it converts §4.3 from a description into a
dynamic, and it explains why the two modes never separated cleanly on any company characteristic
— they are not a company characteristic.

## The step repeats inside one company, which a trend cannot do

31 companies was the standing complaint, and the answer is not more companies but more anchors
inside the ones there are. A company with several dated non-first rounds carries the anchor to
several places in its own window; a company-level time trend can produce a step wherever the
window starts and cannot produce one at each round.

**36 rounds on 13 companies, 11 of them carrying two or more.** Median step **−2.26 points**,
negative at **25 of 35 untied rounds**, sign test **p=0.0083**. Negative at *every one* of its
rounds in **5 companies**.

## The placebo, which answers the timing objection better than a null can

Non-first rounds are not randomly timed — companies raise when the market is open — so a null
that moves the anchor to a random date does not test the objection. A placebo does. Shift every
anchor by a fixed number of months and the calendar month, the market conditions and the
company's own filing rhythm all survive; only the event is removed.

| anchor | events | companies | median step | negative / untied | sign p |
|---|---|---|---|---|---|
| **the round** | 54 | 31 | **−1.08** | **37 / 52** | **0.002** |
| six months before | 39 | 22 | 0.000 | 15 / 33 | 0.757 |
| six months after | 65 | 37 | **+6.48** | 20 / 58 | 0.994 |
| twelve months after | 47 | 30 | 0.000 | 14 / 37 | 0.951 |

At the round the step is there. At every shifted anchor it is gone — a coin flip at 15 of 33 and
14 of 37 — or reversed.

The reversal is the part worth reading twice. Six months after a round the anchor's "before" band
sits in the rebuild, so the statistic should come out *positive*, and it does: **+6.48 points**.
The rebuild rate was measured independently at about 1.4 points a month, which over the five
months the bands span predicts roughly seven. The placebo does not merely fail to reproduce the
step; it fails in the direction and the magnitude the decay rate says it should.

Two things to keep honest about it. The medians at −6 and +12 are exactly 0.000, which is the
same degeneracy the step's own null has — most paired differences are zero — so the sign counts
carry the argument there, not the medians. And the shifted anchors have different event counts,
because moving the anchor moves which cells fall inside the bands; the comparison is between
statistics on overlapping samples, not on one fixed sample.

## The event selection carries the result, and which filter does

The reviewer could not reproduce the placebo table from a naive event list, and at a wider
selection found the step gone. He is right, and the sensitivity is printed here rather than
described. `selection_ladder()` reproduces it.

The funnel: **5,864** company-series pairs carry a letter, **425** are dated (two houses, not
censored), **137** of those are non-first, and **54** have guarded cells in both bands.

| selection | events | median step | negative / untied | sign p |
|---|---|---|---|---|
| dated, non-first, restatement out, guarded | 54 | **−1.08** | 37 / 52 | **0.0016** |
| keep restatement windows | 55 | −0.90 | 37 / 53 | 0.0027 |
| all cells, not only guarded | 54 | −1.08 | 37 / 52 | 0.0016 |
| admit first rounds too | 69 | −0.01 | 46 / 66 | 0.0009 |
| **drop the two-house bar** | 120 | **−0.00** | 65 / 112 | **0.054** |
| drop it and keep restatement | 124 | −0.00 | 67 / 116 | 0.057 |

Two filters turn out not to matter at all: restatement windows move the median by a tenth of a
point, and restricting to guarded cells changes nothing to four decimals. **The two-house bar on
the round date is what carries it.**

That bar was not chosen here. It was read off the N-CSR calibration two rounds before this
statistic existed, and the eight one-house pairs it excludes missed the N-CSR acquisition date by
**49 to 670 days** — Discord Series G at +670, SpaceX B at +570, OpenAI A-2 at +426. Admitting
them does not add rounds; it adds anchors placed months away from the event, and a misplaced
anchor smears a step by construction.

**But the limit is real and is stated as one.** At the widest selection the sign survives — 65 of
112 negative, 58% — and the magnitude does not: the median step is zero to six decimals and the
sign test returns p=0.054. Anyone who does not accept the
two-house bar as a round-dating rule should read this result as a sign with no reliable size.

## The up/down split, and the test this panel cannot run

The endogeneity a placebo cannot reach is that the company chooses when to raise. The reviewer's
discriminator is the right one: split on the change in the median price per share — a level, not
a spread, so not the dependent variable in disguise. If houses converge because the news is good
the step lives in the up rounds; if they converge because a price now exists it lives in both.

| rounds | events | median step | negative / untied | sign p |
|---|---|---|---|---|
| up | 47 | **−1.26** | 34 / 45 | **0.0004** |
| down | **8** | +1.20 | 3 / 8 | 0.86 |
| all | 55 | −0.90 | 37 / 53 | 0.0027 |

**Eight down rounds is not a test.** The step is measured almost entirely on rounds that raised
the price, and the sign in the down rounds is opposite, which on eight events means nothing in
either direction. So the discriminating test is not available on this panel, and the reading
"houses converge on good news" is **not excluded**. That is a limitation of the result, not a
detail of it, and it sits above the endogeneity caveat rather than beside it.

What would run it is more down rounds, which means either a longer panel through a full
down-cycle or a lower bar on what counts as a dated round — and the second is exactly the trade
the ladder above prices.

## What this is, and what it is not

Read with the two rows above in front of it: it is evidence that between-house disagreement collapses in the quarter a company prices a round
and rebuilds over the following year, on 31 companies, at monthly resolution, with the anchor
separated from panel entry.

It is not causal identification. Non-first rounds are not randomly timed — companies raise when
the market is open — so the null tests placement inside a company's own dates and not the
decision to raise. And 31 companies is a small sample for a result this clean; the honest next
step is more companies with several dated rounds, which `round_dates` supplies at 137 companies
with three or more.
