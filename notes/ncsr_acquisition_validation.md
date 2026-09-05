# N-CSR acquisition dates and cost — the sensor, and what it can carry

**Status: built, validated, and not yet in the manuscript.** `src/ncsr_acquisitions.py`
produces `data/ncsr_acquisitions.csv`; nothing in the paper quotes it. This file records what
the source gives, what it does not, and the one result the current harvest supports.

## Why here rather than Form D

Form D failed its validation because the largest private rounds are placed under Section
4(a)(2) and leave no Reg D trace (`notes/form_d_validation.md`). N-CSR is the other side of
the same transaction. Regulation S-X requires the schedule of investments to state, for each
restricted security, the date it was acquired and what it cost. N-PORT carries neither.

Verified on the filing before any code was written around it — ARK Venture Fund, N-CSR of 8
October 2024, accession `0001213900-24-086293`:

| holding | acquired | shares | cost | value | cost/share | mark/share |
| --- | --- | --- | --- | --- | --- | --- |
| Space Exploration Technologies | 10/31/23 | 75,356 | $6,999,961 | $7,309,485 | $92.89 | $97.00 |
| Discord | 11/14/22 | 11,744 | $2,723,641 | $2,606,463 | $231.92 | $221.94 |
| Epic Games | 9/23/22 | 6,560 | $3,133,309 | $3,664,071 | $477.64 | $558.55 |
| Databricks | 9/23/22 | 27,922 | $400,000 | $2,023,507 | $14.33 | $72.47 |
| OpenAI Global | 7/31/24 | 5,797 | $1,000,000 | $1,000,000 | $172.50 | $172.50 |

Databricks at $14.33 is the source warning about itself: that position arrived through the
MosaicML acquisition in stock, per the filing's own footnote, so cost is the fund's entry and
only sometimes a round price.

## The parse, and the version of it that was wrong

The first harvester read the three numbers after the date as shares, cost and value, which
is the order Regulation S-X lists them in and the order ARK uses. Capital Group prints cost,
value and percent of net assets and puts no share count in the row at all, so the same code
reported Anthropic at $4.18 a share against a mark of zero. Eleven of thirteen rows were that
error and the extract was discarded rather than committed.

The parser now reads the header and places columns by where each label appears in it, over
three filers with three layouts:

| filer | header | shares in the row | units |
| --- | --- | --- | --- |
| ARK Venture Fund | Acquisition Date · Shares/Principal/Units · Cost · Value | yes | dollars |
| Capital Group | Acquisition date(s) · Cost (000) · Value (000) · Percent of net assets | no | thousands |
| Destiny Tech100 | Acquisition Date · Cost · Value | no | dollars |

Four smaller traps, each of which silently dropped rows: `Acquisition <br/>Date` is one label
with markup inside it; a security title containing the word "shares" reads as a fifth column
heading unless header labels are required to be adjacent; `$98,961` in one cell and `$` in
its own cell are the same number; and `12/17/24` beside `12/17/2024` for the same lot at two
filers returns NaT from the default date parser, which removed sixteen of thirty-six rows and
every row that made a lot cross-filer.

## What the harvest holds

The cap is gone. Ten §4.3 names, every N-CSR and N-CSRS whose schedule of investments
names them: **767 schedule rows, 10 companies, 44 registrants, 425 lot-period-series.** 155
rows carry a share count, so an entry price per share exists on those and a markup on all 767.

EDGAR's full-text index accepts two required phrases,
so every query now also asks for the schedule's own column header — `"Discord"` alone returns
1,491 N-CSRs, nearly all of them the English word, and `"Discord" "acquisition date"` returns
179, which are the ones a downloader would have kept anyway. Both spellings are used, because
the index matches tokens and "dates" is not "date". Three further changes paid for the rest:
the index hit names the document the phrase was found in, so one fetch replaces an accession
listing plus two speculative downloads; only whole tables that name a target are handed to the
parser, which took the parse from tens of seconds a document to tenths; and four threads run
at three orders of magnitude below SEC's published rate ceiling.

A prefilter that is not a superset of the harvest it replaces is a silent sample cut, so
`validate_prefilter` asks EDGAR for the prefiltered accession set and looks for accessions in
the committed extract that are missing from it. Across all ten companies: **zero missed.**

| | at the cap of 40 | uncapped |
| --- | --- | --- |
| schedule rows | 190 | **767** |
| registrants | 25 | **44** |
| rows with a share count | 29 | **155** |
| lot-period-series with 2+ independent books | 1 | **45** |

## A defect in the paper's own house map, found from this side

The first run of this harvest reported four cross-house lots. One of them was Canva acquired
26 August 2021, held by "Capital Group" and by "EUPAC FUND" at markups agreeing to a
thousandth of a point — which is what one house looks like, not two. EUPAC Fund is the
EuroPacific Growth Fund, and `fund_complex` mapped the full name and not the abbreviation.

That is not a defect in this module. The population panel carries **191 rows** filed under
the short name, and in **nine cells** — including one of §4.3's ten companies — Capital Group
was being counted as two houses. The rule went into `fund_complex`, and at the time the panel
did not move, because none of the nine crossed the ≥2-house bar.

The map's bias is one-directional and this is the direction: an unmapped registrant makes one
house look like two, which inflates apparent disagreement. §5 already says the map "fails
closed" and covers 98% of booked value by rule. The way it was found is what mattered — a
second document type, asked about the same houses, disagreed with the first.

## The same question asked of §5's own panel, and five more affiliates

The sleeve problem below made the general form of it obvious, so it was asked of the
population panel directly. `population.duplicate_books` looks for one holding reported twice:
the same company, the same report date, **the same share count and the same value to the
cent**, under two house labels. Two houses printing one price per share is anchoring, which is
what §5 measures. Two houses printing one price per share *and* one share count is one
portfolio seen twice.

It found 375 such holdings, and behind them five registrant groups that are plainly one house
and were not merged:

| pairs found | registrants |
| --- | --- |
| 54 | Apollo Senior Floating Rate ≡ Apollo Tactical Income |
| 26 + 12 | Gabelli 787 ≡ Gabelli Investor Funds ≡ GDL Fund |
| 20 | AllianzGI Convertible & Income ≡ Fund II |
| 18 | Tekla Healthcare Investors ≡ Tekla Life Sciences |
| 14 | Putnam Asset Allocation ≡ Putnam Variable Trust |

Each was then confirmed the way the rest of the map was, against the series each registrant
files, and four brand rules plus one for Putnam's eighteen trusts went in — 49 registrants in
all. GDL Fund carries Gabelli's book but files a series called "GDL Fund" and nothing else, so
it is deliberately left unmapped: the map fails closed, and merging it would be remembering
rather than verifying. Putnam's trusts merge into Putnam, not into Franklin — the 2024
acquisition stays unmapped for the reason the module already gives.

This moved §5. The panel goes from 4,297 cells across 660 companies to **4,271 across
656**, and the median between-house spread from 11.750% to **12.135%**, because the cells that
leave are ones whose only "second house" was an affiliate — and those are the cells that
agreed. The correction runs in the direction the module predicts: unmapped registrants inflate
apparent agreement, so this correction can only widen the measured spread.

It also removed the one relationship §6.3 had to disown. That section reported the loud/quiet
NAV ratio as 169×, 0.42×, 0.33×, 0.74× and called the sign unstable. The 169× was Putnam's
eighteen trusts and Gabelli's sixteen counted as separate houses at the thinnest cut of the
panel; merged, the sequence reads 0.59×, 0.36×, 0.28×, 0.66× — below one throughout. The sign
is now a result and the magnitude is still a range.

After the merges the detector still finds 245 duplicated holdings on 162 company-dates,
touching **79 of 4,271 guarded cells (1.8%)**. Dropping every cell they touch moves the median
from 12.135% to 12.372%, so the section does not rest on copies. The residue is sub-advisory,
not affiliation: a sleeve is legally a separate house that has bought its opinion from someone
else, and merging those is a modelling choice with consequences for a dependent variable. It
is reported rather than merged.

## RETRACTION: the cross-house result was a period mismatch

The previous version of this note published three cross-house markup gaps of eight to twelve
points on Databricks and called them house policy. **They were not.** Every one was a house's
own revaluation between report dates, and the filter that was supposed to stop that measured
the wrong thing.

A markup is value over cost **as of the period the filing covers**. The filter used how far
apart the filings were *filed*. Those are different: an annual report for a year ended 31
December and a semi-annual for the six months ended 30 April reach EDGAR 119 days apart and
value the same position five months apart. The filter passed them.

Held at the valuation date, the same data reads the other way:

| lot | period | house | markup |
| --- | --- | --- | --- |
| Databricks Series K, 8 Sep 2025 | 2025-12-31 | Alger | **+26.6667%** |
| Databricks Series K, 8 Sep 2025 | 2026-01-31 | ARK | **+26.6667%** |
| Databricks Series K, 8 Sep 2025 | 2026-04-30 | Alger | +14.62% |

ARK and Alger, one reporting step apart, agree to seven decimal places. The twelve-point
"gap" was Alger's own December-to-April move. Series J is the same shape — Alger at +105.41%
on 31 December and +85.87% on 30 April, 19.5 points from one house — and Series L likewise,
0.00% to −9.51%.

**At an exact common valuation date the harvest holds one lot with two houses, and they agree
exactly**: Epic Games acquired 25 June 2020, period 30 June 2025, gap 0.000. Widening to a
month admits nine lot-periods, and every non-zero gap in that table comes with a period span
of 28 days or more — the gap tracks the distance between valuation dates, not the identity of
the house.

So the sensor's current verdict on §4.3's house-policy question is: **no evidence of
cross-house disagreement at a fixed valuation date, on a sample of one exact match and one
near match, both of which agree.** That is a much smaller claim than the one it replaces and
it is the one the data supports.

The error is worth naming precisely because §4.3 does hold the report date fixed and §5 makes
a section of it. The discipline did not travel to the new sensor: the unit was the acquisition
date when it had to be the acquisition date *and* the valuation date.

## What the period key does establish

**A house moves its own mark, hard, between report dates.** Twenty-seven lot-house series
appear at two or more periods; the median drifts 73 points and the largest 414 — Destiny's
SpaceX lot from +31% at the end of 2023 to +444% at the end of 2025. This is the quantity the
old key was accidentally measuring, and it is the reason any cross-house comparison has to
fix the period first.

**Within a house at one date the mark is one number, with one exception.** Across registrants
of a single house at a single period the markup is identical to four decimal places in the
median of 19 cases — Alger's three registrants report −9.5104 ± 0.0001 on Series L, five
registrants at one period. That is §4.2 seen in a second source, and it sharpens the claim
rather than repeating it: **within a house the mark is one number at a date, not through
time.**

**The exception was arithmetic, not a house.** An earlier version of this note reported
Capital Group carrying a Stripe lot 13.8 points apart across two registrants at one period
end, and called it the first observation against within-house determinism. It is not. All
five divergent Capital Group rows are Class B with `lots_spanned = 2` — a position bought on
6 May 2021 and again on 24 August 2023, whose cost in the row is a blend, and two funds with
different weights on the two purchases have different blends. The markup is then incomparable
by construction, the same way a price per share is incomparable without a share basis.

The check is in the same filing: on 28 February 2026 the Series BB-1 row, single lot, two
registrants of the same house, reads **192.4876% against 192.4992%** — a hundredth of a
point. Restricted to single-lot rows the largest within-house spread in the harvest falls
from 13.8 points to **1.2**, with a median of four ten-thousandths.

So the unit is (company, series, period, single lot), and §4.2 comes through the second
source undamaged: within a house the mark is one number at a date. Publishing the blended
row as an exception would have been publishing the row's bookkeeping.

## Two things the entry price cannot yet do

**Cost per share is not comparable across filings without a split check.** ARK reports SpaceX
acquired 31 October 2023 at $92.89 a share against a $185.00 mark in one filing and at $84.00
against $420.99 in another, and a January 2025 lot at $1,850 against $4,210. Those are not
reconcilable as one share basis.

The consequence is worth stating positively rather than as a limitation, because the missing
share column reads like a weakness and is not one. **The markup is a ratio inside a single
row**, so it is immune to the share basis entirely: a split changes the numerator and the
denominator together. It is therefore the sensor's only comparable quantity, and the one the
result above is made of. Cost per share is service data — useful for reading a filing,
unusable across filings until the split history is read out of them — which is why it exists
on eighteen rows and nothing is built on it.

**Cost is the fund's entry, not always a round.** ARK's Databricks lot of 23 September 2022
returns a markup of 1,226% because the position arrived through the MosaicML acquisition in
stock, which the filing says in a footnote. The cross-filer agreement test is what separates
those, and it runs on lot-periods rather than lots — which is why it currently has one exact
match.

## The fiscal-year barrier is not a barrier — the mark comes from N-PORT

The previous version of this note said the cross-house question now needed two houses with
matching fiscal year-ends, which is structural and rare. It does not. **Cost does not move.**
An entry price is a fact about a purchase; only the mark is a fact about a date. So the entry
comes from N-CSR at whatever period the filer happens to print a share count, and the mark
comes from N-PORT on a common report date — where the discipline of holding the date fixed is
already implemented in §5.

`nport_markup` does that: usable cost rows joined to the population panel give **177
house-date observations on 8 companies across 3 houses** (62 on 7 companies and one house
before the cap came off). It computes a quantity the paper does not have
today — how far above its own disclosed entry a house carries a position, quarter by quarter.
ARK's Epic Games entry of $462.67 carries between −22% and +65% across fifteen report dates
from October 2022 to April 2026; its Revolut entry of $869.73 between −2% and +61% across
five.

Two things it does not do, both worth stating rather than discovering later:

**It adds no cross-house test, and the reason is algebra.** If two houses bought one lot at
one price, dividing both marks by that price leaves their ratio untouched — the markup gap
between houses at a fixed date is exactly the mark spread §5 already reports. Cost buys the
level, not the dispersion.

**The share basis has to be checked, and it fails on three names.** ARK's SpaceX mark steps
from $185 to $1,017 between two report dates and Discord's from $289 to $26; neither is a
revaluation. The same 4× ratio §5 uses on class artifacts, applied between consecutive marks,
flags Anthropic, Discord and SpaceX and leaves **140 rows on 5 companies** standing. A company
carrying a break anywhere is dropped throughout, because the entry sits on one side of it.

## Two parser bugs the wider harvest exposed, both invisible at forty filings

**One document, two layouts.** Brighthouse's N-CSR carries nine headers of the main schedule —
Acquisition Date, Shares, Cost, Value, in dollars — and then twelve of the restricted-securities
note: Acquisition date(s), Cost, Value, Percent of net assets, in thousands. The parser read
the first header in the file and applied it to everything. Under that reading the note's row
`8/29/2025 | $86,525 | $154,007 | 0.28%` became 86,525 shares costing $154,007 now worth
$0.28, and Anthropic's Class F lot came out at **−99.999818%** where four other filers put it
at **+77.991332%**. Every `−100%` in the first uncapped run was this.

**The same bug, quieter, in the scale.** Transamerica's first two headers are in dollars and
its remaining twelve in thousands, so every cost came back a thousand times too small. The
markup survived it — a markup is a ratio inside one row — which is exactly why it would have
shipped.

The fix is per-table: a header inside a table governs that table, and a table with no header
of its own takes the nearest one above it, which is what Capital Group's split-out header
needs. Re-run on the 47 documents the capped extract used, the new parser reproduces **104 of
105** company-document results exactly; the one difference is a removal — `Databricks, Inc.,
First Lien Term Loan`, whose "acquisition date" was a maturity date and whose "cost" of 8.27
was an interest rate.

## House labels are not books: the sub-advised sleeve

At forty filings the harvest held two houses. At four hundred it holds seven on one Canva lot,
and they are not seven opinions.

Canva's Series A-3, acquired 4 November 2021, as of 30 June 2023, is filed by Brighthouse
Funds Trust I, John Hancock Variable Insurance Trust, MML Series Investment Fund, Nationwide
Variable Insurance Trust, SunAmerica Series Trust, Transamerica Series Trust and American
Funds Insurance Series — seven registrants under seven sponsors — at **$2,000 thousand cost
and $1,000 thousand value, −50.000000% at all seven.** Insurance-dedicated trusts host
sub-advised sleeves of another manager's portfolio, and a sleeve files the manager's numbers.
That is Capital Group's book under seven names.

Counting distinct (cost, value) pairs instead does not fix it, and the way it fails is
instructive: the same seven registrants also file a second A-3 row at $31,000 thousand against
$22,000 thousand, −29.032258%. Reading those as two books reports a **10.5-point
disagreement** — between two sleeve sizes of one manager.

`shared_books` therefore starts from houses and joins two houses when they file a cost and a
value agreeing to the dollar; books are the connected components. Canva A-3 collapses to one
book and its gap to zero. Starting from rows instead over-counts the other way, because two
funds of one house holding different amounts have different costs.

The count this produces is the round's main number: of 425 lot-period-series, **76 carry two
or more house labels at one valuation date and 45 carry two or more independent books.** The
31 that fall away are sleeve structure.

## The cross-book comparison, which now exists

Same company, same series, same acquisition lot, same valuation date, and two books that do
not share a cost. **45 such comparisons. 37 of them agree to within a hundredth of a point;
the median gap is 0.0000.** Four do not:

| lot | period | books | markups | gap |
| --- | --- | --- | --- | --- |
| Databricks Series K, 8 Sep 2025 | 2026-04-30 | Alger, Neuberger Berman | 14.6200 / 26.6667 | **12.05** |
| Databricks Series J, 17 Dec 2024 | 2025-06-30 | Brighthouse, Alger | 16.9513 / 28.8541 | **11.90** |
| Databricks Series K, 8 Sep 2025 | 2026-02-28 | Capital Group, Neuberger Berman | 18.7668 / 26.6667 | **7.90** |
| Databricks Series G, 1 Feb 2021 | 2021-12-31 | two books | 24.2911 / 27.2046 | 2.91 |

The two largest are on the two newest rounds in the sample, which is where a mark has the
least to anchor to. Against them, Databricks Series G on 30 June 2021 has **three** independent
books — Voya, Brighthouse and Great-West at three different costs — agreeing to **0.0012 of a
point**, and Stripe's Series B lot of 17 December 2019 has two books agreeing to 0.0002 across
eleven consecutive periods.

### RETRACTED: the zero does not establish a common entry price

The previous version of this note argued that Alger and Brighthouse both printing 0.0000 at
31 December 2024 showed the entry price was common "by observation, not by assumption". It
shows nothing of the kind. A markup is value over cost, and a holder that marks a fresh
position at what it paid prints zero whatever it paid. Two books entering the same round at two
different prices would both print 0.0000. The argument was the right shape and rested on the
wrong row.

### The entry price is established by the convergence

The year end does what the zero could not. On 31 December 2025 four rows on four different cost
bases print one ratio:

| filer | cost | value | value / cost |
| --- | --- | --- | --- |
| Alger ETF Trust | 476,560 | 978,880 | 2.054054054 |
| Brighthouse Funds Trust I | 652,680 | 1,340,640 | 2.054054054 |
| Alger Portfolios | 6,290,278 | 12,920,570 | 2.054053891 |
| Brighthouse Funds Trust II | 6,527,910 | 13,408,680 | 2.054054054 |

Three of the four are exactly 76/37 as rationals. The fourth misses in the ninth decimal because
its filed value is rounded to the dollar, and 6,460,285/3,145,139 is what rounding 76/37 × a
$6.29M base to the nearest dollar produces.

The pair behind that ratio is disclosed rather than inferred, which is what makes this exact
rather than merely striking. Both Brighthouse rows carry a share count: 652,680/7,056 and
6,527,910/70,572 are both **$92.50** to the cent, and 1,340,640/7,056 and 13,408,680/70,572 are
both **$190.00**. 190.00/92.50 is 76/37. So two filers print the entry price and the year-end
mark in full, and the two Alger rows reproduce the same ratio on bases ten and thirteen times
larger. Equal ratios alone would only prove the two pairs proportional; the disclosed share
counts fix which pair it is.

Then the midyear divergence reads in dollars rather than in points. Against the same $92.50
entry, Alger's 30 June ratio implies **$119.19** a share on both of its registrants and
Brighthouse's implies **$108.18** on both of its trusts. One entry price, one valuation date,
two houses, eleven dollars apart.

A basis difference is a constant, and it cannot open and then close — that argument survives
intact. What it rests on is the convergence, not the zero.

### A second closing of the same round, at the same price

Brighthouse Funds Trust II carries the acquisition date 21 January 2025 where Trust I carries
17 December 2024, and the two print the same 16.951352 in June and the same 105.405405 in
December. 6,527,910/70,572 is $92.50, which is what Trust I paid in December. January and
December are two closings of one round at one price, read off the filings — a second route to
the common basis that owes nothing to the first.

### The convergence is a result, not the absence of one

Both books carry the position from $92.50 to $190.00 over the year. They disagree about where
it stands in June, by eleven dollars a share, and file the same number to nine decimals in
December. That is this paper's thesis on a single lot with the cost disclosed: houses dispute
the level at a date and agree about where the position has got to. Reporting it as "two houses
disagree" would throw away the half of it that is agreement.

## What is still missing before the event study

A round date needs several funds recording the same acquisition date *and* the same price. The
price half needs the share column, now on 155 rows of 767 rather than 29 of 190. What is still
missing is the split history — so that a price on one side of a break can be compared with a
price on the other — and that is not arithmetic.

The re-pricing event study stays where it was. The round dates are still unsourced, and the
first attempt to measure a house effect out of this source turned out to be measuring time.
Whatever is built next holds the valuation date fixed before it holds anything else, and
counts books rather than house labels.
