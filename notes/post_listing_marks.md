# Marks that outlive the listing

Reproduce: `python3 src/p4_pretest.py` (the last block of the output).
Code: `reclassification_lag`, `lag_summary`, `_post_listing_marks` in `src/p4_pretest.py`.
Tests: `test_a_level_3_mark_after_a_listing_is_usually_still_inside_the_lock_up`,
`test_post_listing_marks_are_too_few_to_carry_a_convergence_test` in
`tests/test_company_class.py`.

## Why this exists

P4's window was corrected to stop strictly before the listing date, because Palantir's last
window cell fell nine days after it began trading. That correction was made on principle; this
measures how much it was worth.

## The panel is Level 3 by construction

The panel is Level 3 by construction: `src/nport_bulk.py` keeps only holdings reported at
fair-value Level 3, so a holding that is promoted out of Level 3 simply stops appearing. The
promotion is therefore never seen. What is seen is the opposite face of it — a mark still
reported at Level 3 at a report date after the company's shares began trading.

So this is persistence of the old classification, not latency of the new one. Either way it is
a lower bound on the interval, and the number that would complete it — the report date at which
each holder first prints Level 1 or 2 — would require re-reading the quarterly bulk files
without the Level-3 filter, which is a different harvest.

## The measurement

Ten names, 57 marks. Listing dates from `src/listing_dates.py`, all of them the validated ones.

| company | listing | marks | holders | first (days) | last (days) | past lock-up |
|---|---|---|---|---|---|---|
| Xiaoju Kuaizhi | 2021-06-24 | 3 | 1 | 37 | 37 | 0 |
| Allbirds | 2021-10-25 | 5 | 3 | 6 | 98 | 0 |
| Palantir | 2020-09-21 | 10 | 9 | 9 | 101 | 0 |
| ROW:33217 | 2020-12-08 | 4 | 2 | 23 | 113 | 0 |
| Rivian | 2021-11-08 | 10 | 3 | 53 | 143 | 0 |
| DraftKings | 2020-04-29 | 5 | 5 | 62 | 154 | 0 |
| Sweetgreen | 2021-11-15 | 4 | 2 | 77 | 166 | 0 |
| Honest | 2021-05-03 | 14 | 1 | 58 | 1246 | 12 |
| Toast | 2021-09-20 | 1 | 1 | 1563 | 1563 | 1 |
| Outset Medical | 2020-09-11 | 1 | 1 | 1603 | 1603 | 1 |

43 of the 57 fall inside 180 days.

## The reading that would be wrong

"Funds are slow to reclassify." Seven of the ten names have nothing at all past the customary
180-day lock-up, and inside a lock-up the shares are genuinely unsaleable — ASC 820 prices that
restriction rather than ignoring it, so a Level-3 measurement there is the accounting and not a
delay. Nine holders carrying Palantir at Level 3 at 30 September 2020, nine days after it began
trading, is what the standard asks for.

The three names that run past the lock-up are residual positions. The largest single
mark among the fourteen late rows is $260,773; Outset Medical's is $10,314 against a company
that listed four years earlier, and Toast's $78,939 is one holder. Honest is twelve of the
fourteen, one holder, one position declining from $531k to $115k over three years. Quoting
"1,603 days" without the dollar figure beside it would turn a stub into a finding.

## What this settles, and what it does not

It settles the reviewer's item A to the extent the data allows: the lag between a listing and
the end of Level-3 treatment is, for the body of the sample, bounded by the lock-up rather than
by fund behaviour.

It also closes item C — reading P4 as convergence error once a price is observable — with a
count. The sample that would carry that test is these 57 marks, on ten names,
at one to three report dates each, and 43 of them price a lock-up restriction rather than the
company. There is no cross-holder cross-date panel here to converge. The test is not deferred
for taste; it is deferred because the denominator is 57, and
`test_post_listing_marks_are_too_few_to_carry_a_convergence_test` fails if a later harvest
changes that.

The convergence question the data does support is the one §4.3 already runs: pre-IPO marks
against the offer price, in `data/ipo_validation.csv`.

## What would change the answer

A harvest of the bulk N-PORT quarters without the Level-3 filter, restricted to the 21 dated
names. That would give the promotion date directly and turn persistence into latency. It is
worth doing when the question is worth a full re-read of the quarterly files; it is not worth
doing to firm up a bound that already sits inside a lock-up.
