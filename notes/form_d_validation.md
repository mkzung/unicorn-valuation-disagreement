# Form D as a round-date sensor — what the harvest says

**Status: measured, not used.** Nothing in the manuscript quotes a Form D date. This file is
the answer to the question the sensor had to pass before anything could be built on it, and
the answer is that it passes for about half the panel and fails structurally for the other
half. `src/form_d.py` produces it; `data/form_d_coverage.csv` and
`data/form_d_offerings.csv.gz` are its output.

## What was harvested

Every quarterly Form D data set the SEC publishes, 2008Q1 through 2026Q2 — **763,014**
offerings. The download recipe is worth recording because it cannot be templated: the files
sit under two different paths, `structureddata` for most of the archive and
`datastandardsinnovation` for the newest quarter, and the older ones carry a `_0` suffix that
the newer ones do not. The index page is parsed instead, which also means a new quarter needs
no code change.

## Coverage, before anything is built on it

Of **467,925** live original offerings (amendments excluded):

| | share |
| --- | --- |
| equity offerings | 59.4% |
| carrying a first-sale date | 79.0% |
| flagged first sale yet to occur | 21.0% |
| issuer declares itself a pooled fund | 38.3% |
| `REVENUERANGE` answered at all | 83.5% |
| `REVENUERANGE` = "Decline to Disclose" | 62.6% |
| `REVENUERANGE` giving a usable bucket | **20.9%** |

The last row settles one of the five proposed uses on its own. A revenue covariate that four
issuers in five decline to give is not a covariate, and the "houses disagree most about
companies with no revenue to anchor on" test cannot be run on this field. Age
(`YEAROFINC`) and capital raised (`TOTALAMOUNTSOLD`) survive; revenue does not.

## The validation, and why it does not pass

Against the 28 companies whose press-reported round dates the panel already carries, matched
on the same normalised issuer name the mark panel resolves on, and after removing SPVs:

- **16** of the 28 have any Form D at all under their own name.
- Of the 15 with a comparable press date: **7 land within a month** and 8 within a quarter.
- The rest run −13, −14, −40, −58, −84 and −118 months.

Sorted, the distances are −118, −84, −58, −40, −14, −13, −4, −2, −1, −1, 0, 0, 0, 0, 0.
There is no gap in that sequence. The listing-date check earned its threshold because the
distances separated at 82 days against 258 with nothing in between; here they form a
continuum, so any cut would be a cut I chose rather than one the data showed.

## Why it fails, which is more useful than the fact that it does

The failures are not noise, and three causes are separable:

1. **The round did not file.** A late-stage round placed under Section 4(a)(2) files
   nothing. SambaNova's last Form D is April 2021 against a February-2026 press round;
   Redwood Materials' is June 2022 against October 2025. These are not missing dates, they
   are rounds that leave no Reg D trace at all.
2. **The round filed under a vehicle.** An SPV raising to buy one company's stock puts that
   company's name in the issuer field: "Anthropic Series D NMJFF Apr 2024 a Series of
   CGF2021 LLC", "Stripe Inc Stock May 2024 a Series of CGF2021 LLC", "Kraken Series A, a
   Series of Providence Venture Capital, LLC". Its first sale is the day the SPV raised, not
   the day the company did. §5 excludes the same vehicles from the mark panel one field over,
   and `is_vehicle` applies the same rule here.
3. **The name is not the company.** "Upgrade Labs Inc." is not Upgrade, Inc. A name join with
   no CUSIP and no LEI invents a company exactly the way §5.3 says it does, and the
   validation is what catches it — an eighty-four-month gap is not a stale date, it is a
   different issuer.

## What this changes

The re-pricing event study was deferred for want of round dates. It stays deferred, and now
for a measured reason rather than an assumed one: on the names with the most fund marks —
Anthropic, Stripe, OpenAI, SpaceX — Form D either does not exist or belongs to a vehicle, so
the sensor is weakest exactly where the panel is strongest. An event study on the names it
does cover would be an event study on the smaller half of the panel, selected by whether a
company happens to raise under Reg D.

Two of the other proposed uses do not depend on the dates and survive:

- `ISSUER_PREVIOUSNAME_*` and `EDGAR_PREVIOUSNAME_*` are an SEC-maintained alias list, and
  alias candidates are a proposal to verify rather than a merge to trust.
- `IS40ACT`, `INDUSTRYGROUPTYPE` and `ENTITYTYPE` are the filer's own declaration of whether
  it is a pooled vehicle or an operating company, which is filing-based evidence for the
  clusters §5.2 leaves `unclassified`.

Both are plumbing rather than results and neither is wired in yet.
