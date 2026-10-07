# Data dictionary

Every numeric datum is a public fact or an attributed published estimate; every row carries a source + date. This package publishes derived metrics, not vendors' tables (see `compliance_audit.md`).


## The core of this paper

Everything below this heading is an input to, or an output of, a number the paper states.
`nport_population_marks` is the panel; `population_cells` is the guarded company-date panel
built from it; everything else is a measurement taken on one of the two or a check on one of
them. Appendix A of the paper carries the same list with its derived objects.

## `data/nport_population_marks.csv.gz` (SEC N-PORT bulk data sets) — built by `src/nport_bulk.py`

Every Level-3 equity holding reported in share terms across all disseminated N-PORT
filings from 2019Q4 onward, one row per (filing, holding). Columns are the SEC's own, plus
`balance`, `val_usd`, `pps` (reported value over share balance) and `src_quarter`.

This is the replacement for the name-by-name EDGAR sweep in `src/nport_fetch.py`, which
could only find companies already on a list and stopped after eighteen filings each.
`IS_RESTRICTED_SECURITY` is carried as a column and never used as a filter — filers
disagree about it for the same security, so filtering on it removes houses rather than
securities (`notes/universe_definition.md`).

## `data/population_cells.csv` — built by `src/population.py`

One row per company-date clearing the panel bar: five or more funds across two or more
fund **complexes**, on a common report date. The complex, not the registrant, is the
unit of independence — a registrant is one legal trust and a house files under many of
them (`src/fund_complex.py`). `n_fams` counts complexes; passing `family="CIK"` to
`population.cells` reproduces the registrant-level panel the manuscript quotes as the
lower bound on the correction.

Rows whose security is a claim against a company rather than a share in it — contingent
value rights, escrow lines, subscription rights, warrants, lock-up placeholders — never
reach this file. They arrive on the issuer's own identifier and so land on the company's
key, but their price per unit is not a price per share, and a cell holding one against the
other would report a spread no house ever expressed (`population.is_claim`,
`tests/test_population.py`).

| column | meaning |
| --- | --- |
| company | resolved company key (the cluster, not the display label — labels repeat) |
| dt | report date |
| n_funds | distinct funds, counting series and, where a filer reports none, the registrant |
| n_fams | distinct fund complexes, which is the count of independent views |
| lo, hi | lowest and highest family mark, each a median across that family's funds |
| nav | total value registered funds carry against the company that quarter |
| spread_pct | `hi/lo − 1`, so a house filing many funds cannot inflate it |
| guarded | `hi/lo ≤ 4`. Wider cells stay in this file but are excluded from every reported figure: a ratio above four is a unit or share-class artifact, not a valuation disagreement. Roughly a quarter of the rows are unguarded, so a median taken over the raw file will not match the paper. |

## `data/company_classification.csv` — built by `src/company_class.py`

One row per reported cluster: what kind of company is on the other side of the mark, and how
that was decided. The filing system carries listed issuers, buyout portfolio companies and
corporate structured preferred alongside the venture-backed names, and §5.2 reports a total
for each because only the venture-backed ones are what the paper is about.

| column | meaning |
| --- | --- |
| company | resolved cluster key, the same identity `population_cells.csv` groups on |
| issuer | the most common issuer string in the cluster, so a reader can find it by name |
| label | `venture` · `private_nonventure` · `listed` · `unclassified` |
| basis | `verified` (checked one at a time, reasoning in the note), `rule`, `unclassified`, or `unresolved` for a cluster that was examined and did not resolve |
| note | the reasoning, for verified clusters |
| rule_label | what the rule alone would have said — the column that makes its 94% accuracy checkable |
| pp, res | the two signals: share of the cluster's filings whose security title says private placement, and share flagged restricted |
| nav, cells, median_spread_pct | the cluster's weight and dispersion in the reported panel |

Every cluster above $500M carries a verified label; `tests/test_company_class.py` fails if a
new one appears without one, and if any verified key stops matching a cluster.

## `data/ncen_advisers.csv` — built by `src/ncen_advisers.py --harvest`

The SEC's own answer to "who manages this trust", one row per registrant CIK in the panel,
used by §4.1 to check the registrant-to-house map against a source it was not built from.
Item C.9 of Form N-CEN names the investment adviser of each series.

The only file here that needs a network to rebuild, and the only one whose rebuild is not a
stage of `src/reproduce.py`. The comparison reads this file and runs offline, so a clone with
no route reproduces every number §4.1 states; a clone that reruns the harvest and gets an
empty answer is stopped rather than shown a clean result.

Coverage is 1,161 of 1,166 registrants, all 1,161 from the SEC's quarterly N-CEN flat files.
The remaining five: four the flat files never name, whose filing was fetched directly and
carries no Item C.9 block at all (each an N-2 closed-end registrant), and one that files no
N-CEN. The flat files exclude submissions in schema 3.1, which is why the fallback exists
even though on this panel it recovered no adviser.

| column | meaning |
| --- | --- |
| CIK | the registrant, as N-PORT files it |
| ncen_accession | the accession of the registrant's most recent N-CEN, empty if it files none |
| filed | that filing's date, empty when the row came from the filing rather than the flat files |
| source | `dera` for the quarterly flat file, `filing` for the fallback, `none` for no N-CEN |
| advisers | the Item C.9 adviser names, pipe-separated, as filed |

## `data/round_event_study.csv` — built by `src/round_event_study.py`

Item D: median between-house spread by months since the company's most recent dated round, on
guarded cells, with restatement windows excluded. Two columns because one of them is the answer
— pooled, and demeaned inside each company.

**Nothing in the manuscript quotes these.** `notes/round_event_study.md` records why the pooled
profile is composition rather than effect, and why the phase-randomised null overrules a
one-sided p below 0.001.

| column | meaning |
| --- | --- |
| m | months since the last dated round, zero to twelve |
| cells, companies | the denominator at that horizon |
| pooled_median | median spread across all cells in the bin |
| within_company_median | the same after each spread is demeaned by its company's median |

## `data/round_event_study_stats.csv` — built by `src/round_event_study.py`
The same arrangement for §8: 110 statistics — the profile, the step, the placebo, the selection
ladder, the up/down split and the rebuild rate — each with the design key. This is the file §8's
prose is pinned against.

## `data/round_dates.csv` — built by `src/round_dates.py`

The first report date each company-series appears on in the population, with the breadth behind
it. Filers name the series in the security title, so a new letter bounds the round from above at
monthly resolution. Calibrated against the earliest N-CSR acquisition date for the same series:
14 of 15 dated pairs inside 35 days, median 16.

**Nothing in the manuscript quotes these.** `notes/round_dates.md` records the two rules the
calibration dictated — two houses, and no series censored at the panel's first date — and the
one pair that breaks the natural claim that the error has a known sign.

| column | meaning |
| --- | --- |
| company, series | the cluster key and the letter, however the filer spells it |
| first_dt | the first report date any fund holds that series |
| funds, houses | breadth; houses via `fund_complex.confirmations`, never registrants |
| censored | first seen on the panel's own first date, so the series predates the window |
| dated | clears the two-house bar and is not censored |

## `data/split_events.csv` — built by `src/split_events.py`

Stock splits recovered from the panel itself, one row per company and split factor. A holder
that did not trade files exactly k times as many shares at the next report date and leaves the
position value where it was; a purchase moves both together. Confirmation is across fund
*houses* inside a three-month window, because houses restate in different months.

**Nothing in the manuscript quotes these.** `notes/split_events.md` records the three places the
detector differs from the rule as proposed, the five events on 2019-12-31 that look like a
filing-convention change rather than five splits, and the consequence that did not hold — the
4x class guard is not mostly absorbing restatement desync.

| column | meaning |
| --- | --- |
| company, k | the cluster key and the split factor, rounded from the balance ratio |
| canonical_k | k is a ratio companies actually split at; 99 and 127 are not |
| first_dt, last_dt, restatement_span_days | the window, and how far apart the houses were |
| funds, houses, registrants | the confirmation count at each of the three units |
| houses_list | who restated, so a reader can check one against the filings |

## `data/ncsr_acquisitions.csv` — built by `src/ncsr_acquisitions.py` (reaches SEC)

What each fund paid for a private position and when, from the schedule of investments in the
annual and semi-annual reports. Regulation S-X requires an acquisition date and a cost for
every restricted security; N-PORT carries neither. One row per lot per filing, for the ten
§4.3 names, uncapped: every N-CSR and N-CSRS whose schedule of investments names one of them,
found by asking EDGAR's index for the company AND the schedule's own column header.

**Nothing in the manuscript quotes these yet.** `notes/ncsr_acquisition_validation.md` records
the verification against a live filing, the filer layouts the parser handles — including the
two that appear inside one document — and the 45 cross-book comparisons the uncapped harvest
supports, of which 37 agree to within a hundredth of a point.

| column | meaning |
| --- | --- |
| company, security | the panel name and the security title as the filing writes it |
| acquired, acquired_last, lots_spanned | the acquisition date, and the span where a filer gives a range |
| cost, value | in dollars; a filing reporting thousands is scaled on the way in |
| markup_pct | value over cost, which needs no share count and exists on every row |
| shares, cost_per_share, mark_per_share | only where the filer prints shares beside the cost |
| period | the report period the filing covers — the date the marks are AS OF |
| lots_spanned | 1 where the row is a single purchase; 2 or more is a blended cost |
| series | the letter, read from "Series J" or "Class L" alike; what makes a lot a lot |
| wrapper | the position is held through an SPV by §4.3's own `fund_marks.WRAPPER` rule |
| filer, cik, house | the registrant, and the fund complex it belongs to |
| in_thousands, form, adsh, doc | how it was filed and where to check it |

## `data/listing_dates.csv` — built by `src/listing_dates.py` (reaches SEC)

When each company in the panel began trading, read off its own EDGAR filing history rather
than the press. The rule is the earliest exchange registration the CIK filed while it carried
that company's name; both halves matter, since Palantir registered twice and DraftKings
inherited a shell's registration filed a year before it existed as a public company.

| column | meaning |
| --- | --- |
| key | cluster id, the same identity the population panel groups on |
| company | the name the registrant carried on its listing date, not today's |
| cik, accession, form | the filing the date comes from: `8-A12B`, `8-A12G` or `8-K12B` |
| era_name, era_from | which naming era of the registrant the rule read |
| mechanism | exchange registration · successor registration · successor name · none |

`validate()` prints each date against the last report date on which that company appears as a
private Level-3 holding. The two agree to within a quarter for eighteen of the twenty-one
dated names and the next-closest is 258 days away, so the threshold separates rather than
cuts; the three outside it stopped being held long before they listed.

## `data/nav_wedge.csv` — built by `src/nav_wedge.py`
One row per fund, company and report date inside a comparable cell, with the NAV wedge that
position carries: `lines`, `lo_line`/`hi_line` (the fund's own price range for the company, which
is what `one_price` tests), `balance`, `val_usd`, `net_assets`, `own_pps`, `consensus_pps`,
`repriced_usd`, `wedge_usd`, `wedge_bps`, `own_vs_consensus_pct`, `position_pct_of_nav`, plus
`SERIES_ID` and `REGISTRANT_NAME` carried as attributes rather than keys — see the module's note
on why keying on them dropped a fifth of the panel. Every figure in Appendix G.

## `data/nav_wedge_stats.csv` — built by `src/nav_wedge.py`
The scalars Appendix G quotes, one per row, with a `design_key` hashing the module's constants and the
source file. `src/paper_numbers.py` reads this rather than recomputing, because rebuilding the
panel three times costs ninety seconds on a guard that runs on every commit;
`tests/test_nav_wedge.py` fails if the key drifts from the current design.

## `data/level1_placebo.csv` — built by `src/level1_placebo.py`
The control of §2.3: five securities two houses both hold at fair-value Level 1, one row per
holder, with `cusip`, `report_date`, `price_per_share`, `fair_val_level` and the `accession` each
came from. The point of the file is that the level and the accession are in it, so the zero
reading can be checked against the filing rather than taken on trust.

## `data/fund_marks.csv` (SEC N-PORT, public domain) — built by `src/nport_fetch.py`
One row per private-equity holding a mutual fund discloses for a target company in Form NPORT-P. Every figure is a verbatim public fact from an SEC filing.
| column | meaning |
| --- | --- |
| company | target (my label) |
| issuer_name | issuer/series as filed (e.g. "DATABRICKS INC SERIES F") |
| fund | filing `seriesName` (the actual fund) |
| registrant | filing `regName` (the trust) |
| series_id | SEC fund series id |
| cik / accession | filer CIK and accession (locates the filing on EDGAR) |
| report_date | `repPdDate` — the as-of date of the mark |
| units | NS = number of shares (PA/OU = other; NS is what carries a price/share) |
| balance | shares held |
| val_usd | fair value of the holding, USD (the mark) |
| price_per_share | `val_usd / balance` (derived here) |
| pct_val | % of fund NAV |
| asset_cat | EC = equity-common, EP = equity-preferred |
| fair_val_level | ASC 820 level (3 = unobservable, the private marks) |
| restricted | `isRestrictedSec` (Y for private placements) |
| cusip | usually a dummy (000000000) for private holdings |
`src/nport_fetch.py` records **only Level-3 marks** (as its docstring states), which also discards public-company namesakes the text query collides with — e.g. the Tokyo-listed PLAID, Inc. (TSE 4165) held by international small-cap funds at Level 2, vs the US private Plaid fintech we target.
Derived (in `src/fund_marks.py`): per (company, fund, report_date) blended price/share = Σ`val_usd`/Σ`balance`; cross-fund spread conditional on the report date. Filters: keep `fair_val_level`=3, `units`=NS, `asset_cat`∈{EC,EP}; drop SPV/fund-of-fund wrappers and 10:1 unit-convention outliers; and exclude composites whose holders split across share classes or legal entities — **SpaceX** (auto-detected by the within-fund class-mix flag) and **ByteDance** (a documented manual exclusion in `CROSS_CLASS_EXCLUDE`: funds hold the Douyin Co Ltd vs ByteDance Ltd entities and common Series E-1 vs convertible-preferred Series E, so per-share is not comparable). The file holds 409 raw rows → 386 clean Level-3 holdings across 104 funds and 15 companies; the per-share comparison covers the 13 non-composite companies, 10 with ≥5 same-date funds (median cross-fund spread 24%).

## `data/fund_marks_bulk.csv` — built by `src/fund_marks_bulk.py`

The ten §4.3 cells recomputed with the eighteen-filing harvest cap lifted and nothing else
changed: same companies, same report dates, same fund-complex family unit, same 4× guard.
It exists to put a size on what the cap cost, not to replace Table 4 — the marks there were
each read against a filing, these are read against a bulk extract of the same filings.

| column | meaning |
| --- | --- |
| company | the published §4.3 name |
| date | the published report date, held fixed |
| funds, houses | distinct funds and fund complexes on that date, uncapped |
| low, high | lowest and highest house median |
| spread_pct | `high/low − 1` |
| guarded | `high/low ≤ 4`. One cell (Discord) fails and is excluded from the median |
| letters | every series or class letter any filer names in that cell |
| published_spread_pct, published_funds | what Table 4 reports, for the side-by-side |

`letter_restricted()` re-runs each cell inside its best-populated shared series, which is the
per-cell answer to the objection that the recovered funds are different share classes.

## `data/version_reconciliation.csv` — built by `src/reconcile_versions.py`

Each cell in the first version's §4.3 table recomputed from the bulk data. A cell that
returns *more* funds measures the old harvest cap; a cell that returns fewer is a
resolution failure and has to be fixed before any population figure is quoted.

## `data/fund_marks_dispersion.csv` — built by `src/fund_marks.py`
Per-company cross-fund dispersion summary at the modal report date: `n_funds`, `min/median/max` price/share, `maxmin`, `spread_pct`, `cv_pct`, `n_families`.

## `data/fund_marks_timeseries.csv` (SEC N-PORT, public domain) — built by `src/nport_timeseries.py`
One row per (tracer fund, company, quarter): the blended implied price/share that fund disclosed for that private company in its NPORT-P filing for that period. Harvested from each tracer fund's **full EDGAR series-level NPORT-P history** (`browse-edgar` atom feed → each filing's `primary_doc.xml`), so it spans 2019Q3–2026 where available. Same holding definition as the cross-section (`fairValLevel`=3, `units`=NS, `assetCat`∈{EC,EP}, non-wrapper); `isRestrictedSec` is *not* filtered (filed inconsistently — ARK marks these "N", others "Y").
| column | meaning |
| --- | --- |
| company | target (my label) |
| fund | tracer fund (series) display label |
| series_id | SEC series id (or the interval-fund CIK where the trust files one series, e.g. ARK Venture) |
| cik | trust CIK (locates the filing on EDGAR Archives) |
| accession | filing accession (locates the exact filing) |
| filing_date | EDGAR filing date |
| report_date | `repPdDate` — as-of date of the mark |
| n_sec | number of matching Level-3 holdings blended in that filing |
| tot_balance | Σ shares across those holdings |
| tot_val_usd | Σ fair value across those holdings (USD) |
| pps | `tot_val_usd / tot_balance` (derived blended price/share) |
Tracer funds (eleven; deep public histories): ARK Venture, Fidelity Contrafund, Fidelity Blue Chip Growth, T. Rowe Price Global Stock, Alger Focus Equity, Baron Partners, Baron Focused Growth, **and (added for cross-family coverage of the single-fund cycle names)** Franklin Growth Fund (Stripe + Canva — Franklin family), New Economy Fund (Stripe — American Funds), T. Rowe Price Communications & Technology (Canva + Epic), T. Rowe Price Global Technology (Epic). The file holds **408 quarterly Level-3 marks across 11 tracer funds and 9 companies** (was 281 / 7 funds). The additions give Stripe a 3-family path (Fidelity, Franklin, American Funds; level co-movement ρ=0.94 over 20–21q), and Canva and Epic Games a second family each — so the Appendix C.1 "funds re-mark in the same direction" claim is confirmed across families (Databricks ρ=0.97, Stripe ρ=0.94) rather than resting on Databricks alone; the cross-fund **median** path shifts only slightly (cycle now −62% / +171%; the Appendix C.2 fund-mark index −60% / +140%, matched-date ρ=0.99). QoQ-change co-movement is strong only for the two deepest names (Databricks 0.87, Stripe 0.79); Canva/Epic (level ρ=0.71) agree on the broad arc but not tick-by-tick; Discord stays the loose outlier (0.22).

## `data/mark_staleness.csv` — built by `src/mark_staleness.py`
One row per company-quarter in which at least two fund families both disclose a mark, used by Appendix D to test whether the cross-family disagreement is really staleness.

| column | meaning |
| --- | --- |
| company, quarter | the cell (report quarter, from the N-PORT report date) |
| n_families | named families disclosing that company that quarter |
| spread_pct | cross-family spread, `max/min − 1`, on family-median marks |
| judgeable | every family in the cell also filed in the immediately preceding quarter, so freshness can be determined; cells that open a family's series are `False` and are excluded from the comparison rather than scored as stale |
| n_moved | how many of the families present moved their mark that quarter (`−1` when the cell is not judgeable) |
| all_remarked | every family in the cell moved its mark that quarter (`|change| > 0.5%`) |
| none_remarked | no family moved: the quiet quarters that test whether the disagreement persists outside repricing episodes (only five such cells exist, so Appendix D reports the question as open) |
| families | the families present, comma-separated |

Cells whose highest family mark exceeds the lowest by more than 4× are dropped as unit-convention or share-class artifacts (the same guard the time-series leg uses). Result: freshly-remarked cells are **not** tighter (median 12.1% against 6.7%), the least frequent remarker is not the outlier, and the conclusion is unchanged across remark tolerances 0.1–5%, class guards 2×-to-none, and a per-company collapse that removes the clustering.

## `data/ipo_validation.csv` (10 exits 2023–26; 7 fund-held) — read by `src/validation.py`
Scores two PRE-IPO public signals against the realized IPO valuation for unicorns that listed: the stale **headline** (last private round) and the last pre-IPO **mutual-fund N-PORT mark**. The fund mark is converted to an implied valuation through the IPO's own per-share price (pre-IPO preferred converts ~1:1 to IPO common at a healthy listing). Where no broad mutual-fund mark exists (Klarna), the 2022 down round is used instead.
| column | meaning |
| --- | --- |
| last_private_val_busd | last private valuation before listing, $B (the headline) |
| last_private_date | date of that round |
| ipo_val_busd | IPO / first-print valuation, $B (realized) |
| ipo_pps | IPO offer price per share, $ (the bridge; blank where no per-share signal) |
| ipo_date | listing date |
| direction | down (headline > IPO) / flat / up (headline < IPO) |
| vintage | round-era tag: `2021-peak` (the four 2021-bubble stale headlines that define the +160% overshoot: Instacart/Reddit/Klarna/Chime) / `2021-fair` (Klaviyo) / `2021-stale` (Figma) / `2022` (ServiceTitan/Circle) / `2024` (CoreWeave) / `2026` (SpaceX-xAI) |
| preipo_signal_type | `fund_mark` (SEC N-PORT) / `down_round` (interim financing) / `na` (no comparable interim signal) |
| preipo_signal_pps | the fund's last pre-IPO implied price/share, $ (fund_mark rows) |
| preipo_signal_busd | the interim signal's implied valuation, $B (down_round rows store it directly; fund_mark rows are rebuilt in code from pps×IPO bridge and the stored value is a cross-check) |
| preipo_signal_date | as-of date of the interim signal |
| preipo_signal_source | source(s) for the interim signal (SEC filing locators / press), ≥2 where possible |
| quality_flag | clean / merger_complex / structured_round (ServiceTitan's Series H + IPO ratchet) / contested_headline (Circle's terminated-SPAC vs Series F) |
| source | source(s) for the headline + IPO facts |
Derived (in `src/validation.py`): `overshoot_pct = last_private/IPO − 1` (headline error); `signal_implied_busd = IPO_val × mark_pps / IPO_pps` for fund_mark rows (else the stored `preipo_signal_busd`); `signal_err_pct = signal_implied/IPO − 1`; `least_wrong` = the signal with the smaller |error|; the +160% overshoot median is computed over `vintage=="2021-peak"` (the four), not `direction=="down"` (which now also holds the modestly-down 2022-vintage ServiceTitan/Circle). Result (**10 exits, 7 fund-held**): the last fund mark is least-wrong in **five of the seven** fund-held exits — |error| median **~11%** (Instacart +8%, Chime −1%, Reddit −5%, ServiceTitan +11%, Figma −28% floor) vs the headline's median **48%**; the four 2021-peak-vintage down-round headlines overshoot by a median **+160%**, and the sign is demand-conditional (repriced consumer-fintech Chime/Klarna overshoot; compounder Figma + momentum SpaceX/xAI are floors). **The two counter-examples (Klaviyo, Circle) are exactly the recent fairly-priced rounds**, so the headline was not stale and beat the fund mark — sharpening the claim to "the fund mark beats the headline *only where the headline has gone stale*" (the edge is the absence of staleness, not foresight). additions (each ≥2-sourced, SEC-anchored): **ServiceTitan** 2024-12 IPO ($71/sh ~$6.3B; 4 T. Rowe Price funds $78.85/sh report 2024-09-30, New Horizons accession 0000080248-24-000041; headline = Series H Nov-2022 $7.6B at $84.57/sh, a structured down round w/ compounding IPO ratchet); **Klaviyo** 2023-09 IPO ($30/sh ~$9.2B; ClearBridge $34.38/sh report 2023-06-30, Variable Small Cap accession 0001752724-23-181447; headline = $9.5B 2021 Series D — fairly priced, the +3% headline beats the mark's +15%); **Circle** 2025-06 IPO ($31/sh ~$6.9B; Fidelity OTC ×2 $23.33/sh report 2025-04-30, OTC Portfolio accession 0001752724-25-160011; headline = $7.65B Apr-2022 Series F — the $9B Concord SPAC was terminated Dec-2022, not a clean round — the +11% headline beats the mark's −25%, which undershot a +168% listing). Klarna's 2022 down round overcorrected to −56% (vs the +205% headline); IPO valued at the offer-price ~$15.1B fully-diluted, the same basis as the other exits. Figure: `figures/ipo_validation.png`.

## `data/ipo_premarks_byfund.csv` — built by `src/validation.py`
The pre-IPO fund marks behind §7, one row per company and fund family: `mark_pps`, `ipo_pps`,
`err_pct` and `n_funds`. It exists because §7 states two of those counts in words, where no digit
scan reaches them.

## `data/robustness_summary.csv` — built by `src/robustness.py`
Tidy long-format ledger of every robustness check behind Appendix D (one row per check). Reuses the production loaders/filters in `src/fund_marks.py` and `src/fund_marks_timeseries.py`, so it stresses the same pipeline the results come from.
| column | meaning |
| --- | --- |
| section | paper section the check defends (4.1 / 4.2 / 4.4 / 4.5) |
| check | the metric name (e.g. `bootstrap_ci_lo`, `favored_vs_rest_mwu_p_one_clean`, `eta2_between_family_med_material`, `drawdown_med_K3`) |
| value | the computed value |
Checks: §4.1 — bootstrap CI, sign-test p, Wilcoxon p, 10%-winsorized mean, leave-one-out median min/max; §4.2 — sector sign-split: Kruskal–Wallis omnibus p (clean/full, null ≈0.28/0.31), and an **unregistered** demand-favored {AI, Data/AI, Defense}-vs-rest contrast (favored/rest clean medians +4.0/−14.6, Mann–Whitney one- & two-sided p, 20k label-shuffle permutation p, rank-biserial, Hodges–Lehmann pts, leave-one-out max p, and the full-panel one-sided p); the grouping is fixed a priori by the demand thesis, not searched; §4.2 multivariate confound (`mv_*` checks): Mann–Whitney balance of favored-vs-rest on round recency (`mv_recency_mwu_p_clean` ≈0.77 — balanced) and headline size (`mv_size_mwu_p_clean` ≈0.03 — favored larger), plus the demand-favored coefficient in `gap ~ favored + recency + log(size)` tested by a Freedman–Lane permutation (residual-permutation, FWL-exact) on both the raw gap (`mv_favored_coef_raw_clean` ≈+37 pts, `mv_favored_fl_p_raw_clean` ≈0.008) and the rank-transformed gap (`mv_favored_fl_p_rank_clean` ≈0.003); the full panel washes out (`mv_favored_fl_p_raw_full` ≈0.31). Round recency = months from `parse_round_date(headline_date)` to the 2026-06-24 Forge observation; §4.3 — median spread under unit-outlier band K∈{2,3,4,5} and fund threshold, family-collapsed spread (median/max), material-name between-family variance share (η²), within-family-zero share; Appendix C.1 — median drawdown & recovery under OUTLIER_K∈{3,4,5,6} and the mean-path variant. The variance decomposition is one-way (log price/share by named fund family, "Other" catch-all excluded, ≥2 named families with ≥1 replicated); η² = SS_between/SS_total.

## `data/nport_expansion_probe.csv` (SEC N-PORT, public domain) — the Appendix D out-of-panel probe

Same columns as `data/fund_marks.csv`, harvested for five names held outside the panel — xAI, Perplexity, Cohere, Groq, Fanatics — to ask whether §4.3's herd-versus-disagree structure shows up on first contact with names the panel never selected. One of the five clears the panel's bar of five or more funds sharing a report date: **Fanatics**, with seven funds across three families on 2026-04-30.

This file was swept more deeply per company than `src/nport_fetch.py` runs by default, and that is why it disagrees with the panel files on the same company and the same date. `data/fund_marks_dispersion.csv` records Fanatics on 2026-04-30 as two funds from one family at a 0.0% spread; the deeper sweep finds five more funds and a **75%** cross-family spread — Fidelity $87.33, Neuberger $73.85, Franklin $50.00, each family internally identical to the cent. The capped harvest is not wrong; it is partial. Whatever it missed was a filing it never opened, which is why the panel's Fanatics cell comes out narrower than the record supports rather than wider. Fanatics enters no headline figure: the §4.3 median is taken over companies reaching five funds *in the panel files*, where it reaches two.

`src/verify_marks.py` re-fetches these marks from live SEC EDGAR alongside the panel's.

## `data/p4_pretest.csv` — built by `src/p4_pretest.py`

The registration's P4 — dispersion collapses into liquidity — run on the exits that already
exist, as an **exploratory pre-test**. One row per venture cluster listing before 2023 with
four qualifying report dates strictly *before* the listing date, which is the correction that
matters: Palantir's last cell falls nine days after it began trading.

| column | meaning |
| --- | --- |
| key, company | cluster id and the name the registrant listed under |
| listing, anchor | the date from `listing_dates.csv` and the form it was read from |
| window_from, window_to, days_to_listing | the four report dates preceding the listing |
| first_spread, last_spread, change_pts | between-house spread at each end and the change |
| rho | per-name rank correlation of spread against date, the whole-window version |

## `data/form_d_offerings.csv.gz` — built by `src/form_d.py` (reaches SEC)

Regulation D notices of exempt offering, harvested from the SEC's quarterly Form D data sets
and cut to the issuers whose names match a company in `valuation_panel.csv`. The full harvest
is 763,014 offerings and is not committed; what is committed is the matched subset and the
coverage table computed over the whole of it.

**Nothing in the manuscript quotes these dates.** `notes/form_d_validation.md` records why:
Form D dates the round for about half the panel and misses the rest by years, because the
largest late-stage rounds are placed under Section 4(a)(2) or raised through an SPV that
files under the company's name.

| column | meaning |
| --- | --- |
| company | the panel company the issuer name matched |
| ENTITYNAME, CIK | the issuer as the filing names it |
| SALE_DATE, YETTOOCCUR | date of first sale, and the flag that there has not been one |
| ISAMENDMENT, PREVIOUSACCESSIONNUMBER | the amendment chain, with the SEC's own link field |
| INDUSTRYGROUPTYPE, SIC_CODE | industry as the filer declares it, and as EDGAR assigns it |
| REVENUERANGE | filer-declared revenue bucket; "Decline to Disclose" in most rows |
| vehicle | the issuer is an SPV or pooled fund raising against the company, not the company |

## `data/form_d_coverage.csv` — built by `src/form_d.py`

Counts and shares over every live original offering in the archive, which is what makes a
fill rate mean anything. The row that decides the most is `REVENUERANGE gives a usable
bucket`: one offering in five.

## `notes/registration.md` — not data; the pre-registration §6 refers to

Drafted and unfiled. It fixes, for the next panel expansion, the demand contrast, an
external dated rule for assigning sectors, P1–P4 with their tests and alphas, and a stopping
rule with no optional stopping. It exists in the package so that §6's claim that a
registration is drafted can be checked rather than believed. Semiconductors are deliberately
excluded from the favored set despite improving the contrast in the current exploratory
data, which is the sort of improvement a registration exists to forbid.

## Reproduction & integrity tooling

- **`src/reproduce.py`** — one-command reproduction. Runs the offline analysis scripts in dependency order (asserting each exits 0; the two SEC harvesters are network and run separately), then recomputes every headline number from the production code and checks it against the manuscript, writing `notes/reproduction_manifest.md`. Exit 0 only if every script ran clean and every number reconciles in both code and prose.
- **`src/paper_numbers.py`** — the single registry of canonical figures. `canonical_numbers()` returns one record per load-bearing number quoted in `paper/draft.md` / `README.md`, each **recomputed live from the production loaders** (never re-implemented), paired with the value the paper states (`value` ± `tol`), the exact prose token (`claim`), the files that must contain it (`in_files`), and — for percentages too common for bare-substring matching (24/11/48/39/88%) — a per-file `context` phrase so partial drift (one stale mention among several) is also caught. `prose_missing()` is the shared prose check.
- **`notes/reproduction_manifest.md`** — auto-generated table of all canonical numbers with their computed value, paper value, tolerance, and code/prose status. A referee-facing reproduction receipt; regenerated by `reproduce.py`, never hand-edited.
- **`tests/test_paper_consistency.py`** — turns drift into a CI failure. Asserts (a) no **code-drift** (`|computed − paper| ≤ tol` for all numbers) and (b) no **prose-drift** (every token, and its context phrase, present in the manuscript). This is the guard the code-only `tests/test_metrics.py` cannot provide — it reads the prose — closing the exact failure mode caught by hand (stale README n=9 robustness block) and (stale result #7). The bare-token check catches a number's total disappearance; the `context` phrases catch partial drift. The registry grows with the paper; `notes/reproduction_manifest.md` lists whatever is currently registered.

## Provenance rule
≥2 independent sources before a figure is treated as settled; single-sourced or disputed figures carry a `quality_flag` and are excluded from headline (clean-subset) results. Exception (documented): the Forge FPMI is a proprietary index published only by Forge Data LLC, so its level/returns are used single-source **with attribution** as inputs to the overlay computed here (never republished as Forge's table), and are cross-checked for internal consistency and against the independently-built fund-mark index.


## Datasets of the second paper, kept in this package

These belong to the three legs this paper cut — the secondary-market cross-section, the
prediction markets and the valuation cycle (§3.4 of the manuscript). They ship because they
are that paper's seed and because the robustness suite imports two of the scripts that build
them. **No number in this paper is computed from any of them.** A reader reproducing the
paper can ignore this section entirely.

## `data/valuation_panel.csv` (cross-section, June 2026)
| column | meaning |
| --- | --- |
| company | company name |
| sector | coarse sector tag (mine) |
| headline_val_busd | last primary-round post-money, $B (fact) |
| headline_type | primary / tender / reported |
| headline_date | round date |
| headline_source | outlet + date for the headline fact |
| forge_val_busd | Forge Global secondary estimate, $B (attributed to Forge) |
| forge_date | as-of date of the Forge estimate |
| quality_flag | clean / tender_not_primary / contested_headline / stale_headline |
| notes | context |
Derived: `gap_pct = forge/headline − 1`.
The panel holds **28 names** (clean primary-round subset **17**). `headline_source` records the outlets behind each `headline_val_busd`: 21 of the 28 rows carry two or more, seven carry one. Every row carries its date. All 28 companies are US-headquartered. Shield AI's year-only `headline_date` is recorded as the verified **Mar-2026** (`2026-03`, fixed against Fortune, TechCrunch and Bloomberg); that matters only for the §4.2 round-recency check, since the `gap` itself does not depend on the date. `src/robustness.py` reads `headline_date` to derive each round's recency.

The Forge per-company secondary estimates are attributed inputs (Forge Global, from its published `^FPMI` component estimates as of 2026-06-24). The panel is a curated, value-added compilation — sector tags, quality flags, independently sourced headlines, and the derived gap — rather than a republication of a vendor's table: one Forge estimate per company enters as an input to a computed column, and no index level, weight or component list is reproduced (see `compliance_audit.md`).

Clean median gap **-4.6%** (n=17, bootstrap 95% CI -20.3%…+4.0%); full-panel median **-7.4%** (n=28, range Flexport -89% … SandboxAQ +142%).

## `data/prediction_markets.csv` (forward-looking) — read by `src/prediction_markets.py`
Dated readings of public prediction-market contracts on late-stage private companies — a distinct signal type (implied probabilities of an *exit/valuation event*, not point estimates). Polymarket launched Nasdaq Private Market-resolved private-company trading on 2026-05-19; Kalshi runs parallel contracts. Each row is one quoted reading with its platform, as-of date and source(s); young/thin markets, so figures are snapshots of a continuously-moving price.
| column | meaning |
| --- | --- |
| company | OpenAI / Anthropic / SpaceX / cross |
| platform | Polymarket or Kalshi |
| contract | the exact market question as quoted |
| metric_type | `ipo_order` (which lists first) / `ipo_complete_by` / `ipo_announce_by` / `closing_mktcap_ge` (debut-cap bracket) / `valuation_threshold_ge` / `listing_resolved` / `combined_valuation` |
| implied_prob_pct | quoted implied probability, % (blank for the combined-valuation point) |
| reference_busd | the valuation threshold / bracket lower bound, $B (where applicable) |
| as_of | date of the reading |
| source | primary source (platform event URL or named outlet) |
| corroboration | secondary source(s) / earlier readings |
| note | resolution definition, caveats, comparison to the last round |
Derived (in `src/prediction_markets.py`): (i) cross-venue / cross-contract disagreement on the same event (e.g. Kalshi "announce" 88% vs Polymarket "complete" 29% on OpenAI's 2026 IPO — a ~59-pt gap, part definitional; and the OpenAI-vs-Anthropic order flipping with the June confidential filings); (ii) the market-implied debut valuation read off the `closing_mktcap_ge` exceedance curve vs each name's last round and Forge estimate (Anthropic implied median debut cap ≈ $1.85T ≈ 1.9× its $965B round; ~81% to debut at/above the round). Caveat: probabilities forecast an exit, not a current valuation; readings are dated snapshots, not a synchronized cross-section.

## `data/forge_index.csv` (Forge Private Market Index, attributed) — read by `src/forge_index.py`
Dated anchor levels of the Forge Private Market Index (FPMI), Forge Data LLC's equal-weighted secondary-market index of ~75 actively-traded late-stage private companies. Forge does not publish a free historical series, so each anchor is derived from Forge's **published** spot level (627.98 on 2026-06-24) and a published trailing return; the derived overlay is what gets published, not Forge's table. Single-source-with-attribution is the sanctioned treatment for a proprietary index (`compliance_audit.md`).
| column | meaning |
| --- | --- |
| date | as-of date of the anchor level |
| fpmi_level | the FPMI index level on that date |
| basis | how the level was derived (which published return × the spot level) |
| source | attribution (Forge Data LLC; via Yahoo Finance display where noted) |
| accessed | date the figure was gathered |
| note | context / cross-check |
Internal consistency check: the 1-year-ago anchor (317.10, from the +98.04% 1Y return) equals Forge's stated 52-week low (317.11). Cross-checks from Forge's monthly/annual Private Market Updates (not levels, so kept as notes): FY2025 FPMI +85.9% through Nov; Jan-2026 +4.4%; May-2026 +11.7%; Nov-2025 +5.3%; trailing-1Y-to-2025-09-30 +75.6%.

## `data/forge_vs_fundmarks.csv` — built by `src/forge_index.py`
The equal-weighted **N-PORT fund-mark index** used in the Appendix C.2 overlay: one row per quarter, `fund_mark_index` = the equal-weighted mean (rebased to 100 at 2021Q4) of the cross-fund **median** implied price/share for the four deep names with a full 2021→2026 path (Databricks, Stripe, Canva, Discord), each forward-filled only within its active filing window. This is the SEC-derived counterpart to the Forge FPMI path; the script reports each path's max drawdown and trough→latest recovery and the matched-date correlation.

## `data/forge_corroboration.csv` — read by `src/forge_corroboration.py` (Appendix D)
Independent cross-check of the §4.1 Forge per-company secondary estimates (the paper's most load-bearing, single-source input, and not independently price-verifiable). One row per panel name for which a **second**, independent public market signal exists.
| column | meaning |
| --- | --- |
| company | panel name (joins to `valuation_panel.csv`) |
| forge_val_busd | the Forge estimate being corroborated; **must equal** the panel's `forge_val_busd` (provenance guard in `load()`) |
| indep_implied_val_busd | the independent signal's implied company valuation, $B (per-share venue quotes pre-converted; raw per-share kept in `note`); blank ⇒ directional-only (Kraken) |
| indep_type | `secondary_venue` (a 2nd secondary platform: NPM/Hiive/Caplight/PM Insights/Notice/Premier) · `tender` (reported employee tender) · `primary_round` (a confirming new round) · `secondary_press` (reputable press of the secondary level) |
| indep_date | as-of date of the independent signal |
| indep_source | outlet(s)/platform(s) + date, ≥2 where available (single-platform rows noted) |
| note | raw per-share basis, caveats, time lag vs the Forge as-of |
Derived (in `src/forge_corroboration.py`): `diff_pct = forge_val/indep_implied_val − 1`; each signal's gap to the last round; `direction_agree` (above/below-round sign match, scored on the independent-*secondary* rows where the test is meaningful — `primary_round`/`tender` anchors equal the headline by construction). Result (**11 names**, 10 numeric + 1 directional): Forge is within **a median of 7%** (mean 7.6%) of the independent signal, 9/10 within ±15%, above/below-round direction agrees **6/6** on the independent-secondary rows; Forge runs *conservative* (below other venues) for Epic Games/PsiQuantum/Perplexity by 7–18% — residual cross-venue dispersion that is itself the paper's disagreement thesis. Strongest corroborations are hard market facts: Databricks +0.4% vs *The Information*'s $165–175B June-2026 round; Ramp +4% vs its $44B round; Stripe +13% above its $159B Feb-2026 tender; Anthropic ≈ its $965B Series H / ~$1T secondary print.

## `data/forge_corroboration_summary.csv` — built by `src/forge_corroboration.py`
Per-name enriched table: `forge_val_busd`, `indep_implied_val_busd`, `indep_type`, `diff_pct`, `forge_gap_pct`, `indep_gap_pct`, `direction_agree`, `indep_date`, `indep_source`.

## `data/coverage_matrix.csv` — built by `src/coverage_matrix.py`
Which signals cover which company, one row per name. It belongs to the three legs cut to a second
paper (§3.4) and is kept because the coverage claim in Appendix A is about the harvest rather than
about the legs.

## `data/cross_signal_consistency.csv` — built by `src/cross_signal.py` (Appendix C.4)
The company-level inner join of the two **cross-sectional** disagreement signals — the §4.1 secondary-to-headline gap and the §4.3 cross-fund mark spread — over the names both signals cover (six, with ≥5 disclosing funds). Reuses the §4.1/§4.3 production loaders in `src/robustness.py`, so it measures exactly the quantities the headline results do.
| column | meaning |
| --- | --- |
| company | the name (in both signals) |
| n_funds / n_families | same-date disclosing funds / distinct families behind the §4.3 spread |
| spread_pct | §4.3 cross-fund mark spread (max/min − 1, %) |
| gap_pct | §4.1 secondary-to-headline gap (Forge/headline − 1, %) |
| quality_flag | the §4.1 headline flag (clean / tender_not_primary / stale_headline) |
| fund_consensus | `herd` if spread < 5%, else `disagree` (the §4.3 bimodality split) |
| secondary_sign | `at/above` if gap ≥ 0, else `below` the last round |
Derived in-script (not stored): Spearman ρ(gap, spread) with an **exact permutation p** (n=6 ⇒ 720 relabellings; no normal approximation), plus coverage counts (secondary 24 / cross-fund-≥5 10 / overlap 6 / all-three 3). Headline reading: ρ=−0.43 (p=0.42, n=6) — directional, not significant; the distribution-free regime view (all 3 herded names trade at/above their round; the only below-round overlap name, Epic Games, is a stale headline) is what carries the one-mechanism point.

## `data/fund_marks_timeseries_summary.csv` — built by `src/fund_marks_timeseries.py`
Per-company cycle metrics from the cross-fund **median** price/share path (after a documented ~10:1 split adjustment and a 4×-of-series-median unit-outlier drop; **SpaceX excluded** — multi-class + 2022 split): `n_funds`, `n_q`, `first_q/first`, `peak_q/peak`, `trough_q/trough` (the **maximum-drawdown** trough and the peak preceding it), `last_q/last`, `run_up_pct`, `drawdown_pct` (max drawdown), `recovery_pct` (trough→latest), `net_pct`.

## `data/sector_specification_curve.csv` — built by `src/sector_specification_curve.py`

One row per possible favored-sector partition of the §4.1 clean subset, with at least two
names on each side: the sectors called favored, how many names that is, the one-sided
Mann–Whitney p against the rest, the median gap difference in points, the rank by p, and two
flags for whether the set contains or overlaps the manuscript's three demand sectors. §4.2
uses it to price its own contrast against every alternative rather than asking a reader to
accept that the split was chosen in advance.
