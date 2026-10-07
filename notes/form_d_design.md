# Form D as the round-date sensor — build spec

*Reviewer note, 2026-08-05. Written against `f625c71`. Nothing here is in the paper yet; this
is the design for the sensor §5 needs before the event study of the re-pricing phase can be
computed, plus four uses of the same download that do not depend on that study.*

The paper replaced press-sourced listing dates with `8-A12B` filings. Round dates are the
remaining press-sourced quantity, and they gate the event study. The analogue exists and it
is a bulk data set, not a search index.

## The source

**SEC Form D Data Sets** — <https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets> —
quarterly zips, **2008Q1 through 2026Q2**, ~3 MB each (~230 MB for the entire history), six
tab-delimited files per quarter. Structurally identical to the N-PORT bulk data sets
`src/nport_bulk.py` already harvests: no scraping, no search index, no per-name cap, and the
same "the filings decide what exists" property that motivated §5.

Schema (from the SEC's own `Form_D.pdf`), fields that matter here:

| File · field | What it gives |
| --- | --- |
| `OFFERING.SALE_DATE` | date of first sale — **the round date** |
| `OFFERING.YETTOOCCUR` | flag: first sale has not happened yet (exclude) |
| `OFFERING.TOTALAMOUNTSOLD` | amount actually sold — cross-check on press-reported round size |
| `OFFERING.ISAMENDMENT`, `PREVIOUSACCESSIONNUMBER` | the amendment chain, **with an explicit link field** — the Palantir-second-8-A12B trap, already solved by the schema |
| `OFFERING.INDUSTRYGROUPTYPE` | industry as the **filer** declares it |
| `FORMDSUBMISSION.SIC_CODE` | industry as **EDGAR** assigns it — a second, independent coding |
| `OFFERING.REVENUERANGE` | filer-declared revenue bucket |
| `OFFERING.IS40ACT`, `ISPOOLEDINVESTMENTFUNDTYPE` | issuer is a registered fund / pooled vehicle — filer-declared |
| `ISSUERS.ISSUER_PREVIOUSNAME_1..3`, `EDGAR_PREVIOUSNAME_1..3` | **an SEC-maintained alias list** |
| `ISSUERS.YEAROFINC_VALUE_ENTERED`, `ENTITYTYPE`, `JURISDICTIONOFINC` | company age, legal form, domicile |

## Use 1 — round dates (what the event study needs)

`SALE_DATE`, restricted to `ISAMENDMENT = N` and `YETTOOCCUR = N`, is the round date. Validate
exactly as `listing_dates.py` was validated: for the names whose round dates are known from the
press, print the distribution of |Form D date − press date| and read the acceptance threshold
off the gap, rather than asserting a fortnight.

Two coverage facts must be measured before anything is built on it, not assumed:

1. **Not every round files a Form D.** Section 4(a)(2) placements and Reg S offshore rounds do
   not. Report the share of known rounds with a matching filing; that share is the sample.
2. **Multiple closings file multiple Form Ds.** Decide once whether a round is the first sale
   date or the union of closings within a window, and state which.

The join is by issuer name and CIK — no CUSIP, which is the weak point of every rule in
`entity_resolution.py`. Mitigations: the previous-name fields below, and the validation above,
which fails loudly on a bad match (a wrong CIK lands hundreds of days away, as the Circle
check already showed).

## Use 2 — the taxonomy the registration needs, mechanically

`notes/registration.md` §4 fixes the sector taxonomy by "the primary industry the company's own
most recent press release or S-1 uses", with **two independent coders** and disagreement
resolving to `Unclassified`. Form D supplies both coders from filings:

- coder A: `OFFERING.INDUSTRYGROUPTYPE` (the issuer's own declaration),
- coder B: `FORMDSUBMISSION.SIC_CODE` (EDGAR's assignment).

Agreement is the label, disagreement is `Unclassified`, and the disagreement rate the
registration promises to report is computed rather than adjudicated. The categories are coarser
than {AI, Data/AI infrastructure, Defense} — Form D's list will not separate AI from SaaS — so
this replaces the *venture / non-venture* and broad-sector layers, not the demand contrast. It
removes press releases from the chain for everything it does cover.

## Use 3 — the 150 `unclassified` clusters, and the venture headline

`data/company_classification.csv` leaves 150 clusters unlabelled by design. A cluster whose
issuer filed a Reg D **equity** offering as an operating company — `IS40ACT = N`,
`ISPOOLEDINVESTMENTFUNDTYPE` unset, `ENTITYTYPE` a corporation — is venture-side evidence
from a filing rather than from a name. The same fields settle the opposite side: a pooled
vehicle declares itself one.

## Use 4 — the alias list `entity_resolution.py` writes by hand

`ISSUER_PREVIOUSNAME_*` and `EDGAR_PREVIOUSNAME_*` are the SEC's own record of what an issuer
used to be called. That is the Allbirds/Smartbird problem — solved for `listing_dates.py` by
reading the name the registrant carried on the listing date — available as data for every
issuer, and a source for alias candidates that no longer depends on reading filings by eye.
The asymmetry rule stands: a candidate alias from this field is a proposal to be verified, not
a merge to be trusted, because fusing two companies still invents a spread.

## Use 5 — the one that is a result rather than plumbing

§6.1 establishes that disagreement is a stable property of particular companies and does not
say **which** companies. Form D attaches filing-declared company characteristics to the
population panel: `REVENUERANGE`, `YEAROFINC_VALUE_ENTERED` (age), `TOTALAMOUNTSOLD` (capital
raised), `ENTITYTYPE`, `JURISDICTIONOFINC`.

The obvious hypothesis is testable on 660 clusters rather than ten names: **houses disagree
most about companies with no revenue to anchor a valuation on.** A cross-sectional regression
of the company's median spread on revenue bucket, age and capital raised turns §6.1's
persistence finding from a description into a mechanism — and it needs no new listings, no
vendor and no press.

Measure the fill rate of `REVENUERANGE` first: "Decline to Disclose" is a permitted answer and
is common. If the fill rate is low, the covariate is `age` and `amount raised`, and the revenue
test waits.

## Order

1. Harvest and validate `SALE_DATE` against known round dates (Use 1). The validation is the
   deliverable; the dates are only usable if it passes.
2. Uses 3 and 4 — they improve figures already in the paper and carry no new claim.
3. Use 5 — a new result, and the natural sequel to §6.1.
4. The re-pricing event study, with the phase-randomised null, once the dates exist.
