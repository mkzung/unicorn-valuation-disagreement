"""The N-CSR schedule parser, checked against the layouts it was calibrated on.

Everything here runs offline against the committed extract. What it asserts is the set of
things that were wrong in the first version and would be wrong again silently: the column
order, the thousands scale, the currency sign glued to a number, and a two-digit year.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import ncsr_acquisitions as na
import population as pop


@pytest.fixture(scope="module")
def rows():
    return na.load()


def test_the_header_decides_the_columns_not_their_order():
    """The two layouts in the sample disagree, and assuming either one breaks the other."""
    ark = "Acquisition Date   Shares/ Principal/ Units   Cost   Value  COMMON STOCKS"
    cap = ("Acquisition date(s) Cost (000) Value (000) Percent of net assets "
           "Anthropic, PBC, Class G-1, preferred shares (a)(b) 1/27/2026")
    assert na.header_spec(ark) == (["acq", "shares", "cost", "value"], False)
    assert na.header_spec(cap) == (["acq", "cost", "value", "pct"], True)


def test_a_security_title_is_not_a_column_heading():
    """"preferred shares" in the first data row is what the gap rule exists to reject."""
    cap = ("Acquisition date(s) Cost (000) Value (000) Percent of net assets "
           "Anthropic, PBC, Class G-1, preferred shares")
    assert "shares" not in na.header_spec(cap)[0]


def test_money_cells_survive_a_glued_currency_or_percent_sign():
    """`$98,961` in one cell and `$` in its own cell are both the same number."""
    assert na._num("$98,961") == 98961
    assert na._num("(1,200)") == -1200
    assert na._num("0.44  %") == 0.44
    assert all(na.MONEY.match(c) for c in ["$98,961", "224,936", "0.44  %", "(1,200)"])


def test_two_digit_years_parse(rows):
    """Half the file writes 12/17/24 and the default parser answers NaT without saying so."""
    assert rows.acq.notna().all()
    assert rows.acquired.str.match(r"\d{1,2}/\d{1,2}/\d{2}$").any(), "no two-digit years left"


def test_the_ark_lot_is_the_one_the_filing_shows(rows):
    """SpaceX, 31 October 2023, 75,356 shares at $6,999,961 — accession 0001213900-24-086293.

    Asserted on the lot rather than on the first SpaceX row, because the same acquisition
    date comes back from several filings with different share bases: $92.89 against a
    $185.00 mark in one and $84.00 against $420.99 in another. That inconsistency is the
    reason `markup_pct`, a ratio inside one row, is the quantity this module reports and
    `cost_per_share` is not.
    """
    r = rows[(rows.company == "SpaceX") & rows.cost_per_share.notna()]
    if r.empty:
        pytest.skip("no SpaceX row in this harvest carries a share count")
    assert (r.cost_per_share.sub(92.89).abs() < 0.01).any(), \
        f"the $92.89 lot is gone; prices present: {sorted(r.cost_per_share.round(2))}"


def test_thousands_are_scaled(rows):
    """A lot filed in thousands has to come back in dollars, checked against a filer who is not.

    The first version of this test asserted a floor — a thousands lot is at least a million
    dollars — and it held only because the sample was forty filings of large funds. At four
    hundred it fails on a real $2,000 sleeve. The invariant that does not depend on position
    size is the one across filers: Anthropic's Class F lot is filed by Capital Group in
    thousands and by Alger in dollars, and both must land on the same number.
    """
    cap = rows[rows.in_thousands]
    assert not cap.empty and (cap.cost > 0).all()
    # The scale is a property of the table, so it is asserted on the table selector rather
    # than on a magnitude. Two headers, the second in thousands: a table sitting after the
    # second must take the second, which is what Brighthouse and Transamerica need.
    marks = [(0, (["acq", "shares", "cost", "value"], False)),
             (500, (["acq", "cost", "value", "pct"], True))]
    assert na.header_for(600, 50, marks) == marks[1][1]
    assert na.header_for(100, 50, marks) == marks[0][1]
    assert na.header_for(490, 100, marks) == marks[1][1], "a header inside the table governs it"
    # And one lot in the extract really is filed at two scales, so the branch is exercised.
    lot = rows[(rows.company == "Databricks") & (rows.series == "K")
               & (rows.acquired == "9/8/2025") & (rows.period == "2026-02-28")]
    assert lot.in_thousands.nunique() == 2, "the mixed-scale lot has left the extract"
    assert lot.cost.min() > 1e5, "a lot filed in thousands was left unscaled"


def test_registrants_are_collapsed_to_houses(rows):
    """Alger Funds and Alger Institutional Funds are one opinion, not two."""
    assert rows.house.notna().all()
    a = na.agreement(rows)
    assert (a.registrants >= a.houses).all()
    assert (a.registrants > a.houses).any(), "no multi-registrant house left to collapse"


def test_series_and_class_are_the_same_letter():
    got = pop.extract_series(pd.Series([
        "Databricks, Inc. (Series L Preferred Stock) (b)(c)",
        "Databricks, Inc., Class L, preferred shares (a)(b)",
        "Databricks,  Inc., Series J",
        "Stripe, Inc."]))
    assert got.tolist()[:3] == ["L", "L", "J"]
    assert pd.isna(got.iloc[3])


def test_one_tranche_written_two_ways_is_one_key():
    """"Series A-2" and "Series A2" are one tranche and the filings carry both spellings.

    Captured as written they are two keys, so a shared acquisition date joins neither to the
    other and §2.3 scores two houses on one series as holding two. The panel writes A-2 1,355
    times and A2 465, so neither spelling is a typo that could be dropped.
    """
    got = pop.extract_series(pd.Series([
        "Anthropic PBC, Series A-2 preferred", "Anthropic PBC, Series A2 preferred",
        "Acme, Class C-10 shares", "Acme, Class C10 shares"]))
    assert got.tolist() == ["A-2", "A-2", "C-10", "C-10"]


def test_every_date_spelling_a_filer_uses_parses():
    """Two spellings of one lot split it in half, and the gap disappears with it.

    A naive group on the raw string returns 65 lots where the normalised key returns 55,
    because filers write 12/16/2025 and 12/16/25 for the same day. A month name would do the
    same, so the pattern takes one and the parser is told the format is mixed.
    """
    for spelling in ["12/16/2025", "12/16/25", "Dec 16, 2025", "December 16, 2025"]:
        assert na.DATE.search(spelling), f"{spelling} is not matched"
    parsed = pd.to_datetime(pd.Series(["12/16/2025", "12/16/25", "Dec 16, 2025"]),
                            format="mixed")
    assert parsed.nunique() == 1


def test_the_wrapper_rule_agrees_with_section_4_4(rows):
    """Two modules must answer "who is the holder" the same way.

    `fund_marks.WRAPPER` is the rule §4.3 uses on the marks; it is applied here to the same
    security titles. A fifth of these rows are positions held through an SPV, whose cost and
    value belong to the vehicle. None of the three cross-house lots is one, which is what
    makes them usable, and this fails if that ever stops being true.
    """
    assert rows.wrapper.any(), "the wrapper rule now matches nothing; check it still runs"
    a = na.agreement(rows)
    multi = a[a.houses > 1]
    assert (multi.wrappers == 0).all(), "a cross-house lot now rests on a vehicle position"


def test_the_valuation_date_is_the_unit_not_the_filing_date(rows):
    """The correction that retracted this module's first result.

    A markup is value over cost as of the period a filing covers. Keying on the acquisition
    date alone and filtering on how far apart the filings were *filed* compared two houses at
    two different valuation dates: a December annual and an April semi-annual reach EDGAR 119
    days apart and value the position five months apart. Three cross-house gaps of eight to
    twelve points were published on that key and every one was a period mismatch.
    """
    a = na.agreement(rows)
    assert "period" in a.columns and a.period.notna().all()
    assert (a.period_span_days == 0).all(), "an exact-period group spans two valuation dates"


def test_the_near_simultaneous_pairs_agree_where_the_periods_meet(rows):
    """Widening to a month admits nine pairs, and the gap tracks the period distance.

    The one pair whose periods are a single reporting step apart on the same lot — ARK at 31
    January against Alger at 31 December on Databricks Series K — agrees to seven decimals.
    """
    near = na.agreement(rows, tol=na.NEAR_PERIOD)
    nm = near[near.books > 1]
    assert len(nm) >= 5
    assert not nm[nm.markup_gap_pts.abs() < 0.01].empty


def test_a_house_moves_its_own_mark_between_periods(rows):
    """The quantity the old key was accidentally measuring, and it is large."""
    hd = na.house_drift(rows)
    assert len(hd) >= 10
    assert hd.drift_pts.median() > 5


def test_within_a_house_at_one_date_the_mark_is_one_number(rows):
    """§4.2 in a second source, once blended lots are out.

    A row spanning two purchases carries a blended cost, and two funds of one house with
    different weights on each purchase then differ by construction. Including them produced a
    13.8-point within-house spread that read like a counterexample and was arithmetic; on
    single-lot rows the largest is 1.2 points.
    """
    wh = na.within_house(rows)
    blended = na.within_house(rows, single_lot=False)
    assert len(wh) >= 10
    assert wh.spread_pts.median() < 0.01
    assert wh.spread_pts.max() < 2, "a single-lot within-house spread has opened up"
    assert blended.spread_pts.max() > 10, "the blended artifact is gone; re-read the note"


def test_the_markup_level_needs_no_matching_fiscal_year(rows):
    """Cost is a fact about a purchase; only the mark is a fact about a date.

    So the entry comes from N-CSR at any period and the mark from N-PORT on the report dates
    §5 already fixes. What it gives is a level; it gives no new cross-house test, because
    dividing two marks by one entry leaves their ratio alone.
    """
    t = na.nport_markup(rows)
    assert not t.empty and (t.entry_pps > 0).all()
    assert t.groupby(["company", "house"]).report_date.nunique().max() > 3


def test_a_share_basis_break_is_caught_rather_than_averaged(rows):
    """ARK's SpaceX mark steps $185 to $1,017 between two report dates; that is not a
    revaluation, and a level computed across it is meaningless."""
    t = na.nport_markup(rows)
    assert t.basis_break.any() and not t.basis_break.all()
    assert "SpaceX" in set(t[t.basis_break].company)


def test_one_document_can_carry_two_layouts(rows):
    """The bug the wider harvest exposed, and the reason 155 rows have a share count and 184 did.

    Brighthouse's N-CSR prints nine main-schedule headers — Acquisition Date, Shares, Cost,
    Value, in dollars — and then twelve restricted-note headers: Acquisition date(s), Cost,
    Value, Percent of net assets, in thousands. Reading the first and applying it to the whole
    file put Anthropic's Class F lot at minus a hundred percent, because $0.28 of "percent of
    net assets" landed in the value column. Transamerica failed the same way more quietly, in
    the scale rather than the order, and the markup survived it because a markup is a ratio.
    """
    f = rows[(rows.company == "Anthropic") & (rows.series == "F")
             & (rows.acquired == "8/29/2025") & (rows.period == "2025-12-31")]
    assert len(f) >= 5, "the Anthropic Class F lot has left the extract"
    assert f.markup_pct.round(4).nunique() == 1, "one lot, one date, several readings"
    assert f.cost.max() / f.cost.min() == 1, "a filer's thousands scale is being misread"
    assert rows.markup_pct.min() > -99.9, "a column shift is back: value is reading as a percent"


def test_a_nested_table_does_not_truncate_the_schedule():
    """EDGAR nests tables for layout, so the closing tag has to be counted, not matched."""
    html = "<table><tr><td>A<table><tr><td>inner</td></tr></table>B</td></tr></table><table>x</table>"
    blocks = na.table_blocks(html)
    assert len(blocks) == 2
    assert blocks[0][1].count("</table>") == 2 and "B" in blocks[0][1]


def test_seven_sponsors_filing_one_cost_are_one_opinion(rows):
    """Canva's Series A-3 lot, seven registrants under seven sponsors, one set of figures.

    Counting house labels made it seven opinions and a 10.5-point disagreement; the ten and a
    half points were the distance between a $2,000 thousand sleeve and a $31,000 thousand one,
    both Capital Group's. `shared_books` joins houses that file a cost and a value agreeing to
    the dollar, which collapses this to one book and the gap to zero.
    """
    g = rows[(rows.company == "Canva") & (rows.series == "A-3")
             & (rows.acquired == "11/4/2021") & (rows.period == "2023-06-30")]
    assert g.house.nunique() >= 6
    assert na.shared_books(g) == 1
    a = na.agreement(rows)
    # The merge joins houses that file identical cost and value, so it can only ever reduce the
    # count. A lot with more books than houses would mean the merge had split one house's book
    # in two, which is the failure that would fabricate a disagreement out of sleeve structure.
    # This assertion carried `or True` for three rounds, which made the one guard on that
    # invariant in the whole suite a tautology.
    over = a[a.books > a.houses]
    assert over.empty, f"{len(over)} lot(s) have more books than houses:\n{over.head()}"
    assert int((a.houses > 1).sum()) > int((a.books > 1).sum()), "the sleeve merge does nothing"


def test_the_year_end_ratio_is_what_fixes_the_entry_price(rows):
    """Not the zero at the start — that row is consistent with any pair of entry prices.

    A markup is value over cost, so a fresh position marked at what it cost prints 0.0000
    whatever it cost. An earlier version of this test asserted those zeros and called the entry
    price established; they establish nothing. What does is 31 December 2025, where four rows on
    four different cost bases print one ratio, and two of them disclose the share count that
    turns the ratio into $92.50 in and $190.00 out.
    """
    from fractions import Fraction
    j = na.series_j(rows)
    dec = j[j.period == "2025-12-31"]
    assert len(dec) == 4 and dec.cost.nunique() == 4, "the four bases are no longer four"
    assert (dec.ratio - 76 / 37).abs().max() < 1e-6, "the ratios no longer agree"
    exact = sum(Fraction(int(v), int(c)) == Fraction(76, 37)
                for c, v in zip(dec.cost, dec.value))
    assert exact >= 3, "the ratio is no longer exactly 76/37 on three of the four rows"
    priced = dec[dec.shares.notna()]
    assert len(priced) == 2
    assert (priced.entry_pps == 92.50).all() and (priced.mark_pps == 190.00).all()
    # And the divergence sits between two dates on which the basis is common.
    jun = j[j.period == "2025-06-30"].groupby("house").ratio.median()
    assert (jun["Alger"] - jun["Brighthouse"]) * 92.50 > 10, "the June gap has closed"


def test_january_and_december_are_one_round_at_one_price(rows):
    """Brighthouse files the same lot under two acquisition dates and one entry price.

    Trust II carries 21 January 2025 where Trust I carries 17 December 2024, and both give
    $92.50 a share. A second route to the common basis, independent of the year-end ratio.
    """
    j = na.series_j(rows)
    by_date = j[j.shares.notna()].groupby("acquired").entry_pps.median()
    assert set(by_date.index) == {"12/17/24", "01/21/25"}
    assert by_date.nunique() == 1 and by_date.iloc[0] == 92.50


def test_the_cross_book_comparisons_mostly_agree(rows):
    """What the uncapped harvest bought: 45 cross-book comparisons where the earlier cap gave 1.

    Same company, same series, same acquisition lot, same valuation date, and two books that
    do not share a cost. Most agree to a hundredth of a point. The exceptions are the newest
    rounds, which is where a mark has the least to anchor to.
    """
    a = na.agreement(rows)
    books = a[a.books > 1]
    assert len(books) >= 30, "the cross-book sample has collapsed; check the harvest"
    assert (books.markup_gap_pts <= 0.01).mean() > 0.6
    assert books.markup_gap_pts.max() > 5, "the disagreements are gone; re-read the note"
