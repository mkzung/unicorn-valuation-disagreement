# Disagreement Without a Price: How Far Apart Mutual Funds Mark the Same Private Company

Max Gorbuk · Independent Researcher (MAM, London Business School) · gorbuk.maxim@gmail.com
*First draft: June 2026 · This version: September 5, 2026 · Comments welcome. I declare no competing interests; all errors are my own.*

> Replication package. Code, data and figures: <https://github.com/mkzung/unicorn-valuation-disagreement>. `python3 src/reproduce.py` redraws every chart and derived table and recomputes every number this paper asserts from the production code, checking each against the prose. The one number it names only to disown it, in §6.3, is the exception and is marked as such. Every input is public.
## Abstract

A private company has no continuously observable price; between transactions its value is whatever holders say. This paper observes what every US registered fund said: 309,654 Level-3 marks in SEC N-PORT, 2019Q4–2026Q2.

An independent valuation belongs to a fund house, not the trust that files. Between registrants the median spread is 0.004%, one committee counted thirty times. Between houses it is 12.1%, with 40.2% over 24% apart. Where filings name the series the gap is mostly composition, 8.45% against 0.74%, but 597 groups exceed 24% on one named series. The width has a shape: between two houses drawn at random the median is 5.88%, and a wide cell is a crowd plus one house outside it, the same house again two thirds of the time. Disagreement compresses at a round, and what compresses it is a price: the top house comes down at the round and at no shifted anchor.

**Keywords:** private-company valuation; unicorns; mutual-fund (SEC N-PORT) marks; valuation disagreement; differences of opinion; fair-value accounting.

**JEL classification:** G24; G12; G23; G14; G32.

## 1. Introduction

Read the SEC's N-PORT filings the way they arrive and American mutual funds agree about private companies almost perfectly. Hold a company and a report date fixed, compare what the filers report, and the median gap is 0.004%: four thousandths of one per cent, on assets that have no market price. That figure is in this paper because it is an artefact, and what produces it is the paper's first result.

N-PORT identifies a filer by registrant, and a registrant is a legal trust, not an asset manager: Fidelity files these marks under 36 registrant CIKs, BlackRock under 56. Counting trusts as opinions lets one house satisfy, by itself, a comparison meant to need two independent views, and then scores the resulting agreement as evidence, when one valuation committee set both numbers. Correct the unit to the fund complex and the same filings give a median of 12.1%. One definition moves the headline by three orders of magnitude, and §4.2 shows why the direction is not a matter of taste: within a house the mark is a single number in 89.0% of the cells — one company on one report date — where a house files more than one fund, so a house is one opinion and a fund is not.

The 0.004% is the registrant illusion: agreement manufactured by counting one committee many times over, and any study that takes the filer at face value will reproduce it.

The corrected number is two things at once, and the paper separates them before it makes anything of them. An issuer identifier names the company, not the security, so two houses can hold two rounds of one company and price them apart for a reason that has nothing to do with disagreement. Filers are not obliged to name the round and 32.5% of rows do anyway, in the security title, which makes the question answerable wherever two houses name the same letter. On those cells the median gap is 0.74% against 8.45% scored the usual way: the *typical* gap between two houses is mostly composition. 

The tail is not. Stated as a count, not a conditional median, 597 company-date-series groups across 68 companies carry two houses on one named series more than 24% apart. Section 3.3 gives the decomposition and says plainly which half of the population the test can reach, which is the calmer half.

One lot shows what a wide cell looks like when every deflationary reading is closed. In December 2024 Databricks priced its Series J; Alger and Brighthouse both bought in, and both had to tell the SEC what they paid and what they thought it was worth. On 30 June 2025 one carried the share at $119.19 and the other at $108.18. Section 2.1 closes the readings one at a time and closes them on the filers' own disclosures: the same named series, the same acquisition date, one cost path that four different cost bases print identically, and both books arriving at the same number by 31 December, which is not what a stale mark does.

Two sophisticated investors, holding one security bought on one day at one disclosed price, were eleven dollars a share apart about what it was worth in between. That is an existence proof and it is stated as one. It is one of four disagreements among the 45 comparable lots the N-CSR harvest reaches. Thirty-seven agree to a hundredth of a point and four more differ by about a tenth, which is rounding on a large base (§2.2).

Frequency needs a population, because a search that finds wide spreads cannot say whether wide spreads are common. So no company list is used anywhere in this paper's core. From the SEC's quarterly N-PORT bulk data sets, twenty-seven of them, September 2019 to April 2026, I keep every holding a registered fund reports at fair-value Level 3 in a share-denominated equity category: 309,654 marks on 15,443 issuer strings. Which companies exist, and which are held widely enough to compare, is decided by the filings and not by a list. Of the 4,271 company-dates that clear the bar, on 656 companies, only 17.0% are unanimous; the median company-date stands 12.1% apart between its extreme houses; the 75th percentile is 49.5% and the 90th 120.7%.

Four results follow.

**A wide cell is a crowd with one house outside it.** The headline median is a maximum over a minimum, so it grows with the number of houses compared: two-house cells are 39% of the panel at 0.94% apart, six-house cells sit at 29.63%. Scored between two houses drawn at random instead, the panel median is 5.88%, and the gradient inverts. Across the 2,326 cells carrying three or more houses and a dissenter the furthest house stands a median 25.54% from the median of the others, whose own widest pair is 1.57% apart.

Which house it is holds still: where a repeat is possible at all the same house is out again in 65.1% of cases, against a resampled null of 25.4%, and the propensity is a house's own: over 27 houses, outliers observed against outliers expected at each house's coverage run from 0.08 to 2.36. Nor is any of this stationary — the median falls to 4.82% in 2021, when almost every company sat near a fresh round, and trebles afterwards without closing.

**Disagreement is a property of the company, and it is not staleness.** Differences between companies account for 58.8% of the variance in log spread against a 9.7% permutation null, and a company's spread predicts its own next observation at ρ=0.734. The deflationary reading, that one house is merely sitting on an old number, is tested where it is testable: of the 760 cells in which *no* house moved its mark, 179 differ by more than 24%. Both sides are standing still, at different prices, and each filing is an affirmative statement of fair value, not an omission.

**What compresses it is a transaction, and only briefly.** Rounds are dated from the filings themselves, by the first report month in which a new series letter appears across two houses. That dating is calibrated against N-CSR acquisition dates, to within 35 days on fourteen of fifteen pairs. Between-house disagreement falls 2.52 points across the round month, is narrower afterwards in 22 of 29 companies, and rebuilds at roughly 1.1 points a month. Anchors shifted six months before, six months after or twelve months after the round produce no step at all: a median of exactly zero at all three.

**And the compression is a price arriving, not news arriving.** A placebo cannot separate those two, because shifting the anchor removes both at once. Decomposing the cell can: news moves every house the same way, so it has no mechanism for pulling the most optimistic house down. At the round the top house comes down in 29 of 34 untied anchors, and at none of the three shifted anchors does it do so — two of them sit below a coin. That is the half of the compression good news cannot produce, and it is the strongest identification this panel supports.

A fourth question, what the disagreement costs, is answered in Appendix G rather than here. A spread that is large as a fraction of an asset can be small as a fraction of a diversified fund. Repricing every fund's private book at the cross-house consensus moves a median 0.33 basis points of its own net assets, on a panel that agrees more than the population does. It is a lower bound on a small number, and printing it beside the three results above would give it a weight the measurement cannot carry.

### 1.1 Claimed and not claimed

A paper built in layers can read as an author hedging against his own weakest result, so the claims are separated here.

*Claimed.* A structural fact: within a house the mark is one number, so the count of independent valuations is the count of houses, and reading the filings any other way manufactures agreement. A census on that unit: how far apart US registered funds mark the same private share, on the population of such marks. A decomposition that needs a population and the filers' own series names, and is run here on both: of that gap, how much is two houses valuing one security differently and how much is two houses holding two securities of one company. 

Four falsification tests, the fourth of which is that decomposition: a Level-1 placebo, a no-house-moved subsample, a lot with a disclosed common entry price, and the population's own cells where the filings name the series and two houses name the same one. The fourth is the strongest because it runs on the population, not on one lot, and it is also the one that most constrains what the headline can be said to mean. An external check: at the exits where a price is finally revealed, the fund marks are closer to it than the headline round. And four measurements recovered from public filings, each calibrated against an independent document type and released with the replication package.

*Not claimed.* That the disagreement is a systemic mispricing of mutual-fund NAV. Appendix G measures its size in the number investors transact at and finds it small, and concentrated in 75 funds rather than spread across the industry. That measure runs on a panel that agrees more than the population does, so it is a lower bound on a small number. 

Causal identification of the round. Non-first rounds are not randomly timed, and no instrument here breaks that. The event study rests on 49 dated anchors and its magnitude rests on a dating rule that discards most of the series letters in the panel. Section 8 prints the sensitivity ladder that says so, and the attempt to replace the rule with a better one, which dates worse and leaves the sign standing where the magnitude does not.

Seven down rounds is not enough to separate "a price now exists" from "the news was good", so that reading is not excluded in general. One version of it is: §8.4 decomposes the cell and finds the *most optimistic* house coming down at the round and at no other date, which houses converging on good news does not produce. What that leaves standing is the timing of the round itself, not the direction of the news. The paper also does not re-estimate anyone's fair value: it reports what holders say, not what the assets are worth.

### 1.2 Position against the anchor result

Gornall and Strebulaev (2020) price the contractual terms of a company's most recent round and find the reported post-money valuation averages 48% above the option-adjusted fair value of the cap table, with 65 of 135 unicorns losing unicorn status once revalued. Their object is the *level* of the headline and their evidence is deal terms. This paper's object is the *dispersion* of what sophisticated holders report, and its evidence is the holders' own filings. The two are complementary rather than competing. Their haircut is largest where the downside protections are deepest in the money, the distressed and repriced names, and collapses for winners whose equity is far above the preference stack. That is precisely the cross-section in which the marks here disagree most and the exits repudiate the headline hardest. 

Mutual-fund Level-3 marks are reported as fair value under ASC 820, so §5 measures how far apart sophisticated practitioners land when each attempts, under one accounting standard, the adjustment Gornall–Strebulaev perform analytically. Appendix C.1 gives the reconciliation in full. Nothing in this paper re-derives their 48%, which would require per-round legal terms that public filings do not carry.

### 1.3 Related work and contribution

Chernenko, Lerner and Zeng (2021), Kwon, Lowry and Qian (2020) and Agarwal, Barber, Cheng, Hameed and Yasuda (2023) establish that funds mark the same private company differently and that marks track public markets, on samples running through roughly 2016. Two recent papers mark the frontier. Agarwal, Barber, Cheng, Hameed, Shanker and Yasuda (2023, working paper) (the same team with one addition) price fund marks against a contingent-claims fair value and find funds mark earlier-round holdings near the latest-round price. They find it in the funds' *secondary purchases* too, so the overstatement is not a reporting artefact. Bias, Cassel and Sensoy (2026) find secondary prices forward-looking and predictive of later fund marks.

This paper differs from all of them in the object and in the denominator. The object is not whether marks are right but how far apart they are when nothing has priced the asset, which makes the interesting variation the *dispersion* rather than the level. The denominator is the population: every Level-3 private position in the US registered-fund system over twenty-seven quarters, rather than a sample of names known in advance to be held. That distinction is not rhetorical. Section 5 shows that the ten broadly-held companies a targeted search finds sit just above the *middle* of the population, not in its tail, so a sampled result of this kind cannot be known to generalise until the denominator exists.

Three further literatures set the frame. Fund managers exercise discretion over these marks, understating at top funds and overstating when fundraising, and smoothing relative to public markets (Barber and Yasuda 2017; Jenkinson, Sousa and Stucke 2013; Brown, Gredil and Kaplan 2019; Getmansky, Lo and Makarov 2004). The within-house determinism of §4 is that literature's public-filing signature. 

The cross-house spread is the private-market analogue of *differences of opinion* in public equities, where forecast dispersion predicts lower returns (Diether, Malloy and Scherbina 2002), which Appendix C.4 turns into a testable prediction. And divergent NAVs are exploitable by fund investors (Zitzewitz 2003), which is why Appendix G asks what the disagreement costs. Two features of the setting matter for inference. One is the staying-private equilibrium that produced these companies (Ewens and Farre-Mensa 2020). The other is the dynamic sample selection any exit-based test inherits (Cochrane 2005; Korteweg and Sorensen 2010), which §7 confronts by scoring every screened exit, not the favourable ones. The reopening of late-stage private-market liquidity these marks are taken during is surveyed by the World Economic Forum and Stanford GSB Venture Capital Initiative (2026).

Contributions, stated narrowly:

1. The house-not-registrant correction, which changes the headline by three orders of magnitude and which three separate metrics built here got wrong before it was fixed.
2. The population of US registered-fund Level-3 private marks, resolved by identifier and released in full.
3. A decomposition of the corrected headline into different-security and different-opinion components, which needs both a population and the filers' own series names.
4. Four falsification tests, including a lot with a disclosed and provably common entry price.
5. A dated dynamic: compression at a transaction, and a measured rebuild rate, from round dates recovered out of the filings.
6. Four filing-derived measurements (§9) other work can use without this paper's data.

### 1.4 Road map

Section 2 is the microscope and its control: one lot with a disclosed common entry price, against a Level-1 placebo showing what the same measurement returns when a screen price exists. Section 3 gives the population, the rules that keep identity honest, and how much of the headline is a different security, not a different opinion. Section 4 establishes the unit of an opinion; Section 5 measures how far apart houses are and how much booked value sits in the gap; Section 6 shows the gap is a company trait and not staleness. Section 7 asks which mark was right at the exits, and Section 8 what compresses disagreement — both carry their limits inside themselves, not in a note at the end.

Section 9 sets out the four measurements, Section 10 what would overturn each claim, and Section 11 concludes. What the disagreement costs, in basis points of the net asset value at which fund investors actually transact, is in Appendix G rather than the body: it is a lower bound on a small number, and printing it as a headline would misrepresent both.

Appendix A defines every dataset and variable, Appendix B carries the robustness battery, Appendix C the population's construction and the anchor reconciliation, Appendix D the exits in full, Appendix E what each measurement cannot see, and Appendix F the measurement detail the body sends a reader to check rather than read.

## 2. The microscope and its control

A population median answers *how often* and *how much*. It cannot answer *whether the thing being measured is real*, because every wide cell in it admits a deflationary reading: a different share class, a different lot, a stale number, a units convention. This section closes those readings on one lot where the filings themselves rule each of them out, and pairs it with a placebo that shows the measurement reads zero when there is nothing to measure.

### 2.1 One lot, two houses

N-PORT states what a fund thinks a position is worth and nothing about what it paid. Regulation S-X requires the other half: in the annual and semi-annual reports funds file on Form N-CSR, the schedule of investments must state, for each restricted security, the date it was acquired and what it cost. Appendix E.4 documents the harvest: 767 schedule rows across 44 registrants for the ten most broadly held names, with the accession of every row committed. What that source buys is a comparison in which the entry price is held fixed by disclosure, not by assumption.

Databricks' Series J, acquired 17 December 2024, is carried by two independent books. On 31 December 2025 four filings report it, and Table 1 prints all four:

**Table 1.** Databricks Series J as of 31 December 2025: four filings on four cost bases, three of them printing exactly 76/37. Acquisition date 17 December 2024 except Brighthouse Funds Trust II, which carries the round's January closing. Cost and value as filed, in dollars; share counts as filed where a filer reports them. Sources: SEC Form N-CSR schedules of investments, accessions in `data/ncsr_acquisitions.csv`.

| Filer | Cost | Value | Ratio | Shares | Per share, cost → value |
| --- | --- | --- | --- | --- | --- |
| Alger ETF Trust | 476,560 | 978,880 | 2.054054054 | — | — |
| Alger Portfolios | 6,290,278 | 12,920,570 | 2.054053891 | — | — |
| Brighthouse Funds Trust I | 652,680 | 1,340,640 | 2.054054054 | 7,056 | $92.50 → $190.00 |
| Brighthouse Funds Trust II | 6,527,910 | 13,408,680 | 2.054054054 | 70,572 | $92.50 → $190.00 |

Three of the four ratios are exactly 76/37 as rationals — 978,880×37 = 476,560×76 and so on, to the last digit. Alger Portfolios prints 2.054053891, which differs in the seventh decimal. That difference is one dollar: 12,920,570 against the 12,920,571 an exact 76/37 on a $6,290,278 base would give, and one dollar in $6.29M moves a ratio by 1.6×10⁻⁷.

Equal ratios alone would establish only that the two pairs are proportional. What fixes *which* pair it is, is that the Brighthouse rows carry share counts. Both cost figures divide by their share counts to $92.50 to the cent, and both value figures to $190.00, on two positions differing by a factor of ten. The entry price is disclosed, not inferred, and the two Alger rows reproduce that same path on their own cost bases. The four bases run from $476,560 to $6,527,910, a factor of fourteen, which is what makes the shared ratio informative: a coincidence would not survive that spread.

A second closing confirms it from another direction. Brighthouse Funds Trust II carries the acquisition date 21 January 2025 where Trust I carries 17 December 2024, and the two print the same 16.951352% markup in June and the same 105.405405% in December. January and December are two closings of one round at one price, read off the filings, and that route to the common basis owes nothing to the first.

Now the midpoint. Against the same $92.50 entry, Alger's 30 June 2025 ratio implies $119.19 a share on both of its registrants and Brighthouse's implies $108.18 on both of its trusts. One security, one acquisition date, one entry price, one valuation date, two houses, eleven dollars a share apart, a 10.2% spread on a lot where nothing is left to explain it away (`figures/databricks_series_j.png`).

Every deflationary reading fails on the filings' own fields. It is not a share class, because the filers name the series and it is the same series. It is not two lots: three of the four filings carry the same acquisition date, and the fourth carries the round's January closing at the same price, which the same markup on both dates shows. It is not a units convention, because the share counts divide into the filed values at the filed prices. It is not one house's arithmetic, because each house files the identical number across two of its own registrants on two different bases. And it is not staleness. A stale mark cannot converge, and by 31 December the two books print the same ratio to the last digit a nine-decimal reading holds.

The convergence is the result, not the absence of one. Both books carry the position from $92.50 to $190.00 over the year. They dispute where it stands in June and agree exactly, as rationals, not to a tolerance, about where it has arrived in December. Reporting this as "two houses disagree" would discard the half of it that is agreement, and the half that is agreement is what rules out a constant difference in basis: a constant cannot open and then close.

*A retraction, recorded because the discipline it enforces is the paper's.* An earlier version of this argument rested on both books printing a markup of exactly 0.0000 at 31 December 2024 and read that as proof of a common entry price "by observation, not assumption". It proves nothing of the kind. A markup is value over cost, and a holder that marks a fresh position at what it paid prints zero *whatever* it paid. Two books entering the same round at two different prices would both print 0.0000. The argument was the right shape and rested on the wrong row. The year-end convergence, on four cost bases with two disclosed share counts, is what carries it.

### 2.2 Is this lot unusual?

One lot is a microscope, not a census, and a microscope trained on a cherry is worth nothing. So the same comparison is run wherever the harvest supports it: same company, same series, same acquisition lot, same valuation date, and two books that do not share a cost. There are 45 such comparisons. 37 agree to within a hundredth of a point and the median gap is 0.0000.

That is the right result to report first, and it points the other way from Series J. Where two independent books hold the identical lot of one of the ten most broadly held private companies, they usually file the identical mark. Eight comparisons exceed a hundredth of a point. Four are Epic Games at about a tenth of a point, which is rounding on a large base, not a view. The other four are the finding.

**Table 2.** The four cross-book comparisons that do not agree, out of 45. Each holds the company, the series, the acquisition lot and the valuation date fixed, and compares books rather than house labels. Markup is value over cost as filed.

| Lot | Valuation date | Books | Markups (%) | Gap (pts) |
| --- | --- | --- | --- | --- |
| Databricks Series K, 2025-09-08 | 2026-04-30 | Alger, Neuberger Berman | 14.62 / 26.67 | 12.05 |
| Databricks Series J, 2024-12-17 | 2025-06-30 | Brighthouse, Alger | 16.95 / 28.85 | 11.90 |
| Databricks Series K, 2025-09-08 | 2026-02-28 | Capital Group, Neuberger Berman | 18.77 / 26.67 | 7.90 |
| Databricks Series G, 2021-02-01 | 2021-12-31 | Brighthouse, Voya | 24.29 / 27.20 | 2.91 |

All four are Databricks, and three of them are its Series J and K, the rounds its holders were still re-marking across 2025 and 2026. Against them, the same Databricks Series G lot at 30 June 2021 (the fourth row of Table 2 is that lot six months later) has *three* independent books, at three different costs, agreeing to 0.0012 of a point, and Stripe's Series B lot of 17 December 2019 has two books agreeing to 0.0002 across eleven consecutive periods. What this source shows is narrower than a pattern and should not be dressed as one: on the ten most broadly held names, two books holding one lot usually file one number, and where they do not, it is a company in the middle of repricing itself.

Two further disciplines are needed, because a comparison of markups fails without either. The unit is (company, series, valuation period, single lot). A filter that compares how far apart two filings were *filed* recovers one house's own revaluation between report dates and scores it as two houses disagreeing: an annual report for a year ended 31 December and a semi-annual for the six months ended 30 April reach EDGAR 119 days apart and value the same position four months apart. The periods valued are what has to match. 

And a *book* is not a house label. Insurance-dedicated trusts host sub-advised sleeves that file another manager's numbers: Canva's Series A-3 of 4 November 2021 is filed by seven registrants under seven sponsors at the identical −50.000000%, which is Capital Group's book under seven names. Books are recovered as connected components over houses that file a cost and a value agreeing to the dollar. Of 429 lot-period-series, 76 carry two or more house labels and 45 carry two or more independent books. The 31 that fall away are sleeve structure, and counting them would have manufactured disagreement out of a distribution list.

### 2.3 The control: a Level-1 placebo

The microscope needs a zero reading. If two houses differ because their reporting pipelines differ, whether by pricing vendor, rounding rule or as-of convention, the difference should show up on holdings whose price is not in dispute at all.

It does not. On the common report date 31 March 2026, Fidelity Contrafund and T. Rowe Price Blue Chip Growth (two funds of two different houses) carry five shared public (Level-1) securities at the identical price per share, to the cent:

**Table 3.** The Level-1 placebo. Common report date 2026-03-31; Fidelity Contrafund (accession 0000035402-26-003312) and T. Rowe Price Blue Chip Growth (accession 0001099263-26-006586). These are five shared Level-1 holdings verified to the cent against both filings, not an exhaustive intersection of the two portfolios. Measured the same way on private (Level-3) names, §4.3 finds the ten most broadly held companies a median 24% apart across their disclosing funds.

| Security | CUSIP | Fidelity Contrafund | T. Rowe Price Blue Chip Growth | Cross-house spread |
| --- | --- | --- | --- | --- |
| Alphabet Inc Class A | 02079K107 | $286.86 | $286.86 | 0.00% |
| Alphabet Inc Class C | 02079K305 | $287.56 | $287.56 | 0.00% |
| Amazon.com Inc | 023135106 | $208.27 | $208.27 | 0.00% |
| Apple Inc | 037833100 | $253.79 | $253.79 | 0.00% |
| Cintas Corp | 172908105 | $169.14 | $169.14 | 0.00% |

The pair is the argument, and its two halves rest on two different pairs of houses, which is a feature. The placebo runs on Fidelity and T. Rowe Price. The Series J lot is Alger and Brighthouse. Nothing here claims one pair of houses that agrees on public stock and disagrees on a private lot. What is claimed is a property of the *measurement*: applied to holdings with a screen price it returns zero, and applied to a private lot where every deflationary reading is closed it returns eleven dollars a share. That the two halves come from independent pairs of houses makes the claim about the instrument stronger, not weaker.

One sentence of it does rest on a single pair. Fidelity and T. Rowe Price agree to the cent on the five shared Level-1 securities above, and the same two houses appear in §4.3's private cells, where the widest gap between them, on Gusto, is 12.5% ($19.03 against $21.40 on 31 March 2026). Same two houses, two asset classes: zero on the public side, twelve and a half per cent on the private one. The stronger cross-house numbers in §4.3 belong to other pairs, and they are not claimed here.

Both halves are checkable by a referee in EDGAR from the accessions printed above, without this paper's pipeline. What neither establishes is frequency, and the placebo does not establish exhaustiveness either: five shared securities are not the whole intersection of two large portfolios, and the claim is only that on these five the same houses do not differ at all. Five public securities and one private lot are an existence proof, and existence proofs are exactly what a population is needed to size. The rest of the paper supplies the denominator.

## 3. The data, and the rules on identity

A claim about disagreement is a claim about two numbers attached to one thing. Everything therefore turns on what "one thing" means: one company, one security, one opinion. Each is a decision, and each of them made carelessly manufactures the paper's dependent variable out of nothing. This section settles the first two, and §4 settles the third, which needs the population to be in hand before it can be tested.

### 3.1 Every Level-3 private position

The SEC republishes N-PORT as quarterly bulk data sets. I take all twenty-seven from 2019Q4 through 2026Q2, with report dates running from September 2019 to April 2026. From those I keep every holding a registered fund reports at fair-value Level 3, in the two equity asset categories, in share-denominated units. That is 309,654 marks on 15,443 distinct issuer strings, of which 200,002 are US-domiciled. No company list is consulted at any point. Which companies exist, and which are held widely enough to measure, is decided by the filings.

One screen the §4.3 harvest applies is deliberately dropped here, and the reason is itself a finding. That harvest keeps only holdings a filer flags as restricted securities. Filers do not apply the flag consistently: ARK Venture reports Revolut *unrestricted* while Fidelity reports the same company restricted. The flag therefore removes the one family that disagrees, and Revolut's 35% published spread collapses to zero — a screen that silently selects for agreement, inside a paper about disagreement. Dropping it returns the published cell exactly: eleven funds, 34.7% against the reported 35%. Keeping it would have made the population look calmer than the filings are.

### 3.2 Identity by identifier, never by similarity

Turning 15,443 issuer strings into companies is the step most likely to manufacture the result, so it is built to fail in the harmless direction. Rows join transitively on a validated CUSIP (check digit verified) or an LEI, then on exact normalised names, then on a hand-written alias list of thirteen entries covering what public filings genuinely spell differently, such as Douyin for ByteDance and Space Exploration for SpaceX. No fuzzy matching is used anywhere, because the two errors are not symmetric: splitting one company into two costs coverage, while fusing two invents a price spread out of two unrelated securities, which is this paper's dependent variable.

Jurisdiction parentheticals, feeder wrappers and look-through descriptions are held out rather than read as names, and 262 feeder rows are excluded because a price per unit in a feeder is not the company's price per share. Russian issuers are dropped because they sit at Level 3 by sanction, not by being venture-backed.

One exclusion is less obvious and matters more. A CUSIP and an LEI both name the *issuer*, and a price per share belongs to the *security*. The identifiers that keep this resolver from fusing two companies will happily fuse two instruments of one company, and registered funds hold plenty that is not stock: contingent value rights left over from an acquisition, escrow lines, subscription rights, warrants, earnout shares that vest on a price target, litigation trusts. Each arrives on the issuer's identifier carrying a price per unit that has nothing to say to the price of a share, and left in, each does at the instrument level what a bad name match does at the company level. 25,482 such rows across 1,599 issuers are excluded on the security title, which is where filers put the instrument (`population.is_claim`).

A list of spellings is only as complete as the strings its author has read, and each revision of this paper has found a class the last one missed (Appendix A.2). The filter is therefore backed by two structural tests, not extended one word at a time. The first reads expiry. An instrument that runs out carries a date and a share in a company does not, so the six survivors that carry an expiry word are pinned by name.

The second needs no vocabulary at all. Every leak so far announced itself the same way, as a price two orders of magnitude from the rest of its own cell under a title nobody else in that cell uses, so `population.price_outliers` reports exactly those rows: twelve of them, under six titles on five issuers, each read against its filing one at a time. Four are a genuinely different security of the same issuer, and two are marks that houses really filed, including First Trust's $1.00 on Epic Games against a $600 consensus. That one stays: a rule that dropped low marks because they were low would delete the subject of the paper.

Two limits of the join are visible in the output rather than hypothetical, and Appendix A.2 gives both. What identifiers cannot separate at all, one house holding Series C where another holds Series D, is not fixable by exclusion, and is measured in §3.3.

### 3.3 Which security the mark is of

The exclusion in §3.2 removes instruments that are plainly not the company's stock. It cannot remove the harder case: two houses holding two different rounds of the same company's preferred, which an issuer identifier reads as one security and which may legitimately price apart. No public field resolves this, since N-PORT has no security-level identifier for a private position, so the question is not whether to bound it but how much of the headline it accounts for.

Filers are not obliged to name the round and 32.5% of rows do anyway, in the security title: "SER H PC PP", "CLASS B PP". That is enough to answer it directly wherever two houses name the *same* letter, and the answer is large.

Holding the security fixed removes almost all of the median and almost none of the tail. On the 1,758 cells where two or more houses name the same series (2,717 company-date-series groups over 137 companies), the median between-house spread is **0.74%**. Scored the way §5 scores everything, ignoring the series, those same cells read 8.45%. The share above 24% falls only from 35.4% to 22.0%, on 597 groups across 68 companies. Appendix C.5 and Table C.1 give the decomposition in full, and the same result sits beside the part of the panel it cannot reach (`figures/series_decomposition.png`).

So the headline is two things at once, and they are separable: the *typical* gap between two houses is mostly composition, two houses holding two rounds of one company, while the *wide* gap is mostly not. This is the population-scale version of what §2.2 finds by hand on N-CSR lots, where 37 of 45 identical lots agree to a hundredth of a point, four differ by a tenth on a large base, and the four that actually disagree are one company mid-repricing.

Three limits on that reading, and the first is sharper than a note about selection. **The test is available exactly where disagreement is smallest and unavailable exactly where it is largest.** The cells no filing describes are the widest group in the panel and the most numerous, so the decomposition is not a statement about the population's disagreement but about the calmer half of it. Appendix C.5 gives that half its figures and states which way the ignorance runs.

A shared letter is also not a shared lot: two houses can enter one series at two closings months apart, which §2.1 shows priced identically and which this test cannot rule out in general.

And a named letter is not necessary for agreement, which is the counter-example that keeps this from being read as a correction, not a decomposition. The most widely held private company in the data is held almost entirely on letter-mixed cells: SpaceX, on 32 letter-mixed cells, and its houses file one price. Cells naming two or more letters sit at a median of 12.90%, barely above the panel's 12.13%, so mixing letters is not by itself what widens a cell.

### 3.4 One signal from outside the filing system

Everything above comes from EDGAR. One thing does not, and it is the only thing: the realised offer valuations of the 2023–26 listings, which §7 scores the marks against. That is deliberate. Three further public signals were built and then kept out of the argument: a secondary-market cross-section priced by a vendor, that vendor's private-market index, and exchange-traded contracts on IPO timing. They rest on sources this paper cannot audit, one of them takes the primary round as a modelling input and is therefore partly circular against the very quantity in question, and none of them is needed for any claim made here. The code and data remain in the repository for anyone who wants them. The argument does not use them. Appendix A defines every dataset and variable and records each row's source and date.

## 4. The unit of an opinion

Section 2 compared two houses. Whether that is the right unit (whether a house is one opinion and a fund is not) is not a definitional preference. It is a measurable property of the filings, it is measured three ways here, and getting it wrong costs three orders of magnitude in the headline.

### 4.1 A filer is a trust, not a house

A comparison has two sides. §3.2 settled the security side, which rows are one company's stock. 

N-PORT identifies the filer by registrant, and a registrant is one legal trust. Fidelity files these marks under 36 registrant CIKs, T. Rowe Price under 40, BlackRock under 56. Counting registrants as families does two things at once, both wrong in the same direction. It lets a company held by two Fidelity trusts clear a bar meant to require two independent opinions. It then records those two trusts agreeing, which they do by construction, because one valuation committee sets both marks. The mechanism is easier to document than its implication, and Appendix D carries the case: twenty-two sub-advised funds across five variable-insurance trusts run by four insurers carrying Instacart at T. Rowe Price's identical $32.50.

So the family here is the fund complex, mapped from registrant names to houses by verified rule and covering 98% of the booked value. The rules that matter are the ones a reader would not guess: Fidelity's VIP trusts, BlackRock's iShares trusts, and Capital Group's American Funds, which file under fund names carrying no house brand at all. The map fails closed: a registrant matching no rule keeps its own identity and counts as its own house, so anything the map misses shrinks the correction instead of inventing it. Series trusts that host unrelated advisers are left unmapped for the same reason.

Two rules were dropped when checked against the series each registrant actually files. Ivy Funds files "Delaware Ivy" series and so belongs to Macquarie rather than Invesco. The trusts named "Variable Insurance Products Fund" file VIP portfolios and so belong to Fidelity instead of standing alone. One merge is deliberately withheld. Franklin Templeton bought Putnam in 2024, and a static rule would backdate that over four years of filings. The same question was measured for the merges the map does make: the pre-acquisition exposure of Legg Mason, Eaton Vance and the Ivy trusts together is 0.13% of the value in the reported cells.

The merge is validated on the data. If it fused two genuinely different houses, marks inside a "complex" would disagree. They do not. On the reported cells, 87.5% of multi-fund groups inside a single registrant file an identical price, and 89.0% do inside a mapped complex: slightly *tighter*, not looser. Across complexes only 28.5% of those groups agree, and the 90th percentile of the spread runs past 100%. That 28.5% sits a tenth of a point from §5.1's 28.4% and counts something else, multi-fund groups rather than cells.

Form N-CEN closes it from outside. Every registered fund files one annually and Item C.9 names each series' adviser, so the SEC states who manages a trust independently of anything here: an adviser is recovered for 1,161 of the panel's 1,166 registrants. Of the 55 houses this map merges, 22 file more than one adviser name, and all 22 were read: 13 are one firm's several advisory entities, 8 are firms the house bought, still filing their own name, and 1 is an outside manager of a sleeve the house sells. Not one fuses two unrelated firms. The error the filings do show runs the other way: 96 advisers appear under more than one house, each a merge this map declines to make, the largest being the one withheld above: Franklin Advisers now advises nine Putnam trusts. The fail-closed rule makes all 96 understate the correction.

### 4.2 Within a house, one number

If the house is the unit, the marks inside one should be a single number, not a tight cluster, and that is a testable difference. It holds at both scales: on the population here, and on the ten names §4.3 reads one by one.

§4.3's sharpest structural claim — that the number of independent valuations is the number of *houses*, not the number of funds — was measured on ten names. Across the population, 89.0% of 9,210 house-cells in which one complex files more than one fund report a single identical mark, and the median between-house share of variance in log price is 1.000 across 3,278 multi-house cells. Within a house the mark is one number, essentially always. A name held by forty funds across three houses carries three views, and a reader counting funds as independent opinions overstates the evidence by an order of magnitude.

The N-CSR schedules of §2 confirm this from a second document type, and sharpen it. Across registrants of a single house at a single period the markup is identical to four decimal places, in the median of the 19 such cases the harvest holds. Alger's registrants report −9.5104 ± 0.0001 on Databricks Series L. On 28 February 2026 Capital Group's two registrants report Stripe's Series BB-1, a single lot, at 192.4876% against 192.4992%: a hundredth of a point.

The claim needs one qualification, and it was found by getting it wrong. Five Capital Group rows do diverge, by as much as 13.8 points across two registrants at one period end, and they read as the first observation against within-house determinism. They are not. All five divergent Capital Group rows are Class B with two lots spanned. The position was bought on 6 May 2021 and again on 24 August 2023, so the cost in the row is a blend, and two funds with different weights on the two purchases have different blends. The markup is then incomparable by construction, the same way a price per share is incomparable without a share basis. Restricted to single-lot rows the largest within-house spread in the harvest falls from 13.8 points to 1.2, with a median of 0.0001 of a point.

So the sharpened form is: within a house the mark is one number at a date. It is not one number through time, and Appendix E.2 finds it is not one number about the share *count* either.

### 4.3 Ten companies, mark by mark

One caution before the table. These ten cells come from a by-company harvest that stops after eighteen filings per name, so each is a lower bound on the spread a complete sweep would find. The bound is not tight. Appendix C.3 recomputes all ten from the bulk data and the median goes from 23.5% to 34.7%. Stripe is the extreme case, reading +1% here and 73% on the complete filing set for the same security on one date. So read the levels below as an anatomy of named marks, not as the paper's measurement of how far apart houses are. That measurement is §5.

SEC N-PORT filings let any reader observe what each mutual fund states a private holding is worth. Holding the report date fixed and comparing funds that hold the *same* security, the cross-fund spread in the implied price per share has a median of 24% across the ten companies with ≥5 same-date funds, but is sharply bimodal:

**Table 4.** Cross-fund dispersion of SEC N-PORT Level-3 marks for the same private security on a common report date. The spread is the highest implied price per share over the lowest, minus one, across the funds filing that security on that date, each company being read at its own modal report date in 2025 or 2026. Companies with ≥5 disclosing funds; Plaid, at 4, shown for completeness. Every spread here is a floor: the harvest behind this table stops after eighteen filings a name, and Appendix C.3 recomputes the same ten cells on the complete filing set, where the median runs from 23.5% to 34.7%. Read the column as an anatomy of named marks, not as how far apart houses are; §5 is that measurement.

| Company | Funds (same date) | Cross-fund spread | Per-share marks |
| --- | --- | --- | --- |
| Discord | 8 | +53% | $22.28 (Fidelity ×6) → $34.06 (Private Shares Fund) |
| Anthropic | 14 | +39% | $259.14 (Alger) → $361.35 (Nuveen); a single identical security |
| Revolut | 11 | +35% | $1,110 (ARK Venture) → $1,496 (Fidelity ×10) |
| Epic Games | 7 | +33% | $447 → $594 |
| Gusto | 8 | +32% | $16.18 (Franklin) → $19.03 (Fidelity) → $21.40 (T. Rowe) |
| Databricks | 12 | +15% | $171.93 (Alger) → $198.01 (ARK Venture) |
| Plaid | 4 | +12% | $251.11 (Franklin) → $282.42 (BlackRock, Fidelity) |
| Canva | 5 | +10% | $1,496 → $1,646 |
| Anduril | 7 | +4% | ~$64–66 |
| Stripe | 8 | +1% | ~$63 |
| OpenAI | 13 | 0% | all 13 funds at $687.69 |

Three things stand out. The shape is bimodal rather than graded: disagreement is large for stale, repriced or contested names and absent for names carrying a single fresh, well-publicised round, with nothing in between. Within a house the marks are identical rather than merely close. And the two together point at valuation policy rather than private information, which is the private-market counterpart of the discretion illiquid-asset funds exercise over reported marks (Getmansky, Lo and Makarov 2004; Jenkinson, Sousa and Stucke 2013; Brown, Gredil and Kaplan 2019). Appendix F.5 walks the ten names one by one.

## 5. How far apart, and how much money

**Ten companies cannot answer a question about frequency.** The names in Table 4 got there by being findable. I queried EDGAR's full-text index for private companies I already knew mutual funds held, then kept the ones with at least five funds filing on a common date. That is a reasonable way to build an anatomy of disagreement and no way at all to measure how often it happens. If wide spreads are rare and my search found the rare cases, a 24% median describes the search, not the market. Nothing inside the sample settles the question, because the sample has no denominator. This section builds one — not by adding more names to the list, but by discarding the list.

### 5.1 Between houses, disagreement is the normal state

A *cell* is one company on one report date held by at least five funds across at least two complexes. Each house's mark is the median across its own funds, so a complex filing thirty series cannot widen the spread by itself. The same 4× guard drops cells whose extreme marks differ by more than fourfold: at that distance the likely explanation is a share class, not a disagreement. That guard is not a rounding detail at this scale. It removes 31% of the company-dates that otherwise qualify, against 22% when the comparison ran between registrants. Two houses are more likely to hold different classes of the same company than two trusts of one house are.

N-PORT reports position-level detail for each month-end, so a report date is a month and not a quarter: the twenty-seven bulk data sets carry 104 distinct report dates, of which 92 yield at least one cell. Those 104 dates spread over 80 month-ends, because 24 months carry two: some filers date to the last business day and others to the calendar month-end. That leaves 4,271 cells across 656 companies — a count §5.5 narrows twice over, once for what kind of company each is and once for issuers reaching a cell under more than one key.

Only 17.0% of company-dates are unanimous and 28.4% agree to within a basis point. The median spread between houses is 12.1%, the 75th percentile is 49.5% and the 90th is 120.7%. Measured this way the ten-company median of 24% is not exceptional at all: it sits at the population's 60th percentile, and scored the population's own way — a spread between house medians rather than between funds — those same ten cells land in the same place. The next paragraph explains why the two agree.

That comparison is still not quite like for like, and the mismatch is worth removing. §4.3's 24% is a spread across *funds*; the population percentile is a spread across *house medians*, which strips the within-house dispersion the fund-level figure carries. Scored the population's own way, the same ten cells give a median of 23.7%, and that lands at the 60th percentile. The two framings do not merely agree on the substance: on this panel they are the same number to nine decimal places, because on every one of the ten names the widest and the narrowest fund sit in different houses, so collapsing funds to house medians removes nothing.

An earlier version of this sentence put the house-level figure at 12.6%, and that gap was manufactured by this panel's own catch-all bucket: it pooled seven distinct managers into a single unit whose median sat between the extremes, which is the paper's headline defect running in the other direction. On the measure §5 uses throughout, the ten broadly-held names sit just above the middle of the distribution. The registrant-level reading had put those ten names in the top quarter of the population. They are not there. The population is wider than they suggested.

**Table 5.** The population panel: spread between fund complexes on a common report date, 2019Q4–2026Q2 bulk N-PORT, cells with ≥5 funds across ≥2 complexes (4,271 cells, 656 companies). "Identical" = every house files the same mark to within a rounding tolerance. NAV is the fair value funds booked in that cell. Two sums in this table are a tenth short of the figure quoted beside them, both for the same reason: each band is rounded before it is added. The three bands above 24% come to 179.9 against the $180.0B used throughout, and the whole NAV column comes to 517.2 against $517.3B. Table 8 partitions the same dollars a different way and happens to add to 517.3 exactly, which is rounding rather than a second measurement.

| Spread | Company-dates | Share of cells | Booked NAV ($B) | Share of NAV |
| --- | --- | --- | --- | --- |
| identical | 725 | 17.0% | 80.2 | 15.5% |
| 0–10% | 1,300 | 30.4% | 168.7 | 32.6% |
| 10–24% | 531 | 12.4% | 88.4 | 17.1% |
| 24–50% | 660 | 15.5% | 105.9 | 20.5% |
| 50–100% | 499 | 11.7% | 51.0 | 9.9% |
| >100% | 556 | 13.0% | 23.0 | 4.4% |
| all cells | 4,271 | 100% | 517.3 | 100% |

40.2% of all company-dates exceed 24%, a tenth exceed 120%, and measured per company rather than per report date, 32.5% of the 656 names carry a median spread above 24%.

### 5.2 What the median is made of

That median is a mixture of two things, and Appendix F.1 supplies the reason: the spread is a maximum over a minimum, so it can only grow as more houses are added. That appendix uses the fact to defend §8, where the house count is 4.0 either side of the round. It applies here too. Two-house cells are 1,685 of the 4,271 and $113.2B of the $517.3B, and their median spread is 0.94%, while cells carrying six or more houses sit at 29.63%. The headline is part dispersion of opinion and part distribution of coverage, and Table 6 separates them.

**Table 6.** Cells grouped by how many houses report the company that quarter. "Median spread" is this paper's statistic, the highest house mark over the lowest. "Median pair" is the median across all pairs of houses in a cell of the absolute log price difference, stated as a percentage. It asks how far apart two houses drawn at random are, and it cannot grow mechanically with the count. "Above 24%" is scored on the first of the two. Only "Median pair" is pairwise; every other column here is end to end.

| Houses | Cells | Companies | Median spread | Median pair | Above 24% | Booked NAV ($B) |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 1,685 | 343 | 0.94% | 0.94% | 26.2% | 113.2 |
| 3 | 971 | 233 | 17.64% | 15.38% | 44.2% | 94.8 |
| 4 | 630 | 173 | 20.57% | 10.68% | 47.5% | 79.1 |
| 5 | 370 | 114 | 29.16% | 4.71% | 55.1% | 50.6 |
| 6 or more | 615 | 142 | 29.63% | 2.84% | 55.6% | 179.5 |

The second column inverts the first instead of flattening it. Across the panel the median pair is 5.88% against the end-to-end figure of §5.1, and it puts 29.1% of cells above 24% where the end-to-end statistic puts 40.2%. A widely held company has one or two houses far from the rest and a crowd that agrees; a three-house company is three ways apart. Neither number is the right one alone. The range is what an allocator holding both extremes faces, the typical pair is what a reader pictures on being told two houses disagree, so both are reported. Two houses is also where a sub-advised sleeve would hide: Appendix A.3 records that this map cannot separate a house from an outside manager mirroring its marks, and a mirrored pair reads as two houses agreeing.

### 5.3 The same median, year by year

Nothing here is stationary either, and a paper measuring dispersion across twenty-seven quarters should say so, which is Table 7. The median runs 8.22% in 2019, falls to 4.82% in 2021, then trebles and stays: 13.30%, 17.45%, 18.04%, 17.42% through 2025. Composition cannot explain it, because composition runs the other way. The mean number of houses in a cell falls monotonically from 4.14 to 3.45 across those years, which shrinks a maximum over a minimum rather than growing it, and the last two columns repeat the exercise on cells carrying three or more houses and find the same shape at twice the size.

**Table 7.** Report years, 2026 being two quarters of one. The last two columns restrict to cells carrying three or more houses, which removes the coverage mixture Table 6 measures.

| Year | Cells | Median spread | Mean houses | Cells (3+) | Median (3+) |
| --- | --- | --- | --- | --- | --- |
| 2019 | 191 | 8.22% | 4.14 | 129 | 12.50% |
| 2020 | 564 | 10.68% | 3.84 | 356 | 18.65% |
| 2021 | 670 | 4.82% | 3.73 | 408 | 7.06% |
| 2022 | 735 | 13.30% | 3.72 | 448 | 26.78% |
| 2023 | 659 | 17.45% | 3.58 | 395 | 33.29% |
| 2024 | 609 | 18.04% | 3.49 | 359 | 32.00% |
| 2025 | 643 | 17.42% | 3.45 | 373 | 29.80% |
| 2026 | 200 | 11.10% | 3.40 | 118 | 17.45% |

The trough is §8's mechanism read off the calendar. 2021 is the year in which almost every company in the panel sits near a fresh priced round, and where a price exists the houses agree about it; when the rounds stop the marks drift apart, and on this evidence they do not come back together. Disagreement being the normal state is a statement about 2022 onwards rather than a constant of the asset class, and §8's rebuild rate of about 1.1 points a month is what that aggregate looks like from underneath.

### 5.4 A consensus, and a dissenter

That structure has a testable consequence. If a wide cell is a crowd with one house away from it, the away-house can be identified: in each cell of three or more houses it is the one furthest, in absolute log price, from the median of the others. Not every cell has one. In 260 of the 2,586 such cells every house files a single price and there is no dissenter to name. Across the 2,326 that have one, the outlier sits a median 25.54% from the others' median while the houses it leaves behind are 1.57% apart at their widest. Disagreement in this panel is not a fan of views. It is agreement with a dissenter.

The dissenter is a house rather than an accident of the quarter. Restricted to the 1,334 consecutive pairs where the previous cell's outlier is still present in the next one, so that a repeat is possible at all, the same house is the outlier again in 65.1% of them. Resampling each cell's outlier uniformly from the houses actually in it puts the null at 25.4%, and no draw of two thousand reached 30%. Some houses are the dissenter far more often than their coverage implies. Over the 27 houses appearing in a hundred or more of these cells, the ratio of outliers observed to outliers expected at that house's own coverage runs from 0.08 to 2.36. The side is lopsided too: 45.5% of outliers sit above the houses they leave, so the dissent is a little more often a discount than a premium.

This is the same object §8.4 moves and Appendix G.3 finds persistent, seen from a third direction: §8.4 shows the top house coming down when a round prices the company, that appendix shows a house keeping its side, and the count here shows the side is a house's own and not the cell's. What none of the three establishes is why a particular house sits where it does, and this paper does not attempt it.

### 5.5 What kind of company

Section 3.3 settled which security is being compared. This settles the other half of the same question, which an identifier also does not answer: what kind of company is on the other side of it.

This is the question a referee reaches first. §3.1 keeps every Level-3 equity position registered funds report, which describes the filings honestly and unicorns badly. The panel contains AT&T Mobility II's structured preferred at $25.0B, AmSurg and Southeastern Grocers out of buyout portfolios, and Neiman Marcus and Intelsat after their reorganisations. It also contains Taiwan Semiconductor, listed on the Taiwan exchange and carried at Level 3 for a single month. None is a venture-backed private company. The paper already makes exactly this argument about Russian issuers, whose marks track a sanctions freeze, not a company; it simply never applied the argument anywhere else.

Every cluster carries a label and, beside it, the basis for that label: the clusters holding 93.6% of the booked value are verified one at a time against the filings, and the rest are labelled by an abstaining rule. Appendix C.2 gives the rule, its measured accuracy and its failure modes.

**Table 8.** The population by what kind of company the mark is on, same cells as Table 5. "Private, other" is a private operating company that is not venture-backed — a buyout portfolio company, corporate structured preferred, or equity issued in a reorganisation. "Verified" and "rule" in §5.5 describe how each cluster's label was reached, not how the spread was computed.

| Kind of company | Clusters | Cells | Booked NAV ($B) | Median spread | Above 24% | NAV above 24% ($B) |
| --- | --- | --- | --- | --- | --- | --- |
| venture-backed | 142 | 2,113 | 402.2 | 10.1% | 37.0% | 152.8 |
| private, other | 18 | 314 | 72.8 | 16.1% | 36.9% | 17.0 |
| listed | 348 | 967 | 28.0 | 19.0% | 47.9% | 4.8 |
| unclassified | 148 | 877 | 14.3 | 10.6% | 40.5% | 5.3 |

The correction narrows the population and sharpens the result instead of softening it. The companies this paper is about are 2,113 cells over 142 clusters. Five of the seven split issuers named in Appendix A.2 are venture-backed — xAI, Ant, Caris, Didi and Rivian, each reaching a cell under two keys — so those 142 clusters are 137 distinct issuers. That is still fourteen times the ten names of §4.3, and it is no longer a count inflated by 348 listed clusters whose marks sit at Level 3 for reasons that have nothing to do with venture valuation. Among them the median spread is 10.1% rather than 12.1%, and 37.0% of company-dates exceed 24% rather than 40.2%.

The dollars move the other way. Venture cells hold $402.2B, of which $152.8B (38.0%) sits above 24%, against 34.8% on the mixed panel. Disagreement is *more* concentrated in the venture population than in the population at large, not less: the listed and non-venture clusters that the correction removes were diluting it. Whatever the boundary is argued to be, the direction of the result does not depend on where it is drawn.

### 5.6 Where the booked value sits

Funds booked $517.3B across these cells, of which $180.0B (34.8%) sits where houses disagree by more than 24%; across the venture-backed companies alone it is $152.8B of $402.2B, and that narrower pair is what the paper's claim rests on. The more useful fact is in Table 5's last rows. The widest spreads are the *smallest* positions: cells disagreeing by more than 100% are 13.0% of the count and 4.4% of the value, while the 24–50% band alone carries $105.9B. Extreme disagreement is largely a small-position phenomenon, plausibly thin coverage and residual class effects; the money is exposed to the moderate, systematic disagreement the house analysis explains (`figures/population_spread.png`).

The absolute scale should be stated at book rather than inflated. The fifteen companies the by-company harvest of Appendix A reaches carry $24.7B of booked Level-3 fair value, of which $1.9B sits in the six names where houses disagree by 15% or more. Registered funds hold only a sliver of late-stage private equity, so the dollars visible in this window are modest against the asset class. What is not modest is the marking convention the window exposes: the same convention values the multi-trillion-dollar private-NAV layer across the fund and limited-partner industry, where no public N-PORT disclosure exists to measure the disagreement at all. The measurable claim is the one this paper makes, the sum inside the window. The reason it matters is the layer outside it that nobody can measure.

### 5.7 Which number to quote

Four medians appear in this section and they answer four different questions. Between registrants, 0.004%: whether two filings of one trust agree, which they do by construction, reported only because it bounds the correction from below. Between houses on the mixed panel, 12.1%: every Level-3 private position registered funds report. Between houses on the venture-backed clusters alone, 10.1%: the companies the term "unicorn" refers to, and the number that carries any claim about them. Between two houses drawn at random rather than end to end, 5.88%: the same cells scored by the size-invariant statistic of Table 6, which is the number to quote when the question is what a typical pair of houses does rather than how wide the disagreement runs.

The mixed panel is quoted where the object is the filing system, the venture panel where the object is venture-backed companies. Both are printed wherever either is used, because the difference between them is a fact about what funds hold at Level 3, not a modelling choice.

What the population adds to §4.3's ten names is scale and structure, not a correction. Those ten sit just above the middle of the distribution, not in its tail. They remain the right place to see the mechanism, because only there can individual marks be read against named houses and known rounds.

## 6. A company trait, not staleness

Two deflationary readings remain after §2 and §5. The first is that the spread is noise: houses land at different numbers because private marks are imprecise, and a re-draw would reorder them. The second is that one house has simply left an old number in place, so what looks like disagreement is a lag. Both are testable on the population, and both fail.

### 6.1 A property of the company

Restricting to the 290 companies observed on four or more report dates, differences between companies account for 58.8% of the variance in log spread, against 9.7% when company labels are permuted within report dates (200 draws, 95th percentile 10.8%). A company's spread predicts its own next observation at Spearman ρ=0.734 (n=3,439). The obvious deflationary reading is that a house simply left an old number in place, so persistence is stale data, not a persistent view; restricting to consecutive pairs in which the top-marking house actually repriced leaves ρ=0.665 (n=2,228). Which companies houses argue about is stable, and it survives the marks moving.

One reading of that survives the control and is a different claim. Holdings are sticky, so the set of houses in a company's cell barely changes from date to date, and Appendix G.3 finds a house's own deviation from consensus persistent in its own right. Company identity could therefore be standing in for the identity of the pair of houses doing the arguing, which would make this a fact about valuers rather than about assets. Scoring each pair of houses in each cell separately separates them: across 31,358 pairs on 656 companies, company identity reproduces 29.0% of the variance in the absolute log difference and pair identity 35.2%, which appears to settle it the other way.

It does not. Most of the 3,010 distinct pairs are seen on one or two companies, so a pair label is largely a company label in disguise. Restricted to the 754 pairs that appear on three or more companies, company reproduces 31.7% and the pair 25.1%. Both are real and the company is the larger of the two; the shares are marginal rather than additive, since the two groupings are not orthogonal.

Noise does not do this. A spread that reordered on re-draw would not predict its own next observation, and it would not put more than half the variance between companies while a permutation of the same labels puts a tenth there.

### 6.2 Neither house moved, and they differ

Appendix B put the deflationary reading at its strongest and could not close it: if one house is simply carrying an old number, the spread is a lag, not a difference of opinion, and the way to settle it is to look at cells where *nobody* is lagging. Nine names could not supply enough of those. The population can.

A house has moved when its median across its own funds changes by more than half a per cent against its previous observation of that company, provided that observation is recent enough to be a comparison at all. Filings arrive quarterly for most funds and monthly for some, so a gap longer than a quarter is a hole in the record and not a decision to stand pat. On 3,238 cells every house present clears that bar, so the cell's freshness is knowable. In 760 of them, spread across 197 companies, not one house moved.

Those are the cells the deflationary reading predicts should be quiet. 66.4% of them are not unanimous and 23.6% (179 cells, holding $5.3B) exceed 24%. The head count is the weaker of the two: "not unanimous" admits a difference of eight millionths of a point, which is what the median quiet cell shows. What carries this subsection is the tail — 179 cells, on both sides standing still, more than 24% apart.

One further restriction shuts the other door. The quiet cells answer staleness and leave composition open, because the widest group in the panel is the one no filing describes; the cells where every filing names the same series letter answer composition and leave staleness open. Their intersection answers both, and it is 132 cells on 40 companies. Three quarters agree to within a twentieth of a point, which is the herding regime and is most of this subsample. What survives is small and is stated as small: 76 are not unanimous and six differ by more than 24%, the widest by 233% on seven funds across three houses. Six cells establish that it can happen with both explanations shut off. They do not establish how often, and §2.1's lot is the same kind of evidence.

Nor is the standstill a one-quarter coincidence: in the wide ones, 26.0% of the houses involved have carried the identical number across four or more consecutive reports. Both sides are stale and they are stale at different prices, which is not a lag but a standing difference of view — each filing is an affirmative statement of fair value on that date, not an omission. The measurement is the strict one, besides: a house whose median shifts because its own fund roster changed counts as having moved, which can only take cells out of the no-house-moved set.

Run the comparison the other way and the deflationary reading fails a second time. Cells where *every* house remarked show a median spread of 9.9% against 0.0% where none did — repricing widens the gap instead of closing it (n=1,147, Mann–Whitney p=1×10⁻²⁰). That pooled figure is confounded by which companies are in it, and the within-company version is weaker but points the same way.

Of the 129 companies contributing both kinds of cell, 34 file the same median either way and are counted as ties rather than as evidence in either direction. Among the remaining 95 companies the remarked cells are wider in 54. That is a bare majority, and a sign test cannot separate it from a coin (two-sided p=0.22), while a signed-rank test on the magnitudes can (p=0.001). The conclusion rides on the magnitudes and on the pooled comparison, not on the head count, which is the right way round, because a head count is exactly the statistic a tie rule can move. Ties are decided by a tolerance rather than by float equality, and the replication package fails if any pair sits close enough to the boundary for a rounding change to move the count.

### 6.3 A relationship this paper disowned

Across four cuts of the panel the ratio of loud to quiet median booked NAV reads 0.59×, 0.36×, 0.28× and 0.66× — below one throughout, but moving by a factor of two as the panel fills. The first cut has fourteen companies in it and separates nothing (p=0.48); on the first twenty-four report dates the estimate is highly significant (p=2×10⁻¹¹) and on the full 92 it is weaker but still clear (p=6×10⁻⁵).

An earlier draft reported this sequence starting at 169× and read it as a sign reversal. That first number was an artefact of the house map. At eight report dates the panel is thin, and Putnam's eighteen trusts and Gabelli's sixteen were then counted as separate houses, which put cells into the quiet bucket that one merged house does not produce. Merging them removed the reversal. What the section claims is therefore the sign, not the magnitude, which still spans 0.28× to 0.66×, and the whole sequence is printed rather than its endpoint.

That sequence is left in the main text deliberately. In a paper whose chief risk is that I found what I was looking for, one visible self-killed result is worth more than the space it takes.

## 7. Which mark was right

Everything to this point measures how far apart the marks are. It says nothing about which of them was closer to the truth, because between transactions there is no truth to be closer to. At an exit there is. This is the paper's only confrontation with a realized price.

Ten unicorns listed between 2023 and 2026 with a public-data trail, and seven were broadly mutual-fund-held before listing. For each, two pre-IPO signals are scored against the realized offer valuation: the stale headline, meaning the last private primary round, and the last N-PORT fund mark, converted through the IPO's own per-share price. **The fund mark is the less-wrong signal in five of the seven, with a median absolute error of 11% against the headline's 48%.**

Three things bound that immediately. Seven exits cannot support a count: an exact sign test on the five wins returns p=0.23, so the content is in the magnitudes, which do survive a paired test at p=0.078. Both medians are single observations, because with seven exits the fourth-ranked error *is* the median: the 48% is Figma's own −48.19% and the 11% is ServiceTitan's +11.06%. And that 48% is unrelated to the 48% of §1.2, where Gornall and Strebulaev put the headline above the option-adjusted fair value of the cap table. Two different objects against two different benchmarks land on one number.

The two exceptions are what sharpen the claim. Klaviyo and Circle are the only exits whose last private round was recent and fairly priced, and they are exactly the two where the headline wins. So the fund mark's advantage is not foresight. It is the absence of staleness, and it holds where, and only where, the headline has gone stale, which is the condition §8 shows is the normal one, because disagreement rebuilds within a year of the last transaction.

What this leg establishes is direction, not frequency. The marks whose *disagreement* §5 measures are not noise around a worse number. Where a price is finally revealed they sit closer to it than the number the press was citing. Appendix D carries the exit-by-exit table, the per-family harvest, the conversion-ratio robustness and the four qualifications each named exit needs.

## 8. What compresses disagreement: distance from a transaction

Sections 5 and 6 establish a level and show it is a stable trait of the company. A level is a description. This section adds the axis that description is missing (time since the last transaction) and reports the profile along it: houses converge in the month a transaction tells them what to converge on, and drift apart again at a measurable rate afterwards.

That is a dated fact about a distribution. It is not causal identification and the section does not build toward claiming it is. Five readings that would explain the shape without a round are tested and fail below — a trend in event time, a change in which houses are compared, a restatement masquerading as agreement, the calendar itself, and houses agreeing on good news, not on a price — and each has its own number, not a sentence.

The last of those is the one the placebo cannot reach and §8.4 reaches another way: news cannot push the most optimistic house down, and it comes down. What survives is that the company still chooses when to raise. The limits sit inline where each claim is made instead of in a note at the end, because they are large enough that a reader who met them later would be right to discount everything above them.

### 8.1 The hypothesis, and the confound

A priced round is the one moment a private company has something like an observable price. If between-house disagreement is *uncertainty about value*, it should be smallest just after a round and widen as the round recedes. If it is instead a standing difference in method, which is what §6.2 concludes from the cells where nobody moved, the round should do nothing at all. The test needs two dates the filings do not give directly: when a company priced a round, and when a share count was redefined so that a spread means a restatement, not a view. Section 9 builds both out of the filings, and this section spends them.

One confound has to be named before any of it can be read, because it defeated the first version of this design and it is built into the sample rather than into the estimator. A company enters this panel because a fund bought it in a round. For a company's *first* dated round, months-since-round and months-since-entering-the-observation-window are the same quantity, so any anchor placed early in the window reproduces the profile whether or not a round does anything. The collinearity does not weaken with more data. Every anchor in this section is therefore a company's second or later dated round, and §8.5 prices what admitting the first ones costs.

Two changes separate the hypotheses. Non-first rounds only: for a company already in the panel, the next round is not the reason it is there, so the anchor moves while the window does not. This is expensive (it cuts the sample from 858 cells on 123 companies to 462 on 43) and it is the price of identification. A symmetric window: a mechanism that says a round resolves disagreement predicts a *discontinuity* at zero, wide before and narrow after. The confound predicts a monotone trend and no step. Looking only forward cannot tell those apart. Looking both ways can.

### 8.2 The profile, and the step at zero

462 guarded cells on 43 companies within six months before and twelve months after a non-first dated round: 139 cells on 31 companies before it, 323 on 43 after. Because §6.1 finds the spread is a trait of the company, every observation is demeaned within its own company before anything is averaged, and Table 9 prints the pooled version beside it, so the difference is visible.

**Table 9.** Between-house spread by months to the nearest non-first dated round. "Pooled" is the median spread across cells, in per cent. "Within-company" is the median deviation from the company's own median spread, in percentage points, so a positive number is a company wider than its own norm. Restatement windows (Appendix E.2) are excluded. Selected months; all nineteen are released.

| Months to round | Cells | Companies | Pooled median | Within-company |
| --- | --- | --- | --- | --- |
| −5 | 15 | 11 | 21.94% | +2.25 |
| −2 | 23 | 16 | 12.75% | +1.80 |
| −1 | 31 | 20 | 6.82% | +0.61 |
| 0 | 46 | 29 | 0.01% | −1.40 |
| 1 | 35 | 20 | 0.00% | −3.53 |
| 2 | 33 | 21 | 0.46% | 0.00 |
| 7 | 16 | 13 | 15.56% | +3.67 |
| 10 | 12 | 10 | 24.36% | +19.79 |
| 11 | 15 | 13 | 17.64% | +10.86 |

The within-company column moves, which is the whole difference from the first design, where it was flat at every horizon. It is positive before the round, negative at it, and back above ten points a year afterwards, which is the shape of a trough.

Months −3 to −1 against months 0 to +2, paired inside each company, 31 companies: median 5.22% before, 0.00% after, a step of −2.52 points — the median of the paired per-company changes, not the difference of the two medians — narrower after in 22 of 29 untied companies. Signed-rank p<0.001, sign test p=0.0041. The bands are adjacent and narrow on purpose, so that a smooth trend in event time contributes only its slope across five months while a jump at the round contributes all of itself.

One observation per company, and why the tables below differ. The step above pairs each company's own before and after bands once: 31 companies, 29 untied. The placebo and the ladder cannot do that, because shifting an anchor changes which rounds fall in the window and therefore which company contributes, so they take one observation per anchor date: 49 anchors, 46 untied, a median step of −1.94 points at p=0.0008. Both are negative and significant; the per-company figure is quoted elsewhere because it is the conservative one, and every table below states its unit in the caption.

A phase-randomised null, with event dates reshuffled within each company's own observed report dates over 400 draws, matches or beats the observed step in 0 of 400. That number is weaker than it looks: with a random anchor both bands draw from one distribution, most companies' paired difference is *exactly zero*, and the median across companies is zero in nearly every draw. "0 of 400" therefore says only that the observed step is negative and the null never is. The statistic whose null does not collapse is the sign test, and that is the one this section rests on.

The contrast between two statistics on the same sample is the actual evidence. The first design's near-versus-far comparison gives −7.77 points at p=0.010 on this data and is still reproduced by 31% of random anchor placements. The step at zero is reproduced by none. Random anchors make a trend. Only the round makes a jump (`figures/round_event_study.png`).

### 8.3 The placebo

Three arithmetic explanations are checked before the placebo and none survives contact with the panel: the cells do not get wider across the round, the round-month cell is not the newly priced security agreeing with itself, and a restatement is not masquerading as either. Appendix F.1 gives all three with their numbers.

Non-first rounds are not randomly timed (companies raise when the market is open) so a null that moves the anchor to a random date does not test that objection. A placebo does. Shift every anchor by a fixed number of months and the calendar month, the market conditions and the company's own filing rhythm all survive. Only the event is removed.

**Table 10.** The step at the round and at three shifted anchors. Each row re-runs the whole design with the anchor moved by the stated offset. One observation per round, not per company (§8.2). Sign p is one-sided against the alternative that the post band is narrower.

| Anchor | Events | Companies | Median step (pts) | Negative / untied | Sign p |
| --- | --- | --- | --- | --- | --- |
| the round | 49 | 31 | −1.94 | 34 / 46 | 0.0008 |
| six months before | 37 | 22 | 0.000 | 14 / 31 | 0.763 |
| six months after | 49 | 35 | 0.000 | 17 / 41 | 0.894 |
| twelve months after | 37 | 29 | 0.000 | 13 / 31 | 0.859 |

Table 10 runs all four. At the round the step is there; at all three shifted anchors it is gone, and gone in the same way each time: a median of exactly zero and a sign count on the wrong side of a coin, 14 of 31, 17 of 41 and 13 of 31.

Those three zeros are the same degeneracy the step's own null has, so the sign counts and not the medians carry the argument on those rows. One earlier reading of this table is withdrawn: the six-month anchor appeared to move, an anomaly the text then predicted from the rebuild rate, and it was an artefact of an event list that counted one anchor date once for every series letter first seen in that month. Deduplicated, that anchor gives zero like the other two.

The placebo is stronger for losing it. A predicted anomaly asks a reader to accept the rebuild rate before the placebo can be read as passing; three anchors that each return exactly zero and a sign count on the wrong side of a coin ask for nothing at all.

### 8.4 Which side of the cell moves

The placebo removes the event. It cannot remove the reading that a price arriving and good news arriving are the same thing, because both are removed together. That reading has a signature the data can check: news moves every house the same way. All of them revise toward the new number, and the cell narrows because the laggards catch up. Nothing about good news pushes the *most optimistic* house down.

So the cell is decomposed rather than measured. With the consensus taken as the median across house medians, the upper gap is how far the top house sits above it and the lower gap how far the bottom house sits below. A one-sided story moves one of them.

The decomposition costs two cells in five, and the reason is not a robustness choice. Asking which of two houses moved is asking something two numbers cannot answer: with two opinions the median is the midpoint between them, so the upper and lower gaps are the same number by algebra, and the top house coming down is indistinguishable from the bottom house going up. Somebody has to have stayed put. So the table is computed on the cells carrying three houses or more, 60.5% of the panel's guarded cells, and the ones it drops are silent on the question rather than inconvenient in their answer.

**Table 11.** Which side narrows across the round, and at the same three shifted anchors. Sign p is one-sided against the alternative that the gap narrows. Selecting the top house selects partly on its own error, so the placebo rows are the test, not the decoration.

| Anchor | Events | Top house narrows | Sign p | Bottom house narrows | Sign p |
| --- | --- | --- | --- | --- | --- |
| the round itself | 42 | 29 / 34 | 2×10⁻⁵ | 23 / 37 | 0.094 |
| six months earlier | 31 | 14 / 22 | 0.143 | 11 / 23 | 0.661 |
| six months later | 43 | 14 / 30 | 0.708 | 15 / 34 | 0.804 |
| a year later | 32 | 10 / 24 | 0.846 | 14 / 27 | 0.500 |

At the round the top house comes down in 29 of 34 untied anchors (Table 11). No shifted anchor reproduces it. Two sit below a coin, 14 of 30 and 10 of 24 at the later anchors, and the third leans the same way at 14 of 22 without clearing five per cent, p=0.143 against 2×10⁻⁵ at the round. The bottom house clears five per cent at no anchor, the round included.

The asymmetry is the finding, and it is a smaller finding than a symmetric one would have been. Read the round row across and the temptation is to call 0.094 confirmation because the column beside it is 2×10⁻⁵; that is reading a p of 0.09 as a result on the strength of its neighbour, and this paper does not have the events to earn it. What the table supports is the one-sided claim: the optimist comes down. Whether the pessimist comes up is a question the 37 untied anchors on that side cannot answer.

The one-sided claim is the one that does the work, because it is the half good news cannot produce. It is also the half most exposed to a mechanical objection, the one Appendix G.3 refuses to let pass there: a house is selected as the top house partly on its own error, so mean reversion narrows the upper gap whether or not anything converges. Mean reversion does not know where the rounds are. It operates at every date, and the shifted anchors are every date: pooled across the three, the top house narrows in 38 of 76 untied anchors, a coin to four decimal places.

What this removes is one specific story (that the compression is houses agreeing on good news) because that story has no mechanism for pulling the optimist down. The endogeneity of the timing itself is untouched, and it is §8.5's.

### 8.5 The limits: selection, a better rule, and the down rounds

The result is sensitive to which events are admitted, and the sensitivity is printed here. The funnel: 5,885 company-series pairs in the panel carry a letter, 434 are dated under the rule of §9, 75 of those are non-first anchor dates, and 49 have guarded cells in both bands.

**Table 12.** The selection ladder: the step recomputed as each filter is relaxed. One observation per round, as in Table 10.

| Selection | Events | Median step (pts) | Negative / untied | Sign p |
| --- | --- | --- | --- | --- |
| dated, non-first, restatement out, guarded | 49 | −1.94 | 34 / 46 | 0.0008 |
| keep restatement windows | 50 | −1.60 | 34 / 47 | 0.0015 |
| all cells, not only guarded | 49 | −1.94 | 34 / 46 | 0.0008 |
| admit first rounds too | 64 | −1.08 | 43 / 60 | 0.0005 |
| drop the two-house bar | 103 | −0.00 | 55 / 93 | 0.048 |
| drop it and keep restatement | 107 | −0.00 | 57 / 97 | 0.052 |

Two filters turn out not to matter at all: restatement windows move the median by three tenths of a point and restricting to guarded cells changes nothing to four decimal places. Two move the magnitude, and they move it in the way §8.1 predicts. Admitting first rounds halves it, from −1.94 to −1.08, which is the confound arriving on schedule.

A first round's anchor sits on top of panel entry, and 15 such anchors are enough to halve a step measured on 49. Its sign test reads *stronger* than the base rung, at p=0.0005 against 0.0008, and that is the point, not a puzzle: fifteen extra events add power to a sign test while the thing being signed shrinks. This is why §8 quotes the magnitude and carries the p-value beside it. Dropping the two-house bar on the round date takes the magnitude to zero at six decimal places, and that one has no such defence.

That bar was not chosen here and it is not a researcher degree of freedom exercised after seeing this statistic. It was read off the N-CSR calibration in Appendix E.3, before this statistic existed, and the eight one-house pairs it excludes miss the N-CSR acquisition date by 49 to 670 days: Discord Series G at +670, SpaceX Series B at +570, OpenAI A-2 at +426. Admitting them does not add rounds. It adds anchors placed months away from the event, and a misplaced anchor smears a step by construction.

The limit is real and it is a limit on the size, not on the direction. At the widest selection the magnitude collapses to zero at six decimal places while the sign holds: 55 of 93 untied anchors are negative, 59%, at a sign test of p=0.048. *A reader who does not accept the two-house bar as a round-dating rule should read this result as a direction with no reliable size.* That rung read as indistinguishable from a coin until the event list was deduplicated: 17 of its anchors were the same date counted twice, and a sign test reads duplicates as independent draws. The magnitude still does not survive, and that is what bounds the result.

The obvious way out is a better dating rule, not a looser one, and there was a candidate: a round creates a *price*, so a round month should be the first in which two or more houses report the new series at prices that agree. It dates worse, for a reason this paper finds elsewhere — houses are a median 30 days apart in recognising a corporate action (Appendix E.2), so waiting for the second house waits on its reporting calendar, not on the company's. Appendix E.3 runs it against the count rule in full. What it does to the step belongs here, because it is the one place in this section where the halves of a result come apart cleanly: the magnitude goes with the anchor, −1.94 points to −0.06, and the sign holds at p=0.022. The count rule stands, and so does the limit on its size.

The endogeneity a placebo cannot reach is that the company chooses when to raise. The discriminating test splits rounds on the change in the median price per share, a level, not a spread, so not the dependent variable in disguise. If houses converge because *the news is good*, the step lives in the up rounds. If they converge because *a price now exists*, it lives in both.

**Table 13.** The step split on the change in the median price per share across the round. Per anchor date, as in Tables 10 and 12, and (unlike them) with restatement windows kept, which is why the "all" row reads 50 events rather than 49 and matches the second rung of Table 12, not the first.

| Rounds | Events | Median step (pts) | Negative / untied | Sign p |
| --- | --- | --- | --- | --- |
| up | 43 | −1.94 | 31 / 40 | 0.0003 |
| down | 7 | 0.000 | 3 / 7 | 0.77 |
| all | 50 | −1.60 | 34 / 47 | 0.0015 |

Table 13 splits the rounds. Seven down rounds is not a test. The step is measured almost entirely on rounds that raised the price, and the down rounds return nothing at all instead of something opposite: a median of zero and three of seven negative. The reading "houses converge on good news" is therefore not excluded. That is a limitation of the result, not a caveat to it, and it sits above the endogeneity note rather than beside it. What would run the test is a panel through a full down-cycle, or a lower dating bar, and the ladder above prices exactly what the second costs.

### 8.6 What survives the limit: a rate, and the step inside one company

The limit above is about the *event list*: admit anchors the dating rule cannot place and the magnitude goes. Two things do not depend on that list, and they are what a reader who accepts the limit is left with.

The within-company deviation runs −3.53 at month one and +10.86 at month eleven, so there is a rate in there. Fitted per company over months 0 to 12 and taken as the median across companies: +1.11 points a month, rising in 24 of 36 companies, sign p=0.033.

A slope is a trend, and a trend is exactly what the phase null reproduces for the near-far statistic, so this one has to clear the same null. It does (4% of random placements match or beat it) but the null's own median slope is +0.05 points a month, which is the general within-window drift. The number to quote is therefore not the raw slope:

> A round buys house agreement for about a quarter, after which disagreement rebuilds at roughly 1.1 points a month, almost all of it attributable to the round, not to the drift any anchor produces.

That is a dated, filing-sourced rate, and it is the one quantity in this section that does not depend on which anchors are admitted.

Thirty-one companies is the standing complaint about this result, and the answer is not more companies but more anchors inside the ones there are. A company with several dated non-first rounds carries the anchor to several places in its own window. A company-level time trend can produce a step wherever the window starts. It cannot produce one at each round.

30 rounds on 12 companies, 10 of which carry two or more. Median step −8.81 points, negative at 23 of 29 untied rounds, sign test p=0.0012, and negative at *every one* of its own rounds in 5 companies.

### 8.7 What this is, and what it is not

Section 4.3 reports a bimodal picture: names with a fresh, believed round are herded and stale ones are dispersed, and read on its own that looks like two kinds of company. The trough says otherwise. The same company is herded in the month it prices a round and dispersed a year later. The bimodality is a snapshot of a distribution of companies over one phase variable, not two populations, which is why the two modes never separated cleanly on any company characteristic. They are not a company characteristic.

It also says what §2's microscope can and cannot corroborate. The four cross-book disagreements the N-CSR schedules find are all Databricks, on the series it issued most recently, in the quarters it was repricing. That is consistent with a phase effect and is not evidence of one: ten names and four disagreements cannot separate a phase from a company. The population panel and the event study carry that claim. The schedules of investments show what a single lot looks like when the deflationary readings are closed.

It is evidence that between-house disagreement collapses in the quarter a company prices a round and rebuilds over the following year: on 31 companies, at monthly resolution, with the anchor separated from panel entry, surviving a within-company demeaning, a composition check, a new-series check, three shifted-anchor placebos and a repetition test inside single companies.

It is not evidence about why a company raised when it did. The null tests placement inside a company's own dates, not the decision to raise, and §1.1 lists what that leaves unclaimed. The honest next step is more companies with several dated rounds, which Appendix E.3 supplies at 24 companies with three or more, and a panel long enough to contain a down-cycle.

## 9. Four measurements recovered from filings

The tests above need four dates the filing system does not publish as dates: when a company listed, when its share count was redefined, when it priced a round, and what a holder paid. Table 14 sets out all four. Each is recovered from documents that are public, machine-readable and already on disk, and each is calibrated against an independent document type. Every threshold below is read off a gap in the observed distribution rather than chosen, which is the only defence available when a threshold is set by the person who later benefits from it.

**Table 14.** The four measurements, what each recovers, what it is calibrated against and how well it does. Appendix E gives each in full: the design, the corrections that shaped it, and what it cannot see.

| Measurement | Recovered from | Reach | Calibrated against | Accuracy |
| --- | --- | --- | --- | --- |
| Listing dates | Form 8-A12B, or 8-K12B through a shell | 21 of 23 classified listings | the last date the panel carries the name private | eighteen of 21 inside a quarter, widest 82 days against a next-closest 258 |
| Share splits | the share-count panel: a split multiplies the balance by *k* and leaves the value alone | 601 candidates → 29 events on two or more houses | the ratios companies actually split at | 26 of 29 canonical; restatement spans a median 30 days and up to 92 |
| Round dates | the first report month a new series letter appears across two houses | 434 company-series pairs on 287 companies | the earliest N-CSR acquisition date for the same series | Fourteen of fifteen dated pairs land inside 35 days, median gap 16 |
| Acquisition dates and cost | Regulation S-X schedules of investments on Form N-CSR | 767 schedule rows, 10 companies, 44 registrants, 429 lot-period-series | EDGAR's own prefiltered accession set | zero missed accessions across all ten companies |

Three of the four produced a finding of their own on the way, and each is a correction some other part of this paper needed: restatement is not simultaneous, so a one-month confirmation window is the wrong unit; confirmation counts houses and never registrants; and a cost per share is not comparable across filings where a markup is. Appendix F.3 gives all three with their numbers.

## 10. What would overturn each claim

A paper that reports its own limits at the end invites the reading that the limits were an afterthought. Sections 7 and 8 therefore carry theirs inline. What this section adds is the falsification map, the observation that would kill each claim, followed by the limits that belong to the design as a whole, not to any one result.

**Table 15.** Each claim, what would overturn it, and where the paper already tests that.

| Claim | What would overturn it | Where tested |
| --- | --- | --- |
| The unit of an independent valuation is the house | Marks inside a mapped complex disagreeing more than marks inside a single registrant | §4.1: 89.0% identical inside a complex against 87.5% inside a registrant |
| Between houses the median company-date is 12.1% apart | A resolver error fusing two companies, or an instrument that is not the stock | §3.2: identifiers only, 25,482 claim-instrument rows excluded, twelve price outliers decided one by one |
| The disagreement is not a reporting artefact | Two houses disagreeing on the Level-1 holdings they share | §2.3: Fidelity and T. Rowe Price, cross-house spread 0.00% on the five verified shared public holdings, against 12.5% for the same pair on a shared private name and tens of per cent across other pairs (§4.3) |
| The disagreement is not a share class or a lot | A wide cell where the series and the acquisition date are provably identical turning out to be neither | §2.1: both are disclosed on the Series J lot and the spread is 10.2% |
| The disagreement is not staleness | Cells where no house moved being unanimous | §6.2: 66.4% of 760 such cells are not unanimous |
| It is a company trait, not a date effect | Between-company variance falling to the permutation null | §6.1: 58.8% against 9.7% |
| Disagreement compresses at a round | A shifted anchor reproducing the step | §8.3: a median step of exactly zero at all three shifted anchors |
| …and the compression has a size | The step surviving a wider event selection | §8.5: it does not — the median step is zero to six decimals at the widest rung, p=0.048, and this is reported as the result's limit |
| The marks beat the headline at exit | The fund mark losing once the conversion bridge is varied | §7 and Appendix B: 4–6 of 7 across conversion ratios 0.8–1.2 |

The one row of Table 15 that fails is printed alongside the ones that pass. That is deliberate: §8's magnitude does not survive its own widest selection, the paper says so where the claim is made and again here, and a reader who discounts §8 to a sign should still be left with §§2–7 intact.

### 10.1 Nothing here is pre-registered

Nothing in this paper is pre-registered, and that applies to every number above.

One thing can be offered in its place, and it is offered because it costs something. Of the five predictions the drafted registration makes, P4 (that cross-house dispersion collapses as a company approaches its listing) can already be run on the listings that predate the registered window, and it was. It does not hold: fifteen names, six narrowing, seven widening and two unchanged, a one-sided signed-rank test at p=0.43, with a power calculation beside it saying the null means *not large* rather than *absent* (Appendix F.4). A prediction this paper's own framework generates, tested before filing and reported failing, is worth more than the same prediction filed and left unrun.

Which framework failed matters, because two of them predicted opposite things here and only one is this paper's. If disagreement closes because information arrives, P4 had to hold: the weeks before a listing carry a roadshow, a range and a prospectus, which is as much news as a private company ever generates. If it closes because a *price* arrives, as §8.4 argues, P4 had no reason to hold, because before the IPO prices there is still no price. The data chose the second. The weak tilt to widening is what §8's rebuild rate of about 1.1 points a month implies for names whose last round is by then maximally stale. P4 is therefore a discriminating test that the anticipation reading lost, not a hole in the price-arrival one, and the power calculation stands unchanged: at fifteen names the null means *not large*.

A registration is drafted and not filed. Appendix F.4 gives the argument in full: what filing before the next panel extension would buy, the power calculation behind P4, and the one contrast in this project that a registration was written for. That contrast (a demand-favored sector split) is not in this paper. It left with the secondary leg (§3.4), and Appendix F.4 keeps its pre-registration record because the record is what makes the exclusion checkable.

### 10.2 What the p-values in this paper are, and are not

Two properties of the design bear on every significance figure above, and both are stated
here because the paper quotes dozens of them.

The observations are not independent. A cell is a company on a report date, and cells of one
company share whatever makes that company contested, while cells of one date share whatever
the market did that month. Appendix B says so for the tracer panel and quotes its pooled
p-value "only to show which way the comparison runs"; the same caveat governs the population
tests, and §6.2's p=1×10⁻²⁰ in particular is a pooled figure on 1,147 cells that are
correlated in both directions. What is *not* pooled is the evidence the paper actually rests
on: the step at the round is a paired within-company comparison, one observation per company
or per anchor date, and §6.2's within-company version is reported beside the pooled one and
is weaker. Where the two disagree the paper quotes the within-company figure.

Nothing here corrects for multiple comparisons, and the paper runs on the order of thirty
sign and signed-rank tests. The core survives any correction that could reasonably be
applied: the step at the round is p=0.0008 and the top house coming down is p=2×10⁻⁵, and a
Bonferroni factor of thirty leaves both under conventional thresholds. Two results do not,
and they are the two the paper already flags as its weakest — the widest rung of §8.5's
selection ladder at p=0.048, which a correction of any size removes, and the reversion tilt
of Appendix G.3, which does not reach five per cent in either direction even uncorrected, at
p=0.085 one-sided and 0.170 two-sided. Neither carries a claim on its own, and a reader should take
the first as a direction without a size and the second as not established.

## 11. Conclusion

Four things, and the first makes the other three possible.

**The unit of an independent valuation is the fund house, not the trust that files.** N-PORT names a legal trust. A house files under dozens of them, and one valuation committee sets every mark inside it. Counting trusts as opinions turns the whole finding into a median company-date spread of 0.004%. That is agreement manufactured by counting one committee thirty times. On the corrected unit, independent houses carry the same private share a median of 12.1% apart, and 10.1% apart across the venture-backed companies the term "unicorn" is about. Only 17.0% of company-dates are unanimous. The census runs over 309,654 marks and twenty-seven quarters, with no company list consulted anywhere.

**That width is about the price roughly half the time, and the paper says which half.** Where the filings name the series and two houses name the same one, the median gap falls to 0.74% from 8.45% on those same cells. The typical gap is largely two houses holding two rounds of one company. The tail is not, and it is a count, not a conditional median: 597 company-date-series groups across 68 companies where two houses hold one named series more than 24% apart. What the test cannot reach is the half of the population no filing describes. Those cells are wider than the ones it can reach, so the unmeasured part is more contested than the measured part rather than less.

Three further tests say the residue is real. Two houses agree to the cent on five shared public securities and stand apart on the private names in the same filings. In 179 cells no house moved its mark and the two sides stand still more than 24% apart. And one lot has an entry price that is disclosed and provably common: Databricks Series J at $92.50, carried by two houses eleven dollars a share apart six months later, and to the same number by year end.

**And that width has a shape: a consensus and a dissenter.** The headline is a maximum over a minimum and grows with the number of houses in the cell, so the panel is read a second way, between two houses drawn at random. That median is 5.88%, and the gradient inverts: the widely held companies are the ones where most houses agree and one does not. In the 2,326 cells with three or more houses and a dissenter the furthest house stands 25.54% from the median of the rest, whose widest pair is 1.57% apart. Which house sits outside is a standing fact about the house: the same one returns in 65.1% of cases against a 25.4% null, and how often a house plays that part varies thirty-fold across the twenty-seven the panel can measure.

**What closes it is a transaction, and only briefly.** Disagreement falls 2.52 points across the month a company prices a round and rebuilds at roughly 1.1 points a month, on rounds dated out of the filings themselves. Shifted anchors show no step. What it costs is small: repricing every fund's private book at the cross-house consensus moves a median 0.33 basis points of its own net assets, concentrated in 75 funds and above a full per cent for five of them. That measure runs on a panel that agrees more than the population does, so it is a lower bound on a small number (Appendix G).

Private-company value is not a number but a distribution. Its width is a function of how long it has been since anything traded, its shape is a consensus with one house outside it, and both are now measurable, decomposable and dated.

## Appendix A. Data and variable definitions

### A.1 Every dataset, and how each is built

Every dataset is a committed CSV in `data/`; each row carries its own source and date, and `notes/data_dictionary.md` in the replication package documents every column. Table A.1 summarises the datasets and the derived object each feeds; Table 3 of §2.3 reports the Level-1 placebo in full.

All signals are public; headline rounds are non-copyrightable facts sourced from company announcements and financial press (each row in `data/` carries source + date). Every other input is an SEC filing. One window runs throughout: 2019Q4–2026Q2, the span of quarterly bulk data sets harvested. Where a figure is quoted against a narrower one, the narrower window is named where it is used.

- Cross-fund N-PORT marks, the by-company harvest. This file is the input to §4.3's anatomy of ten named cells and is not the input to any population figure: Appendix C.3 recomputes all ten from the bulk data, where the median runs from 23.5% to 34.7%, and the body quotes the bulk figures wherever the object is a level rather than a named mark. (`data/fund_marks.csv` carries 409 raw Level-3 rows harvested by `src/nport_fetch.py` from EDGAR full-text search over Form NPORT-P; the documented cleaning below cuts these to 386 Level-3 holdings across 104 mutual funds and 15 companies. The harvester keeps only Level-3 marks, which also discards public-company namesakes the text query collides with — e.g. the Tokyo-listed PLAID, Inc. vs the US private Plaid). For each fund × company I compute the blended implied price per share, Σ(fair value)/Σ(shares), from the private-equity holdings (`<invstOrSec>` with `fairValLevel`=3, `isRestrictedSec`=Y, `units`=NS, `assetCat`∈{EC,EP}). My metric is the cross-fund spread in that price conditional on the report date, so it measures disagreement instead of differing fund fiscal quarter-ends. special-purpose-vehicle (SPV) / fund-of-fund wrappers and 10:1 unit-convention outliers are dropped, and composites whose holders split across share classes or legal entities — SpaceX (auto-detected) and ByteDance (a documented manual exclusion: Douyin Co Ltd vs ByteDance Ltd, common vs convertible-preferred) — are excluded from the per-share comparison (`src/fund_marks.py`).

- IPO-exit validation (`data/ipo_validation.csv`, `src/validation.py`): for the ten unicorns that listed 2023–26 (seven broadly mutual-fund-held pre-IPO: Instacart, Reddit, Chime, Figma, ServiceTitan, Klaviyo, Circle) I score two pre-IPO signals against the realized IPO valuation — the headline (`overshoot = last_private/IPO − 1`) and the last pre-IPO mutual-fund N-PORT mark, converted to an implied valuation through the IPO's own per-share price (`implied = IPO_val × mark_pps / IPO_pps`, since pre-IPO preferred converts ~1:1 to the IPO common at a healthy listing, so the implied-valuation error equals the per-share error). The least-wrong signal is the one with the smaller absolute error; the `vintage` field tags the 2021-peak cohort, whose headlines are the stale ones. Klarna, with no broad mutual-fund mark, uses its 2022 down round.

- Statistics (`src/robustness.py`): binomial sign tests and Wilcoxon signed-rank tests throughout, and permutation nulls where a statistic has no closed form. The module also computes a bootstrap interval on the secondary cross-section's median, which belongs to a leg this paper no longer carries (§3.4) and is left in place for the second paper.

**Table A.1.** Datasets, key fields and derived objects (all inputs public; SEC N-PORT is public domain).

| Dataset (`data/*.csv`) | Coverage · key fields → derived object (§) · source basis |
| --- | --- |
| `nport_population_marks.csv.gz` | the paper's core. 309,654 Level-3 private marks · 15,443 issuer strings · 104 report dates, 2019Q4–2026Q2: CIK, series, report date, balance, valUSD, fair-value level, issuer name/title, CUSIP/LEI → the company × report-date panel (§2.1, §5, §6). SEC N-PORT quarterly bulk data sets, public domain. |
| `population_cells` | 4,271 guarded cells · 656 companies: company key, report date, house count, min/max house median, fund count, booked NAV → every figure in §5 and §6. Derived from the marks file by `src/population.py`. |
| `company_classification` | 656 clusters: label, basis (verified / rule / unclassified), reasoning line, booked NAV → Table 8 and the venture-backed population (§5.5, Appendix C.2). Filings plus the public record, one cluster at a time. |
| `ncsr_acquisitions` | 767 schedule rows · 10 companies · 44 registrants · 429 lot-period-series: filer, CIK, accession, acquisition date, cost, value, shares, period → the disclosed entry price and the cross-book comparison (§3.1–3.2, Appendix E.4). SEC Form N-CSR schedules of investments. |
| `round_dates` | 5,885 company-series pairs, 434 dated on 287 companies: first report date, funds, houses, censored, dated → the round anchor of §8 and its calibration (Appendix E.3). Derived from the marks file. |
| `split_events` | 601 candidates → 29 confirmed events: company, k, window, restatement span, funds, houses, registrants → the restatement windows §8 drops (Appendix E.2). Derived from the marks file. |
| `round_event_study` / `..._stats` | 19 event months and 110 statistics: profile, step, placebo, ladder, up/down, rebuild rate, plus a design key hashing the inputs → every number in §8. Derived; regenerated by `src/round_event_study.py`. |
| `listing_dates` | 21 of 23 classified listings: CIK, form (8-A12B / 8-K12B), listing date, days to the last private mark → the listing anchor (Appendix E.1, §10.1). SEC EDGAR. |
| `mark_staleness` | 116 multi-family company-quarters: family medians, remark flags, cross-family spread → the staleness test on the tracer panel (Appendix B). Derived from `fund_marks_timeseries`. |
| `fund_marks_bulk` / `version_reconciliation` | the ten §4.3 cells recomputed with the eighteen-filing cap lifted → Appendix C.3. Derived from the marks file. |
| `ipo_validation` | 10 exits (7 fund-held): headline, realized IPO ($B, $/sh), pre-IPO signal ($/sh, date, SEC accession), vintage → overshoot and fund-mark error via the per-share bridge (§7). SEC N-PORT; CNBC/Bloomberg/Fortune et al. |
| `ipo_premarks_byfund` | 18 family-exit rows: family, last pre-IPO mark $/sh, IPO $/sh, error → family-level adjudication (§7). SEC N-PORT (paginated full-text search). |
| `fund_marks` | 409 raw → 386 clean Level-3 marks · 104 funds · 15 companies: fund, registrant, accession, report date, balance, valUSD, fair-value level → per-fund implied $/sh = Σval/Σshares and the same-date cross-fund spread (§4.3). SEC EDGAR Form NPORT-P. |
| `level1_placebo` | 5 securities × 2 families: CUSIP, fund, $/sh, accession → cross-family spread on *public* marks, reported in Table 3 (§2.3). SEC N-PORT. |
| `nport_expansion_probe` | 29 marks · 5 names, schema as `fund_marks` → out-of-panel replication and the universe boundary (Appendix B, §10). SEC EDGAR Form NPORT-P. |

The Level-1 placebo is reported in full in the body, as Table 3 of §2.3, because it is a falsification test of the paper's central claim, not a robustness detail.

### A.2 What the resolver has missed

§3.2 excludes non-stock instruments on the security title and says that each revision of this paper has found a class the previous one missed: contingent value rights, contra positions, warrants and rights written in the singular, and lock-up placeholders — the last a line a filer books as DUMMY before the paper it stands for exists, Foresight Energy's carried at $1.47 against real equity between $7.93 and $16.33. That is the history the two structural tests in §3.2 replaced the spelling list with, and it is written down here because the useful thing about it is the failure mode, not the four spellings.

Switching off the dummy-equity class and the expiry test costs fifteen cells and moves the population median by a third of a point, which is the right order for lines this small. They are not harmless where they land, though, and the sign runs both ways: removing the dummy equity from three cells brought those cells back inside the class guard, so the panel gains cells as well as losing them.

Two limits of the join survive both tests, and both are visible in the output.

The issuer *name* can simply be false. Two hundred and nineteen rows read "VENTURE CORP LTD" in the issuer field while the security title reads "VENTURE GLOBAL LNG INC SR C PP", a listed Singapore electronics manufacturer's name on a private LNG developer's stock, and they carry no CUSIP and no LEI, so nothing contradicts it. The resolver clustered them on the name it was given, which is what it is for, and the one genuine Venture Corp row in the data ended up attached to them. Across the reported cells, 2.52% of rows put one company in the issuer field and a different company in the security title, spread over 57 clusters. `company_class.name_mismatch` reports the condition as a queue for review instead of acting on it, because the title is not automatically the truthful field either.

A third limit is not a defect of the resolver but of the comparison it feeds, and §4.3's two exclusions are the clearest cases of it. SpaceX is out of the per-share panel because funds hold genuinely different classes (common near $526, others several-fold higher) and some report share counts on a 10:1 basis. ByteDance is out for a sharper version of the same problem: its holders do not agree on *what* they hold. Fidelity books the Douyin Co Ltd entity (~$257), BlackRock the ByteDance Ltd Series E-1 common (~$253), T. Rowe Price a convertible-preferred Series E (~$386), so its apparent 53% spread is a class-and-entity artefact, not a valuation view. That two sophisticated holders can disagree about the security label is the reason §3.3 exists.

Failing closed has a price of its own. An issuer whose filers spell it several ways lands on several keys, each of which must then clear the five-fund two-house bar alone. In this panel seven companies reach a cell under more than one key: xAI, Ant, Caris, Didi, Rivian, Windstream and Venture Global. That can only cost coverage, never invent a spread, but it inflates any count of companies, so §5.5 reports issuers as well as clusters.

### A.3 Limits of the population panel

Sections 7 and 8 carry their limits inline, where the claim is made. This subsection and the next are the second statement, for the panels, not for a single result, and they sit here so that the body states each limit once.

The population panel (§5) carries five limits of its own. Its unit of independence is the fund complex, and the map from registrant to complex is mine: it covers 98% of the booked value by rule and leaves the rest as singleton houses, which biases every reported figure toward *agreement*, so the disagreement it reports is a floor. It cannot see sub-advisory mirroring at all — the twenty-two insurance-trust funds carrying T. Rowe's Instacart mark (Appendix D) sit under four different insurers and count as four houses here, which is what the map is for and is also why the mirroring is invisible to it, but two genuinely different houses running the same sub-advisor would still read as two views.

The share-class guard discards 31% of otherwise qualifying company-dates, and while inspection says those are unit and class artefacts, the guard is a threshold, not a diagnosis. And the panel covers what registered funds happen to hold at Level 3, which is a sample of the private market drawn by the holders, not by the companies: a private company no mutual fund holds is invisible to it.

Fifth, the venture label of §5.5 is a judgement wherever the filings stop short of one. It is checked cluster by cluster over 93.6% of the booked value and applied by rule over 3.7% more, where it is right 94% of the time against the clusters that were checked, but 94% is not 100%, its errors run in one direction (a private buyout company no filer called a private placement reads as listed), and 2.5% of the value carries no label at all. A reader who draws the boundary differently can read the alternative straight off Table 8, which is why all four totals are printed, not only the one the paper quotes.

Three further limits belong to the four measurements and are stated with them in Appendix E: the round-date rule cannot see rounds that reuse a letter, the split detector dates a restatement to a window, not a day, and the N-CSR harvest covers ten companies and whichever filers happen to schedule them.

### A.4 Limits of the cross-fund panel

For the fund-mark leg, per-share marks are comparable only after dropping SPV wrappers, 10:1 unit-convention outliers, and composites whose holders split across share classes or legal entities (SpaceX, auto-detected; ByteDance, a documented manual exclusion — Douyin Co Ltd vs ByteDance Ltd, common vs convertible-preferred). Cross-fund spreads are reported conditional on the report date to remove fiscal-quarter timing. And because marks cluster by family the effective number of independent views is the number of *families*, not funds — so the cross-fund spreads document disagreement, not a precise distribution.

The level of the median spread is itself sample-dependent (it rose from 13% to 24% when the panel was widened from eight to ten broadly-held names) and, on the same ten names, coverage-dependent in one direction only: the harvest behind Table 4 stopped at eighteen filings per name, and lifting that cap moves the median to 34.7% (Appendix C.3), so 24% is a floor, not an estimate. What survives the change of sample is the bimodal split — herding on fresh rounds versus tens-of-per cent disagreement on stale, repriced or contested names — not the precise median.

N-PORT also covers only mutual-fund-held names, a second selection, though a structurally bounded one: a five-name expansion probe (Appendix B; `data/nport_expansion_probe.csv`) found exactly one further name clearing the bar and the rest disclosed by at most a handful of funds or in mixed preferred classes (Perplexity's D-1/E-1 against common), so the ten-name ≥5-fund panel sits close to the full broadly-co-held universe instead of being a convenience subset, and widening it is linear archival work, not a suppressed sample. And the named additions (Plaid, Revolut, Gusto, plus the excluded ByteDance) were chosen because they are broadly held, so they describe large fund-held unicorns, not unicorns generally.

For the IPO-exit leg (§7), ten exits clear the public-data bar and seven were broadly mutual-fund-held pre-IPO, so the "fund mark beats headline" finding — now five of seven, with two clean counter-examples — is a stronger illustration on a handful of large, fund-held listings, but still not a population inference; the fund-mark→valuation bridge assumes the pre-IPO preferred converts ~1:1 to the IPO common (so the implied-valuation error equals the per-share error).

Reddit's, Chime's, ServiceTitan's, Klaviyo's and Circle's marks each come from a single fund family (Fidelity; Alger; T. Rowe Price; ClearBridge, a Franklin Templeton affiliate; Fidelity), and several (Chime ~6 weeks, Circle ~5 weeks, ServiceTitan and Figma ~2–3 months) are dated close to a visible exit, so part of their accuracy reflects proximity to the listing — indeed, a fund marking a holding weeks before a *visible* IPO may be anchoring toward the roadshow price itself, so the edge is best read as the absence of staleness (possibly aided by IPO anticipation), not independent foresight.

The two counter-examples are themselves informative rather than noise — Klaviyo and Circle are the two names whose last round was recent and fairly priced, so the headline was not stale and the fund mark had no staleness edge (and Fidelity's Circle mark in fact *undershot* a hot crypto listing), which is why the paper frames the fund mark's advantage as conditional on headline staleness rather than universal.

Figma's "floor" is itself partly a staleness artefact (no priced primary round after 2021). ServiceTitan's headline is a *structured* Nov-2022 down round carrying a compounding IPO ratchet, and Circle's is its 2022 Series F (the widely-cited $9B was a terminated SPAC, not a round), both flagged.

For Instacart I use the T. Rowe Price / American Funds series that two families mark alike ($32.50), Fidelity's senior Series I preferred being a higher-priced class (the §4.3 cross-class caveat again). Exits are self-selected — only companies that chose to list, at a price the bookrunners could clear (the dynamic sample-selection of Cochrane 2005 and Korteweg and Sorensen 2010). And the three additions (ServiceTitan, Circle, Klaviyo) are the broadly-fund-held 2023–25 unicorn listings I screened *together* for a clean pre-IPO Level-3 mark — all three had one and all three are reported, including the two that break the pattern, so the result is not cherry-picked, though I do not claim to have screened every 2023–25 listing.

Finally, the reconciliation with Gornall–Strebulaev (Appendix C.1) is *interpretive*. I do not re-estimate their contingent-claims model, because the public signals used here carry no per-round legal terms, so the mapping from their term-structure wedge to this paper's cross-section is a qualitative correspondence the sign pattern supports, not a re-derivation of the 48%. It resolves the apparent tension and organises the cross-section. It is not itself a fresh estimate of fair value.

## Appendix B. Robustness

Every headline result survives the obvious attacks; the suite and its outputs are released (`src/robustness.py` → `data/robustness_summary.csv`).

Table B.1 is the summary: every result, the stress test it was put through, and what came back.

*Cross-fund marks (§4.3).* The 24% median spread over the ten names with ≥5 funds is invariant to the unit-outlier band (identical at 23.7% for every K∈[2,5], that being the median once the band removes Discord's pair of BlackRock marks at ~10× the fund cluster, the sole 10:1 unit-convention artefact among the median-entering names) and to the fund-count threshold, since no mark sits near the cut. Collapsing each family to one mark, so that a house filing many funds cannot inflate the spread by sheer count, leaves the disagreement intact: Anthropic 39% across 3 families, Gusto 32% across 3, Databricks 15% across 6.

A one-way variance decomposition of the log marks then measures the house-policy pattern §4.3 asserts qualitatively. Among the names with material disagreement (Anthropic, Revolut, Gusto, Discord, Databricks, Canva) the between-family share of variance is ≈1.00: essentially all of the cross-fund variance is between houses, none within. The within-family spread is exactly zero, funds in a house filing the identical mark to the cent, in 89% of family-cells, and the one exception is the Fidelity Anthropic complex at 3%. So the effective number of independent views is the number of families, not of funds.

That this is discretion in *private* valuation, not a reporting or units artefact is settled by the Level-1 placebo of §2.3, where the same two houses mark the five verified shared public securities to the cent (cross-family spread 0.00%, `data/level1_placebo.csv`), public marks being pinned to an observable close and private marks not.

The structure also replicates out of panel. Of a five-name expansion probe (xAI, Perplexity, Cohere, Groq, Fanatics; `data/nport_expansion_probe.csv`), exactly one name cleared the ≥5-same-date-funds bar, Fanatics, with 7 same-date funds across three families, and it reproduces §4.3's anatomy on first contact: a cross-family spread of 75% on the common report date (Fidelity $87.33, Neuberger $73.85, Franklin $50.00, 2026-04-30), with both multi-fund families internally identical to the cent. All of these are common equity, though the issuer label varies between holders (Fanatics Inc against Fanatics Holdings Class A), which is §4.3's like-for-like caveat, disclosed, not assumed away. Fanatics also exposes a limit of the harvest: `src/nport_fetch.py` stops after eighteen filings per company, and on this same date the panel files hold only two Franklin funds for it, one family and no spread at all, while the deeper sweep reached five more filers and the 75% gap. A harvest that stops early can miss the houses that disagree, and it cannot put a disagreement into a filing that does not contain one, so every cross-fund spread reported here is a lower bound on what a complete sweep of N-PORT would show.

*Is the cross-family disagreement simply staleness (§4.3)?* The deflationary reading is that one family has merely failed to refresh an old mark. The quarterly panel rejects it three ways (`src/mark_staleness.py` → `data/mark_staleness.csv`; each family collapsed to its median mark per company-quarter, cells guarded at 4×). First, no house is dormant: a family's mark moves in 79% of adjacent-quarter pairs, from 58% at the least active (T. Rowe Price) to 92% at the most (ARK), and the median move is 12%.

Second, disagreement survives conditioning on freshness. The comparison runs on the 105 of 116 multi-family cells where freshness can be determined at all, meaning every family present also filed in the immediately preceding quarter. The other eleven open a family's series and carrying no evidence either way, so scoring them stale would be an error. Among the 67 cells in which *every* family moved its mark, where no mark can be stale by construction, the median cross-family spread is 12.1% (this tracer panel's own statistic, which happens to round the same way as §5.1's population median and is not it) against 6.7% in the 38 cells where at least one house stood pat. A one-sided test that the freshly-remarked cells are tighter returns p=0.97.

Third, the least frequent remarker is not the outlier: remark frequency and mean deviation from the cross-family median are unrelated across families (Spearman ρ=0.14, p=0.76), T. Rowe Price deviating by +2.4% at a 0.58 remark rate and Baron by −4.9% at 0.89. Staleness is real in these data, and §7 is the finding that the *headline* suffers from it. It is not what makes two houses carry the same share at different prices.

Neither threshold carries that result. Varying what counts as a mark "moving" from 0.1% to 5% leaves the freshly-remarked median between 12.0% and 12.3% against 6.6–8.2% for the rest, and the class guard can be tightened to 2× or dropped without moving either figure by a fifth of a point. The cells are not independent (105 company-quarters over seven companies), so the pooled p-value overstates the evidence and is quoted only to show which way the comparison runs. Collapsed to one comparison per company it holds, the freshly-remarked cells being wider in five of the six companies with cells of both kinds, all but Epic Games.

One rival reading survives all of it, and the test says nothing about it. Conditioning on "every family moved" selects quarters carrying news, so staleness is ruled out without establishing that the disagreement is a *permanent* difference in policy rather than one that widens during a repricing and closes in between. This panel cannot separate them: only five judgeable cells have nobody moving a mark, and they split: three sit at a 0% spread, which is §4.3's herding regime, not recovered agreement, and Epic Games and SpaceX sit near 14%, SpaceX entering here because staleness cells are spreads between family medians. §6.2 answers the question on the 760 such cells the full N-PORT universe supplies: two thirds are not unanimous and a quarter differ by more than 24%.

Two smaller qualifications belong with it. The pooled ordering runs *against* staleness rather than merely failing to support it, because families remark most actively when they disagree most (the 2022 repricing supplies fourteen of the fresh cells at a 39% median spread), and that ordering does not hold year by year, so only the negative result is claimed. And this quarterly cross-*family* statistic is more compressed than §4.3's cross-*fund* 24% at a single modal date, so only the within-panel comparison is used.

*IPO-exit bridge (§7).* The "fund mark beats the headline" result does not hinge on the 1:1 preferred-to-common conversion the bridge assumes. Varying the conversion ratio across 0.8–1.2, the fund mark is the less-wrong signal in 4–6 of the seven fund-held exits and its median absolute error (11–21%) stays far below the headline's 48% throughout; the headline's errors (+294% Instacart, +116% Chime) are simply too large for any plausible bridge adjustment to overturn the differentiator. What the leg cannot carry is the *count*: on seven exits an exact sign test on the five wins returns p=0.23, so "five of seven" is an illustration and not evidence of a population regularity — a fact §7 states.

The content is in the magnitudes, which do survive a paired test: the fund mark's absolute error is smaller exit by exit at p=0.078 (Wilcoxon), its median error is 11% against the headline's 48%, and three of the five wins are by a factor of two or more (Chime 136×, Instacart 35×, Reddit 12×). Restricting to the five exits with a clean quality flag (dropping ServiceTitan's structured down round and Circle's contested headline) the mark still wins four of five.

**Table B.1.** Robustness summary: each headline result, its stress test, and the outcome.

| Result | Headline | Stress test | Outcome |
| --- | --- | --- | --- |
| §4.3 cross-fund spread | median 24% (10 names) | unit-outlier band K∈[2,5] · fund threshold | 23.7% (invariant) |
| §4.3 family clustering | "clusters by family" | between-family variance share · within-family spread | η²≈1.00 · within-family spread = 0 in 89% of cells |
| §4.3 dispersion is private-specific | 24% on private (Level-3) marks | Level-1 placebo: 2 families' shared *public* holdings | cross-family spread 0.00% (5 names, same date) |
| §4.3 spread is not staleness | houses disagree, not lag | remark rate · spread where *every* family just remarked · rate vs deviation · both thresholds swept · per-company collapse | 79% of quarters (58% to 92% by house) · 12.1% (n=67) vs 6.7% (n=38), one-sided p=0.97 · ρ=0.14, p=0.76 · fresh median 12.0–12.3% throughout · wider in 5 of 6 companies |
| §7 IPO leg, what the count carries | fund mark least wrong 5 of 7 | exact sign test · paired Wilcoxon on \|errors\| · clean-flag subset | count p=0.23 (illustrative only) · p=0.078 · 4 of 5 |

## Appendix C. The population's construction, and the anchor reconciliation

The machinery the body compresses to a sentence: the reconciliation with the deal-terms literature, how each cluster's label was reached, what the published cells look like with the harvest cap lifted, and the predictions this framework can be refuted by.

### C.1 Reconciling with Gornall–Strebulaev

Section 1.2 states the anchor result: on option-adjusted terms the reported post-money averages 48% above the fair value of the cap table, and common shares are 56% overvalued. This paper never re-derives that number and could not: it would need each company's per-round legal terms, which public filings do not carry. What it can do is say why the two do not conflict, and where they meet.

The objects differ. Gornall and Strebulaev compare the headline to a contingent-claims fair value of the *whole cap table*, valuing each share class separately because the newest preferred carries downside protections that common and junior shares lack: IPO-return guarantees, vetoes over down-round IPOs, liquidation seniority. This paper compares fund houses to each other on one security at one date, and never to a fair value of its own. One measures a level against a model. The other measures dispersion against nothing.

But the marks are the same kind of object as their answer, which is what makes the two comparable at all. A mutual-fund Level-3 mark is reported as fair value under ASC 820. So §5 measures how far apart sophisticated practitioners land when each attempts, under one accounting standard and on the same security, the adjustment Gornall–Strebulaev perform analytically on contract terms. Their result is that the naive headline is wrong by an average amount. This paper's is that the practitioners attempting to correct it do not agree with each other about by how much, and that where they disagree is a stable property of particular companies.

Where the two meet is the cross-section, and the meeting is a prediction, not a coincidence. The G-S haircut is largest where the protections are deepest in the money, on at-risk and repriced names whose equity sits near the preference stack, and collapses toward zero for winners so far above the stack that every class converges on one per-share value. That is exactly where this paper finds the marks doing different things. Houses herd to the round on fresh, believed winners, and disagree by tens of per cent on the stale, repriced and contested names (§4.3), and the exits repudiate the headline hardest on the same cohort (§7). The term wedge and the practitioner scatter locate the headline's untrustworthiness in the same companies, by two routes that share no data.

What follows is a reconciliation, not a re-derivation. Nothing here re-estimates the 48%.

### C.2 How each cluster's label was reached

Section 5.2 reports what kind of company each mark is on. This is the rule behind it, its measured accuracy, the direction of its errors, and the two readings of Table 8 that a reader is likeliest to take and the table does not support.

So every cluster carries a label and, beside it, the basis for that label, because the labels are not all worth the same. 118 clusters covering 93.6% of the booked value are verified one at a time against the filings and the public record, with a line of reasoning recorded for each in the replication package. Every cluster above $500M is among them but one: a $1.15B position filed as "AH PARENT, INC. SER A PREFERRED SHARES PP" whose filings name no operating company and which no public source resolves, so it is left unresolved rather than labelled from its rule. A further 390, holding 3.7%, are labelled by rule. The remaining 147, holding 2.5%, are left `unclassified` rather than guessed at, and Table 8 counts 148 because one further cluster reaches no label for a different reason: the resolver could not settle its identity (Appendix A.2).

There is no threshold to be had, and looking for one was the temptation worth resisting. The sharpest signal is the filer's own security title, since a private placement gets written as one, and among clusters whose kind is known that token separates venture from non-venture at an AUC of 0.96. It is not a boundary: across the 656 clusters its distribution runs continuously upward from a seventh of a per cent, and the only genuine discontinuity is between clusters no filer ever marked that way and clusters where one did. A cut placed on that slope would be invented precision.

The rule therefore fires only at the two ends — never a private placement and never flagged restricted on one side, mostly both on the other — and abstains in between. What that abstention is worth is measured: on the clusters where a verified label also exists, the rule declines to call 32 of them and fires on 84 — 116 of the 118, the other two carrying no security title for it to read — of which it gets 94% right. Its errors run one way and the tail inherits them: Sequa and Windstream II are private companies out of a buyout and a reorganisation that no filer ever called a private placement, and the rule reads them as listed.

The listed row invites a reading it does not support: a wider median there would say a Level-3 mark predicts disagreement whatever the company is. Split it by whether the marks ever move and the halves come apart. Where every house has frozen its number — 135 clusters, the suspensions and halts for which Level 3 is exactly right — the median is 0.7% and 7.4% sit above 24%. The dispersion lives in the 213 clusters still being repriced, at 32.8%, and those are residue: reorganisation stubs, contra positions and delisted microcaps carrying a median $3.7M per cell against $66.6M for a venture cell. The bucket is what is left after the paper's subject is removed, not a second finding about it.

Scored inside the venture population rather than the mixed panel, §5.1's ten names land at the 63rd percentile on house medians and the 63rd on fund spreads, against the 60th on both in the mixed panel. The conclusion is unchanged and the number now comes from the population it belongs to.

### C.3 Every published cell reappears, and wider

The §4.3 harvest stopped after eighteen filings per name, so its fund counts were a lower bound of unknown tightness. Recomputing all ten published cells from the bulk data — resolving the hand-labelled rows and the population jointly, so both sit on one identity — returns nine cells with *more* funds and one exactly matching, none narrower and none missing. The median cell goes from 8 funds to 15.5 (`src/reconcile_versions.py` → `data/version_reconciliation.csv`). The cap was real, it was one-directional, and the ten anatomies in Table 4 understate coverage rather than overstate it.

It also understates the spread, and by enough to state as a number, not a worry. The published cells carry a median spread of 23.5% — the 24% §4.3 quotes. Recomputed on the complete filing set, with the same 4× guard applied, the same cells give 34.7%; Discord is the one of the ten the guard removes, since the bulk data puts BlackRock's mark ten times above Fidelity's, so the comparison is over nine of the ten. The published figure is therefore a floor, and the distance to the ceiling is about eleven points.

Two things had to be checked before that number could be printed. The first is whether it is an artefact of choosing different cells: it is not, because nothing is re-chosen. The comparison holds the company, the date, the family unit and the guard fixed and lifts the cap alone.

That constraint is not fastidiousness — the first attempt re-selected each company's date by the modal-report-date rule Table 4 already uses, and over seven years of filings that rule lands on a December-2024 Epic Games cell where one filer reports $1.00 against everyone else's $640–680, and on a March-2026 Anthropic cell where six houses agree to the cent, returning a median of 3.6%. A name's spread depends on where it sits in a repricing far more than on how many filings you read: Anthropic is unanimous on 31 March and spans 49.8% on 30 April, when some houses had taken the new round and others had not. Re-selecting dates is therefore a different measurement, not a better one, and it is not made here.

The second is whether the recovered funds are simply different share classes. Where filers name the round this can be tested cell by cell, not bounded in aggregate, and it is: a named series is shared by two or more houses in seven of the nine cells, and restricting each to its best-populated shared series leaves the spread unchanged in three of them — Gusto at 32.3%, Anduril at 9.9%, OpenAI at 0.0%. The other four narrow, one of them almost completely: Stripe 73.1% to 1.4%, Anthropic 49.8% to 28.7%, Canva 39.3% to 33.3%, Databricks 17.1% to 13.0%. The median across the nine under that restriction is 28.7% against 34.7% unrestricted, so the class objection is worth about six points here, not the difference between 23.5% and 34.7%. Coverage per cell across those nine goes from 8 to 16 funds (`src/fund_marks_bulk.py` → `data/fund_marks_bulk.csv`).

The figure is not restated as the headline, because §4.3's value is an anatomy each of whose marks was read against its filing, and swapping that for coverage is a different paper, not a correction to this one, but a reader should know which side of the number the missing filings sit on, and by how much.

The clearest of the recovered cells is set out in full: every deflationary reading of a wide spread is available somewhere in this data, and none of them is available here. On 31 March 2026, four fund houses name Stripe's Series I preferred in the security title of their own filings, across nine funds. Morgan Stanley's two Growth Portfolio funds carry it at $36.90. Fidelity's five funds carry it at $63.00, Capital Group at $63.00, and Franklin Templeton at $63.87 — a 73.1% spread on an explicitly identical series, on one date. The four write the issuer down differently — "STRIPE INC", "STRIPE LLC", "Stripe, Inc." — and all four rows carry the same LEI, `549300CLHGIPTCYHQ143`, so the naming is a house style rather than four different entities.

It is not a share class, because the class is named and the same. It is not a unit convention: dividing the booked value by the share balance returns the filed price per share for all nine rows, in units of shares. Nor is it one house that simply failed to reprice, though that was the first thing to check and it needed the whole series to settle.

Morgan Stanley reports this holding quarterly and has done so on twelve dates since mid-2023. It tracked the others through 2024, sitting within a few per cent either side of their median. It has been below them on each of the last five quarters — by 27%, 20%, 16%, 19% and now 71% — that last figure against the other houses' median, where the cell's 73.1% is its highest mark over its lowest — with its own mark rising at every one of those dates, from $27.90 to $36.90. Between the last two it moved 5.9% while the others moved 52.1%. And $36.90 was never the consensus: the other houses went from $41.42 to $63.00 without passing through it.

So this is not a stale copy of anyone's number. It is one house's own valuation, revised on its own schedule, running below a consensus it used to sit inside — a standing difference that a sharp repricing widened rather than created. Two sophisticated houses, holding the same security on the same day, disagree by seventy per cent about what it is worth. The eighteen-filing cap is why this cell reads as a 1% spread in Table 4 (`src/reconcile_versions.py`).

### C.4 Four testable predictions

The framework is falsifiable. Each prediction below is adjudicable by the public-signal pipeline built here as the exited sample grows, and none needs private data.

**P1. Dispersion predicts returns.** By the differences-of-opinion analogue (Diether–Malloy–Scherbina 2002), names carrying high cross-fund mark dispersion (§4.3) should underperform low-dispersion names at and after exit.

**P2. The fund-mark edge scales with staleness.** The last N-PORT mark's accuracy advantage over the headline (§7) should rise monotonically in headline age. Section 7 establishes only the binary stale-versus-fresh version. The continuous test needs more exits.

**P3. The wide cells resolve against the wider mark.** Where two houses hold one named series more than 24% apart (§3.3) and the company later prints a price, the realised value should land nearer the lower mark more often than nearer the higher, because §7 finds the marks least wrong where the headline is stale and the headline is what the higher mark tends to track.

**P4. Dispersion collapses into liquidity.** Cross-fund disagreement on a name (§4.3) should shrink as it nears an exit, the marks converging on the clearing price. This is the one of the four already run, as a pre-test on the pre-2023 listings, and it does not hold there (§10.1). The 2023–26 listings are the registered test bed and are not yet a large enough panel.

Each sharpens the paper from a description of disagreement into a set of refutable claims about it.

### C.5 How much is a different security

Section 3.3 states the result. This is the construction, the decomposition and the selection check.

Two houses can differ about one security or hold two securities of one company. An issuer identifier cannot separate those, and the separation matters more than any robustness check in this paper, because one reading is a fact about valuation and the other is a fact about portfolios. The 32.5% of rows that name a series in the security title separate them wherever two houses name the same one.

**Table C.1.** The headline decomposed by whether the security is verifiable. Rows 1–4 partition the panel's guarded cells by what their filings name, and rows 5–7 hold the security fixed and are computed at company × date × series with two or more houses, the 4× class guard re-applied inside the group.

| | groups | cells | companies | median spread | above 24% |
| --- | --- | --- | --- | --- | --- |
| all guarded cells | — | 4,271 | 656 | 12.13% | 40.2% |
| no filing names a letter | — | 1,941 | 488 | 16.42% | 43.8% |
| one letter, named by only some filings | — | 590 | 92 | 15.34% | 42.4% |
| every filing names the same letter | — | 366 | 58 | 0.00% | 14.8% |
| two or more letters named | — | 1,374 | 107 | 12.90% | 40.8% |
| **security fixed: one named series, 2+ houses** | **2,717** | **1,758** | **137** | **0.74%** | **22.0%** |
| the same 1,758 cells, series ignored | — | 1,758 | 137 | 8.45% | 35.4% |

Three readings follow. The first constrains the other two and belongs before them.

*The test is available where disagreement is smallest and unavailable where it is largest.* The cells no filing describes are the widest group in the table at 16.42% and the most numerous at 1,941 of 4,271. The cells this test can reach run 8.45% before any series is fixed, against 12.13% for the panel. Composition is therefore not measurable at all on the most disputed part of the population, and every figure below describes its calmer part. The direction of that ignorance is knowable even though its content is not: the cells the test cannot reach are *wider* than the ones it can, so what is unmeasured is more contested than what is measured, not merely unknown. This is a stronger statement than "the subset is selected", and it is the one a reader should carry: the decomposition does not apportion the headline, it apportions the half of the headline that admits the question.

*Within that half, the median is composition and the tail is not, and the two belong in one sentence.* Holding the series fixed takes the median from 8.45% to 0.74%, while the share above 24% falls only from 35.4% to 22.0%. Two houses that verifiably hold the same paper file, typically, the same number, which is what §2.2's N-CSR harvest finds by hand and this reproduces at population scale on a different source. But 597 groups on 68 companies have the series named, shared, and the houses still more than 24% apart, and the five most frequent names account for only 29% of them, so the tail is not one company's artefact either.

*Why the previous version of this bound was withdrawn.* Earlier drafts restricted to cells whose filings never name two *different* letters, reported 11.6% across 2,897 cells on 606 companies with 39.9% of them above 24%, and read the gap to 12.1% as "the round-mixing objection is worth about a third of a point". That restriction is satisfied two ways and only one of them fixes the security. The median share of rows carrying any letter inside those 2,897 cells is **zero**: 1,941 of them pass because nobody named anything, and those cells are *wider* than the panel at 16.42%, not narrower. Only 366 pass because every row named the same letter, and those sit at a median of 0.00%. A bound computed mostly on cells of unknown security is not a bound, and the third of a point it appeared to license was an artefact of pooling the two.

*What moved this figure most, and why nothing caught it.* An earlier version of this decomposition read 0.12% where it now reads 0.74%, and the whole of that difference is the pattern that decides what names a series. It stopped at `[A-K]` and dropped the numeric suffix, so Databricks Series L — a series §2.1 quotes by name — was invisible to it, and Series A-2 read as Series A, which scored two houses holding C-1 and C-3 of one company as holding *the same* named series. That is precisely the composition this test exists to remove, arriving inside the test itself. Widening it past K and past the suffix left a third case: the convention after Z is AA, BB, CC, and Stripe's Series BB-1, which §4.2 quotes, was unread until the pattern learned a doubled letter. Corrected, composition explains the typical gap by a factor of eleven, not the seventy-four the old pattern implied. The tail is unchanged in kind and larger in size, 597 groups on 68 companies against 515 on 65.

No guard could see it, and the reason bounds what the other guards in this project are worth. Every pinned figure in the paper was recomputed from production code on every run, and all of them were recomputed by the same wrong pattern. A registry compares a value against the code that produces it; it cannot see the code answering one question consistently and wrongly. What found it was a scan for the same decision defined in more than one module, and what would have found it earlier is the paper quoting a series its own decomposition could not read, which it did, twice, for two versions.

*A second instance of the same blindness, and a harder one, because the guard had already fired once.* The decomposition in §8.4 measures the upper and lower gap against a consensus. Its first version took that consensus to be the midpoint of the two extremes, under which the two gaps are the same number by algebra, and it was caught in minutes — both columns printed identical statistics to four decimal places, which no pair of real measurements does. The consensus was moved to the median across house medians and the correction was believed. It was three fifths of a correction. At three houses or more the median is genuinely interior and the two gaps separate; at exactly two the median *is* the midpoint and the identity returns intact, and 39.5% of cells carry exactly two houses. The repaired estimator was reporting the spread twice on two cells in five while every guard in the repository stayed green, because each printed number was individually correct and no guard reads two columns as one claim. On the identified cells the bottom-house result does not survive, which is why §8.4 states an asymmetry and not a pair.

*The count is the part immune to the objection.* A conditional median on a selected subset can always be argued about. A count of instances cannot be explained away by composition, because composition is what has been held fixed: in 597 cases two houses named the same series and disagreed by more than 24% about it. That is the fact this appendix contributes, and it is why the abstract gives the tail as a count while the conditional median stands beside it as the composition result.

What the test cannot do: a shared letter is not a shared lot, because two houses can enter one series at closings months apart. And it cannot reach those 1,941 unnamed cells, which is the next thing worth measuring and the one place where a real answer would change the headline rather than qualify it.

### C.6 The ten names, beyond the table

Section 4.3 prints the anatomy and Appendix C.3 recomputes every cell without the harvest cap. Three readings belong with them, not in the body.

First, §4.3's inference — valuation policy rather than private information — is drawn from dispersion on one date, and one name lets it be watched through time instead. Morgan Stanley has reported Stripe on twelve dates since mid-2023, tracked the field for six of them, and has run below it on every date from March 2025 while still raising its own mark: between the last two quarters the field moved **52.1%** and Morgan Stanley moved **5.9%**. Its number was never the consensus at any earlier date, so this is a valuation committee declining a repricing, not a lag. Appendix C.3 gives the cell and the whole series.

Second, the level of the median is sample-dependent even where the shape is not. Going from the original eight broadly held names to ten roughly doubles it, 13% to 24%, because both names that newly clear the ≥5-fund bar (Revolut, Gusto) sit in the high-disagreement mode. What survives the change of sample is the bimodality, not the level. The deflationary reading, that a house is sitting on an old mark rather than disagreeing, is tested in Appendix B and fails: restricting to quarters in which every family refreshed leaves the spread wider.

Third, the count of houses overstates the count of opinions, since many holders are variable-insurance or sub-advised sleeves that mirror their sub-advisor's mark to the cent (Appendix D: twenty-two sub-advised funds across five variable-insurance trusts, all at one house's number), so even a widely held name typically has two or three independent valuations behind it. This reproduces Chernenko–Lerner–Zeng and Kwon–Lowry–Qian out of sample on public-domain data (`figures/fund_marks_dispersion.png`).

Two names are excluded from the per-share comparison because their holders are not holding the same thing: SpaceX on share class, ByteDance on the entity itself. Appendix A.2 gives both.

## Appendix D. The exits, in full

Section 7 states the finding and its weight. This is the table, the per-family harvest, the robustness of the conversion bridge, and the qualification each named exit carries.

**Table D.1.** IPO-exit validation, 2023–26 listings: the headline (last private round) and the last pre-IPO N-PORT fund mark scored against the realized IPO valuation (error = signal/IPO − 1).

| Company | Headline (last private) | Last pre-IPO fund mark ⇒ implied | Realized IPO | Headline error | Fund-mark error |
| --- | --- | --- | --- | --- | --- |
| Instacart (2023) | $39B (2021) | $32.50/sh ⇒ ≈$10.7B (T. Rowe ×4 + American Funds, mid-2023) | $9.9B ($30/sh) | +294% | +8% |
| Klarna (2025) | $46B (2021) | — (no broad fund mark) | $15.1B | +205% | — |
| Chime (2025) | $25B (2021) | $26.77/sh ⇒ ≈$11.5B (4 Alger funds, Apr-2025) | $11.6B ($27/sh) | +116% | −1% |
| Reddit (2024) | $10B (2021) | $32.37/sh ⇒ ≈$6.1B (Fidelity ×3, Jan-2024) | $6.4B ($34/sh) | +56% | −5% |
| ServiceTitan (2024) | $7.6B (2022)‡ | $78.85/sh ⇒ ≈$7.0B (T. Rowe ×4, Sep-2024) | $6.3B ($71/sh) | +21%‡ | +11% |
| Circle (2025) | $7.65B (2022)§ | $23.33/sh ⇒ ≈$5.2B (Fidelity ×2, Apr-2025) | $6.9B ($31/sh) | +11%§ | −25% |
| Klaviyo (2023) | $9.5B (2021) | $34.38/sh ⇒ ≈$10.5B (ClearBridge, Jun-2023) | $9.2B ($30/sh) | +3% | +15% |
| CoreWeave (2025) | $23B (2024) | — (thin mutual-fund coverage) | $23B | +0% | — |
| SpaceX/xAI (2026) | $1.25T (2026) | — (multi-class; marks rose into listing) | $1.75T | −29% | — |
| Figma (2025) | $10B (2021)† | $23.73/sh ⇒ ≈$13.9B (Fidelity OTC ×2, Apr-2025) | $19.3B ($33/sh) | −48%† | −28% |

Klarna is the one listing with a headline but no broad fund mark, so the fund-mark column holds exactly the seven fund-held exits the text counts. Its interim signal is a 2022 down financing round at $6.7B, which overcorrected to −56% against the $15.1B listing: a repriced round is not infallible either, only far less wrong than a stale headline. Two facts stand out. First, the headline's sign versus the IPO is unstable and demand-conditional, not a clean function of cycle timing: the four 2021-bubble-vintage down-round listings overshot the realized IPO by a median +160% (headline = ceiling; the full 2021-vintage cohort also holds fairly-priced Klaviyo, +3%, and stale-but-bid-up Figma, −48% — spanning the entire sign range), but the floor cases are not simply the later vintages — among the 2025–26 listings, *repriced* consumer-fintech (Chime +116%, Klarna +205%) still overshot while a *compounder* (Figma) and a *momentum* name (SpaceX/xAI — Musk's February-2026 merger of SpaceX and xAI at a combined $1.25T — −29%) listed above its last round, with CoreWeave flat.

(†Figma's headline is its last *primary* round, the 2021 Series E at $10B — the $20B Adobe figure was an acquisition agreement, not a round, terminated 2023, and the 2024 $12.5B was a tender; with no primary round printed after 2021 its frozen headline is maximally stale, which is *why* it sat 48% below the IPO. ‡ServiceTitan's headline is its Nov-2022 Series H, $7.6B at $84.57/share — itself a structured down round carrying a *compounding IPO ratchet*, already repriced from the $9.5B 2021 peak — so it overshot the $6.3B IPO by only +21%. §Circle's headline is its April-2022 Series F, $7.65B led by BlackRock and Fidelity — *not* the $9B Concord SPAC renegotiation, which was terminated in December 2022 and is no more a clean round than Figma's Adobe figure.)

This is the same demand-conditional sign the population's own cross-section shows (§4.3): the headline is a ceiling for the repriced and a floor for the in-demand, at exit as in the secondary market.

Second (the differentiator) across the seven exits where mutual funds held the company pre-IPO, their last N-PORT mark was the least-wrong signal in five, and for the stale-headline names by an order of magnitude. Instacart's last mark ($32.50/share, four T. Rowe Price funds in 2023Q2 and American Funds a month before listing) implied ≈$10.7B against the $9.9B IPO — +8% versus the headline's +294% (35× closer); Chime's ($26.77, four Alger funds six weeks before the June-2025 listing) landed within ~1% of the $27 IPO against the stale 2021 headline's +116%; Reddit's ($32.37, three Fidelity funds, Jan-2024) implied ≈$6.1B against $6.4B — −5% versus +56% (12× closer); ServiceTitan's ($78.85, four T. Rowe Price funds, 2024Q3) implied ≈$7.0B — +11%, modestly less wrong than its already-repriced +21% headline; and even Figma's floor case fits — with the headline 48% below the IPO, the last fund mark ($23.73, two Fidelity OTC funds) was −28%, still less wrong than the maximally-stale headline. Across the seven fund-held exits the median absolute error of the last fund mark is 11%, against 48% for the headline.

But the win is not universal, and the two exceptions are the tell. In the only two exits where the last private round was *recent and fairly priced*, so the headline was not stale, the headline beat the fund mark: Klaviyo, a profitable martech name, listed within 3% of its 2021 Series D ($9.5B → $9.2B IPO), so the headline's +3% beat ClearBridge's marked-up +15%; and Circle's last clean round (the 2022 Series F at $7.65B) put the headline at +11%, closer than Fidelity's conservative −25% mark, which *undershot* a crypto listing that then popped 168% on day one.

Every IPO valuation here is on one basis — the offer price times fully-diluted shares, recorded per row in `data/ipo_validation.csv` — and one of these two exceptions depends on that choice. Both signals are scored against the same denominator, so a basis change moves them together and cannot reorder same-signed errors: ServiceTitan's verdict holds at any basis within ±15%, and Klaviyo's holds until +8.9%. Circle's two errors have *opposite* signs (+11% against −25%), and a listing valued about 10% below the offer-price figure would hand the round to the fund mark. The reading below is therefore firm on Klaviyo and provisional on Circle.

That is what the staleness mechanism predicts: the fund mark's edge over the headline is the absence of staleness, not fund foresight — the very N-PORT marks that *disagree* in the cross-section (§4.3) carry materially better exit information than the number the press kept citing only when that headline has frozen at a years-stale round, and that edge vanishes (or reverses) when the headline is itself a recent, fairly-priced number. Klarna keeps the interim-signal side honest too: its 2022 down round overcorrected to −56% (the IPO valued at the offer-price ~$15.1B fully-diluted, the same basis as the other exits), so interim signals are not infallible, only (where the headline is stale) far less wrong (`figures/ipo_validation.png`).

A completed per-series harvest of every disclosing fund for these exits (`src/family_forecast.py` → `data/ipo_premarks_byfund.csv`) adds two family-level facts to the adjudication. (The harvest sweeps every sister series, so its counts exceed Table D.1's named source funds: twenty-two T. Rowe series file Instacart's $32.50, and twenty-two Fidelity series Reddit's $32.37.) First, no house emerges as a systematically better forecaster — each family scores only one to four exits, too few to rank — and the one directional regularity is Fidelity's conservatism: its last pre-IPO mark undershot in all three of its clean fund-mark exits (Reddit −5%, Circle −25%, Figma −28%), the signature of a cautious house policy (§4.3's smoothing discretion), not of private information.

Second, §4.3's mirror structure survives to the listing: twenty-two sub-advised funds across five variable-insurance trusts of four insurers (Lincoln, Voya, Brighthouse and MassMutual, the last via two trusts) carried Instacart into its IPO at T. Rowe Price's identical $32.50, and the same platforms mirror T. Rowe's ServiceTitan mark to the cent, while other sleeve trusts carried the higher Instacart share-class levels ($37.18, $41.62). A nominally broad pre-IPO holder base thus again collapses to two or three independent valuation views, with §4.3's share-class caveat alive at exit: the $32.50–$41.62 Instacart span mixes house policy with class seniority, and the realized $30 listing sat closest to the most broadly carried level — a breadth that, by the paper's own family logic, was one house's view widely mirrored, not many independent ones.

## Appendix E. The four measurements in full

Section 9 states what each sensor recovers, what it is calibrated against and how well it does. This carries the design of each, the corrections that shaped it, its blind spot, and one defect in this paper that the fourth sensor found in the first.

### E.1 Listing dates

A test of what happens as a company approaches a listing needs a listing date per name, and the press is not a source this repository will cite. EDGAR is: a company registering a class of securities on an exchange files Form 8-A12B, or, where it reached the market through a shell, a successor-issuer Form 8-K12B. `src/listing_dates.py` asks EDGAR for each name's own filing and dates 21 of the 23 companies whose classification records a listing or a merger. The date is then checked against something the panel already knows: the last report date on which the company appears as a private Level-3 holding. Of the 21, eighteen land within a quarter of it, the widest at 82 days. The next-closest is 258, and the three beyond that threshold are names whose funds stopped holding them long before they listed. The cut therefore sits in a gap in the observed distribution, at 82 against 258, rather than at a round number. The check is not decoration: it caught a CIK pinned from memory that belonged to a different company altogether.

*What it cannot see.* A promotion out of Level 3 is invisible by construction, because the panel keeps only Level-3 rows and a promoted holding simply stops appearing. What is visible is the opposite face (a mark still filed at Level 3 after the shares began trading) and there are 57 of those across ten names. 43 of the 57 fall inside 180 days, the customary lock-up, during which the shares are genuinely unsaleable and ASC 820 prices that restriction instead of ignoring it. Nine holders carrying Palantir at Level 3 nine days after it began trading is what the standard asks for, not a delay. The three names running past the lock-up are stubs: the largest single late mark is $260,773 and Outset Medical's is $10,314 against a company that listed four years earlier. Quoting "1,603 days" without the dollar figure beside it would turn a residual position into a finding.

### E.2 Share splits

A share count is a count. When a company splits *k* for one, a holder that did not trade files exactly *k* times as many shares at its next report date, so the balance ratio is *k* to the precision of an integer. The price side is not exact and must not be treated as though it were: the same filing usually carries a fresh mark, so the price falls by roughly 1/*k* rather than exactly 1/*k*. Baron restated SpaceX at $57.41 in the same month Fidelity restated it at $56.00, both from a tenfold share count.

The balance is therefore held to half a per cent and the price side is asked only to rule out the alternative: a purchase multiplies balance and value together, a split multiplies the balance and leaves the value alone. Requiring the price ratio to equal 1/*k* within a few per cent, which is the natural first design, drops Baron from the SpaceX event and roughly halves the sample. `src/split_events.py` finds 601 candidate fund-dates on 228 companies and confirms 29 events by two or more houses, 26 of them at a ratio companies actually split at. The largest is Databricks three-for-one in the autumn of 2022, filed by fourteen independent houses inside two months.

*Not every integer is a split ratio.* The three events outside the canonical set are Carbon Health at *k*=99, Pine Private at *k*=127 and Iron Horse II at *k*=9: arithmetic that lands near an integer, not a corporate action. Delhivery at *k*=100 is inside the set and flagged in the output anyway, because a hundred-for-one is a redenomination in everything but name. And five of the 29 events sit on one date, 2019-12-31, all at *k*=2 with a zero span, and five simultaneous two-for-one splits at the panel's second report date is not what that looks like. A filing-convention change is.

*What they establish beyond their own use.* §4.2 says that within a house the mark is one number. This says the same house is not one number about the share count. Houses differ not only in what they think a share is worth but in when they recognise that the share has been redefined, and the second is visible in a field nobody reads for disagreement.

*What it does not establish.* The proposal that motivated it (that §5's 4× class guard is largely absorbing split desynchronisation) does not hold. The guard drops 1,945 cells and 22 of them (1.1%) sit inside a restatement window. Conditioning on companies with a confirmed split at all, 21% of the 104 cells dropped there are inside a window: material for those names, immaterial for the panel. The guard is not mostly doing this.

### E.3 Round dates

Three sources for round dates were tried and all three failed. Form D misses the large rounds, which go out under Section 4(a)(2) and leave no Regulation D trace. N-CSR gives an acquisition date, but that is the fund's entry, not the round. The press gives a date this repository will not cite. The fourth was already on disk: filers name the series in the security title, as "SER H PC PP" or "Class B PP", and 32.5% of population rows carry a letter, so the first report date on which a new letter appears anywhere in the population bounds the round from above.

**Table E.1.** Calibration of the series-letter round date against the earliest N-CSR acquisition date for the same company and series. Two document types, one structured and already downloaded, the other parsed out of an HTML schedule of investments.

| Company | Series | N-CSR entry | First in N-PORT | Gap (days) | Funds | Houses |
| --- | --- | --- | --- | --- | --- | --- |
| Anthropic | F | 2025-08-29 | 2025-08-31 | 2 | 35 | 2 |
| Anthropic | G-1 | 2026-01-27 | 2026-01-31 | 4 | 7 | 4 |
| Databricks | F | 2019-10-22 | 2019-10-31 | 9 | 22 | 7 |
| Databricks | G | 2021-02-01 | 2021-02-26 | 25 | 61 | 13 |
| Databricks | H | 2021-08-31 | 2021-08-31 | 0 | 51 | 10 |
| Databricks | I | 2023-09-14 | 2023-09-30 | 16 | 38 | 7 |
| Databricks | J | 2024-12-17 | 2024-12-31 | 14 | 37 | 9 |
| Databricks | D | 2025-03-12 | 2025-03-31 | 19 | 4 | 3 |
| Databricks | K | 2025-09-08 | 2025-09-30 | 22 | 29 | 5 |
| Databricks | L | 2025-12-11 | 2025-12-31 | 20 | 39 | 7 |
| OpenAI | A | 2025-10-28 | 2025-11-30 | 33 | 17 | 2 |
| Stripe | B | 2019-12-17 | 2019-12-31 | 14 | 48 | 14 |
| Stripe | H | 2021-03-15 | 2021-03-31 | 16 | 30 | 3 |
| Stripe | I | 2023-03-15 | 2023-03-31 | 16 | 15 | 4 |
| Anthropic | G | 2026-03-31 | 2026-01-31 | −59 | 37 | 3 |

Table E.1 is that calibration. Fourteen of fifteen dated pairs land inside 35 days, and the median gap is 16, the worst inside the tolerance is 33 and the nearest outside it is 59. The tolerance sits in that gap and is read off it.

Two rules follow from the calibration instead of preceding it. Two houses: every pair that misses by months rests on a single house: Discord Series G at +670 days, SpaceX B at +570, OpenAI A-2 at +426 and A-3 at +259, Stripe G at +62, Databricks B, C and E at +49. A letter one fund reports is that fund's holding, and a letter several houses report in the same quarter is a round. Censoring: a series first seen on the panel's own first date is not dated but censored: SpaceX Series A first appears on 2019-09-30 against an N-CSR entry of 2022-06-08, which is a series that existed before the window, not a 982-day error.

**Table E.2.** The count rule against the price-coordination rule, implemented as "the first month with two or more houses whose median prices lie within 2% of each other". The step is one observation per anchor date, as in §8's Tables 10 and 12. Both columns are computed by the pipeline; the coordination column was hand-computed and copied for two rounds, which is how its neighbour kept a p-value from an earlier tolerance.

| | count rule | coordination rule |
| --- | --- | --- |
| pairs dated | 434 | 406 (333 uncensored) |
| non-first anchors | 75 | 56 |
| calibration pairs inside 35 days | 14 of 15 | 11 of 15 |
| median absolute gap to N-CSR | 16 days | 20 days |
| step on the non-first set | −1.94, p=0.0008 | −0.06, p=0.022 |

Table E.2 is what the price-coordination rule dates, and §8.5 gives the short version. It fixes one case and breaks four: Anthropic Series G goes from −59 days to 0, which is exactly what the rule was built to do, but Databricks J moves to +45, Anthropic G-1 to +63, Databricks F to +70 and Databricks D to +80, all of which were inside 35 days under the count rule. The step is the part worth reading twice. The magnitude goes with the anchor, −1.94 points to −0.06, and the sign survives at p=0.022, which is what a misplaced anchor does to a size. That is a narrow piece of robustness and it should be read narrowly: both rules require two houses, so what has been varied is the criterion (naming the series against agreeing on a price) and not the two-house bar itself. The bar remains the one filter with no independent defence.

*Reach.* 434 company-series pairs on 287 companies clear both rules, against ten companies with any N-CSR coverage at all. Ninety-seven companies carry two or more dated rounds and 24 carry three or more. That 97 is the pool §8.6's repetition test draws from and not its sample: once the anchor is restricted to non-first rounds and both bands are required to carry guarded cells, the repetition test runs on 30 rounds on 12 companies. That is the point of calibrating on a small set: the rule then applies where no schedule was ever read.

*The sign of the error is not guaranteed, and the natural argument that it is fails.* One would expect a fund to report a series only after it exists, so the N-PORT date should be at or after the round. Anthropic Series G breaks it: the series appears in N-PORT in January 2026 and the earliest N-CSR entry for it is 31 March 2026, a gap of −59 days on a pair with 37 funds across 3 houses, neither censored nor thin. The reason is structural: N-PORT covers every registered fund while the N-CSR harvest covers ten names and whichever filers happen to schedule them, so an N-CSR date is one filer's purchase and can be later than the series' arrival in the filing system. Neither quantity is the round close. What licenses the N-PORT date as a proxy is the agreement on the clean cases at monthly resolution, not an argument about which side the error falls on.

*What it cannot see.* Rounds that create no new class — extensions, SAFEs, secondaries, and any priced round reusing an existing letter. Resolution is the reporting month, not the day. And a letter can appear because one fund bought an old series on the secondary market, which the two-house rule removes on average, not by construction.

### E.4 Acquisition dates and cost

N-PORT carries neither what a holder paid nor when it bought. Regulation S-X requires both in the schedule of investments that accompanies the annual and semi-annual reports on Form N-CSR. `src/ncsr_acquisitions.py` queries EDGAR's full-text index for each of the ten §4.3 names *together with the schedule's own column header*, since `"Discord"` alone returns 1,491 filings, nearly all of them the English word, while `"Discord" "acquisition date"` returns 179, and parses the schedule tables out of the returned documents. Both spellings of the header are required, because the index matches tokens and "dates" is not "date". The harvest is 767 schedule rows, 10 companies, 44 registrants, 429 lot-period-series, of which 155 rows carry a share count and therefore an entry price per share.

That 429 is not §9's 434, and the coincidence matters because the two sit close together: the round-date measurement counts company-series pairs dated across 287 companies of the whole population, this counts lot-period-series inside ten companies' schedules. Nothing connects them but the arithmetic. A prefilter that is not a superset of the harvest it replaces would be a silent sample cut, so `validate_prefilter` asks EDGAR for the prefiltered accession set and looks for accessions in the committed extract that are missing from it: across all ten companies, zero missed.

**Table E.3.** What lifting the forty-filing cap on the N-CSR harvest reached.

| | at a cap of 40 filings | uncapped |
| --- | --- | --- |
| schedule rows | 190 | 767 |
| registrants | 25 | 44 |
| rows with a share count | 29 | 155 |
| lot-period-series with 2+ independent books | 1 | 45 |

Table E.3 reports what the lift reached.

*What the source can and cannot carry.* Cost is the fund's entry and not always a round: ARK's Databricks lot of 23 September 2022 returns a markup of 1,226% because the position arrived through the MosaicML acquisition in stock, which the filing says in a footnote.

Two parse failures were invisible at forty filings and both would have shipped. One filer's document carries two table layouts, and a parser reading everything under the first header printed an Anthropic lot at −99.999818% where four other filers put it at +77.991332%; another's switches from dollars to thousands part-way through, so every cost came back a thousand times too small while the markup, a ratio inside a single row, survived. The fix reads each table under its own header, and re-run on the capped extract it reproduces 104 of 105 company-document results exactly — the single difference a term loan whose "cost" of 8.27 was an interest rate.

*One defect in this paper found from this side.* The first run of the cross-house comparison reported Canva held by "Capital Group" and by "EUPAC FUND" at markups agreeing to a thousandth of a point, which is what one house looks like, not two. EUPAC is the EuroPacific Growth Fund, and the house map matched the full name and not the abbreviation. The population panel carries 191 rows filed under the short name and, in nine cells, was counting Capital Group as two houses. The bias of an unmapped registrant is one-directional and this is its direction: it makes one house look like two, which *inflates* apparent disagreement. What mattered was how it surfaced: a second document type, asked about the same houses, disagreed with the first.

## Appendix F. Measurement detail moved out of the body

Three passages that a reader checking the design needs and a reader following the argument
does not. Each is the full text as it stood in the body, with its numbers registered exactly
as before.

### F.1 Three arithmetic explanations of the step at the round

*The cell could get wider.* The spread is a maximum over a minimum of house medians, so it grows mechanically with the number of houses compared. If a round brought new buyers in, cells after it would be wider by composition and part of the step would be an artefact of counting. Median houses per cell: 4.0 before the round against 4.0 after, Mann–Whitney p=0.60, and the month-by-month medians take three distinct values across the whole nineteen-month window. The composition does not move.

*The round-month cell could be the new security agreeing with itself.* If a cell at month zero consisted only of funds that had just bought at the round price, they would agree because they had all paid the same and nothing about valuation would follow. Across the 46 round-month cells the newly priced series is a median 26% of the rows and the whole cell in none of them. The convergence runs over the company's whole position, not over the security that has just traded.

*A restatement could masquerade as agreement or as a gap.* A cell in which one house has restated a share split and another has not carries a spread that is the split factor. Those windows are dated in Appendix E.2 and dropped. Removing that filter moves the median step by a third of a point (§8.5), so dropping those windows disciplines the estimate without moving it.

### F.2 The three filters the NAV wedge runs behind

Section 5's median can absorb a handful of contaminated cells. This measure cannot, because its entire content is in the tail, and two of the three restrictions below were written after reading the largest rows of a previous run rather than before.

**One price per fund per company, applied throughout.** The first run's largest wedge was JPMorgan on Claire's Stores: $881 a share against a $12.50 consensus. JPMorgan files *two lines* for Claire's in each fund, one at $10.00 and one at $1,765.66. Two prices under one issuer key are two instruments, and the value-weighted blend of them is not a price. The same defect produced a Baron position in SpaceX at $1,294 against a $527 consensus, 2,227 basis points of one fund's net assets. That fund's own two lines are $526.59 and $5,265.90: the ten-to-one unit convention §4.3 excludes SpaceX for. Any fund whose own lines disagree by more than half a per cent is dropped, and this restriction is on in every row of Table G.1: §3.2's identification problem arriving where it does real damage.

The same guard is applied a second time, to the position, not the fund. A fund can file one internally consistent line and still be on a different unit convention from every other holder of the company. First Trust reports 2,145,462 Epic Games "shares" at $1.00 against a $637 consensus, which is a share count expressed in dollars. It would otherwise contribute a wedge of 421,062 basis points on a $32m fund. Any position more than four times the consensus or less than a quarter of it is dropped, on §4.3's threshold and for §4.3's reason.

**One series, and it does not do what the tail suggested.** Restricting to §3.3's cells that never name two different letters removes 13,571 of 40,361 fund-positions and cuts the count above ten basis points from 976 to 620. It takes three per cent off the single largest wedge, from 460.0 to 444.4 basis points. The filter removes a third of the positions and a thirtieth of the extreme, so it thins the body of the distribution and leaves its far end where it was, and a reader who expected it to be the tail filter, as an earlier draft of this section did, should see that it is not.

**Venture-backed only.** The filing system carries buyout stubs, reorganisation equity and delisted microcaps at Level 3, and §5.5 separates them because only the venture-backed names are what this paper is about. This is the restriction that moves the tail: the largest wedge falls from 460.0 to 161.1 basis points. What it removes at the top is Venture Global LNG, an energy company that carries the widest wedge in the unfiltered panel at every one of PIMCO's report dates. It also removes a block of Russian listings frozen after 2022 that US funds still carry at Level 3: Nebius, Ozon, X5 Retail, T-Tekhnologii and Solidcore.

Everything, cell membership and the class guard and the consensus, is rebuilt at the *position* unit rather than taken from §5, which builds cells on filing lines. Mixing the two units is what produced the Claire's row.

### F.3 What the measurements turned up on the way

Three of the four produced a finding of their own on the way, and each is a correction some other part of this paper needed.

**Restatement is not simultaneous, so a one-month confirmation window is the wrong unit.** Across the 29 confirmed split events the median restatement span is 30 days and the longest is 92, and only 18 of 29 fit inside a single month. Requiring one month would discard eleven events and, worse, would score the desynchronisation as the absence of a split. This is the quantity §8.5 uses to explain why the price-coordination dating rule dates worse than the count rule.

**Confirmation counts houses, never registrants.** Four T. Rowe Price series restating one name are one confirmation. At the median event, counting registrants multiplies the count by 1.7×, and on the Databricks three-for-one it is 47 registrants against 14 houses. This is §4.1's correction arriving in a second measurement, and it is the third metric in this project whose first version counted trusts.

**A cost per share is not comparable across filings; a markup is.** ARK reports SpaceX acquired 31 October 2023 at $92.89 a share against a $185.00 mark in one filing and at $84.00 against $420.99 in another, because a split changes the basis. The markup is a ratio inside one row and immune to it. That is why every cross-filing comparison built on this source in §2.2 and §4.2 is a markup, and why the per-share figures in §2.1 are read off share counts inside single filings, where the basis is disclosed.

### F.4 The pre-registration argument in full

**Nothing in this paper is pre-registered, including the sector contrast.** I formed the demand-favored split (AI, data/AI infrastructure, defense against the rest) from the 2021–26 funding cycle before computing the gaps. That sentence is exactly as much assurance as an unregistered claim can offer, which is none. That contrast has been cut from this paper along with the secondary leg it belonged to; the specification curve that priced it against all 2,032 alternative partitions is in the repository. One of the registration's five predictions has now been run on the data that already exists, because the alternative is a hypothesis nobody has ever sized. P4 says cross-house dispersion collapses as a company approaches its listing, which needs a listing date per name; §9 builds those from each company's own exchange registration and validates them against the panel.

On the pre-2023 listings this leaves fifteen names with four qualifying report dates ahead of the event, and P4 does not hold on them. Six narrow and seven widen, two are unchanged, and a one-sided signed-rank test on the per-name change returns p=0.43. Reading the whole window rather than its endpoints (a per-name rank correlation of spread against date) gives the same verdict at p=0.84. Two earlier versions of the membership rule, kept runnable because their results were seen first, gave twelve names at p=0.58 and eighteen at p=0.38.

What that null is worth is a question about power, so the power is computed. Resampling the observed changes, this design detects a ten-point narrowing 0.43 of the time and needs about forty points to reach the conventional four-in-five. The textbook normal approximation with the same standard deviation says 0.17, and it understates the rank test because a third of these names sit within a point of zero where the test is most sensitive. Put in P4's own units the picture is worse: if every name's spread collapsed to nothing over its last four dates, this sample would return a significant result 0.73 of the time. A null on fifteen names therefore says the collapse is not large; it does not say there is none. It is also a pre-test, not the registered test — these names were examined while §5 was being written, so nothing here predates its data, and the registration reserves P4 for listings completed after it is filed (`src/p4_pretest.py`).

One detail of the first version is worth recording because it was invisible until the dates were sourced. The window used each company's last four cells, and Palantir's last cell falls nine days *after* it began trading — a Level-3 mark on a security that already had a public price, carried there because reclassification lags the event. One cell in fifteen, on the name whose anchor was strongest, testing the wrong side of the thing the hypothesis is about. The window now stops strictly before the listing date.

Every result in this paper is exploratory. A registration is the only instrument that would change that, and one is drafted at `notes/registration.md` and not filed. Filing it before the panel is next extended would let the following version be judged on a hypothesis that predates its data, and until that happens the compression at a round should be read as the paper's best-supported mechanism and not as a tested one.

### F.5 The ten names, one by one

Three things stand out, and the first is the shape, not the level. Disagreement is large for stale, repriced or contested names (Discord's 2021 round, Epic's 2022 round, the Databricks/Anthropic cascade, Revolut and Gusto's mid-2025 secondaries) and absent for names carrying a single fresh, well-publicised round: OpenAI's 13 funds all mark exactly $687.69, Stripe and Anduril cluster within a few per cent. On the hottest names the houses herd to the last primary round, which is what the headline-as-benchmark view predicts.

Second, what disagrees is the house, not the fund. *Family* and *house* are used interchangeably here for the asset manager behind a fund, which §4.1 distinguishes from the legal trust a filing names. All five Alger funds mark Anthropic at $259.14, and ten Fidelity funds mark Revolut at exactly $1,495.97 while ARK Venture marks the same ordinary stock at $1,110. Determinism inside a house and divergence across houses points at valuation policy rather than private information: a common procedure, plausibly a common smoothing convention. What the spread measures is therefore methodological difference, the private-market counterpart of the discretion illiquid-asset funds exercise over reported marks (Getmansky, Lo and Makarov 2004; Jenkinson, Sousa and Stucke 2013; Brown, Gredil and Kaplan 2019). Zitzewitz (2003) adds the motive. A stale NAV is an arbitrage target, and that is what the fair-value regime whose Level-3 output N-PORT now discloses was written against. Since shares outstanding are common to every holder, a 39% spread in per-share marks is a 39% spread in implied company value: in April 2026 Alger's books carry Anthropic 28% below Nuveen's and 22% below Fidelity's.

## Appendix G. What the disagreement costs

The body measures what holders say. A referee is entitled to ask what it costs, and the question has a precise form. A mutual fund's net asset value is not a statistic. It is the price at which its investors buy and sell that day. If two houses carry one company far apart, two sets of investors are credited with different value for the same asset on the same date, and one of them transacts at a number the other's own filing contradicts. Zitzewitz (2003) showed that a *stale* NAV is exploitable. This is the same question with a different cause, and it has not been asked of private marks because nobody has had the population to ask it on.

The answer is small, the reason it is small is not the reason the first draft of this measure gave, and the panel it is measured on agrees more than the population does. All three are stated below because each of them limits the claim. That it is an appendix, not a section, is an editorial judgment about length and not about weight: §1 and §11 quote the number, and this is where it is derived.

### G.1 The measure, and its filters

For every fund holding a company inside a comparable cell, reprice its position at the cross-house consensus and express the change in basis points of that fund's own net assets. The consensus is the median of house medians, so a complex filing thirty series cannot vote thirty times. That is the disagreement seen from the only position in which it is a cost, not a curiosity: the person who owns the fund.

Three restrictions run behind it — one price per fund per company, one series, and venture-backed companies only — and Appendix F.2 gives each with the case that forced it. Everything is rebuilt at the *position* unit rather than taken from §5, which builds cells on filing lines, because mixing the two units is what produced the widest row of the first run.

**Table G.1.** What each restriction removes. "Max" is the largest wedge any single fund-date carries, in basis points of that fund's own net assets. The one-price restriction is on in all three rows.

| Selection | Fund-positions | Fund-dates | Median \|wedge\| (bps) | Max \|wedge\| (bps) | Over 10 bps |
| --- | --- | --- | --- | --- | --- |
| all comparable cells | 40,361 | 14,853 | 0.08 | 460.0 | 976 |
| + one series only | 26,790 | 13,160 | 0.04 | 444.4 | 620 |
| + venture-backed only | 8,529 | 3,590 | 0.33 | 161.1 | 258 |

### G.2 The answer, and why it is small

Across 8,529 fund-positions on 100 venture-backed companies, held by 296 funds across 57 houses over 3,590 fund-dates, funds booked $101.6B. Repricing every position at the cross-house consensus moves $6.6B of booked value in absolute terms.

**Table G.2.** The NAV wedge, in basis points of the reporting fund's own net assets, at each cut.

| Wedge over | Fund-dates | Share | Distinct funds |
| --- | --- | --- | --- |
| 1 bp | 1,341 | 37.3% | 199 |
| 5 bp | 486 | 13.5% | 127 |
| 10 bp | 258 | 7.2% | 75 |
| 25 bp | 104 | 2.9% | 36 |
| 50 bp | 43 | 1.2% | 17 |
| 100 bp | 12 | 0.3% | 5 |

Table G.2 puts the wedge at each cut. The median fund-date carries a wedge of 0.33 basis points, three thousandths of one per cent of the number its investors transact at. The largest is 161 basis points, and twelve fund-dates on five funds carry more than a hundred.

For scale, the private book of a fund in this panel is a median 0.22% of its net assets and at most 11.9%. A fund whose private book is that median size would move its NAV by eleven basis points even if it marked the whole book fifty per cent away from consensus. The median wedge is thirty times smaller than that, so the size of the book is not what makes it small.

What makes it small is the mass at zero. 56.4% of the 8,529 positions sit at the consensus to within a hundredth of a per cent, and 22.5% of fund-dates carry a wedge of exactly zero. The median is small because the median fund does not disagree at all, and a fund at the consensus contributes nothing by construction. An earlier draft gave the small book as the reason, and its own arithmetic disagreed by a factor of thirty.

The panel this is measured on agrees more than the population does, and that is a limit, not a footnote. The median cell in this panel carries a spread of 5.9%, against 10.1% for the venture-backed cells of §5.5. Requiring five funds, two houses, one series, one price per fund and a venture label selects the widely held names, which are exactly the names §4.3 and §8 show herd to a recent round. So this measure runs on the agreeing end of the distribution, and the number it returns is best read as a lower bound on what the population's disagreement is worth in NAV. The cells carrying §5's widest spreads are largely cells this test cannot reach, because they are held too narrowly to clear its bar.

What is not small is the concentration. 258 fund-dates on 75 distinct funds carry a wedge above ten basis points. A tenth of a per cent of net assets is an order of magnitude below a typical day's move in a diversified equity fund, and far above the tolerance a fund board applies to a pricing error. Twelve of those fund-dates, on five funds, carry more than a full per cent of net assets. Those funds are not a random sample, and most of them are not open-end mutual funds. Nine of the twelve are filed by vehicles that report no series identifier, which is what interval funds, closed-end funds and tender-offer funds are. Those are the vehicles permitted to hold illiquid assets in size. Those vehicles are 258 fund-dates themselves, the same count as the over-ten-basis-point set by coincidence and not the same set: the two overlap in 109. In all they are 7.2% of the fund-dates here and carry a median wedge of 5.3 basis points against the panel's 0.33.

This is a partly negative answer and it should be read as one. The disagreement §5 measures is large as a fraction of the asset and small as a fraction of the median fund. A reader who came expecting the 12.1% to be an error of the same size in someone's NAV should leave with 0.33 basis points at the median. A reader who concludes from that median that no fund is affected should leave with the five funds at the other end. What §5 measures is a fact about how private assets are valued. It is not, on this evidence, a systemic mispricing of mutual-fund NAV, and it is not nothing for the funds that hold the most.

### G.3 Is it forecastable?

A wedge matters more if it is *predictable*: an investor who knows which way a fund's private mark will move knows something about tomorrow's NAV today, which is the Zitzewitz condition.

The obvious test is mechanically broken. The house furthest above consensus at a date is selected partly on its own error, and its next change carries that error back with a minus sign, so regression to the mean produces "reversion" whether or not anything reverts. The test therefore selects on the deviation at the *previous* date and measures the change over the next step, paired inside the cell so whatever happened to the company is common to both houses. Steps in which nobody re-marked are dropped, and cells where every house sits at the consensus are skipped. With 56.4% of positions at the consensus there is no house above and none below, and letting a tie-break choose would measure floating-point noise.

That skip is load-bearing, and it is only half of the problem. Without it a round-trip of the same panel through the committed CSV moves the cell count from 540 to 538: two cells, but not zero, and a replication that cannot reproduce a count has not reproduced anything. It also reaches only the cell in which *every* house ties. Where the top is shared and the bottom is not, "the house above consensus" is a pair rather than a house — forty of the 421 cells are like that, and in sixteen the tied houses are not identical to the last bit, so an index-of-maximum separates them on how a logarithm rounded. Multiplying every price by a relative 1×10⁻¹⁵, the size of a disagreement between two implementations of `log`, moves the count from 226 of 415 to 223 of 412 and the one-sided p from 0.039 to 0.052.

Houses tied at an extreme are therefore averaged, which is what the position means when more than one house occupies it, and the average does not move under that perturbation. Dropping those cells instead was measured and rejected: ties are commoner where houses agree, so dropping them would select on the herding regime §4.3 names.

**Table G.3.** Does the house above consensus mark down relative to the house below it? Both designs are printed so the bias in the naive one is a number, not an assertion. "High house moves less" counts only the cells whose two sides differ at all, which is why its denominator is below the cell count. Sign p is one-sided; the two-sided value is beside it.

| Design | Cells | High house moves less | Share | Sign p (one-sided) | Two-sided |
| --- | --- | --- | --- | --- | --- |
| selected on the previous date (unbiased) | 421 | 223 of 417 | 53.5% | 0.085 | 0.170 |
| selected on the same date (mechanically negative) | 483 | 275 of 483 | 56.9% | 0.001 | 0.003 |

Table G.3 runs both designs. Deviations tilt toward reverting, and the naive one overstates the tilt by 3.5 points: 53.5%, not the 56.9% the obvious test returns. Three and a half points of tilt away from a coin clears no conventional threshold one-sided or two-sided, at p=0.085 and 0.170, and this section reads it as a direction rather than a result.

Persistence is the other half, and it is a different quantity from §6.1's. There the object is a *company's* spread and the statistic a rank correlation; here a *house's* deviation and an OLS slope. Regressing a house's deviation on its own lag gives 0.76 across all house-dates and 0.84 among those with a side at all, half having none because in a cell with an odd number of houses one house *is* the median. Among the 1,071 house-dates with a side, 85% are on the same side one step later. Measurement error attenuates both slopes, so each is a floor. An earlier version reported that share as 70%, having scored the consensus houses as agreeing with themselves (`sign(0) == sign(0)`). The correction is in the direction that flatters the argument, which is why it is named.

A house that carries a company away from the consensus is very likely still on the same side next quarter, and slightly more likely than not to have narrowed the gap. That is a persistent difference of view with a weak pull toward the middle, not a stale number correcting itself and not a random walk.

### G.4 What this does not establish

It does not establish that anyone *acts* on the wedge. The natural test is whether funds carrying larger disputed private books see different net flows or reported returns. It needs a table this repository does not extract: N-PORT's monthly total return, and its monthly sales, redemption and reinvestment flow items. They sit in `FUND_REPORTED_INFO.tsv`, inside the same quarterly bulk archives as the holdings table, in the same file this paper already opens for each fund's net assets. It is four more column groups from one source, and it is named here with its file so that a reader can run it without asking.

It does not establish direction. The consensus is not the truth. It is the middle of a set of opinions the rest of this paper shows to be persistently different, so a fund above consensus is not thereby overstating its NAV. What Appendix G.2 measures is the *size of the disagreement expressed in NAV*, the quantity a fund board, an auditor and a regulator each need and none of them currently has. What Appendix G.3 adds is that it does not resolve itself quickly.

## References

Agarwal, V., B. M. Barber, S. Cheng, A. Hameed, and A. Yasuda (2023). "Private company valuations by mutual funds." *Review of Finance* 27(2), 693–738. https://doi.org/10.1093/rof/rfac037

Agarwal, V., B. M. Barber, S. Cheng, A. Hameed, H. Shanker, and A. Yasuda (2023). *Do investors overvalue startups? Evidence from the junior stakes of mutual funds.* Working paper. https://doi.org/10.2139/ssrn.4425744

Barber, B. M., and A. Yasuda (2017). "Interim fund performance and fundraising in private equity." *Journal of Financial Economics* 124(1), 172–194. https://doi.org/10.1016/j.jfineco.2017.01.001

Bias, D., J. Cassel, and B. A. Sensoy (2026). "Secondary markets for VC-backed startup equity." May 2026. https://ssrn.com/abstract=6749078 (accessed 2026-06-28).

Brown, G. W., O. R. Gredil, and S. N. Kaplan (2019). "Do private equity funds manipulate reported returns?" *Journal of Financial Economics* 132(2), 267–297. https://doi.org/10.1016/j.jfineco.2018.10.011

Chernenko, S., J. Lerner, and Y. Zeng (2021). "Mutual funds as venture capitalists? Evidence from unicorns." *Review of Financial Studies* 34(5), 2362–2410. https://doi.org/10.1093/rfs/hhaa100

Cochrane, J. H. (2005). "The risk and return of venture capital." *Journal of Financial Economics* 75(1), 3–52. https://doi.org/10.1016/j.jfineco.2004.03.006

Diether, K. B., C. J. Malloy, and A. Scherbina (2002). "Differences of opinion and the cross section of stock returns." *Journal of Finance* 57(5), 2113–2141. https://doi.org/10.1111/0022-1082.00490

Ewens, M., and J. Farre-Mensa (2020). "The deregulation of the private equity markets and the decline in IPOs." *The Review of Financial Studies* 33(12), 5463–5509. https://doi.org/10.1093/rfs/hhaa053

Getmansky, M., A. W. Lo, and I. Makarov (2004). "An econometric model of serial correlation and illiquidity in hedge fund returns." *Journal of Financial Economics* 74(3), 529–609. https://doi.org/10.1016/j.jfineco.2004.04.001

Gornall, W., and I. A. Strebulaev (2020). "Squaring venture capital valuations with reality." *Journal of Financial Economics* 135(1), 120–143. https://doi.org/10.1016/j.jfineco.2018.04.015

Jenkinson, T., M. Sousa, and R. Stucke (2013). *How fair are the valuations of private equity funds?* Working paper, Said Business School, University of Oxford.

Korteweg, A., and M. Sorensen (2010). "Risk and return characteristics of venture capital-backed entrepreneurial companies." *The Review of Financial Studies* 23(10), 3738–3772. https://doi.org/10.1093/rfs/hhq050

Kwon, S., M. Lowry, and Y. Qian (2020). "Mutual fund investments in private firms." *Journal of Financial Economics* 136(2), 407–443. https://doi.org/10.1016/j.jfineco.2019.10.003

World Economic Forum and Stanford GSB Venture Capital Initiative (2026). *The Future of Venture Capital: Unlocking Liquidity and Growth.* Insight Report.

Zitzewitz, E. (2003). "Who cares about shareholders? Arbitrage-proofing mutual funds." *Journal of Law, Economics, and Organization* 19(2), 245–280. https://doi.org/10.1093/jleo/ewg011
