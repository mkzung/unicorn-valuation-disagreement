# Disagreement Without a Price: How Far Apart Mutual Funds Mark the Same Private Company

Max Gorbuk · Independent Researcher (MAM, London Business School) · gorbuk.maxim@gmail.com
*First draft: June 2026 · This version: October 7, 2026 · Comments welcome. I declare no competing interests.*

## Abstract

Between funding rounds a startup has no market price, yet mutual funds that own it must value it monthly. Using 309,654 such values filed with the SEC, 2019 to 2026, I compare managers holding the same company on the same date. For the median venture-backed company, the most and least optimistic managers are 10.1% apart. Two managers that bought identical Databricks shares at one price valued them eleven dollars a share apart six months later. Stale marks do not explain the gap, which is a lasting trait of the company and narrows when a new round sets a price.

**Keywords:** private-company valuation; unicorns; mutual funds; fair value; valuation disagreement; differences of opinion.

**JEL classification:** G24; G23; G12; G14.

## 1. Introduction

Between funding rounds a private company has no market price. The mutual funds that own its shares must still report a value for them to the SEC every month, and that value is the fund's own estimate. For most private companies these estimates are the closest thing to a public price. They matter more each year. Companies stay private longer than they used to (Ewens and Farre-Mensa 2020), and the World Economic Forum and Stanford GSB Venture Capital Initiative (2026) estimate that venture portfolios hold trillions of dollars of value that no sale has confirmed. Gornall and Strebulaev (2020) show that the headline valuations quoted for these companies overstate fair value, and estimating that fair value is the fund managers' job.

I measure how far apart their estimates are. I collect every value US funds reported for shares without a market price, 309,654 of them in N-PORT filings from September 2019 to April 2026, and compare the asset managers, which I call houses, that hold the same company on the same date. For the median company and date, the most optimistic house values the company 12.1% above the most pessimistic one, and in two cases out of five the gap exceeds 24%. For venture-backed companies alone the median is 10.1%.

One lot of Databricks shares shows the disagreement in its cleanest form. In December 2024 Databricks sold its Series J shares at $92.50. Funds run by Alger and Brighthouse bought in that round, and their shareholder reports disclose what they paid and what they later thought the shares were worth. On 30 June 2025 Alger valued a share at $119.19 and Brighthouse at $108.18: the same security, bought on the same day at the same price, eleven dollars apart. By the end of the year they agreed again. Section 2 rules out different share classes, purchase lots, stale marks and reporting conventions as explanations. It is one case, and most comparable lots agree almost exactly.

The disagreement is a trait of the company, not noise. Companies that are contested in one report tend to be contested in the next, and the gap remains when no house has changed its number since the previous report, so stale marks do not explain it.

A new funding round narrows the gap, but only for a while. I date rounds from the filings themselves, as the month in which a new class of shares first appears in the holdings of two or more houses. In the month of a round, disagreement falls well below the company's usual level, and afterwards it rebuilds by about one percentage point a month. The same test placed six or twelve months away from a round finds nothing. The narrowing comes with the most optimistic house marking down toward the others, which good news alone would not produce, so I read it as the effect of a new price.

Measuring disagreement this way depends on counting opinions correctly. SEC filings name the legal trust that files, not the house that runs it, and a single house can file through dozens of trusts; Fidelity uses 36. One valuation committee sets prices for the whole house, so its funds report the identical value 89.0% of the time. Counted trust by trust, funds appear to agree almost perfectly, with a median gap of 0.004%. Grouping trusts into houses, and checking the grouping against the SEC's record of who advises each fund (Section 4), gives the 12.1% above.

Houses can also hold different classes of the same company's shares, and different classes can carry different prices for good reasons. About a third of filings name the class. Where two houses name the same class, the typical gap falls from 8.45% to 0.74%, so much of the everyday disagreement comes from holding different securities. The large gaps remain: in 597 cases two houses holding the same named class are more than 24% apart (Section 3.3).

The disagreement says more about private-company values than about fund investors' returns. Private companies are a small share of most funds, and repricing every fund's private holdings at the houses' consensus changes its net asset value by a median 0.33 basis points. A spread that is large as a fraction of an asset can be small as a fraction of a diversified fund. The round result is also not causal. Companies choose when to raise, and with only seven down rounds in the sample I cannot rule out that good news explains part of the narrowing (Section 8.5).

Section 2 presents the Databricks lot and a check on public stocks, where the same houses agree to the cent. Section 3 describes the data, and Section 4 explains why the house is the unit of an opinion. Section 5 measures how far apart houses are, and Section 6 shows that the gap is a lasting trait of each company. Section 7 compares fund values with later IPO prices, Section 8 shows what compresses the gap around a new round, and Section 9 describes the dates recovered from the filings. Section 10 lists what would overturn each result, and Section 11 concludes.

### 1.1 Related work

The closest papers study mutual funds as investors in startups. Chernenko, Lerner and Zeng (2021), Kwon, Lowry and Qian (2020) and Agarwal, Barber, Cheng, Hameed and Yasuda (2023) document that funds value the same private company differently and that their values follow public markets, on samples that end around 2016. Agarwal, Barber, Cheng, Hameed, Shanker and Yasuda (2023, working paper) find that funds value older share classes close to the latest round price. Bias, Cassel and Sensoy (2026) find that secondary-market prices anticipate later venture valuations and are partly reflected in fund values. I ask how far apart fund values are, not whether they are right, and I use every private holding registered funds reported from 2019 to 2026 instead of a list of known companies.

Gornall and Strebulaev (2020) find that reported unicorn valuations average 48% above fair value, because they treat every share as if it were the newest preferred share; once revalued, 65 of 135 unicorns lose unicorn status. Their overstatement is largest for distressed and repriced companies, and those are also the companies on which houses disagree most here (Appendix C.1).

More broadly, the finding that each house reports a single number fits work on the discretion managers use over reported values (Barber and Yasuda 2017; Jenkinson, Sousa and Stucke 2013; Brown, Gredil and Kaplan 2019). Illiquid portfolios also report smoothed returns (Getmansky, Lo and Makarov 2004). Disagreement among analysts predicts lower stock returns (Diether, Malloy and Scherbina 2002), and stale fund prices can be exploited by fund investors (Zitzewitz 2003). Tests that rely on exits face selection, because only some companies exit (Cochrane 2005; Korteweg and Sorensen 2010).

## 2. The same lot, eleven dollars apart

A wide gap between two funds can have mundane causes: different share classes, different purchase lots, a stale number or different units. One lot of Databricks shares rules out all four from the filings, and the gap is still there. On public stocks the same measurement reads zero.

### 2.1 Databricks Series J: one lot, two values

N-PORT reports what a fund thinks a position is worth, not what it paid. The annual and semi-annual reports funds file on Form N-CSR supply the other half: under Regulation S-X, the schedule of investments states the acquisition date and cost of each restricted security. I collect 767 schedule rows across 44 registrants for the ten most broadly held names (Appendix E.4). With the entry price disclosed, two funds can be compared on a common basis without assuming one.

Databricks sold its Series J shares on 17 December 2024. Two houses bought in that round, Alger through two registrants and Brighthouse through two trusts, and Table 1 shows all four positions at the end of 2025.

**Table 1.** Four filings of one Databricks lot share one value-to-cost ratio at the end of 2025. Series J as of 31 December 2025, four filings on four cost bases, three of them printing exactly 76/37. Acquisition date 17 December 2024 except Brighthouse Funds Trust II, which carries the round's January closing. Cost and value as filed, in dollars; share counts as filed where a filer reports them. Sources: SEC Form N-CSR schedules of investments, accessions in `data/ncsr_acquisitions.csv`.

| Filer | Cost | Value | Ratio | Shares | Per share, cost → value |
| --- | --- | --- | --- | --- | --- |
| Alger ETF Trust | 476,560 | 978,880 | 2.054054054 | — | — |
| Alger Portfolios | 6,290,278 | 12,920,570 | 2.054053891 | — | — |
| Brighthouse Funds Trust I | 652,680 | 1,340,640 | 2.054054054 | 7,056 | $92.50 → $190.00 |
| Brighthouse Funds Trust II | 6,527,910 | 13,408,680 | 2.054054054 | 70,572 | $92.50 → $190.00 |

Three of the four filings state a value-to-cost ratio of 2.054054054, which is exactly 76/37: 978,880×37 = 476,560×76, and so on to the last digit. The fourth, Alger Portfolios, prints 2.054053891 because its value is one dollar short, 12,920,570 against the 12,920,571 an exact 76/37 would give on a $6,290,278 base. The Brighthouse rows also report share counts, and both divide to a cost of **$92.50** a share and a value of **$190.00** a share, on two positions ten times apart in size. The two Alger rows follow the same path on their own cost bases. Four cost bases from $476,560 to $6,527,910 sharing one ratio is not a coincidence.

The second closing confirms the common entry price. Brighthouse Funds Trust II records the round's January closing, 21 January 2025, as its acquisition date, while Trust I records 17 December 2024, and the two trusts print the same markup, 16.951352% in June and 105.405405% in December. The two closings were at one price.

In between, the two houses part. Against the same $92.50 entry, Alger's ratio on 30 June 2025 implies **$119.19** a share on both of its registrants, and Brighthouse's implies **$108.18** on both of its trusts. One security, one entry price, one valuation date, and the two houses are eleven dollars a share apart, a 10.2% spread (`figures/databricks_series_j.png`).

The filings rule out each mundane explanation. The funds name the same series, so the gap is not a share class. Three filings carry the same acquisition date and the fourth carries the round's second closing at the same price, so it is not two lots. The share counts divide into the filed values at the filed prices, so it is not a units convention. Each house files the identical number on two registrants with different cost bases, so it is not one fund's arithmetic. And it is not a stale mark, because a stale mark cannot converge, and by 31 December the two houses print the same ratio, 76/37 to within a dollar.

The convergence matters as much as the gap. Both houses carry the lot from $92.50 to $190.00 over the year. They differ about where it stands in June and agree exactly about where it ends in December, and a constant difference in cost basis cannot open and then close.

### 2.2 Most identical lots agree

One lot could be a lucky find, so I run the same comparison wherever the schedules allow it: same company, same series, same acquisition lot, same valuation date, and two books with different costs. There are **45** such comparisons. **37 agree to within a hundredth of a point**, and the median gap is 0.0000.

Identical lots usually carry identical marks, the opposite of Series J. Eight comparisons differ by more than a hundredth of a point. Four are Epic Games at about a tenth of a point, which is rounding on a large base. The other four are in Table 2.

**Table 2.** Where identical lots disagree, the company is Databricks. The four cross-book comparisons that do not agree, out of 45. Each holds the company, the series, the acquisition lot and the valuation date fixed, and compares books rather than house labels. Markup is value over cost as filed.

| Lot | Valuation date | Books | Markups (%) | Gap (pts) |
| --- | --- | --- | --- | --- |
| Databricks Series K, 2025-09-08 | 2026-04-30 | Alger, Neuberger Berman | 14.62 / 26.67 | 12.05 |
| Databricks Series J, 2024-12-17 | 2025-06-30 | Brighthouse, Alger | 16.95 / 28.85 | 11.90 |
| Databricks Series K, 2025-09-08 | 2026-02-28 | Capital Group, Neuberger Berman | 18.77 / 26.67 | 7.90 |
| Databricks Series G, 2021-02-01 | 2021-12-31 | Brighthouse, Voya | 24.29 / 27.20 | 2.91 |

All four are Databricks, and three are its Series J and K, the rounds its holders were still re-marking in 2025 and 2026. The same Databricks Series G lot on 30 June 2021 has three independent books at three different costs agreeing to 0.0012 of a point, and Stripe's Series B lot of 17 December 2019 has two books agreeing to 0.0002 across eleven consecutive periods. On the ten most broadly held names, two books holding one lot usually file one number, and where they do not, the company is in the middle of repricing.

Two rules keep the comparison honest. First, the unit is the company, series, valuation period and lot. Comparing filings by the date they were filed would score one house's own revaluation between report dates as two houses disagreeing: an annual report for a year ending 31 December and a semi-annual report for the six months ending 30 April reach EDGAR 119 days apart and value the same position four months apart. Second, a book is not a house label. Insurance-dedicated trusts host sub-advised sleeves that file another manager's numbers: Canva's Series A-3 of 4 November 2021 is filed by seven registrants under seven sponsors at an identical −50.000000%, which is Capital Group's book under seven names. I group houses into one book when they file a cost and a value that agree to the dollar. Of 429 lot-period-series, **76 carry two or more house labels and 45 carry two or more independent books.** The other 31 are sleeves, and counting them would create disagreement out of a distribution list.

### 2.3 On public stocks the same houses agree to the cent

If two houses differed only because their reporting systems differ, through pricing vendors, rounding rules or date conventions, they would also differ on holdings whose price nobody disputes. They do not. On 31 March 2026, Fidelity Contrafund and T. Rowe Price Blue Chip Growth, two funds of two different houses, carry five shared public (Level-1) securities at the identical price per share, to the cent (Table 3).

**Table 3.** Two houses agree to the cent on the public stocks they share. Common report date 2026-03-31; Fidelity Contrafund (accession 0000035402-26-003312) and T. Rowe Price Blue Chip Growth (accession 0001099263-26-006586). These are five shared Level-1 holdings verified to the cent against both filings, not an exhaustive intersection of the two portfolios. Measured the same way on private (Level-3) names, §4.3 finds the ten most broadly held companies a median 24% apart across their disclosing funds.

| Security | CUSIP | Fidelity Contrafund | T. Rowe Price Blue Chip Growth | Cross-house spread |
| --- | --- | --- | --- | --- |
| Alphabet Inc Class A | 02079K107 | $286.86 | $286.86 | 0.00% |
| Alphabet Inc Class C | 02079K305 | $287.56 | $287.56 | 0.00% |
| Amazon.com Inc | 023135106 | $208.27 | $208.27 | 0.00% |
| Apple Inc | 037833100 | $253.79 | $253.79 | 0.00% |
| Cintas Corp | 172908105 | $169.14 | $169.14 | 0.00% |

The public-stock check and the Series J lot use different pairs of houses: Fidelity and T. Rowe Price for the first, Alger and Brighthouse for the second. Applied to holdings with a screen price it returns zero, and applied to a private lot where every mundane explanation is closed it returns eleven dollars a share.

One comparison does use a single pair. Fidelity and T. Rowe Price agree to the cent on the five public securities, and the same two houses appear in §4.3's private cells, where the widest gap between them, on Gusto, is 12.5% ($19.03 against $21.40 on 31 March 2026). The same two houses are zero apart on public stocks and twelve and a half per cent apart on a private one.

Anyone can check both halves in EDGAR from the accession numbers above. Neither says how often disagreement occurs, and five public securities are not the whole overlap of two large portfolios. Together they show that the measurement can read zero and that a real gap exists. The population panel of Section 5 counts how often.

## 3. The data: every private holding US funds report

A disagreement compares two values of one thing: one company, one security, one opinion. The company and the security are defined here, and the opinion, the house, in Section 4.

### 3.1 Every Level-3 private position

The SEC publishes N-PORT filings as quarterly bulk data sets. I take all twenty-seven from 2019Q4 to 2026Q2, with report dates from September 2019 to April 2026, and keep every equity holding that a registered fund reports at fair-value Level 3 and in shares. That gives 309,654 marks on 15,443 distinct issuer names, of which 200,002 are US-domiciled. No list of companies is used at any point: the filings decide which companies exist and which are held widely enough to measure.

I do not use the filers' restricted-security flag, although the ten-company harvest of §4.3 does. Filers apply it inconsistently: ARK Venture reports Revolut as unrestricted while Fidelity reports the same company as restricted. Filtering on the flag would drop the one house that disagrees and turn Revolut's published 35% spread into zero. Without the filter the population reproduces the published cell: eleven funds, 34.7% against the reported 35%.

### 3.2 Companies are matched by identifier, never by similarity

I join rows into companies on a validated CUSIP (check digit verified) or LEI, then on exact normalised names, then on a hand-written list of **thirteen** aliases for names that public filings spell differently, such as Douyin for ByteDance and Space Exploration for SpaceX. There is no fuzzy matching, because the two possible errors are not symmetric. Splitting one company into two loses coverage. Merging two companies creates a price spread out of two unrelated securities, which is exactly the quantity being measured.

Three kinds of rows are excluded. The 262 feeder rows go, because a feeder fund's price per unit is not the company's price per share. Russian issuers go, because they sit at Level 3 by sanction, not by being venture-backed. And 25,482 rows across 1,599 issuers go because they are not shares: contingent value rights, escrow lines, subscription rights, warrants, earnout shares and litigation trusts, identified from the security title (`population.is_claim`). An issuer identifier cannot tell these instruments from the company's stock, and left in they would do to a price what a bad name match does to a company.

Each revision of that list has found a class the previous one missed (Appendix A.2), so two structural tests back it up. The first catches instruments that expire: a share carries no expiry date, so the six remaining rows whose titles name one are checked by name. The second needs no vocabulary. It flags any price two orders of magnitude from the rest of its cell under a title nobody else in the cell uses (`population.price_outliers`), and it finds twelve of them, under six titles on five issuers, each read against its filing. Four are a different security of the same issuer, and two are marks that houses really filed, including First Trust's $1.00 on Epic Games against a $600 consensus. That mark stays in, because a rule that dropped low marks for being low would delete the very disagreement being measured.

What identifiers cannot separate at all, one house holding Series C where another holds Series D, is measured in §3.3. Appendix A.2 lists the two known limits of the join.

### 3.3 Share classes explain the typical gap, not the wide one

Two houses can hold different rounds of the same company's preferred stock, which an issuer identifier reads as one security and which can legitimately carry different prices. N-PORT has no security-level identifier for a private position, so this cannot be fixed by exclusion, but it can be measured. Filers need not name the round, yet 32.5% of rows do so in the security title ("SER H PC PP", "CLASS B PP"), and wherever two houses name the same letter the comparison holds the security fixed.

Holding the security fixed removes almost all of the median gap and little of the tail. On the 1,758 cells where two or more houses name the same series (2,717 company-date-series groups on 137 companies), the median gap between houses is **0.74%**. Scored the way §5 scores everything, ignoring the series, the same cells read 8.45%. The share above 24% falls only from 35.4% to 22.0%, leaving 597 groups across 68 companies. Appendix C.5 and Table C.1 give the decomposition in full (`figures/series_decomposition.png`).

So the typical gap between two houses is mostly composition, two houses holding two rounds of one company, while the wide gap mostly is not. The N-CSR lots of §2.2 show the same thing by hand: 37 of 45 identical lots agree to a hundredth of a point.

Three limits apply. First, the test works exactly where disagreement is smallest. The cells no filing describes are the widest and most numerous group in the panel, so the decomposition describes the calmer half of the data; Appendix C.5 gives the other half its figures. Second, a shared letter is not a shared lot, because two houses can enter one series at closings months apart. Third, naming different letters does not by itself widen a cell. SpaceX, the most widely held private company in the data, appears on 32 letter-mixed cells, and its houses file one price. Cells naming two or more letters sit at a median of 12.90%, barely above the panel's 12.13%.

### 3.4 One signal from outside the filings: IPO prices

Every input comes from EDGAR except one, the offer valuations of the 2023–26 listings, against which §7 scores the fund marks. Three other public signals were built and left out of the argument: a vendor-priced secondary-market cross-section, the same vendor's private-market index, and exchange-traded contracts on IPO timing. I cannot audit their sources, one of them uses the primary round as a model input and so partly assumes what is being measured, and no claim here needs them. Their code and data remain in the repository. Appendix A defines every dataset and variable and records each row's source and date.

## 4. A house, not a fund, is one opinion

Section 2 compared two houses. Whether the house is the right unit, one opinion per house rather than per fund, can be measured in the filings, and getting it wrong changes the headline by three orders of magnitude.

### 4.1 Trusts file, houses decide

N-PORT identifies each filer by registrant, and a registrant is one legal trust. Fidelity files these marks under **36** registrant CIKs, T. Rowe Price under 40 and BlackRock under 56. Treating each registrant as a separate opinion makes two errors in the same direction. A company held by two Fidelity trusts passes a bar meant to require two independent opinions, and the two trusts then agree by construction, because one valuation committee sets both marks. Appendix D gives an extreme case: twenty-two sub-advised funds across five variable-insurance trusts, run by four insurers, all carrying Instacart at T. Rowe Price's identical $32.50.

I therefore map registrants to houses, the fund complexes, using verified rules that cover **98%** of the booked value. The rules that matter are the ones a reader would not guess: Fidelity's VIP trusts, BlackRock's iShares trusts and Capital Group's American Funds, which file under fund names carrying no house brand. The map fails closed. A registrant that matches no rule counts as its own house, so a gap in the map shrinks the correction instead of inventing it, and series trusts that host unrelated advisers stay unmapped for the same reason. Appendix A.5 lists the rules that were dropped or withheld.

The map can be checked in the data. If it fused two different houses, marks inside a mapped complex would disagree more than marks inside one registrant. They do not: 87.5% of multi-fund groups inside a single registrant file an identical price, and 89.0% do inside a mapped complex. Across complexes only 28.5% of those groups agree, and the 90th percentile of the spread exceeds 100%. (That 28.5% counts multi-fund groups, not cells, and so differs from §5.1's 28.4%.)

Form N-CEN checks the map from outside. Every registered fund files it annually, and Item C.9 names each series' adviser, so the SEC records who manages a trust independently of the map. An adviser is recovered for 1,161 of the panel's 1,166 registrants. Of the 55 houses this map merges, 22 file more than one adviser name, and I read all 22: 13 are one firm's several advisory entities, 8 are firms the house bought, still filing their own name, and 1 is an outside manager of a sleeve the house sells. None fuses two unrelated firms. The errors run the other way: 96 advisers appear under more than one house, each a merge the map declines to make. The largest is Putnam, which Franklin Templeton bought in 2024 and which the map keeps separate rather than backdate the merger over four years of filings; Franklin Advisers now advises nine Putnam trusts. All 96 make the correction smaller.

### 4.2 Within a house, one number

If the house is the unit, the marks inside one house should be a single number, not a tight cluster. Across the population, 89.0% of 9,210 house-cells in which one complex files more than one fund report a single identical mark, and the median between-house share of variance in log price is 1.000 across 3,278 multi-house cells. A company held by forty funds across three houses carries three views, and counting funds as independent opinions overstates the evidence by an order of magnitude.

The N-CSR schedules of §2 confirm this from a second document type. Across registrants of one house at one period, the markup is identical to four decimal places in the median of the 19 such cases the harvest holds. Alger's registrants report −9.5104 ± 0.0001 on Databricks Series L, and on 28 February 2026 Capital Group's two registrants report Stripe's Series BB-1, a single lot, at 192.4876% and 192.4992%, a hundredth of a point apart.

Five Capital Group rows are the exception, diverging by as much as 13.8 points across two registrants at one period end. All five are Class B positions bought in two lots, on 6 May 2021 and 24 August 2023, so the cost in each row is a blend, and two funds with different weights on the two purchases report different markups for the same holding. Restricted to single-lot rows, the largest within-house spread in the harvest falls from 13.8 points to 1.2, with a median of 0.0001 of a point. Within a house the mark is one number at a given date. It is not one number through time, and Appendix E.2 finds it is not one number about the share count either.

### 4.3 Ten widely held companies

The ten companies below come from a by-company harvest that stops after eighteen filings per name, so each spread is a lower bound on what a complete sweep would find, and the bound is not tight. Appendix C.3 recomputes all ten from the bulk data and the median rises from 23.5% to 34.7%. Stripe reads +1% here and 73% on the complete filing set for the same security on one date. Table 4 is therefore an anatomy of named marks, and §5 is the measurement of how far apart houses are.

Holding the report date fixed and comparing funds that hold the same security, the spread in the implied price per share has a median of 24% across the ten companies with at least five same-date funds, and the spreads fall into two groups:

**Table 4.** Ten widely held private companies: large spreads on some names, almost none on others. Cross-fund dispersion of SEC N-PORT Level-3 marks for the same private security on a common report date. The spread is the highest implied price per share over the lowest, minus one, across the funds filing that security on that date, each company being read at its own modal report date in 2025 or 2026. Companies with ≥5 disclosing funds; Plaid, at 4, shown for completeness. Every spread here is a floor: the harvest behind this table stops after eighteen filings a name, and Appendix C.3 recomputes the same ten cells on the complete filing set, where the median runs from 23.5% to 34.7%. Read the column as an anatomy of named marks; §5 measures how far apart houses are.

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

Two patterns stand out. The spreads are bimodal rather than graded: large for stale, repriced or contested names, and absent for names with a single fresh, well-publicised round. And within a house the marks are identical. Together they point to valuation policy rather than private information, the private-market counterpart of the discretion illiquid-asset funds exercise over reported marks (Getmansky, Lo and Makarov 2004; Jenkinson, Sousa and Stucke 2013; Brown, Gredil and Kaplan 2019). Appendix F.5 discusses the ten names one by one.

## 5. How far apart houses are

Ten companies cannot say how often houses disagree. I found the names in Table 4 by searching EDGAR's full-text index for private companies I already knew mutual funds held, then kept those with at least five funds filing on a common date. That builds an anatomy of disagreement but not a frequency. If wide spreads are rare and the search found the rare cases, a 24% median describes the search, not the market. The population panel supplies the denominator.

### 5.1 Disagreement is the normal state

A *cell* is one company on one report date, held by at least five funds across at least two houses. Each house's mark is the median across its own funds, so a house filing thirty series cannot widen the spread on its own. Cells whose extreme marks differ more than fourfold are dropped, because at that distance the likely explanation is a share class, not a disagreement. This guard removes 31% of otherwise qualifying company-dates, against 22% when the comparison ran between registrants: two houses are more likely than two trusts of one house to hold different classes of the same company.

N-PORT reports positions at every month-end, so a report date is a month and not a quarter. The twenty-seven bulk data sets carry 104 distinct report dates, of which 92 yield at least one cell. The 104 dates fall on 80 month-ends, because some filers date to the last business day and others to the calendar month-end. That leaves 4,271 cells across 656 companies, a count §5.5 narrows to the venture-backed companies.

Only 17.0% of company-dates are unanimous, and 28.4% agree to within a basis point. The median spread between houses is 12.1%, the 75th percentile is 49.5% and the 90th is 120.7% (Table 5).

**Table 5.** Houses disagree in most company-dates, and about a third of the booked value sits in cells more than 24% apart. The population panel: spread between fund complexes on a common report date, 2019Q4–2026Q2 bulk N-PORT, cells with ≥5 funds across ≥2 complexes (4,271 cells, 656 companies). "Identical" = every house files the same mark to within a rounding tolerance. NAV is the fair value funds booked in that cell. Two sums in this table are a tenth short of the figure quoted beside them, both for the same reason: each band is rounded before it is added. The three bands above 24% come to 179.9 against the $180.0B used throughout, and the whole NAV column comes to 517.2 against $517.3B. Table 8 partitions the same dollars a different way and happens to add to 517.3 exactly, which is rounding rather than a second measurement.

| Spread | Company-dates | Share of cells | Booked NAV ($B) | Share of NAV |
| --- | --- | --- | --- | --- |
| identical | 725 | 17.0% | 80.2 | 15.5% |
| 0–10% | 1,300 | 30.4% | 168.7 | 32.6% |
| 10–24% | 531 | 12.4% | 88.4 | 17.1% |
| 24–50% | 660 | 15.5% | 105.9 | 20.5% |
| 50–100% | 499 | 11.7% | 51.0 | 9.9% |
| >100% | 556 | 13.0% | 23.0 | 4.4% |
| all cells | 4,271 | 100% | 517.3 | 100% |

In 40.2% of all company-dates the spread exceeds 24%, and a tenth exceed 120%. Measured per company rather than per date, 32.5% of the 656 names carry a median spread above 24%.

Against this distribution the ten-company median of 24% is ordinary: it sits at the population's 60th percentile. Scored the population's own way, as a spread between house medians rather than between funds, the same ten cells give a median of 23.7%, which also lands at the 60th percentile. The two readings coincide because on every one of the ten names the widest and narrowest funds sit in different houses, so collapsing funds to house medians removes nothing. The ten widely held names sit just above the middle of the distribution.

### 5.2 More houses widen the range, not the typical gap

The spread is the highest house mark over the lowest, so it can only grow as houses are added; Appendix F.1 uses the same fact for §8. Two-house cells are 1,685 of the 4,271 and $113.2B of the $517.3B, and their median spread is 0.94%, while cells with six or more houses sit at 29.63%. The headline mixes dispersion of opinion with breadth of coverage, and Table 6 separates the two.

**Table 6.** The range grows with the number of houses; the typical pair does not. Cells grouped by how many houses report the company on that date. "Median spread" is the statistic used throughout, the highest house mark over the lowest. "Median pair" is the median across all pairs of houses in a cell of the absolute log price difference, stated as a percentage. It asks how far apart two houses drawn at random are, and it cannot grow mechanically with the count. "Above 24%" is scored on the first of the two. Only "Median pair" is pairwise; every other column here is end to end.

| Houses | Cells | Companies | Median spread | Median pair | Above 24% | Booked NAV ($B) |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 1,685 | 343 | 0.94% | 0.94% | 26.2% | 113.2 |
| 3 | 971 | 233 | 17.64% | 15.38% | 44.2% | 94.8 |
| 4 | 630 | 173 | 20.57% | 10.68% | 47.5% | 79.1 |
| 5 | 370 | 114 | 29.16% | 4.71% | 55.1% | 50.6 |
| 6 or more | 615 | 142 | 29.63% | 2.84% | 55.6% | 179.5 |

The pairwise measure reverses the pattern instead of flattening it. Across the panel the median pair is 5.88% apart, and it puts 29.1% of cells above 24% where the end-to-end statistic puts 40.2%. A widely held company has one or two houses far from the rest and a crowd that agrees, while a three-house company is three ways apart. Both numbers are reported because they answer different questions: the range is what an investor holding both extremes faces, and the typical pair is what a reader pictures on hearing that two houses disagree. Two-house cells are also where a sub-advised sleeve would hide, because the map cannot separate a house from an outside manager copying its marks, and a copied pair reads as two houses agreeing (Appendix A.3).

### 5.3 Disagreement rose after 2021 and stayed high

The median is not stable over time (Table 7). It is 8.22% in 2019, falls to 4.82% in 2021, then roughly triples and stays there: 13.30%, 17.45%, 18.04% and 17.42% from 2022 to 2025. Composition cannot explain the rise, because it runs the other way. The mean number of houses in a cell falls steadily from 4.14 to 3.45, which shrinks a maximum over a minimum rather than growing it, and cells with three or more houses show the same shape at about twice the level.

**Table 7.** Disagreement bottomed out in 2021 and has been higher since. Report years, 2026 being two quarters of one. The last two columns restrict to cells carrying three or more houses, which removes the coverage mixture Table 6 measures.

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

The 2021 trough is §8's mechanism on the calendar. In 2021 almost every company in the panel was close to a fresh priced round, and where a price exists the houses agree about it. When the rounds stopped, the marks drifted apart, and on this evidence they have not come back together. Disagreement as the normal state describes 2022 onwards, and §8's rebuild rate of about 1.1 points a month is what the aggregate looks like from inside.

### 5.4 A consensus and one dissenter

If a wide cell is a crowd with one house away from it, that house can be identified: in each cell with three or more houses, it is the house furthest, in log price, from the median of the others. In 260 of the 2,586 such cells every house files the same price and there is no dissenter. Across the 2,326 that have one, the dissenter sits a median 25.54% from the others' median, while the houses it leaves behind are 1.57% apart at their widest. Disagreement in this panel is usually one house against a consensus, not a spread of views.

The dissenter tends to be the same house from one date to the next. In the 1,334 consecutive pairs where the previous cell's dissenter is still present, so that a repeat is possible, the same house is the outlier again in 65.1% of them. Drawing each cell's outlier at random from the houses in it puts the null at 25.4%, and no draw of two thousand reached 30%. Some houses dissent far more often than their coverage implies: over the 27 houses appearing in a hundred or more of these cells, the ratio of observed to expected dissents runs from 0.08 to 2.36. Slightly fewer than half, 45.5% of outliers, sit above the houses they leave, so dissent is a little more often a discount than a premium.

§8.4 and Appendix G.3 show the same pattern from two other directions: §8.4 finds the top house coming down when a round prices the company, and Appendix G.3 finds a house keeping its side over time. None of the three explains why a particular house sits where it does, and I do not attempt that here.

### 5.5 Venture-backed companies alone

Section 3.3 fixed which security is compared. The other half of the same question is what kind of company is on the other side of it. §3.1 keeps every Level-3 equity position that registered funds report, and not all of them are startups. The panel includes AT&T Mobility II's structured preferred at $25.0B, AmSurg and Southeastern Grocers from buyout portfolios, Neiman Marcus and Intelsat after their reorganisations, and Taiwan Semiconductor, listed in Taiwan and carried at Level 3 for a single month. None is a venture-backed private company, and like the sanctioned Russian issuers of §3.2, their marks follow forces other than a startup's value.

So every cluster carries a label for the kind of company, together with the basis for that label. Clusters holding **93.6%** of the booked value are verified one at a time against the filings, and the rest are labelled by a rule that abstains when unsure. Appendix C.2 gives the rule, its measured accuracy and its failure modes.

**Table 8.** Venture-backed companies hold most of the booked value, and most of the value in wide cells. The population by what kind of company the mark is on, same cells as Table 5. "Private, other" is a private operating company that is not venture-backed: a buyout portfolio company, corporate structured preferred, or equity issued in a reorganisation. "Verified" and "rule" in §5.5 describe how each cluster's label was reached, not how the spread was computed.

| Kind of company | Clusters | Cells | Booked NAV ($B) | Median spread | Above 24% | NAV above 24% ($B) |
| --- | --- | --- | --- | --- | --- | --- |
| venture-backed | 142 | 2,113 | 402.2 | 10.1% | 37.0% | 152.8 |
| private, other | 18 | 314 | 72.8 | 16.1% | 36.9% | 17.0 |
| listed | 348 | 967 | 28.0 | 19.0% | 47.9% | 4.8 |
| unclassified | 148 | 877 | 14.3 | 10.6% | 40.5% | 5.3 |

Restricting to venture-backed companies narrows the population and sharpens the result. They are **2,113** cells over 142 clusters. Five of the seven split issuers named in Appendix A.2 are venture-backed (xAI, Ant, Caris, Didi and Rivian, each reaching a cell under two keys), so those 142 clusters are **137** distinct issuers, still fourteen times the ten names of §4.3, and the count is no longer inflated by 348 listed clusters whose marks sit at Level 3 for reasons unrelated to venture valuation. Among them the median spread is **10.1%** rather than 12.1%, and **37.0%** of company-dates exceed 24% rather than 40.2%.

The dollars move the other way. Venture cells hold $402.2B, of which $152.8B (38.0%) sits above 24%, against 34.8% on the full panel. Disagreement is more concentrated among venture-backed companies than in the population at large, and the listed and non-venture clusters were diluting it. The direction of the result does not depend on where the boundary is drawn.

### 5.6 Where the money sits

Funds booked $517.3B across these cells, of which $180.0B (34.8%) sits where houses disagree by more than 24%; among venture-backed companies alone it is $152.8B of $402.2B. The widest spreads are on the smallest positions. Cells disagreeing by more than 100% are 13.0% of the count and 4.4% of the value, while the 24–50% band alone carries $105.9B. Extreme disagreement is mostly a small-position phenomenon, probably thin coverage and remaining class effects, and the money sits in the moderate, systematic disagreement between houses (`figures/population_spread.png`).

In absolute terms the visible sums are modest. The fifteen companies the by-company harvest of Appendix A reaches carry $24.7B of booked Level-3 fair value, of which $1.9B sits in the six names where houses disagree by 15% or more. Registered funds hold only a sliver of late-stage private equity. The marking convention they expose matters more than the sum: the same convention values the multi-trillion-dollar layer of private holdings across funds and limited partners, where no public filing exists to measure disagreement at all.

### 5.7 Which number to quote

Four medians appear in this section, and each answers a different question. Between registrants, 0.004%: whether two filings of one trust agree, which they do by construction; it is reported only because it bounds the correction from below. Between houses on the full panel, 12.1%: every Level-3 private position registered funds report. Between houses on venture-backed companies alone, 10.1%: the companies the term "unicorn" refers to, and the number behind any claim about them. Between two houses drawn at random rather than end to end, 5.88%: the size-invariant statistic of Table 6, the number to quote for what a typical pair of houses does.

The full panel is quoted when the object is the filing system, the venture panel when the object is venture-backed companies. Both are printed wherever either is used, because the difference between them is a fact about what funds hold at Level 3, not a modelling choice.

Relative to the ten names of §4.3, the population adds scale and structure. Those ten remain the place to see the mechanism, because only there can individual marks be read against named houses and known rounds.

## 6. A company trait, not staleness

Two simpler explanations remain after §2 and §5. The spread could be noise: private marks are imprecise, and a re-draw would reorder the houses. Or one house could have left an old number in place, so that the gap is a lag. Both can be tested on the population, and both fail.

### 6.1 Contested companies stay contested

Among the 290 companies observed on four or more report dates, differences between companies account for 58.8% of the variance in log spread, against 9.7% when company labels are permuted within report dates (200 draws, 95th percentile 10.8%). A company's spread predicts its own next observation with Spearman ρ=0.734 (n=3,439). Restricting to consecutive pairs in which the top-marking house actually repriced still gives ρ=0.665 (n=2,228), so the persistence is not a stale number carried forward. Which companies houses disagree about is stable, and it survives the marks moving.

The persistence could still belong to the pair of houses rather than to the company. Holdings are sticky, so the same houses meet in a company's cell from date to date, and Appendix G.3 finds a house's deviation from consensus persistent on its own. Scoring each pair of houses in each cell separately, across 31,358 pairs on 656 companies, company identity reproduces 29.0% of the variance in the absolute log difference and pair identity 35.2%. But most of the 3,010 distinct pairs are seen on only one or two companies, so a pair label is largely a company label. Restricted to the 754 pairs that appear on three or more companies, company reproduces 31.7% and the pair 25.1%. Both matter and the company matters more. The shares are marginal, not additive, because the two groupings overlap.

Noise does not behave this way. A spread that reordered on each draw would not predict its own next value, and it would not put more than half its variance between companies when permuted labels put a tenth there.

### 6.2 The gap persists when no house has moved

If one house is simply carrying an old number, the gap is a lag, and the test is to look at cells where nobody is lagging. A house has moved when its median across its own funds changes by more than half a per cent from its previous observation of that company, provided that observation is recent. Filings arrive quarterly for most funds and monthly for some, so a gap longer than a quarter is a hole in the record, not a decision to stand pat. In 3,238 cells every house present clears that bar, so the cell's freshness is known. In 760 of them, across 197 companies, no house moved.

These are the cells that should be quiet if the gap were a lag. Of them, 66.4% show some disagreement, and 23.6% (179 cells, holding $5.3B) exceed 24%. The first figure is the weaker one, because "some disagreement" includes differences as small as eight millionths of a point, which is what the median quiet cell shows. The evidence is the tail: 179 cells in which both sides stood still and are more than 24% apart.

One further restriction closes the other explanation. The quiet cells rule out staleness but not share classes, since the widest group in the panel is the one no filing describes, while cells where every filing names the same series letter rule out share classes but not staleness. Their intersection rules out both, and it is 132 cells on 40 companies. Three quarters of them agree to within a twentieth of a point; 76 are not unanimous and six differ by more than 24%, the widest by 233% on seven funds across three houses. Six cells show that a wide gap can occur with both explanations closed. They do not show how often, and §2.1's lot is the same kind of evidence.

The quiet wide cells are not a one-quarter coincidence either: in them, 26.0% of the houses involved have carried the same number for four or more consecutive reports. Both sides are stale, at different prices, which is a standing difference of view rather than a lag, since each filing is an affirmative statement of fair value on that date. The measure is strict: a house whose median shifts because its own fund roster changed counts as having moved, which can only remove cells from the quiet set.

The comparison also runs the other way. Cells where every house remarked show a median spread of 9.9%, against 0.0% where none did, so repricing widens the gap instead of closing it (n=1,147, Mann–Whitney p=1×10⁻²⁰). That pooled figure depends on which companies are in each group, and the within-company version is weaker but points the same way. Of the 129 companies with both kinds of cell, 34 file the same median either way and count as ties. Among the other 95 companies the remarked cells are wider in 54, a bare majority that a sign test cannot separate from a coin (two-sided p=0.22), while a signed-rank test on the magnitudes can (p=0.001). The conclusion rests on the magnitudes and the pooled comparison. Ties are decided by a tolerance rather than exact equality, and the replication package fails if any pair sits close enough to the boundary for rounding to move the count.

## 7. Fund marks beat the last round in five of seven listings

Everything so far measures how far apart the marks are, not which was closer to the truth, because between transactions there is no truth to be closer to. At an exit there is, and exits give the only comparison with a realised price here.

Ten unicorns listed between 2023 and 2026 with a public-data trail, and seven were broadly mutual-fund-held before listing. For each I score two pre-IPO signals against the offer valuation: the headline, meaning the last private primary round, and the last N-PORT fund mark, converted through the IPO's own price per share. **The fund mark is closer in five of the seven, with a median absolute error of 11% against the headline's 48%.**

Three limits apply at once. Seven exits cannot support a count: an exact sign test on the five wins gives p=0.23, so the content is in the magnitudes, which pass a paired test at p=0.078. Both medians are single observations, because with seven exits the fourth-ranked error is the median: the 48% is Figma's own −48.19%, and the 11% is ServiceTitan's +11.06%. And this 48% is unrelated to the 48% of §1.1, where Gornall and Strebulaev compare the headline with the option-adjusted fair value of the cap table; two different comparisons happen to land on one number.

The two exceptions sharpen the claim. Klaviyo and Circle are the only exits whose last private round was recent and fairly priced, and they are the two where the headline wins. The fund mark's advantage is therefore freshness rather than foresight. It holds where the headline has gone stale, which §8 shows is the normal condition, because disagreement rebuilds within a year of the last transaction.

This comparison establishes direction, not frequency. The marks whose disagreement §5 measures are not noise around a worse number: where a price finally appears, they sit closer to it than the number the press was quoting. Appendix D gives the exit-by-exit table, the per-house harvest, the conversion-ratio robustness and the qualifications each named exit needs.

## 8. A new round compresses disagreement

Sections 5 and 6 establish a level and show that it is a stable trait of the company. This section adds time since the last transaction. Houses converge in the month a round gives them a price to converge on, and drift apart again at a measurable rate afterwards.

The result is a dated fact about a distribution, not causal identification. Five readings that would produce the same shape without a round are tested below and fail: a trend in event time, a change in which houses are compared, a restatement that looks like agreement, the calendar itself, and houses agreeing on good news rather than on a price. The last is the hardest, and §8.4 addresses it by showing that the most optimistic house comes down, which good news would not produce. What remains open is that companies choose when to raise. Each limit is stated where the claim it limits is made.

### 8.1 Design: later rounds and a symmetric window

A priced round is the one moment a private company has something close to an observable price. If disagreement between houses reflects uncertainty about value, it should be smallest just after a round and widen as the round recedes. If it is a standing difference in method, as the quiet cells of §6.2 suggest, a round should do nothing. The test needs two dates the filings do not state: when a company priced a round, and when a share count was redefined, so that a spread reflects a restatement rather than a view. Section 9 recovers both from the filings.

One confound is built into the sample. A company enters the panel because a fund bought it in a round, so for its first dated round, months since the round and months since entering the panel are the same quantity. Any anchor placed early in the window reproduces the profile whether or not rounds matter, and more data does not help. Every anchor in this section is therefore a company's second or later dated round, and §8.5 shows what admitting first rounds does.

Two design choices separate the hypotheses. Using only later rounds moves the anchor while the window stays put, because for a company already in the panel the next round is not why it is there. This cuts the sample from 858 cells on 123 companies to 462 on 43. And a symmetric window distinguishes a step from a trend. If a round resolves disagreement, there should be a discontinuity at zero, wide before and narrow after, while the confound predicts a smooth trend and no step. Looking only forward cannot tell the two apart; looking both ways can.

### 8.2 Disagreement drops in the month of a round

The window holds 462 guarded cells on 43 companies, from six months before to twelve months after a later dated round: 139 cells on 31 companies before and 323 on 43 after. Because §6.1 finds the spread is a trait of the company, every observation is demeaned within its company before averaging, and Table 9 shows the pooled version beside it.

**Table 9.** Disagreement dips at a round and rebuilds over the following year. Between-house spread by months to the nearest non-first dated round. "Pooled" is the median spread across cells, in per cent. "Within-company" is the median deviation from the company's own median spread, in percentage points, so a positive number is a company wider than its own norm. Restatement windows (Appendix E.2) are excluded. Selected months; all nineteen are released.

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

The within-company column is positive before the round, negative at it, and above ten points a year later: a trough.

Comparing months −3 to −1 with months 0 to +2, paired within each of 31 companies: median **5.22%** before, 0.00% after, a step of **−2.52 points** (the median of the per-company changes, not the difference of the two medians), narrower after in 22 of 29 untied companies; signed-rank p<0.001, sign test p=0.0041. The bands are adjacent and short on purpose, so that a smooth trend contributes only its slope over five months while a jump at the round contributes all of itself.

Two units appear in the tables below. The step above pairs each company's before and after bands once: 31 companies, 29 untied. The placebos and the selection ladder cannot do that, because shifting an anchor changes which rounds fall in the window and which companies contribute, so they use one observation per anchor date: 49 anchors, 46 untied, a median step of −1.94 points at p=0.0008. Both are negative and significant. The per-company figure is the conservative one, and each table states its unit in the caption.

A phase-randomised null, which reshuffles event dates within each company's own report dates over 400 draws, matches or beats the observed step in **0 of 400**. This count is weaker than it looks. With a random anchor both bands come from one distribution, most companies' paired difference is exactly zero, and the median across companies is zero in nearly every draw, so "0 of 400" says only that the observed step is negative and the null's never is. The sign test does not have this problem, and it is the statistic this section rests on.

The evidence is the contrast between two statistics on the same sample. The first design's near-versus-far comparison gives −7.77 points at p=0.010 and is still reproduced by 31% of random anchor placements. The step at zero is reproduced by none. Random anchors make a trend; only the round makes a jump (`figures/round_event_study.png`).

### 8.3 Shifted anchors find nothing

Three arithmetic explanations fail before the placebo is needed: cells do not get wider across the round, the round-month cell is not just the newly priced security agreeing with itself, and restatements do not produce the step. Appendix F.1 gives all three with their numbers.

Later rounds are not randomly timed, since companies raise when markets are open, so a null that moves the anchor to a random date does not answer that objection. A placebo does. Shift every anchor by a fixed number of months, and the calendar month, the market conditions and the company's own filing rhythm all remain; only the event is removed.

**Table 10.** The step appears at the round and at none of three shifted anchors. Each row re-runs the whole design with the anchor moved by the stated offset. One observation per round, not per company (§8.2). Sign p is one-sided against the alternative that the post band is narrower.

| Anchor | Events | Companies | Median step (pts) | Negative / untied | Sign p |
| --- | --- | --- | --- | --- | --- |
| the round | 49 | 31 | −1.94 | 34 / 46 | 0.0008 |
| six months before | 37 | 22 | 0.000 | 14 / 31 | 0.763 |
| six months after | 49 | 35 | 0.000 | 17 / 41 | 0.894 |
| twelve months after | 37 | 29 | 0.000 | 13 / 31 | 0.859 |

At the round the step is present. At all three shifted anchors it is gone, in the same way each time: a median of exactly zero and a sign count on the wrong side of a coin, 14 of 31, 17 of 41 and 13 of 31. Those zero medians share the degeneracy of the step's own null, so on those rows the sign counts carry the argument.

### 8.4 The most optimistic house comes down

The placebo removes the event, but it cannot separate a price arriving from good news arriving, because both come with the round. Good news has a signature: it moves every house the same way, so all revise toward the new number and the cell narrows because the laggards catch up. Nothing about good news pushes the most optimistic house down.

So I decompose the cell. With the consensus taken as the median of house medians, the upper gap is how far the top house sits above it and the lower gap is how far the bottom house sits below. Good news narrows only the lower gap. The decomposition needs cells with three or more houses, 60.5% of the panel's guarded cells: with two houses the median is their midpoint, the two gaps are equal by construction, and the top house falling cannot be told apart from the bottom house rising.

**Table 11.** At a round the top house comes down; the bottom house does not clearly come up. Which side narrows across the round, and at the same three shifted anchors. Sign p is one-sided against the alternative that the gap narrows. Selecting the top house selects partly on its own error, so the placebo rows are the test.

| Anchor | Events | Top house narrows | Sign p | Bottom house narrows | Sign p |
| --- | --- | --- | --- | --- | --- |
| the round itself | 42 | 29 / 34 | 2×10⁻⁵ | 23 / 37 | 0.094 |
| six months earlier | 31 | 14 / 22 | 0.143 | 11 / 23 | 0.661 |
| six months later | 43 | 14 / 30 | 0.708 | 15 / 34 | 0.804 |
| a year later | 32 | 10 / 24 | 0.846 | 14 / 27 | 0.500 |

At the round the top house comes down in 29 of 34 untied anchors (Table 11). No shifted anchor reproduces this. Two sit below a coin, 14 of 30 and 10 of 24 at the later anchors, and the earlier one leans the same way at 14 of 22 without clearing five per cent, p=0.143 against 2×10⁻⁵ at the round. The bottom house clears five per cent at no anchor, the round included.

The finding is one-sided. At the round the bottom house reaches p=0.094, and reading that as confirmation because the next column shows 2×10⁻⁵ would treat a p of 0.09 as a result on the strength of its neighbour. The table supports the one-sided claim: the optimist comes down. Whether the pessimist comes up, the 37 untied anchors on that side cannot say.

The one-sided claim is the one that matters, because good news cannot produce it. It is also exposed to mean reversion: the top house is selected partly on its own error, so its gap narrows whether or not anything converges. But mean reversion does not know where the rounds are. It works at every date, and the shifted anchors are every date: pooled across the three, the top house narrows in 38 of 76 untied anchors, exactly a coin.

This rules out one story, houses agreeing on good news, because that story cannot pull the optimist down. The timing of rounds remains endogenous, which is the subject of §8.5.

### 8.5 The size depends on which rounds are admitted

The result is sensitive to which events are admitted, and Table 12 shows how. Of the 5,885 company-series pairs in the panel that carry a letter, 434 are dated under the rule of §9, 75 of those are later-round anchor dates, and 49 have guarded cells in both bands.

**Table 12.** The step shrinks as the event selection widens, but keeps its sign. The selection ladder: the step recomputed as each filter is relaxed. One observation per round, as in Table 10.

| Selection | Events | Median step (pts) | Negative / untied | Sign p |
| --- | --- | --- | --- | --- |
| dated, non-first, restatement out, guarded | 49 | −1.94 | 34 / 46 | 0.0008 |
| keep restatement windows | 50 | −1.60 | 34 / 47 | 0.0015 |
| all cells, not only guarded | 49 | −1.94 | 34 / 46 | 0.0008 |
| admit first rounds too | 64 | −1.08 | 43 / 60 | 0.0005 |
| drop the two-house bar | 103 | −0.00 | 55 / 93 | 0.048 |
| drop it and keep restatement | 107 | −0.00 | 57 / 97 | 0.052 |

Two filters do not matter: keeping restatement windows moves the median by three tenths of a point, and restricting to guarded cells changes nothing to four decimal places. Two filters change the size, in the way §8.1 predicts. Admitting first rounds halves the step, from −1.94 to −1.08, as the confound implies: a first round's anchor sits on the company's entry into the panel, and 15 such anchors are enough to halve a step measured on 49. Its sign test reads stronger than the base row, p=0.0005 against 0.0008, because fifteen extra events add power to a sign test even as the effect being signed shrinks. That is why §8 quotes the size and reports the p-value beside it.

Dropping the two-house bar on the round date takes the size to zero. That bar was not chosen after seeing this statistic. It comes from the N-CSR calibration in Appendix E.3, and the eight one-house pairs it excludes miss the N-CSR acquisition date by 49 to 670 days: Discord Series G by 670, SpaceX Series B by 570, OpenAI A-2 by 426. Admitting them adds no rounds, only anchors placed months away from the event, and a misplaced anchor smears a step by construction.

So the limit is on the size, not the direction. At the widest selection the median step is zero to six decimal places while the sign holds: 55 of 93 untied anchors are negative (59%), with a sign test at p=0.048. *A reader who does not accept the two-house bar as a round-dating rule should read this result as a direction without a reliable size.*

I also tried a different dating rule. Because a round creates a price, a round month could be defined as the first in which two or more houses report the new series at prices that agree. It dates worse, because houses are a median 30 days apart in recognising a corporate action (Appendix E.2), so waiting for the second house waits on its reporting calendar rather than on the company. Under that rule the size moves with the anchor, from −1.94 points to −0.06, while the sign holds at p=0.022 (Appendix E.3). The count rule stands, and so does the limit on its size.

The endogeneity a placebo cannot reach is that the company chooses when to raise. The discriminating test splits rounds by the change in the median price per share, a level rather than a spread, and so not the dependent variable in disguise. If houses converge because the news is good, the step lives in the up rounds; if they converge because a price now exists, it lives in both (Table 13).

**Table 13.** The step comes from up rounds; the seven down rounds show nothing. The step split on the change in the median price per share across the round. Per anchor date, as in Tables 10 and 12, and (unlike them) with restatement windows kept, which is why the "all" row reads 50 events rather than 49 and matches the second rung of Table 12, not the first.

| Rounds | Events | Median step (pts) | Negative / untied | Sign p |
| --- | --- | --- | --- | --- |
| up | 43 | −1.94 | 31 / 40 | 0.0003 |
| down | 7 | 0.000 | 3 / 7 | 0.77 |
| all | 50 | −1.60 | 34 / 47 | 0.0015 |

Seven down rounds are not a test. The step comes almost entirely from rounds that raised the price, and the down rounds return nothing rather than the opposite: a median of zero and three of seven negative. The reading that houses converge on good news is therefore not excluded, and this limits the result itself. A panel through a full down-cycle, or a lower dating bar, would run the test, and Table 12 shows what the second costs.

### 8.6 Disagreement rebuilds by about one point a month

The limit above concerns the event list: admit anchors the dating rule cannot place and the size goes. Two results do not depend on that list.

The first is a rate. The within-company deviation runs −3.53 at month one and +10.86 at month eleven. Fitted per company over months 0 to 12, the median slope is +1.11 points a month, rising in 24 of 36 companies, sign p=0.033. A slope is a trend, and the phase null reproduces trends, so the slope has to clear the same null. It does, with 4% of random placements matching or beating it, but the null's own median slope is +0.05 points a month, the general drift within the window. A round therefore buys agreement among houses for about a quarter, after which disagreement rebuilds at roughly 1.1 points a month, almost all of it attributable to the round rather than to the drift any anchor produces. This rate does not depend on which anchors are admitted.

The second is repetition inside a company. Thirty-one companies is the standing complaint about this result, and the answer is more anchors inside the companies there are. A company with several dated later rounds carries the anchor to several places in its own window. A company-level time trend can produce a step wherever the window starts, but it cannot produce one at each round. Across 30 rounds on 12 companies, 10 of which carry two or more, the median step is −8.81 points, negative at 23 of 29 untied rounds, sign test p=0.0012, and negative at every one of its own rounds in 5 companies.

### 8.7 What the round result shows and what it does not

The round result explains the bimodal picture of §4.3, where names with a fresh, believed round are herded and stale ones dispersed. Read alone, that looks like two kinds of company. The trough says otherwise: the same company is herded in the month it prices a round and dispersed a year later. The two modes are a snapshot of companies spread along one phase variable, which is why they never separated cleanly on any company characteristic.

The N-CSR lots of §2 fit the same pattern without proving it. The four cross-book disagreements are all Databricks, on its most recent series, in the quarters it was repricing. The pattern is consistent with a phase effect, but ten names and four disagreements cannot separate a phase from a company, and the population panel and the event study carry that claim.

The evidence shows that disagreement between houses collapses in the quarter a company prices a round and rebuilds over the following year: on 31 companies, at monthly resolution, with the anchor separated from panel entry, after within-company demeaning, a composition check, a new-series check, three shifted-anchor placebos and a repetition test inside single companies.

It does not show why a company raised when it did. The null tests placement within a company's own dates, not the decision to raise, and §1 states what that leaves unclaimed. The next step is more companies with several dated rounds, which Appendix E.3 supplies at 24 companies with three or more, and a panel long enough to contain a down-cycle.

## 9. Four measurements recovered from filings

The tests above need four facts the filing system does not publish as dates: when a company listed, when its share count was redefined, when it priced a round, and what a holder paid. Table 14 shows how each is recovered from public, machine-readable documents and calibrated against an independent document type. Every threshold is read off a gap in the observed distribution rather than chosen, which is the only defence available when the person who sets a threshold later benefits from it.

**Table 14.** Four dates the filings do not state, recovered and calibrated. The four measurements, what each recovers, what it is calibrated against and how well it does. Appendix E gives each in full: the design, the corrections that shaped it, and what it cannot see.

| Measurement | Recovered from | Reach | Calibrated against | Accuracy |
| --- | --- | --- | --- | --- |
| Listing dates | Form 8-A12B, or 8-K12B through a shell | 21 of 23 classified listings | the last date the panel carries the name private | eighteen of 21 inside a quarter, widest 82 days against a next-closest 258 |
| Share splits | the share-count panel: a split multiplies the balance by *k* and leaves the value alone | 601 candidates → 29 events on two or more houses | the ratios companies actually split at | 26 of 29 canonical; restatement spans a median 30 days and up to 92 |
| Round dates | the first report month a new series letter appears across two houses | 434 company-series pairs on 287 companies | the earliest N-CSR acquisition date for the same series | Fourteen of fifteen dated pairs land inside 35 days, median gap 16 |
| Acquisition dates and cost | Regulation S-X schedules of investments on Form N-CSR | 767 schedule rows, 10 companies, 44 registrants, 429 lot-period-series | EDGAR's own prefiltered accession set | zero missed accessions across all ten companies |

Three of the four measurements produced a finding of their own, each a correction another part of the paper needed. Restatement is not simultaneous, so a one-month confirmation window is the wrong unit; confirmation counts houses, never registrants; and a cost per share is not comparable across filings, while a markup is. Appendix F.3 gives all three with their numbers.

## 10. What would overturn each claim

Table 15 lists, for each claim, the observation that would overturn it and where the paper tests it. The limits that belong to the design as a whole follow in §10.1 and §10.2.

**Table 15.** Each claim, what would overturn it, and where the paper tests it.

| Claim | What would overturn it | Where tested |
| --- | --- | --- |
| The unit of an independent valuation is the house | Marks inside a mapped complex disagreeing more than marks inside a single registrant | §4.1: 89.0% identical inside a complex against 87.5% inside a registrant |
| Between houses the median company-date is 12.1% apart | A resolver error fusing two companies, or an instrument that is not the stock | §3.2: identifiers only, 25,482 claim-instrument rows excluded, twelve price outliers decided one by one |
| The disagreement is not a reporting artefact | Two houses disagreeing on the Level-1 holdings they share | §2.3: Fidelity and T. Rowe Price, cross-house spread 0.00% on the five verified shared public holdings, against 12.5% for the same pair on a shared private name and tens of per cent across other pairs (§4.3) |
| The disagreement is not a share class or a lot | A wide cell where the series and the acquisition date are provably identical turning out to be neither | §2.1: both are disclosed on the Series J lot and the spread is 10.2% |
| The disagreement is not staleness | Cells where no house moved being unanimous | §6.2: 66.4% of 760 such cells are not unanimous |
| It is a company trait, not a date effect | Between-company variance falling to the permutation null | §6.1: 58.8% against 9.7% |
| Disagreement compresses at a round | A shifted anchor reproducing the step | §8.3: a median step of exactly zero at all three shifted anchors |
| …and the compression has a size | The step surviving a wider event selection | §8.5: it does not; the median step is zero to six decimals at the widest rung, p=0.048, reported as the result's limit |
| The marks beat the headline at exit | The fund mark losing once the conversion bridge is varied | §7 and Appendix B: 4–6 of 7 across conversion ratios 0.8–1.2 |

The one row of Table 15 that fails is printed with the rows that pass. The size of the step in §8 does not survive its widest selection, and a reader who discounts §8 to a sign keeps §§2–7 intact.

### 10.1 Nothing here is pre-registered

Nothing in this paper is pre-registered, and that applies to every number above.

In place of a registration I report one prediction tested before filing. Of the five predictions the drafted registration makes, P4, that cross-house dispersion collapses as a company approaches its listing, can already be run on listings that predate the registered window. It does not hold: fifteen names, six narrowing, seven widening and two unchanged, a one-sided signed-rank test at p=0.43, and a power calculation showing that the null means *not large* rather than *absent* (Appendix F.4).

Which reading failed matters, because two readings predict opposite things here. If disagreement closes because information arrives, P4 should hold: the weeks before a listing bring a roadshow, a price range and a prospectus, as much news as a private company ever produces. If it closes because a price arrives, as §8.4 argues, P4 has no reason to hold, because until the IPO prices there is still no price. The data favour the second. The weak tilt toward widening matches §8's rebuild rate of about 1.1 points a month for names whose last round is by then very stale. P4 is therefore a test the anticipation reading failed, and at fifteen names the null still means *not large*.

The registration is drafted and not filed. Appendix F.4 gives the full argument: what filing before the next panel extension would buy, the power calculation behind P4, and the one contrast in this project that a registration was written for. That contrast, a demand-favoured sector split, left this paper with the secondary-market signals (§3.4), and Appendix F.4 keeps its pre-registration record so that the exclusion can be checked.

### 10.2 Dependence and multiple testing

Two properties of the design bear on every significance figure above. First, the observations are not independent. A cell is a company on a report date: cells of one company share whatever makes that company contested, and cells of one date share whatever the market did that month. Appendix B makes this point for the tracer panel and quotes its pooled p-value only to show which way the comparison runs. The same caveat applies to the population tests, and §6.2's p=1×10⁻²⁰ in particular is a pooled figure on 1,147 cells correlated in both directions. The evidence the paper rests on is not pooled: the step at the round is a paired within-company comparison, one observation per company or per anchor date, and §6.2's within-company version is reported beside the pooled one and is weaker. Where the two disagree, I quote the within-company figure.

Second, nothing here corrects for multiple comparisons, and the paper runs about thirty sign and signed-rank tests. The core survives any reasonable correction: the step at the round is p=0.0008 and the top house coming down is p=2×10⁻⁵, and a Bonferroni factor of thirty leaves both below conventional thresholds. Two results do not survive, and they are the two already flagged as weakest: the widest rung of §8.5's selection ladder at p=0.048, which any correction removes, and the reversion tilt of Appendix G.3, which does not reach five per cent even uncorrected, at p=0.085 one-sided and 0.170 two-sided. Neither carries a claim on its own. The first is a direction without a size, and the second is not established.

## 11. Conclusion

Between funding rounds, professional investors disagree about what the same startup is worth, and the disagreement is a lasting trait of the company rather than noise or stale reporting. A new round narrows it, and it reopens within months.

The main practical lesson is about measurement. Counted trust by trust, fund filings suggest near-perfect agreement, with a median gap of 0.004%, because one valuation committee appears many times. Counted by the houses that set the prices, the same filings show a median gap of 12.1%. Any study that treats fund marks as prices for private companies has to count houses. The cost to fund investors is small, a median 0.33 basis points of net asset value, so the disagreement matters mainly for what fund marks can say about a private company's value.

Two limits remain. The cases no filing describes by share class are the most contested, and I cannot say what drives them. And the sample holds only seven down rounds, so whether a falling price closes the gap the way a rising one does is still open.

## Appendix A. Data and variable definitions

### A.1 Every dataset and how it is built

Every dataset is a CSV committed in `data/`. Each row carries its own source and date, and `notes/data_dictionary.md` documents every column. Table A.1 lists the datasets and what each one feeds.

Every input is public. Headline rounds are facts taken from company announcements and the financial press, and everything else is an SEC filing. One window runs throughout, 2019Q4 to 2026Q2, the span of the quarterly bulk data sets; where a figure uses a narrower window, the text names it.

**Cross-fund N-PORT marks, the by-company harvest.** This file feeds only the ten named cells of §4.3. No population figure uses it, and Appendix C.3 recomputes all ten from the bulk data, where the median rises from 23.5% to 34.7%. `src/nport_fetch.py` collects 409 raw Level-3 rows from EDGAR full-text search over Form NPORT-P, and the cleaning below cuts them to 386 Level-3 holdings across 104 mutual funds and 15 companies. Keeping only Level-3 marks also drops the public-company namesakes the text query catches, such as the Tokyo-listed PLAID, Inc. For each fund and company I compute the blended implied price per share, Σ(fair value)/Σ(shares), from the private-equity holdings (`<invstOrSec>` with `fairValLevel`=3, `isRestrictedSec`=Y, `units`=NS, `assetCat`∈{EC,EP}). The spread across funds is taken on a common report date, so it measures disagreement rather than different fiscal quarter-ends. Special-purpose-vehicle and fund-of-fund wrappers and 10:1 unit-convention outliers are dropped. SpaceX and ByteDance are excluded from the per-share comparison because their holders hold different share classes or legal entities: SpaceX is detected automatically, and ByteDance is excluded by hand (Douyin Co Ltd against ByteDance Ltd, common against convertible preferred; `src/fund_marks.py`).

**IPO-exit validation** (`data/ipo_validation.csv`, `src/validation.py`). For the ten unicorns that listed in 2023–26, seven of them broadly held by mutual funds before the IPO (Instacart, Reddit, Chime, Figma, ServiceTitan, Klaviyo, Circle), I score two pre-IPO signals against the IPO valuation. The first is the headline, with error `overshoot = last_private/IPO − 1`. The second is the last pre-IPO N-PORT mark, converted to a company valuation through the IPO's own price per share, `implied = IPO_val × mark_pps / IPO_pps`. Pre-IPO preferred converts roughly one for one into common at a healthy listing, so the valuation error equals the per-share error. The less wrong signal is the one with the smaller absolute error. The `vintage` field tags the 2021-peak cohort, whose headlines are the stale ones. Klarna has no broad mutual-fund mark, and its interim signal is its 2022 down round.

**Statistics** (`src/robustness.py`). Binomial sign tests and Wilcoxon signed-rank tests throughout, and permutation nulls where a statistic has no closed form. The module also computes a bootstrap interval for the median of the secondary-market cross-section, which belongs to a leg this paper no longer carries (§3.4) and stays in place for the second paper.

**Table A.1.** Every dataset, what it holds and what it feeds. All inputs are public; SEC N-PORT is in the public domain.

| Dataset (`data/*.csv`) | Coverage · key fields → derived object (§) · source basis |
| --- | --- |
| `nport_population_marks.csv.gz` | the paper's core. 309,654 Level-3 private marks · 15,443 issuer strings · 104 report dates, 2019Q4–2026Q2: CIK, series, report date, balance, valUSD, fair-value level, issuer name/title, CUSIP/LEI → the company × report-date panel (§3, §5, §6). SEC N-PORT quarterly bulk data sets, public domain. |
| `population_cells` | 4,271 guarded cells · 656 companies: company key, report date, house count, min/max house median, fund count, booked NAV → every figure in §5 and §6. Derived from the marks file by `src/population.py`. |
| `company_classification` | 656 clusters: label, basis (verified / rule / unclassified), reasoning line, booked NAV → Table 8 and the venture-backed population (§5.5, Appendix C.2). Filings plus the public record, one cluster at a time. |
| `ncsr_acquisitions` | 767 schedule rows · 10 companies · 44 registrants · 429 lot-period-series: filer, CIK, accession, acquisition date, cost, value, shares, period → the disclosed entry price and the cross-book comparison (§2.1–2.2, Appendix E.4). SEC Form N-CSR schedules of investments. |
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

The Level-1 placebo appears in the body (Table 3, §2.3) rather than here, because it tests the paper's central claim instead of a detail of the data.

### A.2 What the resolver has missed

§3.2 excludes non-stock instruments by their security title, and each revision of that list has found a class the previous one missed: contingent value rights, contra positions, warrants and rights written in the singular, and lock-up placeholders. The last kind is a line a filer books as DUMMY before the security it stands for exists; Foresight Energy's was carried at $1.47 against real equity between $7.93 and $16.33. This history is why §3.2 backs the list with two structural tests, and it is recorded here for its failure mode rather than for the four spellings.

Switching off the dummy-equity class and the expiry test costs fifteen cells and moves the population median by a third of a point, about what lines this small should do. The effect runs both ways: removing the dummy equity from three cells brought them back inside the class guard, so the panel gains cells as well as losing them.

Two limits of the join survive both tests, and both are visible in the output.

First, the issuer name can simply be wrong. Two hundred and nineteen rows read "VENTURE CORP LTD" in the issuer field while the security title reads "VENTURE GLOBAL LNG INC SR C PP": the name of a listed Singapore electronics manufacturer on a private LNG developer's stock. They carry no CUSIP and no LEI, so nothing contradicts the name, and the resolver clustered them on it, as it should. The one real Venture Corp row in the data ended up attached to them. Across the reported cells, 2.52% of rows name one company in the issuer field and another in the security title, spread over 57 clusters. `company_class.name_mismatch` lists these rows for review instead of acting on them, because the title is not always the truthful field either.

Second, failing closed has a cost of its own. An issuer that filers spell several ways lands on several keys, and each key must clear the five-fund, two-house bar alone. In this panel seven companies reach a cell under more than one key: xAI, Ant, Caris, Didi, Rivian, Windstream and Venture Global. This can only cost coverage, never create a spread, but it inflates any count of companies, so §5.5 reports issuers as well as clusters.

A third limit belongs to the comparison rather than to the resolver, and §4.3's two exclusions show it best. SpaceX is out of the per-share panel because funds hold different classes (common near $526, others several times higher) and some report share counts on a 10:1 basis. ByteDance is out for a sharper version of the same problem: its holders do not agree on what they hold. Fidelity books the Douyin Co Ltd entity (about $257), BlackRock the ByteDance Ltd Series E-1 common (about $253) and T. Rowe Price a convertible-preferred Series E (about $386), so its apparent 53% spread comes from class and entity, not from a view on value. That two professional holders can disagree about the label on a security is why §3.3 exists.

### A.3 Limits of the population panel

Sections 7 and 8 state their limits where each claim is made. This subsection and the next state the limits of the two panels as a whole.

The population panel (§5) has five limits. First, its unit of independence is the fund complex, and the map from registrant to complex is mine. It covers 98% of the booked value by rule and leaves the rest as single-registrant houses, which biases every figure toward agreement, so the disagreement it reports is a floor. Second, it cannot see sub-advisory mirroring. The twenty-two insurance-trust funds that carry T. Rowe Price's Instacart mark (Appendix D) sit under four insurers and count as four houses, although all of them file one manager's number. Mirroring of this kind makes houses look more alike than independent views would, so it too pushes the panel toward agreement.

Third, the share-class guard discards 31% of otherwise qualifying company-dates. Inspection says these are unit and class artefacts, but the guard is a threshold, not a diagnosis. Fourth, the panel covers what registered funds happen to hold at Level 3, a sample of the private market drawn by the holders rather than by the companies. A private company that no mutual fund holds is invisible to it.

Fifth, the venture label of §5.5 is a judgement wherever the filings stop short of one. It is checked cluster by cluster over 93.6% of the booked value and applied by rule over 3.7% more, where it is right 94% of the time against the clusters that were checked. Its errors run in one direction, since a private buyout company that no filer called a private placement reads as listed, and 2.5% of the value carries no label at all. A reader who draws the boundary differently can read the alternative from Table 8, which prints all four totals for that reason.

Three further limits belong to the four measurements and are stated with them in Appendix E: the round-date rule cannot see rounds that reuse a letter, the split detector dates a restatement to a window rather than a day, and the N-CSR harvest covers ten companies and whichever filers schedule them.

### A.4 Limits of the cross-fund panel and the exit comparison

**Comparability.** Per-share marks are comparable only after dropping special-purpose-vehicle wrappers, 10:1 unit-convention outliers and composites whose holders split across share classes or legal entities (SpaceX, detected automatically; ByteDance, excluded by hand; Appendix A.2). Spreads are taken on a common report date to remove fiscal-quarter timing. And because marks cluster by house, the number of independent views is the number of houses, not funds, so the cross-fund spreads document disagreement rather than a precise distribution.

**The level depends on the sample.** The median spread rose from 13% to 24% when the panel widened from eight to ten broadly held names. On the same ten names it depends on coverage in one direction only: the harvest behind Table 4 stops at eighteen filings per name, and lifting that cap moves the median to 34.7% (Appendix C.3). So 24% is a floor, not an estimate. What survives the change of sample is the bimodal split: herding on fresh rounds, and disagreement of tens of per cent on stale, repriced or contested names.

**Selection by holder.** N-PORT covers only names that mutual funds hold, a second selection but a bounded one. A five-name expansion probe (Appendix B; `data/nport_expansion_probe.csv`) found exactly one further name clearing the bar; the others were held by at most a handful of funds or in mixed preferred classes, such as Perplexity's D-1 and E-1 against common. The ten-name panel therefore sits close to the full set of broadly co-held names, and widening it is archival work rather than a hidden sample. The named additions (Plaid, Revolut, Gusto, and the excluded ByteDance) were chosen because they are broadly held, so they describe large fund-held unicorns, not unicorns in general.

**The exit comparison (§7).** Ten exits clear the public-data bar, and seven were broadly held by mutual funds before the IPO. The finding that the fund mark beats the headline in five of the seven, with two clean counter-examples, illustrates a pattern on a handful of large listings; it is not a population inference. The bridge from mark to valuation assumes that the pre-IPO preferred converts one for one into IPO common.

Reddit's, Chime's, ServiceTitan's, Klaviyo's and Circle's marks each come from a single house (Fidelity; Alger; T. Rowe Price; ClearBridge, a Franklin Templeton affiliate; Fidelity), and several are dated close to a visible exit: Chime's about six weeks before, Circle's about five, ServiceTitan's and Figma's two to three months. Part of their accuracy therefore reflects proximity to the listing, since a fund marking a holding weeks before a visible IPO may be anchoring on the roadshow price. The edge is best read as the absence of staleness, possibly helped by anticipation of the IPO, and not as independent foresight.

The two counter-examples are informative. Klaviyo and Circle are the two names whose last round was recent and fairly priced, so the headline was not stale and the fund mark had no staleness edge; Fidelity's Circle mark in fact undershot a hot crypto listing. That is why §7 states the fund mark's advantage as conditional on a stale headline.

Three headlines carry a flag. Figma's floor is itself partly a staleness artefact, because it had no priced primary round after 2021. ServiceTitan's headline is a structured November 2022 down round carrying a compounding IPO ratchet. Circle's is its 2022 Series F; the widely cited $9B was a terminated SPAC deal, not a round.

For Instacart I use the T. Rowe Price and American Funds series that two houses mark alike, at $32.50; Fidelity's senior Series I preferred is a higher-priced class (the §4.3 class caveat again). Exits are self-selected: only companies that chose to list, at a price the bookrunners could clear, reach this comparison (the dynamic selection of Cochrane 2005 and Korteweg and Sorensen 2010). The three later additions, ServiceTitan, Circle and Klaviyo, are the broadly fund-held 2023–25 unicorn listings I screened together for a clean pre-IPO Level-3 mark. All three had one and all three are reported, including the two that break the pattern, so the result is not cherry-picked, although I do not claim to have screened every 2023–25 listing.

**The reconciliation with Gornall and Strebulaev (Appendix C.1) is interpretive.** I do not re-estimate their contingent-claims model, because the public filings used here carry no per-round legal terms. The link between their term-structure wedge and this paper's cross-section is a qualitative correspondence that the sign pattern supports, not a re-derivation of their 48%. It resolves the apparent tension and organises the cross-section; it is not a new estimate of fair value.

### A.5 The house map: rules dropped and a merge withheld

Two mapping rules were dropped after checking the series each registrant actually files. Ivy Funds files "Delaware Ivy" series and so belongs to Macquarie, not Invesco. The trusts named "Variable Insurance Products Fund" file VIP portfolios and so belong to Fidelity rather than standing alone. One merge is withheld on purpose: Franklin Templeton bought Putnam in 2024, and a static rule would backdate the purchase over four years of filings. For the acquisitions the map does merge, the same question was measured: the pre-acquisition exposure of Legg Mason, Eaton Vance and the Ivy trusts together is 0.13% of the value in the reported cells.

## Appendix B. Robustness

Table B.1 lists each result, the stress test it was put through, and what came back. The code and its output are released (`src/robustness.py` → `data/robustness_summary.csv`).

**The ten named cells (§4.3).** The 24% median spread over the ten names with at least five funds does not depend on the unit-outlier band. It is 23.7% for every K∈[2,5], which is the median once the band removes Discord's pair of BlackRock marks at about ten times the fund cluster, the only 10:1 unit-convention artefact among the names that enter the median. It does not depend on the fund-count threshold either, since no name sits near the cut. Collapsing each house to one mark, so that a house filing many funds cannot widen the spread by count alone, leaves the disagreement in place: Anthropic 39% across 3 houses, Gusto 32% across 3, Databricks 15% across 6.

A one-way variance decomposition of the log marks puts a number on the house pattern that §4.3 describes. Among the names with material disagreement (Anthropic, Revolut, Gusto, Discord, Databricks, Canva), the share of variance between houses is η²≈1.00: almost all of the cross-fund variance lies between houses and none within them. Funds of one house file the identical mark, to the cent, in 89% of house-cells, and the one exception is Fidelity's Anthropic complex at 3%. The number of independent views is the number of houses, not of funds.

The Level-1 placebo of §2.3 shows that this is discretion in private valuation, not a reporting or units artefact: the same two houses mark the five verified shared public securities to the cent (cross-house spread 0.00%, `data/level1_placebo.csv`). Public marks are pinned to an observable closing price, and private marks are not.

**Out of panel.** A five-name expansion probe (xAI, Perplexity, Cohere, Groq, Fanatics; `data/nport_expansion_probe.csv`) found exactly one name that clears the bar of five same-date funds: Fanatics, with 7 same-date funds across three houses. It reproduces §4.3's anatomy at once. On the common report date, 30 April 2026, the cross-house spread of 75% runs from Franklin's $50.00 through Neuberger Berman's $73.85 to Fidelity's $87.33, and both multi-fund houses are internally identical to the cent. All of these are common equity, although the issuer label varies between holders (Fanatics Inc against Fanatics Holdings Class A), which is §4.3's like-for-like caveat, disclosed rather than assumed away.

Fanatics also exposes a limit of the harvest. `src/nport_fetch.py` stops after eighteen filings per company, and on the same date the panel files hold only two Franklin funds for it, one house and no spread at all, while the deeper sweep reached five more filers and the 75% gap. A harvest that stops early can miss the houses that disagree, but it cannot put a disagreement into a filing that does not contain one, so every cross-fund spread reported here is a lower bound on what a complete sweep of N-PORT would show.

**Staleness on the tracer panel (§4.3).** The simplest alternative is that one house has failed to refresh an old mark. The quarterly panel rejects it in three ways (`src/mark_staleness.py` → `data/mark_staleness.csv`; each house collapsed to its median mark per company and quarter, cells guarded at 4×).

First, no house is dormant. A house's mark moves in 79% of adjacent-quarter pairs, from 58% at the least active (T. Rowe Price) to 92% at the most active (ARK), and the median move is 12%.

Second, disagreement survives conditioning on freshness. The comparison runs on the 105 of 116 multi-house cells where freshness can be judged at all, meaning that every house present also filed in the quarter before. The other eleven open a house's series and carry no evidence either way, so scoring them as stale would be an error. In the 67 cells where every house moved its mark, so that no mark can be stale, the median cross-house spread is 12.1%, against 6.7% in the 38 cells where at least one house stood pat. (This figure is the tracer panel's own statistic; it happens to round like the population median of §5.1 and is a different number.) A one-sided test that the freshly remarked cells are tighter returns p=0.97.

Third, the least frequent remarker is not the outlier. Remark frequency and mean deviation from the cross-house median are unrelated across houses (Spearman ρ=0.14, p=0.76): T. Rowe Price deviates by +2.4% at a remark rate of 0.58, and Baron by −4.9% at 0.89. Staleness is real in these data, and §7 finds that the headline suffers from it. It is not what makes two houses carry the same share at different prices.

Neither threshold drives the result. Varying what counts as a mark that moved, from 0.1% to 5%, keeps the freshly remarked median between 12.0% and 12.3%, against 6.6–8.2% for the rest, and the class guard can be tightened to 2× or dropped without moving either figure by a fifth of a point. The cells are not independent (105 company-quarters over seven companies), so the pooled p-value overstates the evidence and is quoted only to show which way the comparison runs. Collapsed to one comparison per company the result holds: the freshly remarked cells are wider in five of the six companies with cells of both kinds, all but Epic Games.

One rival reading survives, and this test says nothing about it. Conditioning on every house having moved selects quarters that carry news, so staleness is ruled out without showing that the disagreement is a permanent difference in policy rather than one that widens during a repricing and closes in between. This panel cannot separate the two, because only five judgeable cells have no house moving a mark. Of these, three sit at a 0% spread, which is §4.3's herding regime rather than recovered agreement, and Epic Games and SpaceX sit near 14% (SpaceX enters here because these spreads are between house medians). §6.2 answers the question on the 760 such cells the full N-PORT population supplies: two thirds are not unanimous, and a quarter differ by more than 24%.

Two smaller qualifications go with it. The pooled ordering runs against staleness rather than merely failing to support it, because houses remark most actively when they disagree most (the 2022 repricing supplies fourteen of the fresh cells, at a 39% median spread); that ordering does not hold year by year, so only the negative result is claimed. And this quarterly cross-house statistic is more compressed than §4.3's cross-fund 24% on a single modal date, so only the comparison within this panel is used.

**The IPO-exit bridge (§7).** The result that the fund mark beats the headline does not depend on the one-for-one conversion of preferred into common that the bridge assumes. Across conversion ratios from 0.8 to 1.2, the fund mark is the less wrong signal in 4 to 6 of the seven fund-held exits, and its median absolute error (11–21%) stays far below the headline's 48% throughout. The headline's errors (+294% for Instacart, +116% for Chime) are too large for any plausible bridge adjustment to overturn. What the comparison cannot carry is the count: on seven exits an exact sign test on the five wins returns p=0.23, so "five of seven" is an illustration and not evidence of a population regularity, as §7 states.

The content is in the magnitudes, which pass a paired test. The fund mark's absolute error is smaller exit by exit at p=0.078 (Wilcoxon), its median error is 11% against the headline's 48%, and three of the five wins are by a factor of two or more (Chime 136×, Instacart 35×, Reddit 12×). Restricted to the five exits with a clean quality flag, dropping ServiceTitan's structured down round and Circle's contested headline, the mark still wins four of five.

**Table B.1.** Every result held up under its stress test; only the IPO count is too small to be evidence. Each headline result, its stress test and the outcome.

| Result | Headline | Stress test | Outcome |
| --- | --- | --- | --- |
| §4.3 cross-fund spread | median 24% (10 names) | unit-outlier band K∈[2,5] · fund threshold | 23.7% (invariant) |
| §4.3 house clustering | "clusters by house" | between-house variance share · within-house spread | η²≈1.00 · within-house spread = 0 in 89% of cells |
| §4.3 dispersion is private-specific | 24% on private (Level-3) marks | Level-1 placebo: 2 houses' shared *public* holdings | cross-house spread 0.00% (5 names, same date) |
| §4.3 spread is not staleness | houses disagree, not lag | remark rate · spread where *every* house just remarked · rate vs deviation · both thresholds swept · per-company collapse | 79% of quarters (58% to 92% by house) · 12.1% (n=67) vs 6.7% (n=38), one-sided p=0.97 · ρ=0.14, p=0.76 · fresh median 12.0–12.3% throughout · wider in 5 of 6 companies |
| §7 IPO leg, what the count carries | fund mark least wrong 5 of 7 | exact sign test · paired Wilcoxon on \|errors\| · clean-flag subset | count p=0.23 (illustrative only) · p=0.078 · 4 of 5 |

## Appendix C. How the population is built and reconciled with the anchor paper

This appendix holds what the body compresses to a sentence: the reconciliation with the deal-terms literature, how each cluster's label was reached, what the published cells look like with the harvest cap lifted, the predictions that could refute the framework, how much of the headline a different security explains, and the ten names followed through time.

### C.1 Reconciling with Gornall–Strebulaev

Section 1.1 states the anchor result: the reported post-money valuation averages 48% above the option-adjusted fair value of the cap table, and common shares are 56% overvalued. I do not re-derive that number and could not, because it would need each company's per-round legal terms, which public filings do not carry. What it can do is show why the two results do not conflict and where they meet.

The objects differ. Gornall and Strebulaev compare the headline with a contingent-claims fair value of the whole cap table, valuing each share class separately because the newest preferred carries protections that common and junior shares lack: IPO-return guarantees, vetoes over down-round IPOs, liquidation seniority. This paper compares fund houses with each other, on one security at one date, and never with a fair value of its own. One measures a level against a model. The other measures dispersion against nothing.

Yet the marks are the same kind of object as their answer, which is what makes the two comparable at all. A mutual fund reports a Level-3 mark as fair value under ASC 820. So §5 measures how far apart professional valuers land when each attempts, under one accounting standard and on the same security, the adjustment that Gornall and Strebulaev make analytically from contract terms. Their result is that the headline is wrong by an average amount. Mine is that the professionals who correct it do not agree by how much, and that where they disagree is a stable property of particular companies.

The two meet in the cross-section, and the meeting is a prediction rather than a coincidence. The Gornall–Strebulaev haircut is largest where the protections are deepest in the money, on at-risk and repriced names whose equity sits near the preference stack, and it shrinks toward zero for winners so far above the stack that every class converges on one value per share. Those are exactly the companies on which the marks behave differently here. Houses herd to the round on fresh, believed winners and disagree by tens of per cent on stale, repriced and contested names (§4.3), and the exits reject the headline hardest on the same cohort (§7). The contract wedge and the dispersion of practitioners' marks locate the headline's untrustworthiness in the same companies, by two routes that share no data.

This is a reconciliation, not a re-derivation: nothing here re-estimates the 48%.

### C.2 How each cluster's label was reached

Section 5.5 reports what kind of company each mark is on. This subsection gives the rule behind the labels, its measured accuracy, the direction of its errors, and two readings of Table 8 that the table does not support.

Every cluster carries a label and, beside it, the basis for that label, because the labels are not all equally reliable. 118 clusters covering 93.6% of the booked value are verified one at a time against the filings and the public record, with a line of reasoning recorded for each in the replication package. Every cluster above $500M is among them except one: a $1.15B position filed as "AH PARENT, INC. SER A PREFERRED SHARES PP", whose filings name no operating company and which no public source resolves, so it is left unresolved rather than labelled by rule. A further 390 clusters, holding 3.7%, are labelled by rule. The remaining 147, holding 2.5%, are left `unclassified` rather than guessed at. Table 8 counts 148 because one more cluster has no label for a different reason: the resolver could not settle its identity (Appendix A.2).

No threshold separates the kinds of company, and searching for one would have produced false precision. The sharpest signal is the filer's own security title, since a private placement is written as one; among clusters whose kind is known, that token separates venture from non-venture companies with an AUC of 0.96. It is still not a boundary. Across the 656 clusters its frequency runs continuously upward from a seventh of a per cent, and the only real discontinuity lies between clusters that no filer ever marked that way and clusters where at least one did.

The rule therefore fires only at the two ends, on clusters that no filer ever wrote as a private placement or flagged as restricted and on clusters whose rows mostly carry both marks, and it abstains in between. Its value is measured: on the clusters that also carry a verified label, the rule declines to call 32 of them and fires on 84, of which it gets 94% right; the other two of the 118 carry no security title for it to read. Its errors run one way, and the tail inherits them. Sequa and Windstream II are private companies out of a buyout and a reorganisation that no filer ever called a private placement, and the rule reads them as listed.

The listed row invites a reading it does not support, namely that a Level-3 mark predicts disagreement whatever the company is. Split by whether the marks ever move, the row comes apart. Where every house has frozen its number (135 clusters, the suspensions and halts for which Level 3 is exactly right), the median is 0.7% and 7.4% sit above 24%. The dispersion lives in the 213 clusters still being repriced, at 32.8%, and those are residue: reorganisation stubs, contra positions and delisted microcaps carrying a median $3.7M per cell against $66.6M for a venture cell. The listed bucket is what is left after the paper's subject is removed, not a second finding about it.

Scored inside the venture population rather than the full panel, the ten names of §4.3 land at the 63rd percentile on house medians and the 63rd on fund spreads, against the 60th on both in the full panel. The conclusion is unchanged, and the percentile now comes from the population it belongs to.

### C.3 Every published cell reappears, wider

The §4.3 harvest stopped after eighteen filings per name, so its fund counts were a lower bound of unknown tightness. Recomputing all ten published cells from the bulk data, with the hand-labelled rows and the population resolved jointly so that both sit on one identity, returns nine cells with *more* funds and one exact match; none is narrower and none is missing. The median cell goes from 8 funds to 15.5 (`src/reconcile_versions.py` → `data/version_reconciliation.csv`). The cap was real and one-directional: the ten anatomies in Table 4 understate coverage and never overstate it.

The cap also understates the spread, by enough to state as a number. The published cells carry a median spread of 23.5%, the 24% that §4.3 quotes. Recomputed on the complete filing set with the same 4× guard, the same cells give 34.7%. The guard removes one of the ten, Discord, because the bulk data put BlackRock's mark ten times above Fidelity's, so the comparison runs over nine of the ten. The published figure is therefore a floor, about eleven points below the figure on complete filings.

Two checks came before that number. The first is whether it comes from choosing different cells. It does not, because nothing is re-chosen: the comparison holds the company, the date, the house unit and the guard fixed, and lifts only the cap.

That constraint matters. A first attempt re-selected each company's date by the modal-report-date rule that Table 4 uses, and over seven years of filings the rule lands on a December 2024 Epic Games cell where one filer reports $1.00 against everyone else's $640–680, and on a March 2026 Anthropic cell where six houses agree to the cent, for a median of 3.6%. A name's spread depends far more on where it sits in a repricing than on how many filings are read: Anthropic is unanimous on 31 March and spans 49.8% on 30 April, when some houses had taken the new round and others had not. Re-selecting dates is a different measurement, not a better one, and it is not made here.

The second check is whether the recovered funds simply hold different share classes. Where filers name the round, this can be tested cell by cell rather than bounded in aggregate. A named series is shared by two or more houses in seven of the nine cells, and restricting each to its best-populated shared series leaves the spread unchanged in three of them: Gusto at 32.3%, Anduril at 9.9%, OpenAI at 0.0%. The other four narrow, one almost completely: Stripe 73.1% to 1.4%, Anthropic 49.8% to 28.7%, Canva 39.3% to 33.3%, Databricks 17.1% to 13.0%. The median across the nine under that restriction is 28.7% against 34.7% unrestricted, so share classes account for about six points here, not for the gap between 23.5% and 34.7%. Coverage per cell across the nine goes from 8 to 16 funds (`src/fund_marks_bulk.py` → `data/fund_marks_bulk.csv`).

The complete-filing figure does not replace the median of §4.3, whose value is an anatomy in which every mark was read against its filing. A reader should still know on which side of that number the missing filings sit, and by how much.

**One recovered cell in full.** Every mundane reading of a wide spread is available somewhere in these data, and none is available in this cell. On 31 March 2026, four fund houses name Stripe's Series I preferred in the security titles of their own filings, across nine funds. Morgan Stanley's two Growth Portfolio funds carry it at $36.90; Fidelity's five funds carry it at $63.00, Capital Group at $63.00 and Franklin Templeton at $63.87. That is a 73.1% spread on an explicitly identical series on one date. The four houses write the issuer differently ("STRIPE INC", "STRIPE LLC", "Stripe, Inc."), but all four rows carry the same LEI, `549300CLHGIPTCYHQ143`, so the naming is house style and not four different entities.

It is not a share class, because the class is named and the same. It is not a unit convention: dividing the booked value by the share balance returns the filed price per share for all nine rows. Nor is it one house that failed to reprice, although settling that took the whole series.

Morgan Stanley reports this holding quarterly and has done so on twelve dates since mid-2023. It tracked the others through 2024, within a few per cent either side of their median. It has sat below them on each of the last five quarters, by 27%, 20%, 16%, 19% and now 71%, while its own mark rose at every one of those dates, from $27.90 to $36.90. (The 71% is measured against the other houses' median; the cell's 73.1% is its highest mark over its lowest.) Between the last two dates it moved 5.9% while the others moved 52.1%, and $36.90 was never the consensus: the other houses went from $41.42 to $63.00 without passing through it.

So this is not a stale copy of anyone's number. It is one house's own valuation, revised on its own schedule and running below a consensus it used to sit inside: a standing difference that a sharp repricing widened rather than created. Two professional houses holding the same security on the same day disagree by seventy per cent about its worth. The eighteen-filing cap is why this cell reads as a 1% spread in Table 4 (`src/reconcile_versions.py`).

### C.4 Four testable predictions

Each prediction below can be settled with the public-filing pipeline built here as more companies exit, and none needs private data.

**P1. Dispersion predicts returns.** By analogy with differences of opinion among stock analysts (Diether, Malloy and Scherbina 2002), names with high dispersion across fund marks (§4.3) should underperform low-dispersion names at and after exit.

**P2. The fund mark's edge grows with staleness.** The accuracy advantage of the last N-PORT mark over the headline (§7) should rise with the age of the headline. Section 7 establishes only the binary version, stale against fresh; the continuous test needs more exits.

**P3. Wide cells resolve against the higher mark.** Where two houses hold one named series more than 24% apart (§3.3) and the company later prints a price, the realised value should land nearer the lower mark more often than nearer the higher, because §7 finds the marks least wrong where the headline is stale, and the higher mark tends to track the headline.

**P4. Dispersion collapses before a listing.** Disagreement across funds on a name (§4.3) should shrink as the name nears an exit, with the marks converging on the clearing price. This is the one prediction already run, as a pre-test on the pre-2023 listings, and it does not hold there (§10.1). The 2023–26 listings are the registered test bed and do not yet form a large enough panel.

Together they turn a description of disagreement into claims that data can refute.

### C.5 How much is a different security

Section 3.3 states the result. This subsection gives the construction, the decomposition and the selection check.

Two houses can differ about one security, or they can hold two securities of one company. An issuer identifier cannot tell these apart, and the difference matters more than any robustness check in this paper: the first is a fact about valuation, the second a fact about portfolios. The 32.5% of rows that name a series in the security title separate the two wherever two houses name the same one.

**Table C.1.** Holding the security fixed removes the median gap but not the tail. The headline decomposed by whether the security is verifiable. Rows 1–4 partition the panel's guarded cells by what their filings name, and rows 5–7 hold the security fixed and are computed at company × date × series with two or more houses, the 4× class guard re-applied inside the group.

| | groups | cells | companies | median spread | above 24% |
| --- | --- | --- | --- | --- | --- |
| all guarded cells | — | 4,271 | 656 | 12.13% | 40.2% |
| no filing names a letter | — | 1,941 | 488 | 16.42% | 43.8% |
| one letter, named by only some filings | — | 590 | 92 | 15.34% | 42.4% |
| every filing names the same letter | — | 366 | 58 | 0.00% | 14.8% |
| two or more letters named | — | 1,374 | 107 | 12.90% | 40.8% |
| **security fixed: one named series, 2+ houses** | **2,717** | **1,758** | **137** | **0.74%** | **22.0%** |
| the same 1,758 cells, series ignored | — | 1,758 | 137 | 8.45% | 35.4% |

Three readings follow, and the first constrains the other two.

**The test works where disagreement is smallest.** The cells no filing describes are the widest group in the table, at 16.42%, and the most numerous, at 1,941 of 4,271. The cells the test can reach run at 8.45% before any series is fixed, against 12.13% for the panel. Composition cannot be measured at all on the most disputed part of the population, and every figure below describes its calmer part. The direction of that ignorance is known even though its content is not: the cells the test cannot reach are wider than the ones it can, so what goes unmeasured is more contested than what is measured. The decomposition therefore does not apportion the headline; it apportions the half of the headline that admits the question.

**Within that half, the median is composition and the tail is not.** Holding the series fixed takes the median from 8.45% to 0.74%, while the share above 24% falls only from 35.4% to 22.0%. Two houses that verifiably hold the same paper typically file the same number, which is what the N-CSR harvest of §2.2 finds by hand, here reproduced at population scale from a different source. But in 597 groups on 68 companies the series is named and shared and the houses are still more than 24% apart, and the five most frequent names account for only 29% of them, so the tail is not one company's artefact either.

**The count is immune to the composition objection.** A conditional median on a selected subset can always be argued about. A count cannot be explained away by composition, because composition is what has been held fixed: in 597 cases two houses named the same series and disagreed by more than 24% about it. That is this appendix's contribution, and it is why §1 gives the tail as a count, with the conditional median beside it as the composition result.

The test has two limits. A shared letter is not a shared lot, because two houses can enter one series at closings months apart. And the test cannot reach the 1,941 unnamed cells, which are the next thing worth measuring and the one place where a real answer would change the headline rather than qualify it. Appendix F.6 records two earlier versions of this test and why each was wrong.

### C.6 The ten names beyond the table

Section 4.3 prints the anatomy, and Appendix C.3 recomputes every cell without the harvest cap. Three further readings belong here.

First, §4.3 infers valuation policy rather than private information from dispersion on one date, and one name lets the inference be watched through time. Morgan Stanley has reported Stripe on twelve dates since mid-2023. It tracked the field on six of them and has run below it on every date since March 2025 while still raising its own mark: between the last two quarters the field moved 52.1% and Morgan Stanley moved 5.9%. Its number was never the consensus at any earlier date, so this is a valuation committee declining a repricing, not a lag (Appendix C.3 gives the cell and the series).

Second, the level of the median depends on the sample even where the shape does not. Going from the original eight broadly held names to ten roughly doubles it, from 13% to 24%, because both names that newly clear the bar of five funds, Revolut and Gusto, sit in the high-disagreement group. The bimodality survives the change of sample; the level does not. The reading that a house is sitting on an old mark rather than disagreeing is tested in Appendix B and fails: restricting to quarters in which every house refreshed its mark leaves the spread wider.

Third, the count of houses still overstates the count of opinions, because many holders are variable-insurance or sub-advised sleeves that copy their sub-adviser's mark to the cent (Appendix D: twenty-two sub-advised funds across five variable-insurance trusts, all at one house's number). Even a widely held name typically has two or three independent valuations behind it. This reproduces, out of sample and on public-domain data, the finding of Chernenko, Lerner and Zeng (2021) and Kwon, Lowry and Qian (2020) that funds value the same private company differently (`figures/fund_marks_dispersion.png`).

Two names are excluded from the per-share comparison because their holders do not hold the same thing: SpaceX differs by share class and ByteDance by legal entity. Appendix A.2 gives both.

## Appendix D. The exits, in full

Section 7 states the finding and its weight. This appendix gives the table, the harvest by house, the robustness of the conversion bridge, and the qualification each named exit carries.

**Table D.1.** The last fund mark was closer to the IPO than the last private round in five of the seven fund-held listings. IPO-exit validation, 2023–26 listings: the headline (last private round) and the last pre-IPO N-PORT fund mark scored against the realised IPO valuation (error = signal/IPO − 1).

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

Klarna is the one listing with a headline but no broad fund mark, so the fund-mark column holds exactly the seven fund-held exits that §7 counts. Klarna's interim signal is a 2022 down round at $6.7B, which overcorrected to −56% against the $15.1B listing: a repriced round is not infallible either, only far less wrong than a stale headline.

**The headline's sign depends on demand.** Against the IPO, the headline's error is not a clean function of when the round happened. The four down-round listings from the 2021 vintage overshot the IPO by a median of +160%, so for them the headline was a ceiling. But the 2021 cohort also holds Klaviyo, fairly priced at +3%, and Figma, stale but bid up, at −48%, and together they span the whole range of signs. Nor are the floor cases simply the later vintages. Among the 2025–26 listings, repriced consumer fintech (Chime +116%, Klarna +205%) still overshot, while a compounder (Figma) and a momentum name (SpaceX/xAI at −29%, after Musk's February 2026 merger of SpaceX and xAI at a combined $1.25T) listed above their last round, and CoreWeave listed flat. The headline is a ceiling for repriced names and a floor for names in demand.

Three headlines need a note. (†) Figma's headline is its last primary round, the 2021 Series E at $10B. The $20B Adobe figure was an acquisition agreement, terminated in 2023, and the 2024 $12.5B was a tender offer; with no primary round after 2021, the frozen headline is as stale as a headline gets, which is why it sat 48% below the IPO. (‡) ServiceTitan's headline is its November 2022 Series H, $7.6B at $84.57 a share, a structured down round with a compounding IPO ratchet, already repriced from the 2021 peak of $9.5B, so it overshot the $6.3B IPO by only +21%. (§) Circle's headline is its April 2022 Series F, $7.65B led by BlackRock and Fidelity, and not the $9B Concord SPAC renegotiation, which was terminated in December 2022 and is no more a clean round than Figma's Adobe figure.

**Where funds held the company, the fund mark was usually closer.** Across the seven exits where mutual funds held the company before the IPO, the last N-PORT mark was the less wrong signal in five, and for the stale-headline names by an order of magnitude. Instacart's last mark ($32.50 a share, four T. Rowe Price funds in 2023Q2 and American Funds a month before listing) implied about $10.7B against the $9.9B IPO: +8% against the headline's +294% (35× closer). Chime's ($26.77, four Alger funds six weeks before the June 2025 listing) landed within about 1% of the $27 IPO price, against +116% for the stale 2021 headline. Reddit's ($32.37, three Fidelity funds, January 2024) implied about $6.1B against $6.4B: −5% against +56% (12× closer). ServiceTitan's ($78.85, four T. Rowe Price funds, 2024Q3) implied about $7.0B, +11%, modestly less wrong than its already repriced +21% headline. Even Figma's floor case fits: with the headline 48% below the IPO, the last fund mark ($23.73, two Fidelity funds) was −28%, still less wrong than the stale headline. Across the seven fund-held exits, the median absolute error of the last fund mark is 11%, against 48% for the headline.

**The two exceptions.** The fund mark does not always win, and the exceptions show why. In the only two exits whose last private round was recent and fairly priced, so that the headline was not stale, the headline beat the fund mark. Klaviyo, a profitable marketing-software company, listed within 3% of its 2021 Series D ($9.5B, against a $9.2B IPO), so the headline's +3% beat ClearBridge's marked-up +15%. Circle's last clean round, the 2022 Series F at $7.65B, put the headline at +11%, closer than Fidelity's conservative −25% mark, which undershot a crypto listing that then rose 168% on its first day.

Every IPO valuation here is on one basis, the offer price times fully diluted shares, recorded row by row in `data/ipo_validation.csv`, and one of the two exceptions depends on that choice. Both signals are scored against the same denominator, so a change of basis moves them together and cannot reorder errors of the same sign: ServiceTitan's verdict holds for any basis within ±15%, and Klaviyo's holds until +8.9%. Circle's two errors have opposite signs (+11% against −25%), and a listing valued about 10% below the offer-price figure would hand that exit to the fund mark. The reading is therefore firm on Klaviyo and provisional on Circle.

This is what staleness predicts. The fund mark's edge over the headline is the absence of staleness, not foresight. The same N-PORT marks that disagree in the cross-section (§4.3) carry much better exit information than the number the press kept quoting, but only when that number has frozen at a years-old round, and the edge vanishes or reverses when the headline is itself recent and fairly priced. Klarna shows the same for interim signals: its 2022 down round overcorrected to −56% against an IPO valued at about $15.1B fully diluted, on the same basis as the other exits. Interim signals are not infallible, only far less wrong where the headline is stale (`figures/ipo_validation.png`).

**By house.** A complete per-series harvest of every disclosing fund for these exits (`src/family_forecast.py` → `data/ipo_premarks_byfund.csv`) adds two facts. The harvest sweeps every sister series, so its counts exceed the named source funds of Table D.1: twenty-two T. Rowe series file Instacart's $32.50, and twenty-two Fidelity series Reddit's $32.37. First, no house emerges as a systematically better forecaster, since each scores only one to four exits, too few to rank. The one directional regularity is Fidelity's conservatism: its last pre-IPO mark undershot in all three of its clean fund-mark exits (Reddit −5%, Circle −25%, Figma −28%), the signature of a cautious house policy rather than of private information.

Second, the mirroring of §4.3 survives to the listing: twenty-two sub-advised funds across five variable-insurance trusts of four insurers (Lincoln, Voya, Brighthouse and MassMutual, the last through two trusts) carried Instacart into its IPO at T. Rowe Price's identical $32.50, and the same platforms mirror T. Rowe's ServiceTitan mark to the cent, while other sleeve trusts carried Instacart's higher share-class levels ($37.18, $41.62). A broad-looking pre-IPO holder base again collapses to two or three independent views, and §4.3's share-class caveat survives to the exit: the Instacart range of $32.50 to $41.62 mixes house policy with class seniority. The $30 listing sat closest to the most widely carried level, which was one house's view copied many times rather than many independent views.

## Appendix E. The four measurements in full

Section 9 states what each measurement recovers, what it is calibrated against and how well it does. This appendix gives the design of each, the corrections that shaped it, what it cannot see, and one error in the house map that the fourth measurement found.

### E.1 Listing dates

A test of what happens as a company approaches a listing needs a listing date for each name, and this repository does not take dates from the press. EDGAR has them: a company registering a class of securities on an exchange files Form 8-A12B or, if it reached the market through a shell, a successor-issuer Form 8-K12B. `src/listing_dates.py` asks EDGAR for each name's own filing and dates 21 of the 23 companies whose classification records a listing or a merger.

Each date is checked against something the panel already knows: the last report date on which the company appears as a private Level-3 holding. Of the 21, eighteen land within a quarter of it, the widest at 82 days. The next closest is 258 days, and the three names beyond the cut are companies whose funds stopped holding them long before they listed. The cut therefore sits in a gap in the observed distribution, between 82 and 258 days, and not at a round number. The check earned its place: it caught a CIK entered from memory that belonged to a different company.

*What it cannot see.* A holding promoted out of Level 3 is invisible by construction, because the panel keeps only Level-3 rows and a promoted holding simply stops appearing. What is visible is the opposite case, a mark still filed at Level 3 after the shares began trading, and there are 57 of those across ten names. Of the 57, 43 fall within 180 days, the customary lock-up, during which the shares cannot be sold and ASC 820 prices that restriction rather than ignoring it. Nine holders carrying Palantir at Level 3 nine days after it began trading is what the standard asks for, not a delay. The three names that run past the lock-up are residual stubs: the largest late mark is $260,773, and Outset Medical's is $10,314 on a company that listed four years earlier. Quoting "1,603 days" without the dollar figure beside it would turn a residual position into a finding.

### E.2 Share splits

A share count is a count. When a company splits *k* for one, a holder that did not trade files exactly *k* times as many shares at its next report date, so the ratio of balances is *k* to integer precision. The price side is not exact and must not be treated as exact, because the same filing usually carries a fresh mark: the price falls by roughly 1/*k*, not exactly 1/*k*. Baron restated SpaceX at $57.41 in the same month that Fidelity restated it at $56.00, both from a tenfold share count.

The balance is therefore held to half a per cent, and the price side is asked only to rule out the alternative: a purchase multiplies balance and value together, while a split multiplies the balance and leaves the value alone. The natural first design, requiring the price ratio to equal 1/*k* within a few per cent, drops Baron from the SpaceX event and roughly halves the sample. `src/split_events.py` finds 601 candidate fund-dates on 228 companies and confirms 29 events by two or more houses, 26 of them at a ratio companies actually split at. The largest is the Databricks three-for-one of autumn 2022, filed by fourteen independent houses within two months.

*Not every integer is a split ratio.* The three events outside the canonical set are Carbon Health at *k*=99, Pine Private at *k*=127 and Iron Horse II at *k*=9: arithmetic that lands near an integer, not a corporate action. Delhivery at *k*=100 is inside the set but flagged in the output, because a hundred-for-one is a redenomination in all but name. Five of the 29 events sit on one date, 31 December 2019, all at *k*=2 with a zero span. Five simultaneous two-for-one splits on the panel's second report date look like a change of filing convention, not five corporate actions.

*What the splits show beyond their own use.* §4.2 finds that within a house the mark is one number. The splits show that houses are not one number about the share count. They differ not only in what they think a share is worth but also in when they recognise that the share has been redefined, and the second difference sits in a field that nobody reads for disagreement.

*What they do not show.* The idea that motivated this measurement, that the 4× class guard of §5 mostly absorbs split desynchronisation, does not hold. The guard drops 1,945 cells, and 22 of them (1.1%) sit inside a restatement window. For companies with a confirmed split, 21% of the 104 cells dropped are inside a window: material for those names, immaterial for the panel.

### E.3 Round dates

Three sources for round dates were tried, and all three failed. Form D misses the large rounds, which are sold under Section 4(a)(2) and leave no Regulation D trace. N-CSR gives an acquisition date, but that is the fund's entry, not the round. The press gives dates this repository will not cite. The fourth source was already on disk. Filers name the series in the security title, as "SER H PC PP" or "Class B PP", and 32.5% of population rows carry a letter, so the first report date on which a new letter appears anywhere in the population bounds the round from above.

**Table E.1.** The date a new series letter first appears in N-PORT falls within five weeks of the N-CSR acquisition date in fourteen of fifteen pairs. Calibration of the series-letter round date against the earliest N-CSR acquisition date for the same company and series: two document types, one structured and already downloaded, the other parsed out of an HTML schedule of investments.

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

Table E.1 is that calibration. Fourteen of fifteen dated pairs land inside 35 days, and the median gap is 16; the worst inside the tolerance is 33 and the nearest outside it is 59. The tolerance sits in that gap and is read off it.

Two rules follow from the calibration rather than preceding it. The first is two houses. Every pair that misses by months rests on a single house: Discord Series G at +670 days, SpaceX B at +570, OpenAI A-2 at +426 and A-3 at +259, Stripe G at +62, and Databricks B, C and E at +49. A letter that one fund reports is that fund's holding; a letter that several houses report in the same quarter is a round. The second is censoring. A series first seen on the panel's own first date is censored rather than dated: SpaceX Series A first appears on 30 September 2019 against an N-CSR entry of 8 June 2022, which is a series that existed before the window, not a 982-day error.

**Table E.2.** Requiring houses to agree on a price dates rounds worse than requiring them to name the series. The count rule against the price-coordination rule, implemented as "the first month with two or more houses whose median prices lie within 2% of each other". The step is one observation per anchor date, as in Tables 10 and 12 of §8, and both columns are computed by the pipeline.

| | count rule | coordination rule |
| --- | --- | --- |
| pairs dated | 434 | 406 (333 uncensored) |
| non-first anchors | 75 | 56 |
| calibration pairs inside 35 days | 14 of 15 | 11 of 15 |
| median absolute gap to N-CSR | 16 days | 20 days |
| step on the non-first set | −1.94, p=0.0008 | −0.06, p=0.022 |

Table E.2 shows what the price-coordination rule does, and §8.5 gives the short version. It fixes one case and breaks four. Anthropic Series G moves from −59 days to 0, which is what the rule was built to do, but Databricks J moves to +45, Anthropic G-1 to +63, Databricks F to +70 and Databricks D to +80, all of which were inside 35 days under the count rule. The step is the part worth reading twice: the size moves with the anchor, from −1.94 points to −0.06, while the sign survives at p=0.022, which is what a misplaced anchor does to a size. This robustness is narrow and should be read narrowly. Both rules require two houses, so what varies is the criterion, naming the series against agreeing on a price, and not the two-house bar itself. That bar remains the one filter with no independent defence.

*Reach.* In all, 434 company-series pairs on 287 companies clear both rules, against ten companies with any N-CSR coverage at all. Ninety-seven companies carry two or more dated rounds and 24 carry three or more. The 97 are the pool from which the repetition test of §8.6 draws, not its sample: once anchors are restricted to later rounds and both bands must carry guarded cells, the test runs on 30 rounds on 12 companies. Calibrating on a small set is what lets the rule apply where no schedule was ever read.

*The sign of the error is not guaranteed.* One would expect a fund to report a series only after it exists, so that the N-PORT date falls at or after the round. Anthropic Series G breaks this: the series appears in N-PORT in January 2026 and its earliest N-CSR entry is 31 March 2026, a gap of −59 days on a pair with 37 funds across 3 houses, neither censored nor thin. The reason is structural. N-PORT covers every registered fund, while the N-CSR harvest covers ten names and whichever filers happen to schedule them, so an N-CSR date is one filer's purchase and can come later than the series' arrival in the filing system. Neither date is the round's close. What licenses the N-PORT date as a proxy is its agreement with the clean cases at monthly resolution, not an argument about which side the error falls on.

*What it cannot see.* Rounds that create no new class: extensions, SAFEs, secondaries, and any priced round that reuses an existing letter. Resolution is the reporting month, not the day. And a letter can appear because one fund bought an old series on the secondary market, which the two-house rule removes on average but not by construction.

### E.4 Acquisition dates and cost

N-PORT records neither what a holder paid nor when it bought. Regulation S-X requires both in the schedule of investments that accompanies the annual and semi-annual reports on Form N-CSR. `src/ncsr_acquisitions.py` queries EDGAR's full-text index for each of the ten §4.3 names together with the schedule's own column header, since `"Discord"` alone returns 1,491 filings, nearly all of them the English word, while `"Discord" "acquisition date"` returns 179. It then parses the schedule tables out of the returned documents. Both spellings of the header are required, because the index matches tokens and "dates" is not "date". The harvest is 767 schedule rows, 10 companies, 44 registrants, 429 lot-period-series, and 155 of the rows carry a share count and therefore an entry price per share.

The 429 lot-period-series are unrelated to the 434 dated company-series pairs of §9, despite the similar numbers: the round-date measurement counts pairs across 287 companies of the whole population, and this harvest counts lots inside ten companies' schedules. A prefilter that was not a superset of the harvest it replaced would silently cut the sample, so `validate_prefilter` asks EDGAR for the prefiltered accession set and looks for accessions in the committed extract that are missing from it. Across all ten companies it finds none. Lifting the cap on the number of filings changed what the source can support (Table E.3).

**Table E.3.** Lifting the forty-filing cap roughly quadrupled the harvest and made the cross-book comparison possible. What the N-CSR harvest reached at a cap of 40 filings and uncapped.

| | at a cap of 40 filings | uncapped |
| --- | --- | --- |
| schedule rows | 190 | 767 |
| registrants | 25 | 44 |
| rows with a share count | 29 | 155 |
| lot-period-series with 2+ independent books | 1 | 45 |

*What the source can and cannot carry.* Cost is the fund's entry and not always a round: ARK's Databricks lot of 23 September 2022 shows a markup of 1,226% because the position arrived in stock through the MosaicML acquisition, as a footnote in the filing explains.

Two parse failures were invisible at forty filings, and both would have shipped. One filer's document carries two table layouts, and a parser reading everything under the first header printed an Anthropic lot at −99.999818% where four other filers put it at +77.991332%. Another switches from dollars to thousands part-way through, so every cost came back a thousand times too small while the markup, a ratio inside a single row, survived. The fix reads each table under its own header. Re-run on the capped extract, it reproduces 104 of 105 company-document results exactly, the one difference being a term loan whose "cost" of 8.27 was an interest rate.

*An error in the house map, found from this side.* The first run of the cross-house comparison reported Canva held by "Capital Group" and by "EUPAC FUND" at markups agreeing to a thousandth of a point, which is what one house looks like, not two. EUPAC is the EuroPacific Growth Fund, and the house map matched the full name but not the abbreviation. The population panel carried 191 rows filed under the short name and, in nine cells, counted Capital Group as two houses. An unmapped registrant biases in one direction only, and this was that direction: one house looked like two, which inflates apparent disagreement. The error surfaced because a second document type, asked about the same houses, disagreed with the first.

## Appendix F. Measurement detail moved out of the body

This appendix holds passages that a reader checking the design needs and a reader following the argument does not. The first five subsections are text moved from the body, and the last collects corrections to earlier versions. Their numbers are registered exactly as in the body.

### F.1 Three arithmetic explanations of the step at the round

*The cell could get wider.* The spread is a maximum over a minimum of house medians, so it grows mechanically with the number of houses compared. If a round brought in new buyers, cells after it would be wider by composition, and part of the step would be an artefact of counting. The median number of houses per cell is 4.0 before the round against 4.0 after (Mann–Whitney p=0.60), and the month-by-month medians take only three distinct values across the whole nineteen-month window. The composition does not move.

*The round-month cell could be the new security agreeing with itself.* If a cell at month zero consisted only of funds that had just bought at the round price, they would agree because they had all paid the same, and nothing about valuation would follow. Across the 46 round-month cells, the newly priced series is a median 26% of the rows and the whole cell in none of them. The convergence runs over the company's whole position, not over the security that has just traded.

*A restatement could pass for agreement or for a gap.* A cell in which one house has restated a share split and another has not carries a spread equal to the split factor. Those windows are dated in Appendix E.2 and dropped. Keeping them moves the median step by a third of a point (§8.5), so dropping them disciplines the estimate without moving it.

### F.2 The three filters behind the NAV wedge

The median of §5 can absorb a handful of contaminated cells. The NAV wedge of Appendix G cannot, because its content lies entirely in the tail, and two of the three restrictions below were written after reading the largest rows of an earlier run rather than before.

**One price per fund per company, throughout.** The first run's largest wedge was JPMorgan on Claire's Stores: $881 a share against a $12.50 consensus. JPMorgan files two lines for Claire's in each fund, one at $10.00 and one at $1,765.66. Two prices under one issuer key are two instruments, and their value-weighted blend is not a price. The same defect produced a Baron position in SpaceX at $1,294 against a $527 consensus, worth 2,227 basis points of one fund's net assets; that fund's own two lines are $526.59 and $5,265.90, the ten-to-one unit convention for which §4.3 excludes SpaceX. Any fund whose own lines disagree by more than half a per cent is dropped, and this restriction is on in every row of Table G.1. It is the identification problem of §3.2, arriving where it does real damage.

The same guard applies a second time, to the position rather than the fund. A fund can file one internally consistent line and still use a different unit convention from every other holder. First Trust reports 2,145,462 Epic Games "shares" at $1.00 against a $637 consensus, which is a share count expressed in dollars; left in, it would contribute a wedge of 421,062 basis points on a $32m fund. Any position more than four times the consensus or less than a quarter of it is dropped, on the threshold of §4.3 and for the same reason.

**One series, which does not do what the tail suggested.** Restricting to the cells of §3.3 that never name two different letters removes 13,571 of 40,361 fund-positions and cuts the count above ten basis points from 976 to 620, but it takes only three per cent off the single largest wedge, from 460.0 to 444.4 basis points. The filter removes a third of the positions and a thirtieth of the extreme: it thins the body of the distribution and leaves its far end in place. It is not the tail filter, whatever one might expect.

**Venture-backed only.** The filing system carries buyout stubs, reorganisation equity and delisted microcaps at Level 3, and §5.5 separates them because only venture-backed companies are the subject here. This is the restriction that moves the tail: the largest wedge falls from 460.0 to 161.1 basis points. It removes Venture Global LNG, an energy company that carries the widest wedge in the unfiltered panel at every one of PIMCO's report dates, and a block of Russian listings frozen after 2022 that US funds still carry at Level 3: Nebius, Ozon, X5 Retail, T-Tekhnologii and Solidcore.

Cell membership, the class guard and the consensus are all rebuilt at the position unit rather than taken from §5, which builds cells on filing lines. Mixing the two units is what produced the Claire's row.

### F.3 What the measurements turned up on the way

Three of the four measurements produced a finding of their own, and each corrected some other part of the paper.

**Restatement is not simultaneous, so a one-month confirmation window is the wrong unit.** Across the 29 confirmed split events the median restatement span is 30 days and the longest is 92, and only 18 of 29 fit inside a single month. Requiring one month would discard eleven events and, worse, would score the desynchronisation as the absence of a split. §8.5 uses this quantity to explain why the price-coordination rule dates rounds worse than the count rule.

**Confirmation counts houses, never registrants.** Four T. Rowe Price series restating one name are one confirmation. At the median event, counting registrants multiplies the count by 1.7×, and on the Databricks three-for-one it gives 47 registrants against 14 houses. This is the correction of §4.1 arriving in a second measurement; it is the third metric in this project whose first version counted trusts.

**A cost per share is not comparable across filings, but a markup is.** ARK reports SpaceX acquired on 31 October 2023 at $92.89 a share against a $185.00 mark in one filing, and at $84.00 against $420.99 in another, because a split changes the basis. The markup is a ratio inside one row and immune to that. This is why every cross-filing comparison built on this source in §2.2 and §4.2 uses markups, and why the per-share figures of §2.1 are read off share counts inside single filings, where the basis is disclosed.

### F.4 The pre-registration argument in full

**Nothing in this paper is pre-registered, including the sector contrast.** I formed the demand-favoured split (AI, data and AI infrastructure, and defence, against the rest) from the 2021–26 funding cycle before computing the gaps. That sentence offers as much assurance as an unregistered claim can, which is none. The contrast has been cut from this paper along with the secondary-market leg it belonged to; the specification curve that priced it against all 2,032 alternative partitions is in the repository.

One of the registration's five predictions has been run on data that already exist, because the alternative is a hypothesis nobody has ever sized. P4 says that disagreement across houses collapses as a company approaches its listing. It needs a listing date for each name, and §9 builds those from each company's own exchange registration and checks them against the panel.

On the pre-2023 listings this leaves fifteen names with four qualifying report dates ahead of the listing, and P4 does not hold on them. Six narrow and seven widen, two are unchanged, and a one-sided signed-rank test on the per-name change returns p=0.43. Reading the whole window rather than its endpoints, through a per-name rank correlation of spread against date, gives the same verdict at p=0.84. Two earlier versions of the membership rule, kept runnable because their results were seen first, gave twelve names at p=0.58 and eighteen at p=0.38.

What that null is worth is a question about power, so the power is computed. Resampling the observed changes, this design detects a ten-point narrowing 0.43 of the time and needs about forty points to reach the conventional four in five. The textbook normal approximation with the same standard deviation gives 0.17, and it understates the rank test because a third of these names sit within a point of zero, where the test is most sensitive. In P4's own units the picture is worse: if every name's spread collapsed to nothing over its last four dates, this sample would return a significant result 0.73 of the time. A null on fifteen names therefore says the collapse is not large; it does not say there is none. It is also a pre-test, not the registered test. These names were examined while §5 was being written, so nothing here predates its data, and the registration reserves P4 for listings completed after it is filed (`src/p4_pretest.py`).

One detail of the first version was invisible until the dates were sourced. The window used each company's last four cells, and Palantir's last cell falls nine days after it began trading: a Level-3 mark on a security that already had a public price, carried there because reclassification lags the event. One cell in fifteen, on the name whose anchor was strongest, tested the wrong side of the hypothesis. The window now stops strictly before the listing date.

Every result in this paper is exploratory. Only a registration would change that, and one is drafted at `notes/registration.md` and not filed. Filing it before the panel is next extended would let the next version be judged on a hypothesis that predates its data. Until then, the compression at a round should be read as the paper's best-supported mechanism, not as a tested one.

### F.5 The ten names, one by one

Three things stand out, and the first is the shape rather than the level. Disagreement is large for stale, repriced or contested names (Discord's 2021 round, Epic's 2022 round, the Databricks and Anthropic cascade, the mid-2025 secondaries of Revolut and Gusto) and absent for names carrying a single fresh, well-publicised round: OpenAI's 13 funds all mark exactly $687.69, and Stripe and Anduril cluster within a few per cent. On the hottest names the houses herd to the last primary round, as a view that treats the headline as the benchmark would predict.

Second, what disagrees is the house, not the fund. (Here, as throughout, the house is the asset manager behind a fund, which §4.1 distinguishes from the legal trust a filing names; some dataset fields call it the family.) All five Alger funds mark Anthropic at $259.14, and ten Fidelity funds mark Revolut at exactly $1,495.97 while ARK Venture marks the same ordinary stock at $1,110. Identical marks inside a house and divergence across houses point to valuation policy rather than private information: a common procedure, possibly a common smoothing convention. The spread therefore measures differences in method, the private-market counterpart of the discretion that illiquid-asset funds exercise over reported marks (Getmansky, Lo and Makarov 2004; Jenkinson, Sousa and Stucke 2013; Brown, Gredil and Kaplan 2019).

Third, Zitzewitz (2003) supplies the motive. A stale NAV is an arbitrage target, and the fair-value regime whose Level-3 output N-PORT now discloses was written against exactly that. Because shares outstanding are common to every holder, a 39% spread in marks per share is a 39% spread in implied company value: in April 2026, Alger's books carry Anthropic 28% below Nuveen's and 22% below Fidelity's.

### F.6 What earlier versions got wrong

Eleven corrections to earlier versions, kept so that each can be checked against the version that made it. The first five concern the body, the last six the appendices.

**The common entry price of the Series J lot.** An earlier version rested this on both books printing a markup of exactly 0.0000 at 31 December 2024 and read that as proof of a common entry price. It proves nothing. A markup is value over cost, and a holder that marks a fresh position at what it paid prints zero whatever it paid, so two books entering the same round at two different prices would both print 0.0000. The year-end convergence on four cost bases with two disclosed share counts (§2.1) carries the argument.

**The house-level reading of the ten names.** An earlier version put the house-level median of the ten names at 12.6%. That figure came from the panel's catch-all bucket, which pooled seven distinct managers into one unit whose median sat between the extremes: the counting error of §4.1, running in the other direction. On the measure used throughout, the ten widely held names sit just above the middle of the distribution, where the registrant-level reading had put them in the top quarter.

**A size relationship, reported and then disowned.** Across four cuts of the panel, the median booked value per cell in contested companies (median spread above 24%) relative to that in quiet ones (median spread at most half a per cent) reads 0.59×, 0.36×, 0.28× and 0.66×: below one throughout, but moving by a factor of two as the panel fills. The first cut has fourteen companies and separates nothing (p=0.48); on the first twenty-four report dates the estimate is highly significant (p=2×10⁻¹¹), and on the full 92 it is weaker but still clear (p=6×10⁻⁵). An earlier draft reported this sequence starting at 169× and read it as a sign reversal. That first number was an artefact of the house map. At eight report dates the panel is thin, and Putnam's eighteen trusts and Gabelli's sixteen were then counted as separate houses, which put cells into the quiet group that one merged house does not produce. Merging them removed the reversal. What survives is the sign, not the magnitude, which still spans 0.28× to 0.66×: contested companies hold smaller positions, as §5.6 finds directly.

**A placebo anomaly that was a duplicated event.** The six-month anchor of Table 10 once appeared to move, and the text then predicted the anomaly from the rebuild rate. It was an artefact of an event list that counted one anchor date once for every series letter first seen in that month. Deduplicated, that anchor returns zero like the other two.

**The widest rung of the selection ladder.** That rung read as indistinguishable from a coin until the event list was deduplicated: 17 of its anchors were the same date counted twice, and a sign test reads duplicates as independent draws. Deduplicated, the sign holds at p=0.048 and the size still does not survive (§8.5).

**The earlier bound on share classes.** Earlier drafts restricted the panel to cells whose filings never name two different letters, reported 11.6% across 2,897 cells on 606 companies with 39.9% above 24%, and read the gap to the panel's median as showing that mixing rounds was worth about a third of a point. That restriction can be met in two ways, and only one of them fixes the security. The median share of rows carrying any letter in those 2,897 cells is zero: 1,941 of them pass because nobody named anything, and those cells are wider than the panel, at 16.42%. Only 366 pass because every row named the same letter, and they sit at a median of 0.00%. A bound computed mostly on cells of unknown security is not a bound (Appendix C.5 gives the corrected decomposition).

**The series pattern.** An earlier version of the decomposition in Appendix C.5 read 0.12% where it now reads 0.74%, and the whole difference came from the pattern that decides what names a series. It stopped at the letter K and dropped the numeric suffix, so Databricks Series L, which §4.2 quotes, was invisible to it, and Series A-2 read as Series A, which scored two houses holding C-1 and C-3 of one company as holding the same series: the very composition the test exists to remove, arriving inside the test. Widening the pattern past K and past the suffix left a third case. After Z the convention is AA, BB, CC, and Stripe's Series BB-1, which §4.2 also quotes, went unread until the pattern learned doubled letters. Corrected, composition explains the typical gap by a factor of eleven, not the seventy-four the old pattern implied, and the tail is larger: 597 groups on 68 companies against 515 on 65. No numeric guard could see the error, because every pinned figure was recomputed on every run by the same wrong pattern; it was found by a scan for one decision defined in more than one module.

**The consensus in the decomposition of §8.4.** Its first version measured both gaps against the midpoint of the two extreme houses, under which the upper and lower gaps are equal by algebra. Both columns printed identical statistics to four decimal places, and the error was caught at once. Moving the consensus to the median of house medians fixed it only where there are three or more houses. At exactly two houses the median is the midpoint again, and 39.5% of cells carry exactly two houses, so the repaired estimator still reported the spread twice on two cells in five. On the cells where the question can be answered, the bottom-house result does not survive, which is why §8.4 states an asymmetry rather than a pair and uses only cells with three or more houses.

**A copied column in Table E.2.** The coordination column was once computed by hand and copied, and for two rounds the cell beside it carried a p-value from an earlier tolerance. Both columns are now computed by the pipeline.

**The reason the NAV wedge is small.** An earlier draft attributed the small median wedge to the small size of private books, and its own arithmetic disagreed by a factor of thirty. The reason is the mass of positions at the consensus (Appendix G.2).

**The persistence share in Appendix G.3.** An earlier version reported that 70% of house-dates stay on the same side of the consensus, having scored houses at the consensus as agreeing with themselves (`sign(0) == sign(0)`). Among house-dates with a side, the share is 85%. The correction runs in the direction that flatters the argument, which is why it is recorded.

## Appendix G. What the disagreement costs

The body measures what holders say. A referee is entitled to ask what it costs, and the question has a precise form. A mutual fund's net asset value is not a statistic: it is the price at which the fund's investors buy and sell that day. If two houses carry one company far apart, two sets of investors are credited with different values for the same asset on the same date, and one of them transacts at a number that the other's filing contradicts. Zitzewitz (2003) showed that a stale NAV can be exploited. This is the same question with a different cause, and it has not been asked of private marks because nobody had the population to ask it on.

The answer is small, for a reason other than the obvious one, and the panel on which it is measured agrees more than the population does. Each of these limits the claim, and each is stated below. The measure sits in an appendix for length, not for weight: §1 and §11 quote its result, and this is where it is derived.

### G.1 The measure and its filters

For every fund holding a company inside a comparable cell, I reprice its position at the cross-house consensus and express the change in basis points of that fund's own net assets. The consensus is the median of house medians, so a complex filing thirty series cannot vote thirty times. This is the disagreement seen from the only position in which it is a cost rather than a curiosity: that of the person who owns the fund.

Three restrictions run behind the measure: one price per fund per company, one series, and venture-backed companies only. Appendix F.2 gives each with the case that forced it. Everything is rebuilt at the position unit rather than taken from §5, which builds cells on filing lines, because mixing the two units is what produced the widest row of the first run.

**Table G.1.** Restricting to venture-backed companies is what shrinks the largest wedge. What each restriction removes. "Max" is the largest wedge any single fund-date carries, in basis points of that fund's own net assets. The one-price restriction is on in all three rows.

| Selection | Fund-positions | Fund-dates | Median \|wedge\| (bps) | Max \|wedge\| (bps) | Over 10 bps |
| --- | --- | --- | --- | --- | --- |
| all comparable cells | 40,361 | 14,853 | 0.08 | 460.0 | 976 |
| + one series only | 26,790 | 13,160 | 0.04 | 444.4 | 620 |
| + venture-backed only | 8,529 | 3,590 | 0.33 | 161.1 | 258 |

### G.2 Why the cost is small

Across 8,529 fund-positions in 100 venture-backed companies, held by 296 funds across 57 houses over 3,590 fund-dates, funds booked $101.6B. Repricing every position at the cross-house consensus moves $6.6B of booked value in absolute terms.

**Table G.2.** Most fund-dates carry a wedge below one basis point; a few carry more than a per cent. The NAV wedge, in basis points of the reporting fund's own net assets, at each cut.

| Wedge over | Fund-dates | Share | Distinct funds |
| --- | --- | --- | --- |
| 1 bp | 1,341 | 37.3% | 199 |
| 5 bp | 486 | 13.5% | 127 |
| 10 bp | 258 | 7.2% | 75 |
| 25 bp | 104 | 2.9% | 36 |
| 50 bp | 43 | 1.2% | 17 |
| 100 bp | 12 | 0.3% | 5 |

Table G.2 puts the wedge at each cut. The median fund-date carries a wedge of 0.33 basis points, three thousandths of one per cent of the price its investors transact at. The largest is 161 basis points, and twelve fund-dates on five funds carry more than a hundred.

For scale, the private book of a fund in this panel is a median 0.22% of its net assets and at most 11.9%. A fund with a private book of median size would move its NAV by eleven basis points even if it marked the whole book fifty per cent away from consensus. The median wedge is thirty times smaller than that, so the size of the book is not what makes the wedge small.

What makes it small is the mass at zero. In all, 56.4% of the 8,529 positions sit at the consensus to within a hundredth of a per cent, and 22.5% of fund-dates carry a wedge of exactly zero. The median is small because the median fund does not disagree at all, and a fund at the consensus contributes nothing by construction.

The panel agrees more than the population does, and this limits the result. The median cell in this panel carries a spread of 5.9%, against 10.1% for the venture-backed cells of §5.5. Requiring five funds, two houses, one series, one price per fund and a venture label selects the widely held names, which are exactly the names that §4.3 and §8 show herding to a recent round. The measure therefore runs on the agreeing end of the distribution, and its result is best read as a lower bound on what the population's disagreement is worth in NAV. The cells with the widest spreads in §5 are mostly cells this test cannot reach, because they are held too narrowly to clear its bar.

What is not small is the concentration. There are 258 fund-dates on 75 distinct funds with a wedge above ten basis points. A tenth of a per cent of net assets is an order of magnitude below a typical day's move in a diversified equity fund, and far above the tolerance a fund board applies to a pricing error. Twelve of those fund-dates, on five funds, carry more than a full per cent of net assets. Those funds are not a random sample, and most of them are not open-end mutual funds: nine of the twelve are filed by vehicles that report no series identifier, which is what interval funds, closed-end funds and tender-offer funds are, the vehicles permitted to hold illiquid assets in size. These vehicles are 258 fund-dates themselves: by coincidence the same count as the set above ten basis points, but not the same set, since the two overlap in 109. In all they are 7.2% of the fund-dates here and carry a median wedge of 5.3 basis points, against 0.33 for the panel.

This is a partly negative answer, and it should be read as one. The disagreement that §5 measures is large as a fraction of the asset and small as a fraction of the median fund. A reader who expected the 12.1% to be an error of the same size in someone's NAV should leave with 0.33 basis points at the median. A reader who concludes from that median that no fund is affected should leave with the five funds at the other end. What §5 measures is a fact about how private assets are valued. It is not, on this evidence, a systemic mispricing of mutual-fund NAV, and it is not nothing for the funds that hold the most.

### G.3 Is it forecastable?

A wedge matters more if it is predictable. An investor who knows which way a fund's private mark will move knows something about tomorrow's NAV today, which is the Zitzewitz condition.

The obvious test is mechanically biased. The house furthest above consensus at a date is selected partly on its own error, and its next change carries that error back with a minus sign, so regression to the mean produces apparent reversion whether or not anything reverts. The test therefore selects on the deviation at the previous date and measures the change over the next step, paired inside the cell so that whatever happened to the company is common to both houses. Steps in which no house re-marked are dropped, and cells where every house sits at the consensus are skipped: with 56.4% of positions at the consensus there is often no house above and none below, and letting a tie-break choose would measure floating-point noise.

That skip matters, and it is only half the problem. Without it, a round trip of the same panel through the committed CSV moves the cell count from 540 to 538: only two cells, but a replication that cannot reproduce a count has not reproduced anything. The skip also reaches only cells in which every house ties. Where the top is shared and the bottom is not, "the house above consensus" is a pair rather than a house. Forty of the 421 cells are like that, and in sixteen the tied houses are not identical to the last bit, so an index-of-maximum separates them on how a logarithm rounded. Multiplying every price by a relative 1×10⁻¹⁵, the size of a disagreement between two implementations of `log`, moves the count from 226 of 415 to 223 of 412 and the one-sided p from 0.039 to 0.052.

Houses tied at an extreme are therefore averaged, which is what the position means when more than one house occupies it, and the average does not move under that perturbation. Dropping those cells instead was measured and rejected: ties are commoner where houses agree, so dropping them would select on the herding regime of §4.3.

**Table G.3.** Chosen on the previous date, the house above consensus moves less than the one below only slightly more often than chance. Does the house above consensus mark down relative to the house below it? Both designs are printed so that the bias of the naive one is a number, not an assertion. "High house moves less" counts only the cells whose two sides differ at all, which is why its denominator is below the cell count. Sign p is one-sided; the two-sided value is beside it.

| Design | Cells | High house moves less | Share | Sign p (one-sided) | Two-sided |
| --- | --- | --- | --- | --- | --- |
| selected on the previous date (unbiased) | 421 | 223 of 417 | 53.5% | 0.085 | 0.170 |
| selected on the same date (mechanically negative) | 483 | 275 of 483 | 56.9% | 0.001 | 0.003 |

Table G.3 runs both designs. Deviations tilt toward reverting, and the naive design overstates the tilt by 3.5 points: 53.5%, not the 56.9% the obvious test returns. A tilt of three and a half points away from a coin clears no conventional threshold, one-sided or two-sided (p=0.085 and 0.170), so I read it as a direction rather than a result.

Persistence is the other half, and it is a different quantity from the one in §6.1. There the object is a company's spread and the statistic a rank correlation; here it is a house's deviation and an OLS slope. Regressing a house's deviation on its own lag gives 0.76 across all house-dates and 0.84 among those with a side at all; half have none, because in a cell with an odd number of houses one house is the median. Among the 1,071 house-dates with a side, 85% are on the same side one step later. Measurement error attenuates both slopes, so each is a floor.

A house that carries a company away from the consensus is very likely still on the same side next quarter, and slightly more likely than not to have narrowed the gap. That is a persistent difference of view with a weak pull toward the middle, not a stale number correcting itself and not a random walk.

### G.4 What this does not establish

It does not establish that anyone *acts* on the wedge. The natural test is whether funds carrying larger disputed private books see different net flows or reported returns. That test needs data this repository does not yet extract: N-PORT's monthly total return, and its monthly sales, redemption and reinvestment flow items. They sit in `FUND_REPORTED_INFO.tsv`, inside the same quarterly bulk archives as the holdings table and in the same file this paper already opens for each fund's net assets. It is four more column groups from one source, named here with its file so that a reader can run the test without asking.

It does not establish direction either. The consensus is not the truth; it is the middle of a set of opinions that the rest of this paper shows to be persistently different, so a fund above consensus is not thereby overstating its NAV. What Appendix G.2 measures is the size of the disagreement expressed in NAV, the quantity that a fund board, an auditor and a regulator each need and none currently has. What Appendix G.3 adds is that the disagreement does not resolve itself quickly.

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
