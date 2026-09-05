"""Guards for the Appendix B staleness test.

The test's whole value is that it rules something out, so the ways it could quietly stop
testing anything are what these assertions cover: an adjacency flag that silently never
fires, cells scored as "stale" when freshness is in fact unknowable, and a conclusion that
depends on either threshold I picked.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import mark_staleness as ms


@pytest.fixture(scope="module")
def fam_q():
    return ms.load()


def test_adjacency_flag_actually_fires(fam_q):
    """A silently-false `adjacent` would make every cell unjudgeable and the test vacuous."""
    assert fam_q.adjacent.sum() > 250
    gaps = (fam_q.q - fam_q.prev_q).dropna().map(lambda d: getattr(d, "n", None))
    assert set(gaps.unique()) == {1}, "series are contiguous; a gap would break `adjacent`"
    assert fam_q.prev_q.isna().sum() == len(fam_q) - fam_q.adjacent.sum()


def test_series_openers_are_not_scored_as_stale(fam_q):
    """A cell that opens a family's series carries no freshness evidence either way."""
    cl = ms.cells(fam_q)
    assert (~cl.judgeable).sum() > 0, "the exclusion should bite on this panel"
    # nothing unjudgeable may be counted as freshly remarked
    assert not cl.loc[~cl.judgeable, "all_remarked"].any()


def test_no_house_is_dormant(fam_q):
    """The first leg of the argument: every family refreshes in most quarters."""
    rates = ms.remark_rates(fam_q)
    assert rates.remark_rate.min() > 0.5
    assert 0.75 < fam_q[fam_q.adjacent].remarked.mean() < 0.85


def test_freshly_remarked_cells_are_not_tighter(fam_q):
    """The claim itself, stated as the negative it is."""
    cl = ms.cells(fam_q)
    ok = cl[cl.judgeable]
    fresh, stale = ok[ok.all_remarked], ok[~ok.all_remarked]
    assert len(fresh) > 50 and len(stale) > 20
    assert fresh.spread_pct.median() >= stale.spread_pct.median()


def test_conclusion_survives_both_thresholds():
    """Neither the remark tolerance nor the class guard may carry the result."""
    s = ms.sensitivity()
    for row in s["tol"] + s["guard"]:
        assert row["fresh"] > row["stale"], row
        assert row["p"] > 0.5, row
    assert ms.REMARK_TOL == 0.005 and ms.CLASS_GUARD == 4.0, "globals must be restored"


def test_clustering_does_not_carry_it():
    """105 cells over seven companies: collapse to one comparison each."""
    s = ms.sensitivity()
    assert s["n_companies"] <= 10
    assert s["companies_fresh_wider"] >= s["companies_compared"] - 1


def _cells(*rows) -> pd.DataFrame:
    """(company, quarter, family, price) tuples as the frame `level_deviation` reads."""
    return pd.DataFrame([{"company": c, "q": q, "family": f, "pps": p} for c, q, f, p in rows])


def test_both_legs_of_the_appendix_score_the_same_cells(fam_q):
    """Legs two and three answer different questions about one set of cells, and the set has
    to be one set. It was written out twice, once in `cells` and once in `level_deviation`, so
    editing the guard in one of them would have moved the spread comparison without moving the
    deviation table and nothing would have said so. `test_shared_constants` cannot reach this:
    it matches module-level constant names, and an inlined predicate has no name.

    Both sides are rebuilt here from the rule as Appendix B states it, not from `qualifies`
    itself. A test that called the function on both sides would move with any change to it and
    assert nothing, which is what the first version of this test did.
    """
    expect = set()
    for (co, q), g in fam_q.groupby(["company", "q"]):
        lo, hi = g.pps.min(), g.pps.max()
        if g.family.nunique() >= 2 and lo > 0 and hi / lo <= ms.CLASS_GUARD:
            expect.add((co, str(q)))
    assert len(expect) > 50, f"only {len(expect)} cells qualify; the check is near-vacuous"

    from_cells = {(r.company, r.quarter) for r in ms.cells(fam_q).itertuples()}
    assert from_cells == expect
    from_levels = {(co, str(q)) for (co, q), g in fam_q.groupby(["company", "q"])
                   if ms.qualifies(g) is not None}
    assert from_levels == expect


def test_the_qualifier_returns_the_range_its_callers_use(fam_q):
    """A predicate that only said yes or no would leave each caller to recompute the low and
    high, which is how the duplication started. The one that matters is `cells`: its
    `spread_pct` column has to be the same pair the guard tested."""
    for (_, _), g in fam_q.groupby(["company", "q"]):
        rng = ms.qualifies(g)
        if rng is None:
            continue
        lo, hi = rng
        assert lo == g.pps.min() and hi == g.pps.max()
        assert hi / lo <= ms.CLASS_GUARD
        break
    else:
        pytest.fail("no cell qualified, so nothing was checked")


def test_a_deviation_is_measured_against_the_median_of_its_own_cell():
    """Appendix B's third leg is a per-family deviation, and its reference point matters.

    Three families at 90, 100 and 110 have a median of 100 and a mean of 100 too, so that pair
    cannot tell the two apart. 90, 100 and 130 can: the median is still 100 and the mean is
    106.67, which would make the middle family look 6.25% low when it is exactly at the
    reference. Hand-built, because on the real panel every cell has some other explanation.
    """
    d = ms.level_deviation(_cells(("CO", "2024Q1", "X", 90.0),
                                  ("CO", "2024Q1", "Y", 100.0),
                                  ("CO", "2024Q1", "Z", 130.0)))
    assert d.loc["Y", "mean_dev_pct"] == 0.0, "the reference point is not the median"
    assert d.loc["X", "mean_dev_pct"] == -10.0
    assert d.loc["Z", "mean_dev_pct"] == 30.0


def test_a_cell_with_one_family_is_not_a_disagreement():
    """A family alone in a cell is at its own median by construction, so scoring it would
    dilute every average toward zero with rows that carry no information."""
    d = ms.level_deviation(_cells(("CO", "2024Q1", "X", 90.0),
                                  ("CO", "2024Q1", "Y", 110.0),
                                  ("SOLO", "2024Q1", "X", 50.0)))
    assert d.loc["X", "cells"] == 1, "the one-family cell was scored"


def test_the_class_guard_holds_at_the_level_test_too():
    """A 100x gap inside one cell is a unit convention, and Appendix B says so. Letting it
    through would put a family thousands of per cent from its own median and the mean
    deviation would then be a report on one artifact."""
    over = _cells(("CO", "2024Q1", "X", 1.0), ("CO", "2024Q1", "Y", 100.0))
    assert ms.level_deviation(over).empty, "a cell 100x wide survived the guard"
    under = _cells(("CO", "2024Q1", "X", 50.0), ("CO", "2024Q1", "Y", 100.0))
    assert not ms.level_deviation(under).empty, "a 2x cell was dropped; the guard is inverted"


def test_a_non_positive_price_is_dropped_rather_than_divided_by():
    """The `lo <= 0` half of the guard, on the only cell that needs it.

    With one zero and one real price the ratio is `inf`, which the class guard rejects on its
    own, so that case cannot tell whether the zero check is doing anything. A cell where EVERY
    family filed zero gives `0/0`, which is `nan`, and `nan > CLASS_GUARD` is False — so
    without the zero check the cell is admitted, its median is zero, and every deviation in it
    is `nan`. That is the row that would reach Appendix B's table.
    """
    d = ms.level_deviation(_cells(("ZEROS", "2024Q1", "X", 0.0), ("ZEROS", "2024Q1", "Y", 0.0),
                                  ("MIXED", "2024Q1", "X", 0.0), ("MIXED", "2024Q1", "Y", 100.0),
                                  ("OK", "2024Q1", "X", 90.0), ("OK", "2024Q1", "Y", 110.0)))
    assert list(d.index) == ["X", "Y"], "a zero-priced cell reached the table"
    assert (d.cells == 1).all(), "the only cell scored should be the one with real prices"
    assert not d.mean_dev_pct.isna().any()


def test_deep_discount_cohort_is_absent_from_the_fund_record():
    """The coverage asymmetry Appendix B reports: the fallen cohort carries no N-PORT marks."""
    panel = pd.read_csv(ROOT / "data" / "valuation_panel.csv")
    held = set(pd.read_csv(ROOT / "data" / "fund_marks.csv").company)
    deep = panel[panel.sector.isin(ms.DEEP_DISCOUNT_SECTORS)]
    assert len(deep) == 8
    assert not deep.company.isin(held).any()
