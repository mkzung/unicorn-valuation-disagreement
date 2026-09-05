# Which companies enter the panel

The first version of this paper worked from a hand-picked list of about thirty private
companies and searched EDGAR for each one by name. That made the sample a judgement call,
and Appendix D showed what it cost: the per-company sweep stops after eighteen filings, so even
for a name on the list the harvest could miss most of the funds holding it.

The rebuild inverts the direction. The SEC's Division of Economic and Risk Analysis
publishes Form N-PORT as quarterly bulk data sets covering every disseminated filing from
2019Q4 onward, in flat tab-delimited tables. Each holding row carries `FAIR_VALUE_LEVEL`
and `IS_RESTRICTED_SECURITY` beside issuer name, share balance and reported value — the
exact fields the fund-mark leg is built on. Companies are discovered from the filings
instead of assumed in advance, so no company is missing because it was not on a list.

## The rule

A holding enters the panel when its filing is an `NPORT-P` (or amendment) and the row is
Level 3, equity (`ASSET_CAT` in `EC`/`EP`), denominated in shares (`UNIT = NS`), with a
positive balance and value. Price per share is reported value over share balance. A
company-date enters the dispersion panel when at least five distinct funds report the
company on one common report date and those funds span at least two fund **complexes** —
the same bar the first version used, applied to every filer rather than to whichever
filings a capped sweep happened to reach, and raised in one respect: the unit is the
fund house, not the registrant.

That distinction is the one this note exists to make. A registrant on N-PORT is a single
legal trust, and Fidelity files under 36 of them. Requiring two registrants therefore
does not require two opinions — two Fidelity trusts share one valuation committee and
agree by construction. `src/fund_complex.py` maps registrants to houses by rule, checked
against the series each registrant files, covering 98% of booked value and failing closed
so that a registrant matching nothing counts as its own house. Reported between houses,
the median company-date spread is 8.0%; reported between registrants it is 0.02%, and the
difference is entirely the double-counting.

One field that looks like it belongs in that list is deliberately absent. N-PORT asks
whether a holding is a restricted security, and the first version required the answer to
be yes. Filers do not answer it the same way: on 2026-04-30 Fidelity reported Revolut as
restricted and ARK reported the identical holding as unrestricted. Requiring a "yes"
therefore selects on a reporting habit rather than on anything economic, and it does so
one house at a time — for Revolut it removed the only family that disagreed, and a 35%
cross-family spread became zero. Measured against a harvest that keeps every Level-3 row,
the requirement dropped more than half of them. The flag is kept as a column so its effect can be measured, and Level 3 carries the
economic condition on its own: it is the tier for inputs that are not observable, which is
where a private holding has to sit.

Nothing outside the SEC files is required. One zip per quarter reproduces the panel
exactly, with no licensed data, no vendor list, and no judgement about who belongs.

## Why there is no billion-dollar threshold

The anchor literature bounds its population by size. Gornall and Strebulaev (2020) study
135 US unicorns, defined as companies that "raised money from a VC and had a post-money
valuation over $1 billion in at least one of [their] private rounds of financing",
restricted to US companies founded after 1994 with a VC round after 2004. Strebulaev's
current statement of the rule keeps the same two conditions, fixes US membership by where
the company was headquartered when it crossed the threshold, and runs robustness at $2B
and $10B rather than adjusting the cutoff for inflation.

That threshold cannot be reproduced from N-PORT. The filings report a price per share and
never a company valuation, so converting a mark into a valuation needs a share count the
data do not contain. Imposing the threshold would mean importing a commercial roster —
and this paper already declined PitchBook for the reason that applies to every such
source: its licence prohibits publishing the data to a public forum, which is
incompatible with a replication package anyone can run (`notes/data_rights_and_method.md`).
A size filter bought at the price of the paper's only real differentiator is a bad trade.

Two public quantities carry the size dimension instead, both computed from the same files:

- **Breadth** — how many funds and how many fund families report the company at all. This
  is also what makes disagreement measurable, so it is doing double duty rather than
  standing in for a valuation.
- **Booked NAV** — the total dollar value registered funds carry against the company on a
  report date. It answers the question a size threshold is usually a proxy for: how much
  regulated money is exposed to this mark.

The change of criterion is not a compromise. Strebulaev is explicit that the threshold
uses post-money valuation because that is the number the industry reports and can be
verified, and equally explicit about the cost — citing the work with Gornall, that fair
value tends to sit below post-money, so "using fair value would shrink the sample." A
registered fund's Level-3 mark *is* a fair-value estimate, struck quarterly by a fiduciary
and filed under oath. This paper measures how far those estimates disagree with each
other, which is a question about fair value itself and does not need a post-money cutoff
to be well posed.

## What the Level-3 universe includes that a reader would not expect

Breadth of coverage brings breadth of content. A single quarter holds Russian issuers
carried at Level 3 because sanctions froze them rather than because they are venture
backed, private biotechs and medical-device companies alongside the software names, and
feeder vehicles that hold one company through a wrapper. The panel therefore reports an issuer-domicile
split and excludes Russian issuers, whose marks track a sanctions freeze rather than a
company. Other domiciles stay: the private companies registered funds hold include British
and Australian names, and cutting by nationality would narrow the population for no
economic reason. Feeder vehicles are flagged and held out of price comparison, because a
fund's price per unit in a feeder is not the company's price per share.

It also holds securities that are not the company's stock at all. Acquisitions leave
contingent value rights behind, mergers leave escrow lines, and funds carry subscription
rights, warrants and lock-up placeholders — all of them filed under the issuer's own CUSIP
or LEI, which is how they reach the same company key as the shares. Their price per unit
answers a different question, so they are excluded from price comparison on the security
title, where filers record the instrument (`population.is_claim`). The residual case, one
house holding Series C where another holds Series D, no public field resolves; §3.3 bounds
it instead of claiming it away.

## Entity resolution, and why it is the main risk

One issuer appears under many strings: `ANTHROPIC PBC`, `Anthropic PBC`, `Anthropic
Foundation`, and elsewhere a wrapper such as `Studio Type One Soul II LLC (OpenAI)`.
Collapsing these is unavoidable at population scale and is the one step that can
manufacture a result, because merging two securities that are not the same company invents
a price spread nobody reported. The rules:

1. Match on `ISSUER_LEI` or `ISSUER_CUSIP` first — identifiers, not text — after
   discarding placeholder values. `000000000` and `999999999` are both used as filler.
2. Normalise names only to strip legal suffixes, share-class and series text, and
   punctuation. Read the parenthetical rather than deleting it: a feeder names its
   underlying inside brackets, and stripping brackets throws away the identifying text.
3. Merge nothing else automatically. A containment rule that lets `ANDURIL` absorb
   `ANDURIL INDUSTRIES` looks safe on thirty names, and on the full population it chains:
   short names reach long ones, the chains meet, and one cluster ended up holding 448
   unrelated issuer strings. Every remaining merge is declared by name.
4. The declared merges live in an alias list in `src/entity_resolution.py`, never in a
   similarity score. It holds thirteen entries, each read off the filings; §5.3 of the
   manuscript states the count and gives two examples rather than reprinting the list.
5. Keep the pre-merge string on every row, and report headline figures on raw strings as
   well as merged names. A result that survives only after merging is a result about the
   merge.

The resolver is validated before use against the companies hand-labelled in the first
version's `data/fund_marks.csv`, which is ground truth: it must reproduce every one of
those groupings, splitting none and fusing none. The first attempt failed that test by
fusing three unrelated companies through the placeholder CUSIP `999999999`, which is the
error rule 1 exists to prevent and the kind that survives unnoticed in a panel too large to
read by eye. A later attempt fused Fanatics into Stripe because the phrase "holdings in"
matches inside "Holdings Inc". Both were caught by the same test.
