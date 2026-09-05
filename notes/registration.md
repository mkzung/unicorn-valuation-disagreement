# Pre-registration for the next panel expansion — drafted, not filed

**Status: drafted, not filed.** §6 of the manuscript says so, and this file is what that
sentence refers to — a reader can check the claim rather than take it. Every result in the
current paper is exploratory, including the sector contrast of §4.2. What follows binds the
*next* version, and binds it only if it is filed before the panel is extended; until then it
is a statement of intent that costs the current results nothing and buys them nothing.

---

## 1. Title

Valuation Disagreement: Is the Unicorn Headline a Ceiling or a Floor? — pre-registration for
the panel expansion following the version dated 5 August 2026.

## 2. What already exists, and what this registers

The current manuscript (SSRN abstract 7016178; repository
`github.com/mkzung/unicorn-valuation-disagreement`) is **exploratory** on every cut it
reports, including the sector contrast of §4.2. This registration binds the *next* version:
the hypotheses below are fixed before the panel is extended beyond the 28 names and the
2026Q2 filing cut, so the following version can be judged on a hypothesis that predates its
data. Prior results are cited here so a reader can see exactly what is being carried forward
and therefore is not itself evidence for these tests.

## 3. Data

- **Secondary cross-section.** Forge per-company estimates as of the extension date, plus
  independently sourced headline rounds, extending `data/valuation_panel.csv`.
- **Fund marks.** SEC N-PORT, both the by-company harvest and the quarterly bulk data sets
  through the extension date, extending `data/fund_marks.csv` and
  `data/nport_population_marks.csv.gz`.
- **Exits.** Any IPO completed between the current cut and the extension date, scored on the
  offer price times fully-diluted shares basis `data/ipo_validation.csv` already uses.

No private or licensed data enters any test below.

**How candidate names are screened, and the two ways that screen lies.** New names enter the
fund-mark legs by EDGAR full-text search over NPORT-P filings. Two corrections to the obvious
procedure, both established by running it:

1. **Count distinct filers, not hits.** A hit count answers a question nobody asked. Cohere
   returns 32 NPORT-P documents and every one of them is the Private Shares Fund under a
   single CIK, so the name is held and can never clear a bar that asks for five funds across
   two houses. "Held by one registrant" is a stronger statement about the ceiling than "not
   held", and it is the statement the search actually supports. The filer count comes back in
   the `entity_filter` aggregation of the same query.
2. **A zero needs two spellings.** Full-text search matches phrases. "Scale AI" returns
   nothing over NPORT-P; that is evidence about the phrase, not about the company, and a
   filer writing "Scale AI, Inc." or a code name would not appear. No name is recorded as
   absent on one query. Each is run bare and with its corporate suffix, and a name that
   returns nothing on both is recorded as absent *from the searchable text*, which is what
   the data can support.

## 4. Sector taxonomy — fixed in advance, and external

The objection this registration answers is that the sector labels are the author's. So the
taxonomy is fixed here, before the new names are known, by an **external, dated rule**:

> A company's sector is read from its own most recent press release or S-1, and assigned by
> the **first match** in the fixed order below. Where no keyword matches, the sector is taken
> from the company's entry in the SEC EDGAR full-text search result for its own filings;
> where neither resolves, the name is recorded as `Unclassified` and **excluded from the
> contrast** rather than assigned by judgement.

The order matters and is fixed here, because "the primary industry a company claims" does not
settle an AI-powered fintech or a defense-focused chip designer — it invites exactly the
judgement this section removes. First match wins, reading top to bottom:

| # | Category | Keywords in the self-description |
| --- | --- | --- |
| 1 | Defense | defense, defence, national security, warfighter, munitions, autonomous weapons |
| 2 | Semiconductors | semiconductor, chip, fab, foundry, wafer, EDA |
| 3 | Data/AI infrastructure | data platform, data warehouse, lakehouse, GPU cloud, inference infrastructure, vector database, MLOps |
| 4 | AI | artificial intelligence, machine learning, foundation model, LLM, generative |
| 5 | Crypto | crypto, blockchain, stablecoin, digital asset, web3 |
| 6 | Quantum | quantum |
| 7 | Energy | energy, battery, nuclear, fusion, solar, grid |
| 8 | Robotics | robot, autonomy, autonomous vehicle, drone |
| 9 | Logistics | logistics, freight, supply chain, shipping |
| 10 | FinTech | payments, banking, lending, insurance, financial infrastructure |
| 11 | SaaS | software, platform, workflow, collaboration (residual for software companies matching nothing above) |
| — | Unclassified | no keyword matches and EDGAR does not resolve it |

Two coders apply the cascade independently to the same descriptions, blind to the gaps.
Disagreement is not adjudicated: the name is recorded `Unclassified` and drops out of the
contrast. The rate of disagreement is reported, because a taxonomy that needs frequent
adjudication is a taxonomy that was doing the work of the hypothesis.

**Favored set, fixed now:** {AI, Data/AI infrastructure, Defense}, not to be revised after
seeing any new gap. Semiconductors is *deliberately excluded* despite strengthening the
contrast in the current exploratory data (p=0.003 against p=0.012), precisely because that
strengthening is the kind of post-hoc improvement this registration exists to forbid.

## 5. Hypotheses

**H0 (the contrast).** In the extended clean subset, a secondary-to-headline gap drawn at
random from the favored group is no more likely to exceed one drawn from the rest than the
reverse.
**H1.** It is more likely.
*Test:* one-sided Mann–Whitney, α = 0.05, on the clean primary-round subset only. The
hypothesis is stated as stochastic dominance rather than as a comparison of medians because
that is what the Mann–Whitney statistic tests; the two coincide only under assumptions this
sample does not license, and writing the hypothesis in terms of medians while testing ranks
is the kind of mismatch a registration exists to prevent. Group medians are reported as
description.

The test is reported alongside the full specification curve and its label-shuffle null
(`src/sector_specification_curve.py`), which in the current data returns p=0.32 for the
count of separating partitions and p=0.43 for their composition — i.e. the curve is expected
to vindicate nothing, and is run to bound the claim rather than support it.

**P1 — dispersion predicts returns.** Names with above-median cross-house mark dispersion at
the last pre-IPO date underperform below-median names from offer price to the first close.
*Test:* one-sided Mann–Whitney on first-day return, α = 0.05.

**P2 — the fund-mark edge scales with staleness.** The fund mark's absolute error advantage
over the headline rises in headline age. *Test:* Spearman correlation between headline age in
months and (headline error − mark error), one-sided, α = 0.05.

**P3 — the secondary's sign persists to exit.** Names the secondary bids above their last
round list above it more often than names it marks down. *Test:* Fisher exact, one-sided,
α = 0.05.

**P4 — dispersion collapses into liquidity.** Cross-house dispersion on a name declines over
the four report dates preceding its listing. *Test:* Wilcoxon signed-rank on the per-name
change, one-sided, α = 0.05.

**P5 — the compression does not scale with the repricing.** §8's step is the paper's one
mechanism claim, and the objection it cannot answer on this panel is that a price arriving
and good news arriving are the same event. The discriminating quantity is the *size* of the
repricing, not its sign: if houses converge because the news is good, the compression should
grow with how far the round moved the price; if they converge because a price now exists at
all, it should not. *Test:* Spearman correlation between the absolute change in the median
price per share across the round and the step in the between-house spread, over every dated
non-first anchor in the extended panel, two-sided, α = 0.05. *Predicted:* no relationship.

*Why this is registered rather than reported.* It was run on the present panel and it does
not give a clean answer, which is exactly why it belongs here instead of in the paper. Over
all fifty anchors the correlation is 0.014 (p = 0.92), the null P5 predicts. That number
hides a shape: the step is absent where the price moved under seven per cent, large where it
moved between eight and forty-four, and absent again above forty-nine, and among the
thirty-three anchors that repriced at all the correlation is +0.457 (p = 0.007) — bigger
repricings compressing *less*, which no reading offered here predicts and which a
desynchronisation story could explain after the fact. Sixteen events a bin, bin edges chosen
by the analyst after seeing the data, and a mechanism available only in hindsight: three
things this project treats as disqualifying. The honest form of the result is a prediction
filed before the panel that could test it, and this is that form.

**What P4 needs, and the sample it is run on.** An earlier draft of this section said the
current panel could not answer P4 at all, on the ground that only three of the ten listings
§4.3 scores have four qualifying report dates within eighteen months of listing. That was
true of those ten and false as a statement about the data, and the error is worth recording
because it is the kind that quietly kills a hypothesis. §4.3's ten names are the exits with
a *verified offer price*, which P4 does not need; P4 needs a *listing date*. Widening to
every venture-labelled cluster whose classification records a listing or a merger gives
**twenty-one** names with four or more guarded cells before they leave the panel — seven
times the sample, from the same data.

The binding input is therefore a sourced listing date per name, and the cheap substitute
does not survive testing. A company that lists stops being carried at Level 3, so the last
private cell looks like a free proxy for the event. Checked against the five §4.3 names that
have both, the gap is three months for Instacart, Circle and SpaceX — and twelve for
CoreWeave and twenty-seven for ServiceTitan. A proxy that is two years early on a fifth of
the sample measures something else. Listing dates come from each company's own SEC filing
history, and the table is built before the test is run, not alongside it.

**The pool is exits completed from 2023 onward, and the reason is independence.** The
2020–21 cohort — Airbnb, DoorDash, Palantir, DraftKings, UiPath, Toast, Sweetgreen,
Allbirds, Warby Parker, Rivian, Didi, Deliveroo, Aurora and the rest — sits entirely inside
data already examined while this section was being written, so a test on it cannot be
described as predating its data whatever this document says. That cohort is available as an
exploratory pre-test and will be reported as one, labelled as such, with the understanding
that a null there neither falsifies P4 nor licenses dropping it. The registered test runs on
listings completed after this registration is filed, pooled cumulatively, under the §6
minimum of ten per compared group.

## 6. Sample size, accumulation, and the stopping rule

No optional stopping. The extension runs to a **fixed date** announced here — the first
quarterly N-PORT bulk data set released after this registration is filed — and every name
meeting the existing entry rules on that date enters. Tests are run once, after the cut.
Names are not added or dropped by inspection of their gaps.

**Exits accumulate; they are not re-drawn each version.** P1, P2 and P3 all condition on
completed listings, and listings arrive at three to five a year that clear the entry rules.
A test run on one year of new exits is a test with no power, and §7 promises to report every
null as a failure — so without a rule the registration would manufacture a run of false
falsifications and then be cited for them. The rule:

- The sample for P1–P3 is the **cumulative** pool of qualifying exits from 2023 onward, not
  the increment since the last version. Earlier exits are never dropped.
- Each hypothesis is tested at every extension, on the pool as it then stands.
- A **minimum of ten observations per compared group** is required before a null counts as
  evidence against the hypothesis. Below it, the result is reported as `underpowered`, with
  the n, the point estimate and the interval — visible, but not a falsification.
- The threshold is fixed here and does not move with the answer. Reaching it is a matter of
  arithmetic on the exit calendar, not of inspecting a p-value.

Testing the same hypothesis at successive extensions is repeated testing, and the α is not
adjusted for it, because these are not independent looks at a fixed sample but one growing
sample. The honest description is that P1–P3 are **sequential and uncorrected**, each
version's result superseding the last rather than adding to it, and that is stated here
rather than discovered by a reader.

## 7. What would falsify each claim

Each hypothesis fails if its test does not clear α at the pre-set direction. A failure is
reported in the next version with the same prominence as a success, in the manner §6.3
already handles the size relationship that reversed. No test is dropped after the fact and
no α is adjusted after the fact.

## 8. Analysis code

The tests above are the ones already implemented in `src/robustness.py`,
`src/validation.py`, `src/population.py` and `src/sector_specification_curve.py` at commit
`b48cc10`. Re-running `python3 src/reproduce.py` on the extended data executes them unchanged;
any modification to those files between this registration and the next version is visible in
the repository history.

The commit named above is the eighth and last of this history, and the pin moves with it.
`src/validation.py` changed in that commit: a three-line conclusion baked into the exit
figure came out of the image and into its caption, where a build can check it, and the
docstring's "0 = nailed it" went with it. No executable line moved and the reproduction run
returns every number unchanged, which is the check that matters rather than the description.
A pin cannot name the commit that contains it, so this is the second of the two commits that
move together: the work, and then the pin. The history was rebuilt from a hundred and
thirty-three working commits into seven before anything was published, so every hash the
account below gives is from that earlier numbering and no longer resolves. They are left as
written. Renaming them to hashes invented after the fact would make an account of what
happened read as though it had been recorded at the time, and the point of this section is
that its claims are checkable rather than that they look tidy.

The pin has moved from `f625c71` twice, and both times for an addition to
`src/population.py` rather than a change to a registered test. The first was
`duplicate_books`, which looks for one holding reported twice under two house labels. It is a diagnostic and not a hypothesis — none of the tests above changed —
but it found five affiliate groups the house map had missed, and merging those moved the panel
from 4,297 cells to 4,271 and the median spread from 11.750% to 12.135%. A registration still
pinning the old commit would be claiming those numbers ran. The second was
`correction_cost`, which recomputes what §3.2's own corrections cost instead of leaving the
answer in prose. The third is a parquet cache for `panel()`, added after a reader ran out of
memory holding the panel twice in one process; it is keyed on the source file so it cannot go
stale, and it changes no number. The fourth moved it from `a585ec7`, and is the thinnest of
the four: the manuscript was rebuilt around a new running order, and the stale section
numbers in the docstrings of `population.py` and `robustness.py` were rewritten to match.
No executable line moved. The pin is a claim about file contents rather than about
behaviour, so a comment is enough to make it false, and moving it is cheaper than
weakening what it checks. None of the four touched a registered test or hypothesis.

**The sixth is not of the same kind, and that is stated first because the previous five
were.** `src/population.py` gains two functions, `series_composition` and
`same_series_spread`, and they answer a question the registration did not anticipate: how
much of the between-house spread is two houses valuing one security differently and how
much is two houses holding two securities of one company. Nothing registered changes — no
hypothesis, no test, no α, and no figure in §§5–8 moves — but this is new analysis rather
than a comment, and calling it housekeeping would be the kind of thing this note exists to
prevent. It was written because a reviewer showed that §3.3's existing bound was vacuous on
two thirds of its own subsample, which is a defect in the old code and not a result of the
new; the withdrawal is recorded in §3.3 and the replacement in Appendix C.5.

The fifth is of the same kind. `PRICE_OUTLIERS`, the list of rows the price detector leaves
behind after each has been read against its filing, was one set with the reasoning in a
comment beside it: four entries are a different security of the same issuer and two are
marks a house really filed. The comment said the opposite — two instruments, four marks —
and nothing could contradict it, because a comment is not checkable. The set is now two
named sets, `OTHER_SECURITY` and `MARKS_THAT_STAND`, whose union is the old constant, so
every membership test and every number is what it was; what changed is that the split is
now a thing a test can count. §3.2's own summary of those survivors was wrong in the same
place and for the same reason — it called six titles "six issuers" where the issuers are
five — and all five counts are registered in `src/paper_numbers.py` now.

The seventh and eighth move it from `fb05246`. The seventh touches all four files, so it is
set out line by line rather than summarised. In `src/robustness.py` the between-family variance share
guarded its denominator with `ss_tot > 0`; that is the float edge `population.house_policy`
replaced with `VAR_FLOOR` after it moved a count by forty between two pandas releases, and it
is now the same floor in both places. In `src/population.py` a second definition of
`REMARK_TOL`, identical in value to the first, is deleted, so §6.2 and `staleness` can no
longer be tuned apart. In `src/sector_specification_curve.py` the `clean_only` parameter of
`curve` is removed: `_setup` reads the clean subsample unconditionally, so the flag did
nothing and `curve(False)` returned the same frame as `curve(True)` — a switch a reader could
have taken for a robustness check that had been run. In `src/validation.py` the exit figure's
headline bars were coloured by the sign of the error while the legend said the colour encoded
the signal; they are one colour now. No registered hypothesis, test or α changes, and the
reproduction run that follows these edits returns every number in §§5–11 unmoved, which is
the check that matters rather than the description. The ninth is a lint pass: eighty-two `noqa`
directives that suppressed nothing, seven unused imports and nine redundant `int()` casts,
across all four files. No executable line changed meaning, and `reproduce.py` returns the same
417 numbers. The eighth is one pass over section
references: the microscope and the data section changed places, so the docstrings in
`population.py` and `robustness.py` that cite them changed with the paper. No executable
line moved.

That sentence is a claim about the repository, so it is checked like one. This draft pinned
`f517309` for a while after two of those four files had been rewritten under it — the claim
was false and nothing complained. `tests/test_registration_pin.py` now reads the commit named
here and fails if any of the four analysis files differs between it and the working tree, so
the pin cannot go stale in silence. Update the pin, or explain the diff; those are the only
two ways to a green build.

---

*Prepared 5 August 2026. Not filed.*
