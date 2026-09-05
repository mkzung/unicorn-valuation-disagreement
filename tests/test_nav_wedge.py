"""What the disagreement costs in NAV, and the four ways that measure could be wrong."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import nav_wedge as nw
import population as pop


@pytest.fixture(scope="module")
def pos():
    return nw.positions()


def test_the_wedge_is_the_arithmetic_it_claims_to_be(pos):
    """Recompute the headline quantity from raw fields on the single largest row.

    A derived column agreeing with itself proves nothing; this checks the definition against
    the four numbers a reader would use — balance, value, consensus price, net assets — on a
    record picked for being the one the paper quotes.
    """
    r = pos.loc[pos.wedge_bps.abs().idxmax()]
    by_hand = (r.val_usd - r.balance * r.consensus_pps) / r.net_assets * 1e4
    assert abs(by_hand - r.wedge_bps) < 1e-6
    # and the shorthand the prose uses: position share of NAV times the deviation
    approx = r.position_pct_of_nav * (1 - r.consensus_pps / r.own_pps) * 100
    assert abs(approx - r.wedge_bps) < 1e-6


def test_a_fund_at_the_consensus_carries_no_wedge(pos):
    """Zero by construction, and worth asserting: a sign error here would be invisible."""
    at = pos[(pos.own_vs_consensus_pct.abs() < 1e-9)]
    assert len(at) > 50, "too few funds sit at the consensus for this check to mean anything"
    assert at.wedge_bps.abs().max() < 1e-6


def test_the_one_price_filter_removes_funds_whose_own_lines_disagree():
    """The filter that killed the Claire's Stores row, asserted on the case that produced it.

    JPMorgan files two lines for Claire's in each fund, at $10.00 and $1,765.66, and the
    value-weighted blend of the two is not a price. If this filter ever stops firing, the
    largest wedge in the paper goes back to being an artifact.
    """
    d, _ = pop.panel()
    f = nw.fund_positions(d)
    multi = f[~f.one_price]
    assert len(multi) > 100, "no fund files two prices for one company — check the tolerance"
    assert (multi.hi_line / multi.lo_line).max() > 10
    kept = nw.positions(d, one_series=False, venture_only=False)
    assert kept.merge(multi[["company", "dt", "fund"]],
                      on=["company", "dt", "fund"]).empty


def test_each_filter_cuts_the_tail_it_was_added_for():
    """The three selections exist because of the tail, so the tail is what they must move.

    Appendix G.1 makes two claims about *which* filter does it, and both are asserted here rather
    than one blanket "the max falls a lot". The one-series filter thins the body and barely
    moves the extreme; the venture filter is the one that cuts the extreme.
    The first version of this test asserted a factor of three against a then-current 4.4x,
    which is a magic constant that says nothing about either claim — and it duly failed for
    the wrong reason when a group-key fix moved the panel to 2.9x.
    """
    fc = nw.filter_cost().set_index("selection")
    allc, one, vent = fc.loc["all comparable cells"], fc.loc["+ one series only"], \
        fc.loc["+ venture-backed only"]
    # Not equality. The one-series filter used to leave the maximum untouched at 460.0, and
    # the corrected series pattern removes the position that carried it: 460.0 -> 444.4, three
    # percent, against a third of the positions gone. The claim Appendix G.1 makes is that this
    # filter is not the tail filter, so what is asserted is the ratio of the two effects.
    assert (allc.max_abs_bps - one.max_abs_bps) / allc.max_abs_bps < 0.10, \
        "Appendix G.1 says the one-series filter thins the body and barely touches the extreme"
    assert vent.max_abs_bps < one.max_abs_bps * 0.5, \
        "Appendix G.1 says the venture filter is the one that moves the tail"
    assert one.over_10bps < allc.over_10bps, "the one-series filter thins the body"
    assert vent.over_10bps < one.over_10bps


def test_the_biased_reversion_design_overstates_the_unbiased_one(pos):
    """Both designs are run precisely so the gap between them is a number.

    If the two ever agree, the argument for the lagged selection is gone and the section
    should say so rather than keep asserting a bias it can no longer measure.
    """
    lagged, same = nw.reversion(pos, lagged=True), nw.reversion(pos, lagged=False)
    assert not lagged.get("underpowered") and not same.get("underpowered")
    assert same["neg_share_pct"] > lagged["neg_share_pct"] + 2, (
        "the mechanically biased design no longer overstates reversion; re-read the section")
    assert lagged["neg_share_pct"] > 50
    # This used to assert `p_sign < 0.05`, and it passed at 0.039 — a figure produced by
    # `idxmax` picking one of several houses tied for the top of the cell. Averaging over the
    # tied houses instead, which is what "the top house" means when several occupy the
    # position, gives 0.085. The section says so. Pinned on the far side so that a change
    # which restores significance has to argue for itself rather than arrive quietly.
    assert 0.05 <= lagged["p_sign"] < 0.5, (
        f"the unbiased reversion's one-sided sign p is {lagged['p_sign']:.4f}; Appendix G.3 "
        "is written around a tilt that does NOT clear five per cent, so if this has moved, "
        "the prose has to move with it")


def test_the_reversion_survives_a_perturbation_the_size_of_a_libm_difference(pos):
    """The answer must not turn on the last bits of a logarithm.

    Shuffling the rows is not the probe, though the first version of this test thought it was.
    `_dev_panel` groups and then sorts by company, house and date, so the order the panel
    arrives in cannot reach the tie-break, and that version passed with `idxmax` restored.

    What does reach it: 40 of the 421 cells the unbiased design reports have two or more
    houses at the top within `ZERO`, and in 16 of them those houses are not bit-identical, so
    `idxmax` picks between them on rounding. Multiplying every price by 1 ± 1e-15, the size of
    a disagreement between two implementations of `log`, moved the shipped design from 226 of
    415 to 223 of 412 and its one-sided sign p from 0.039 to 0.052 — across a conventional
    threshold, on the same data. Averaging over the tied houses does not move at all.
    """
    rng = np.random.default_rng(20260827)
    jit = pos.copy()
    for col in ("house_pps", "consensus_pps"):
        jit[col] = jit[col] * (1 + rng.uniform(-1e-15, 1e-15, len(jit)))
    assert not jit.house_pps.equals(pos.house_pps), "the perturbation did nothing"
    for lagged in (True, False):
        a, b = nw.reversion(pos, lagged=lagged), nw.reversion(jit, lagged=lagged)
        assert (a["cells"], a["negative"], a["untied"]) == \
               (b["cells"], b["negative"], b["untied"]), (
            f"lagged={lagged}: a perturbation in the fifteenth digit moved the counts from "
            f"{a['negative']}/{a['untied']} to {b['negative']}/{b['untied']}")
        assert abs(a["p_sign"] - b["p_sign"]) < 1e-12


def test_a_tied_extreme_is_averaged_not_picked():
    """Two houses tied at the top, moving opposite ways, contribute their average.

    The synthetic panel is the case the real one has 40 of at the top: a high deviation two
    houses share, and different next moves. ALPHA and BRAVO both sit at 110 against a
    consensus of 100, so their deviations are bit-identical and nothing but the rule separates
    them. ALPHA then rises to 143 and BRAVO falls to 99, so the two answers are far apart:
    averaged the cell contributes 7.85 points, picked it contributes 26.24, and the assertion
    is on what `reversion` returns rather than on a second copy of the arithmetic — which is
    what the first version of this test checked, and why it stayed green with the picking
    restored.
    """
    rows = [{"company": f"CO{i:02d}", "dt": dt, "house": h,
             "house_pps": pps, "consensus_pps": 100.0}
            for i in range(12)
            for h, first, second in (("ALPHA", 110.0, 143.0), ("BRAVO", 110.0, 99.0),
                                     ("CHARLIE", 90.0, 90.0))
            for dt, pps in (("2024-03-31", first), ("2024-06-30", second))]
    p = pd.DataFrame(rows)
    p["dt"] = pd.to_datetime(p.dt)
    r = nw.reversion(p, lagged=False)
    assert not r.get("underpowered"), "the fixture fell below the power floor; add companies"
    assert r["cells"] == 12, f"expected one usable cell per company, got {r['cells']}"
    assert abs(r["median_diff_pct"] - 7.8502) < 1e-3, (
        f"the cell contributed {r['median_diff_pct']:.4f} points; 7.8502 is the average of the "
        "two tied houses and 26.2364 is what picking the first of them gives")


def test_the_sign_test_points_at_the_hypothesis(pos):
    """A p-value pointed backwards reads as a clean null while the data says the opposite.

    The first version of `reversion` asked whether NEGATIVES were rarer than half and got
    0.99 on data where they are commoner. This pins the direction.
    """
    r = nw.reversion(pos, lagged=True)
    assert r["negative"] > r["untied"] / 2
    assert r["p_sign"] < 0.5, "the alternative is pointed away from the observed direction"


def test_deviations_are_more_persistent_than_they_are_reverting(pos):
    """The two halves of Appendix G.3 have to be consistent with each other."""
    p = nw.persistence(pos)
    assert not p.get("underpowered")
    assert 0.5 < p["slope"] < 1.0
    assert p["same_side_pct"] > 60


def test_the_committed_statistics_match_the_current_design():
    """Same contract as the event study's: the guard pins prose against a committed file, so
    the file carries a hash of its own inputs and this fails when they move.

    If this fails, re-run `python3 src/nav_wedge.py`; do not edit the key.
    """
    t = pd.read_csv(nw.STATS)
    assert t.design_key.nunique() == 1
    assert t.design_key.iat[0] == nw.design_key(), (
        "data/nav_wedge_stats.csv was produced under different inputs; re-run src/nav_wedge.py")
    assert len(t) > 50 and t.value.notna().all()


def test_every_statistic_the_manuscript_quotes_is_in_the_committed_file():
    s = nw.load_stats()
    for name in ("positions", "companies", "funds", "houses", "fund_dates", "booked_busd",
                 "gross_wedge_busd", "median_abs_bps", "max_abs_bps", "n_over_material",
                 "funds_over_material", "n_over_100bps", "median_private_pct_of_nav",
                 "max_private_pct_of_nav", "rev_lagged_neg_share_pct", "rev_lagged_p_sign",
                 "rev_same_neg_share_pct", "persistence_slope", "persistence_same_side_pct"):
        assert name in s.index, f"{name} missing from {nw.STATS.name}"


def test_the_section_does_not_overstate_what_it_found():
    """The result is partly negative and the manuscript has to keep saying so.

    A later edit that quietly promotes 0.21 basis points into a systemic finding is exactly
    the drift no numeric guard would see, because no number would move.
    """
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    body = draft.split("## Appendix G. What the disagreement costs")[1].split("## References")[0]
    assert "partly negative answer" in body
    assert "not, on this evidence, a systemic mispricing" in body
    assert "does not establish that anyone *acts* on the wedge" in body


def test_the_committed_panel_and_the_in_memory_panel_agree():
    """The same numbers whether the panel is round-tripped through CSV or not.

    The first version decided `chg == 0` and `sign(a) == sign(b)` by raw float equality, and
    reading `data/nav_wedge.csv` back gave 481 cells where memory gave 498 — the same data,
    a different answer, which is precisely what the replication note says this repository
    does not have. Tolerance-based comparisons make the two paths agree.
    """
    live = nw.reversion(nw.positions(), lagged=True)
    from_disk = pd.read_csv(nw.OUT, parse_dates=["dt"])
    disk = nw.reversion(from_disk, lagged=True)
    assert disk["cells"] == live["cells"]
    assert disk["negative"] == live["negative"] and disk["untied"] == live["untied"]
    assert abs(disk["neg_share_pct"] - live["neg_share_pct"]) < 1e-9


def _rev_cells(p, guard: bool) -> int:
    """`reversion`'s cell count with the tie guard forced on or off.

    A copy of the loop rather than a flag on `reversion`, because a flag that exists only
    to be switched off in a test is a way for the wrong branch to ship.
    """
    h = nw._dev_panel(p)
    ok = h.step_ok & h.dev_lag.notna() & h.chg_next.notna() & h.lag_ok
    z = nw.ZERO if guard else 0.0
    n = 0
    for _, g in h[ok].groupby(["company", "dt"]):
        if guard and g.dev_lag.max() - g.dev_lag.min() <= z:
            continue
        # Mirrors `reversion`'s averaging over a shared extreme. A counterfactual that
        # measures a design the module no longer runs is not a counterfactual.
        hi = g.chg_next[g.dev_lag >= g.dev_lag.max() - z].mean()
        lo = g.chg_next[g.dev_lag <= g.dev_lag.min() + z].mean()
        if abs(hi) <= z and abs(lo) <= z:
            continue
        n += 1
    return n


def test_the_tie_guard_is_what_makes_the_two_paths_agree(pos):
    """The guard has to be doing work, and Appendix G.3 quotes how much.

    The test above shows the two paths agree. On its own that is compatible with the guard
    being unnecessary — which is what the manuscript claimed for one round, at a number
    ("fourteen") no configuration of this panel reproduces. So the counterfactual is
    measured here: with the guard removed and float equality restored, the in-memory panel
    gives 529 cells and the same panel read back from CSV gives 527, and Appendix G.3 prints both.

    Exact counts, not a band. A tolerance would let the paper's number drift away from the
    code's while the test stayed green, which is the failure that put "fourteen" in print.
    """
    disk = pd.read_csv(nw.OUT, parse_dates=["dt"])
    assert _rev_cells(pos, guard=True) == _rev_cells(disk, guard=True), \
        "with the guard on, the two paths must agree exactly"
    live_off, disk_off = _rev_cells(pos, guard=False), _rev_cells(disk, guard=False)
    assert (live_off, disk_off) == (540, 538), \
        f"Appendix G.3 says 540 -> 538 without the guard; got {live_off} -> {disk_off}"


def test_the_manuscript_quotes_the_tie_guard_numbers_it_measured():
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    body = draft.split("### G.3")[1].split("### G.4")[0]
    assert "540 to 538" in body, "Appendix G.3 no longer quotes the counterfactual it is pinned to"
    assert "fourteen" not in body, "the unreproducible number is back"


def test_a_missing_series_id_is_recognised_in_every_spelling_the_filings_use():
    """`_no_series` decides which fund-dates Appendix G reports separately, and the filings do
    not spell "absent" one way. Two of these arrive as the strings "None" and "nan" because a
    CSV round trip turns a null into text, and a mask that misses them puts vehicles with no
    series identifier into the identified group, where their wedge is attributed to a fund that
    does not exist. The last row is the direction that matters more: a real identifier with
    whitespace around it must NOT be read as absent.
    """
    fd = pd.DataFrame({"SERIES_ID": ["S000012345", None, "", "   ", "None", "nan",
                                     "  S000099999  ", float("nan")]})
    got = list(nw._no_series(fd))
    assert got == [False, True, True, True, True, True, False, True], got


def test_the_band_is_symmetric_and_never_below_one():
    """The class guard compares a position's price to its cell's consensus, and the comparison
    has to be the same whichever way the pair is written. A one-sided ratio would guard against
    prices that are too high and let every price that is too low through, which is the half
    that carries First Trust's $1.00 Epic Games row.
    """
    p = pd.DataFrame({"own_pps": [100.0, 400.0, 25.0, 637.0], "consensus_pps": [100.0] * 3 + [1.0]})
    band = list(nw._band(p))
    assert band[0] == 1.0
    assert band[1] == band[2] == 4.0, "the band is not symmetric"
    assert band[3] == 637.0
    assert min(band) >= 1.0


def test_the_class_guard_removes_what_it_is_documented_to_remove(pos):
    """Appendix F.2's example is the justification for the filter, so it is recomputed with the
    filter rather than described beside it. Two things are asserted that the registry's pinned
    values cannot see: that every removed row really does breach the band, and that the row the
    appendix calls the worst is the worst by DOLLARS of wedge rather than by the band itself.
    A row can be 600x out of line and move nothing if the fund holds four shares of it.
    """
    c = nw.class_guard_cost()
    assert c["removed_positions"] > 0
    assert c["worst_consensus_pps"] / c["worst_pps"] > pop.CLASS_GUARD

    unguarded = nw.positions(_skip_class_guard=True)
    bad = unguarded[nw._band(unguarded) > pop.CLASS_GUARD]
    assert len(bad) == c["removed_positions"]
    assert (nw._band(bad) > pop.CLASS_GUARD).all(), "a row inside the band was removed"
    by_dollars = (bad.val_usd - bad.balance * bad.consensus_pps).abs()
    assert bad.loc[by_dollars.idxmax()].own_pps == c["worst_pps"], (
        "the worst row is not the one that moves the most money")
    assert len(unguarded) > len(pos), "the guard removed nothing; the comparison is vacuous"


def test_a_house_at_the_consensus_is_not_counted_as_agreeing_with_itself(pos):
    """Half the house-dates are the median house, whose deviation is zero by construction.

    `sign(0) == sign(0)` is True, so the first version scored every one of them as "on the
    same side one step later" and diluted the share from 85% to 70%.
    """
    p = nw.persistence(pos)
    assert p["at_consensus_pct"] > 30, "the consensus mass has vanished; re-read the section"
    assert p["n_sided"] < p["n"]
    assert p["same_side_pct"] > 75
