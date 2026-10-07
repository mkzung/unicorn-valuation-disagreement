# The round-date sensor is in N-CSR, not Form D — build spec

*Reviewer note, 2026-08-05, written against `b37252e` after the Form D verdict. Verified on a
live filing before being proposed; the evidence is quoted below.*

## Why this exists

`src/form_d.py` measured Form D and returned a negative: the sensor is weakest exactly where
the panel is strongest, because the largest private companies raise under Section 4(a)(2) and
leave no Reg D trace. That verdict stands. It also points at where to look next: **the funds
themselves are already required to disclose when they bought and what they paid**, and they
disclose it for precisely the restricted private positions this paper is built on.

Regulation S-X requires the schedule of investments to state, for each restricted security,
the **acquisition date** and the **cost**. N-PORT carries neither — its holdings table has
balance, value, level and the restricted flag and stops there. N-CSR does.

## Verified, not assumed

ARK Venture Fund, N-CSR filed 2024-10-08 (accession `0001213900-24-086293`), schedule of
investments, columns *Acquisition Date · Shares · Cost · Value*:

| Holding | Acquisition date | Shares | Cost | Value |
| --- | --- | --- | --- | --- |
| Space Exploration Technologies | 10/31/23 | 75,356 | $6,999,961 | $7,309,485 |
| Discord Inc. | 11/14/22 | 11,744 | $2,723,641 | $2,606,463 |
| Epic Games, Inc. | 9/23/22 | 6,560 | $3,133,309 | $3,664,071 |
| Databricks, Inc. | 9/23/22 | 27,922 | $400,000 | $2,023,507 |
| OpenAI Global LLC | 7/31/24 | 5,797 | $1,000,000 | $1,000,000 |

Cost ÷ shares gives an entry price per share — SpaceX $92.89, Discord $231.90, Epic $477.64 —
against the same filing's mark. Three quantities the paper does not have today fall out of one
column pair.

## What it buys

**1. A round date from a filing, strongest where Form D is weakest.** Funds hold the mega-caps,
so SpaceX, OpenAI, Databricks, Anthropic and Stripe all carry acquisition dates. The
cross-validation is built into the source: when several funds report the *same* acquisition
date at the *same* cost per share, that is a primary round close confirmed by independent
filings. Where dates and prices differ across funds, the purchase was a secondary — and that
distinction, which the press cannot make, is the discriminator the event study needs.

**2. A round price from a filing.** The headline round price per share is currently press
sourced. Cost ÷ shares is the same number as filed by the buyer.

**3. Markup over cost — a variable the paper does not have.** Two houses that entered the same
round on the same date at the same cost and now carry different marks are the cleanest
possible statement of §4.3's house-policy finding: entry price identical and disclosed, so the
spread cannot be entry, vintage, class or units. It is policy or nothing. That is a stronger
version of the Stripe Series I cell, available on every co-held name rather than one.

## What will go wrong, from the same filing

- **Cost is the fund's entry, not always a round.** ARK's Databricks cost of $400,000 for
  27,922 shares is $14.32 a share — not a Databricks round price. Footnote (d) explains it:
  the position arrived through the MosaicML acquisition, all-stock. So cost equals a round
  price only when the entry *was* a primary purchase. Detectable, because the filer says so and
  because a genuine round shows the same price across several funds.
- **SPV look-through.** Footnote (c): some positions are held through unaffiliated SPVs, with
  shares and cost restated to the underlying. Already the §4.3 wrapper problem, one document
  over.
- **Document structure varies by filer.** ARK puts the schedule in the primary N-CSR document.
  Fidelity's N-CSR primary document does not contain it — the annual report is a separate file
  in the same accession. A harvester must walk the filing index, not the primary document. This
  is the same class of trap as the truncated `filings.recent` that cost the listing sensor 34
  months on DoorDash.
- **N-CSR is HTML tables, not a bulk data set.** There is no structured equivalent, so this is
  parsing work — bounded by running it only on panel companies, not on the population.
- **Semi-annual filings are N-CSRS**, a separate form type. Both carry the schedule; searching
  only N-CSR halves the coverage. (`Anthropic`: 30 filers on N-CSR, 30 on N-CSRS.)

## Order of work

1. Harvest N-CSR **and** N-CSRS for the fifteen panel companies; extract issuer, acquisition
   date, shares, cost, value.
2. Validate before using: for each company, do independent funds agree on date and price per
   share? The share that agrees is the share that is a round; print the distribution rather
   than assert a threshold, exactly as `listing_dates.py` earned its.
3. Markup over cost by house (the new §4.3 result) — needs no dates beyond what the same table
   gives.
4. Round dates → the re-pricing event study with the phase-randomised null, on names where
   step 2 passed.

Form D remains the right instrument for the questions it can answer: entity aliases from
`ISSUER_PREVIOUSNAME_*`, and the `IS40ACT` / `ENTITYTYPE` self-declaration for the 150
unclassified clusters. Neither needs a date.
