# Validating the house map against Form N-CEN

Design note for `src/ncen_advisers.py`. Tests: `tests/test_ncen_advisers.py`. Output:
`data/ncen_advisers.csv`. Quoted in §4.1.

## The objection

The paper's largest single number moves on a definition. Measured between registrants the
median disagreement is 0.004%; measured between fund complexes it is 12.1%. The map from
registrant to complex is `src/fund_complex.py`, and it is mine.

§4.1 already checks it from inside the data: marks agree *more* within a mapped complex
(89.0%) than within a single registrant (87.5%), which is what a correct merge produces and a
wrong one cannot. A referee was right that this closes the question on the same data it was
built from.

## The instrument

Item C.9 of Form N-CEN names the investment adviser of each series. Every registered fund
files one annually. That is the SEC stating who manages a trust, with no input from this
paper, so the two errors the map could make are separately visible:

- **A merge that is wrong.** Two registrants this map calls one house filing two different
  advisers. This would damage the paper, and it is the first count.
- **A merge that is missing.** Two registrants left apart that file one adviser. The map
  fails closed, so an unmapped registrant keeps its own identity and a missed merge can only
  make the reported disagreement *smaller*. Reported separately, not as an error.

The comparison is asymmetric because the map is.

## Where the data comes from, and why not from the filings

The SEC publishes every N-CEN extracted into quarterly flat files at
`sec.gov/files/dera/data/form-n-cen-data-sets/`. `ADVISER.tsv` carries the Item C.9 block
already parsed, keyed by `FUND_ID` = `{accession}_{cik}_{series}`, joined to `SUBMISSION.tsv`
for the CIK and filing date. Twenty-eight quarters is about 250 MB.

Crawling one `primary_doc.xml` per registrant instead would pull roughly five gigabytes, a
large trust's file being 4.6 MB, from the same publisher, with the parsing done by us rather than by
the people who defined the schema. The per-filing path is kept only as a fallback, because
the SEC states that the flat files do not yet include submissions in schema 3.1.

Advisers are taken at the registrant's **most recent** filing, not pooled across quarters. An
adviser genuinely changes when a house is bought, and a union over eight years would read
Legg Mason's own adviser and Franklin's as two advisers inside one house, manufacturing the
exact failure the check exists to find.

Only `ADVISER_TYPE = Advisor`. Item C.9 also names sub-advisers, and a sub-advised sleeve is
sold by one complex and managed by another; folding those in would call every such trust a
different house from itself.

## Normalisation

Deliberately blunt: case, punctuation, connectives, and the corporate suffixes every filer
writes differently. It has to fold the spellings **one filer uses for one adviser**, nothing
more. It does not expand acronyms — `FMR Co., Inc.` stays `fmr` and does not join
`fidelity management research`, because matching by similarity is the problem §3.2 refuses
to solve. The consequence is stated rather than hidden: a house filing the same adviser in full
and abbreviated reads as a house with two advisers, so the first count is an **upper bound**
on wrong merges and every entry in it has to be read.

Seven things were wrong with this module while it looked finished, and every one of them
returned a comforting answer. Not one produced an error or an odd number.

| defect | what it returned |
| --- | --- |
| no CA bundle in the interpreter | every request failed; 1,167 rows of "files no N-CEN" |
| pattern read `adviserName`, SEC writes `investmentAdviserName` | zero advisers on every filing |
| `filings.recent` caps at ~1,000 documents | the largest complexes reported as filing none |
| `&amp;` reached the normaliser | a house split from itself by an entity reference |
| a name of nothing but suffix words | one registrant dropped from both directions, silently |
| only the first adviser of each registrant was read | 6% of the evidence discarded, from the damaging direction |
| a renamed trust counted as two registrants | 79 houses called merged when 55 are |

The first was recorded at the time as "no outbound route", which was wrong in the direction
that excuses the result. `_get` now raises on transport failure and returns `None` only when
the server answered 404 or 403, so an empty extract cannot masquerade as a clean map.

## Result

| quantity | value |
| --- | --- |
| registrant CIKs in the panel | 1,166 |
| an adviser recovered | 1,161 |
| houses covered | 655 |
| houses the map merges (two or more distinct CIKs) | 55 |
| of those, filing more than one adviser name | 22 |
| advisers under more than one house, on two or more CIKs | 96 |
| registrants naming more than one adviser themselves | 69 |

The five not reached: one files no N-CEN, and four file one whose Item C.9 block is empty:
Central Securities, Northeast Investors Trust, 180 Degree Capital and an Oaktree private
fund. Each of the four is an N-2 closed-end registrant. That is what the documents show;
the module does not assert a reason for it.

All 22 split houses are read one by one in `READ_BY_HAND`, with the kind and the reason: 13
are one firm's several advisory entities (BlackRock Advisors beside BlackRock Fund Advisors),
8 are acquisitions still filing their own advisory name (Eaton Vance under Morgan Stanley,
OHA under T. Rowe Price, Nomura on the Ivy and Delaware trusts), and 1 is an outside manager
of a delegated sleeve (PRIMECAP and six others at Vanguard). None fuses two unrelated firms.

Four of those readings were wrong when first written, because they were written from what I
expected the names to be instead of from the names. Fidelity files no entity called FMR; it
files Fidelity Management & Research, Fidelity Diversifying Solutions and Strategic Advisers.
T. Rowe Price's second adviser is not an international arm, it is OHA. Macquarie's is not a
delegation, it is Nomura, which bought the US business. And Putnam's is the strongest result
the check produced, described below. Every reason now names an entity that appears in
`data/ncen_advisers.csv`.

## The merge the paper withholds, confirmed from outside

§4.1 declines one merge deliberately: Franklin Templeton bought Putnam in 2024, and a static
map would backdate that over four years of filings. N-CEN, which knows nothing about that
decision, files **Franklin Advisers** as the adviser of nine Putnam-named trusts. The paper's
judgement and the SEC's record agree, and they agree in the fail-closed direction: treating
the two as separate houses can only make the reported disagreement smaller.

That reading is a judgement, so it is written down where it can be disagreed with, and
`compare` reports how many split houses have **no** reading and how many readings describe a
house that no longer splits. Both are zero and the test fails if either moves. A sentence in
§4.1 saying "not one fuses two unrelated firms" is worth nothing if the set it describes can
change underneath it.

One entry is worth naming: AllianzGI. Virtus bought the AllianzGI US business in 2021 and
advises the funds still carrying the AllianzGI name, so this is a merge the map does **not**
make. It is the fail-closed direction, and it understates the correction.
