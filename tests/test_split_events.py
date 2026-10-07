"""The split detector, and the two ways it could be fooled.

Everything here runs offline against the committed panel. What it asserts is the set of things
that would be wrong silently: a purchase read as a split, a split missed because the price side
was held to a tolerance it does not deserve, and a confirmation count inflated by registrants.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import split_events as se


@pytest.fixture(scope="module")
def ev():
    return se.events()


def test_a_purchase_is_not_a_split():
    """The check that decides whether the detector reads anything at all.

    Doubling the shares at the same price doubles the position value; a two-for-one leaves it
    where it was. If `VALUE_BAND` ever widens to admit the first, the sample stops being splits
    and starts being trades, and every count in the note is wrong.
    """
    lo, hi = se.VALUE_BAND
    assert lo > 0.5 and hi < 2.0, "the band now admits a doubling, which is a purchase"
    assert not (lo <= 2.0 <= hi), "a value that doubled would pass as a split"
    assert lo <= 1.0 <= hi, "a value that did not move would fail as a split"


def test_the_balance_side_is_the_tight_one():
    """A share count is a count; a mark is not.

    Holding the price ratio to 1/k within a few percent — the rule as first proposed — drops
    Baron from the SpaceX event, because Baron restated at $57.41 the month Fidelity restated
    at $56.00 and both had multiplied their share count by exactly ten.
    """
    assert se.BALANCE_TOL <= 0.01, "the integer side has gone loose"


def test_the_events_are_confirmed_by_houses_not_registrants(ev):
    """Four T. Rowe series are one confirmation. Counting the trust inflates it."""
    assert not ev.empty
    assert (ev.houses >= se.MIN_HOUSES).all()
    assert (ev.registrants >= ev.houses).all()
    assert (ev.registrants > ev.houses).any(), "no multi-registrant house left to collapse"
    lag = se.restatement_lag()
    assert lag["houses_inflated_by_counting_registrants"] > 1.2


def test_restatement_is_not_simultaneous(ev):
    """The finding that makes a one-month window the wrong unit.

    If houses restated together the span would be zero everywhere and the window would cost
    nothing. This fails if that ever becomes true, because then the note is wrong.
    """
    assert ev.restatement_span_days.max() > 31
    inside_a_month = int((ev.restatement_span_days <= 31).sum())
    assert inside_a_month < len(ev), "every event now fits in a month; re-read the note"


def test_the_databricks_three_for_one_is_there(ev):
    """Fourteen houses inside two months in the autumn of 2022 — the anchor event."""
    db = ev[(ev.company == "NM:PROJECT DEBUSSY") & (ev.k == 3)]
    assert len(db) == 1, "the Databricks event has split or vanished"
    r = db.iloc[0]
    assert r.houses >= 10 and r.funds >= 50
    assert r.first_dt.startswith("2022-") and r.last_dt.startswith("2022-")


def test_a_ratio_of_ninety_nine_is_flagged_rather_than_believed(ev):
    """Carbon Health at 99 and Pine Private at 127 are arithmetic, not corporate actions."""
    assert (~ev.canonical_k).any(), "nothing is flagged; the canonical list has gone permissive"
    assert ev.canonical_k.sum() >= 15, "most events should still be at a real split ratio"
    assert 99 not in se.CANONICAL_K and 127 not in se.CANONICAL_K


def _two_house_split(k: int = 2, desync_price: float = 1.0) -> pd.DataFrame:
    """One company, two houses, a k-for-one split that H2 restates a month after H1.

    Hand-built so the answer is known rather than read back off the panel. Both funds hold
    $1,000 of the same company throughout, which is what a split does to a position: the share
    count multiplies and the value does not move. `desync_price` scales H1's post-split mark,
    so a caller can ask what happens when the two houses do not agree on the new price.
    """
    rows = []
    for fund, house, cik, jump in [("F1", "H1", 1, "2024-02-29"), ("F2", "H2", 2, "2024-03-31")]:
        for dt in ("2024-01-31", "2024-02-29", "2024-03-31"):
            after = dt >= jump
            bal = 100 * k if after else 100
            val = 1000 * (desync_price if (after and fund == "F1") else 1.0)
            rows.append({"company": "TESTCO", "fund": fund, "house": house, "CIK": cik,
                         "dt": pd.Timestamp(dt), "balance": bal, "val_usd": val,
                         "pps": val / bal})
    return pd.DataFrame(rows)


def test_a_mid_restatement_cell_is_split_by_exactly_k():
    """The prediction the mechanism has to make, on an event whose answer is arithmetic.

    H1 restates a two-for-one in February and H2 not until March, so at the February date the
    two are quoting one security in units that differ by exactly two: $10.00 against $5.00.
    `validate` has to find that one date, put one fund on each side, and return a ratio of 2.
    Read off the committed panel this check would be circular — the ratio would be whatever the
    data says. Built by hand it is 2.0 or the mechanism is wrong.
    """
    d = _two_house_split(k=2)
    ev = se.events(d)
    assert len(ev) == 1 and ev.iloc[0].k == 2 and ev.iloc[0].houses == 2

    v = se.validate(d)
    assert len(v) == 1, f"expected the one mid-restatement date, got {len(v)}:\n{v}"
    r = v.iloc[0]
    # `r["dt"]`, not `r.dt`: on a Series the attribute is pandas' datetime accessor, which
    # raises rather than returning the column and would fail this test for the wrong reason.
    assert r["dt"] == "2024-02-29"
    assert (r.funds_restated, r.funds_not) == (1, 1)
    assert r.pps_not_restated == 10.0 and r.pps_restated == 5.0
    assert abs(r.observed_ratio - 2.0) < 1e-9
    assert r.residual_pct < 1e-9


def test_the_ratio_is_not_forced_to_k_by_construction():
    """The other direction, which is what makes the check above evidence rather than algebra.

    If `validate` computed the ratio from `k` it would report 2.0 whatever the filings said.
    Move H1's post-split mark 10% and the residual has to move with it: the two sides are
    $10.00 and $5.50, a ratio of 1.818, which is 9.1% away from two.
    """
    v = se.validate(_two_house_split(k=2, desync_price=1.1))
    assert len(v) == 1
    r = v.iloc[0]
    assert abs(r.observed_ratio - 10.0 / 5.5) < 1e-9
    assert abs(r.residual_pct - 9.0909) < 1e-3, "the residual is not reading the filed prices"


def test_a_cell_nobody_has_restated_yet_is_not_scored():
    """`validate` reports the ratio between two groups, so it needs both to exist.

    A date where every fund has restated, or none has, carries no comparison. The February
    date above is the only one of the three that does: in January neither house has moved and
    in March both have.
    """
    v = se.validate(_two_house_split(k=2))
    assert set(v.dt) == {"2024-02-29"}, "a one-sided date has been scored as a comparison"


def test_the_guard_overlap_is_measured_and_small():
    """The consequence that did not hold, asserted so it cannot be quietly upgraded.

    The proposal was that §5's 4x guard is largely absorbing restatement desync. It is not:
    around one percent of the cells the guard drops sit inside a restatement window.
    """
    ov = se.guard_overlap()
    assert ov["cells_dropped_by_guard"] > 1000
    assert ov["share_pct"] < 5, "the overlap has grown; the guard may need re-reading"
    assert ov["inside_a_restatement_window"] > 0, "the overlap is zero; check the windows"
