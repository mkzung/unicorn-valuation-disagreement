"""Item D, and the three ways its null could be an artifact rather than a finding."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import round_event_study as res


@pytest.fixture(scope="module")
def cells():
    return res.cells_around_rounds()


def test_the_design_has_a_sample_at_all(cells):
    """A result on an empty frame is not a result.

    The bar fell from 50 companies to 40 when the design dropped each company's first round,
    which is the cost of separating the anchor from panel entry and is stated in the note.
    """
    assert len(cells) > 300 and cells.company.nunique() >= 40


def test_restatement_windows_are_out(cells):
    """A cell mid-restatement carries the split factor, not an opinion about value."""
    assert "in_restatement" not in cells.columns or not cells.in_restatement.any()


def test_the_window_is_symmetric_and_the_first_round_is_out(cells):
    """The two changes the first design's null forced."""
    assert (cells.m < 0).any() and (cells.m > 0).any()
    assert cells.m.min() >= -res.PRE_MONTHS and cells.m.max() <= res.POST_MONTHS
    kept = res.cells_around_rounds(non_first_only=False)
    assert len(kept) > len(cells), "dropping first rounds removed nothing"


def test_the_step_at_zero_is_what_random_anchors_do_not_make(cells):
    """The result, and the contrast that carries it.

    Near-versus-far is reproduced by roughly a quarter of random anchors, because any anchor
    early in a company's window makes a trend. The step across zero is not, because a trend has
    no jump in it. If the two ever stop differing, the note is wrong.
    """
    s = res.step(cells)
    assert not s["underpowered"] and s["companies"] >= 20
    assert s["step_pts"] < -1 and s["p_sign"] < 0.01
    ns = res.null(cells, draws=120, stat=res.step)
    nt = res.null(cells, draws=120, stat=res.test)
    assert ns["share_at_least_as_extreme"] < 0.05
    assert nt["share_at_least_as_extreme"] > ns["share_at_least_as_extreme"]


def test_the_round_month_cell_is_not_just_the_new_series(cells):
    """Otherwise the trough is funds agreeing that they all paid the same price."""
    ns = res.new_series_share(cells)
    assert len(ns) >= 20
    assert ns.share_new_series.median() < 0.6
    assert int((ns.share_new_series > 0.999).sum()) == 0


def test_the_cell_does_not_get_wider_across_the_round(cells):
    """A range statistic grows with n, so the step would be part arithmetic if n moved."""
    w = res.width_test(cells)
    assert w["mwu_p"] > 0.2, "cell composition now shifts across the round; the step is confounded"
    assert abs(w["median_houses_pre"] - w["median_houses_post"]) < 1


def test_the_rebuild_rate_clears_the_same_null_the_step_did(cells):
    """The second dynamic quantity, and the reason the raw slope is not the one to quote.

    Random anchors produce a positive slope of their own — that is the within-window drift — so
    what the round owns is the excess over the null's median, not the whole of it.
    """
    r = res.rebuild_rate(cells)
    assert not r["underpowered"] and r["companies"] >= 20
    assert r["median_slope_pts_per_month"] > 0.8 and r["p_sign"] < 0.05
    n = res.rebuild_null(cells, draws=120)
    assert n["share_at_least_as_extreme"] < 0.10
    assert n["null_median"] > 0, "the null drift has vanished; the excess framing is now wrong"
    assert r["median_slope_pts_per_month"] > n["null_median"]


def test_the_step_repeats_at_a_company_s_own_later_rounds():
    """A company-level trend gives at most one step per company; a round effect gives one each."""
    m = res.multi_round()
    assert not m.get("underpowered")
    assert m["companies_with_two_or_more"] >= 5
    assert m["median_step_pts"] < -0.5 and m["p_sign"] < 0.05
    assert m["companies_negative_at_every_round"] >= 3


def test_a_shifted_anchor_loses_the_step():
    """The placebo, and the reason it beats a randomisation on the timing objection.

    Shifting the anchor keeps the calendar month, the market conditions and the company's filing
    rhythm and removes only the event. The step is at the round and at none of the shifts.

    This test used to require a *reversal* at plus six months, on the reasoning that the
    "before" band then sits inside the rebuild and the statistic should come out positive at
    the magnitude the rebuild rate predicts. It did, at +6.48 — on an event list that counted
    one anchor date once per series letter first seen in that month. Deduplicated, all three
    shifted anchors return a median of exactly zero, so the assertion is now the one the data
    supports: the shifts kill the step and none of them fires in either direction.
    """
    pl = res.placebo()
    real = pl[pl.offset_months == 0].iloc[0]
    assert real.median_step_pts < -0.5 and real.p_sign < 0.05
    shifted = pl[pl.offset_months != 0]
    assert len(shifted) >= 3
    assert (shifted.p_sign > 0.2).all(), "a placebo anchor now shows the step"
    assert (shifted.median_step_pts.abs() < 1e-6).all(), \
        "a shifted anchor now carries a magnitude; §8.3 says all three are zero"


def test_the_ladder_names_the_filter_that_carries_the_result():
    """The reviewer could not reproduce the step at a wider selection. He was right.

    Restatement windows and the guarded restriction are not load-bearing. The two-house bar on
    the round date is, and at the widest selection the MAGNITUDE goes while the sign holds.
    That distinction is the paper's stated limit, so it is asserted on both sides.

    The earlier version required `p_sign > 0.05` at the wide rung, matching a §8.4 paragraph
    that called it indistinguishable from a coin. Deduplicating the anchors took that rung from
    110 untied to 93 and its p from 0.076 to 0.019, so the assertion, and the paragraph, were
    describing seventeen duplicated dates rather than the data.
    """
    L = res.selection_ladder()
    base = L.iloc[0]
    assert base.p_sign < 0.01 and base.median_step_pts < -0.5
    wide = L[L.selection.str.contains("drop the two-house bar")].iloc[0]
    assert wide.events > 2 * base.events
    assert abs(wide.median_step_pts) < 1e-4, \
        "the magnitude survives the wide selection; §8.4's limit is now wrong"
    assert abs(wide.median_step_pts) < abs(base.median_step_pts) / 100, \
        "the wide rung no longer collapses the magnitude relative to the base rung"
    assert wide.negative / wide.untied > 0.5, "the sign no longer survives either"


def test_the_down_round_split_is_not_powered():
    """The discriminating test the panel cannot run, asserted so it is not quietly claimed."""
    ud = res.up_down()
    down = ud[ud.rounds == "down rounds"].iloc[0]
    assert down.events < 20, "there are now enough down rounds to run the test; re-read the note"


def test_the_committed_statistics_match_the_current_design():
    """The manuscript guard pins prose against `data/round_event_study_stats.csv`, because
    recomputing these takes a minute and a half and cannot sit inside the guard. A committed
    artifact the guard trusts is a staleness hole — the prose can agree perfectly with a number
    the code no longer produces — so the file carries a content hash of the marks file and of
    every design constant it is a function of, and this asserts the two still agree.

    If this fails, the fix is to re-run `python3 src/round_event_study.py`, not to edit the key.
    """
    import pandas as pd
    t = pd.read_csv(res.STATS)
    assert t.design_key.nunique() == 1, "the statistics file mixes two runs"
    assert t.design_key.iat[0] == res.design_key(), (
        "data/round_event_study_stats.csv was produced under a different panel or a different "
        "design; re-run src/round_event_study.py")
    assert len(t) > 100 and t.value.notna().all()


def test_every_statistic_the_manuscript_quotes_is_in_the_committed_file():
    """The names the registry looks up, asserted here so a rename fails in this module rather
    than three files away with a KeyError inside the guard."""
    s = res.load_stats()
    for name in ("step_pts", "step_p_sign", "step_narrower_after", "step_untied",
                 "rebuild_slope", "rebuild_null_median", "multi_step_pts",
                 "placebo_+6_step_pts", "ladder4_events", "ladder4_p_sign",
                 "updown_down_events", "width_mwu_p", "new_series_share_median"):
        assert name in s.index, f"{name} missing from {res.STATS.name}"


def test_the_tie_tolerance_sits_between_the_two_scales():
    """`TIE_TOL` must be far below every real step and far above ULP noise.

    Two runs of the same pipeline over the same inputs disagreed about this module's counts —
    65 negatives against 64 at the widest selection, and the sign p with them — because a step
    that is truly zero can arrive an ULP either side of it, and every count here was decided by
    `< 0` and `!= 0`. The tolerance fixes that only if it is calibrated, so the calibration is
    asserted against the real distribution rather than described in a comment: nothing between
    TIE_TOL and a thousand times it, and at least one genuine ULP artifact below it.
    """
    import numpy as np
    import round_dates as rdt
    f = rdt.first_seen().sort_values(["company", "first_dt"]).copy()
    f["rank"] = f.groupby("company").first_dt.rank(method="first")
    a = np.abs(np.asarray(res._steps_for(f[f["rank"] > 1]), dtype=float))
    assert len(a) > 100, f"the widest selection returned {len(a)} steps"
    real = a[a > res.TIE_TOL]
    # Thirty times, not a thousand: the first draft of this test asserted a thousand and failed,
    # which is how the real margin got measured instead of guessed. The smallest genuine step in
    # the panel is 3.1e-8, so the headroom above the tolerance is 31x and the headroom below it
    # (to the 1.1e-14 artifact) is 90,000x. The asymmetry is the honest picture.
    assert real.min() > res.TIE_TOL * 10, (
        f"the smallest real step is {real.min():.3g}, only {real.min()/res.TIE_TOL:.0f}x the "
        f"tolerance — TIE_TOL is close to swallowing a real step")
    noise = a[(a > 0) & (a <= res.TIE_TOL)]
    assert len(noise), ("no sub-tolerance value in the panel any more; either the arithmetic "
                        "changed or this tolerance now guards nothing")
    assert noise.max() < res.TIE_TOL / 1_000, f"sub-tolerance values reach {noise.max():.3g}"
    assert real.min() / noise.max() > 1e5, "the two scales are no longer separated at all"


def test_a_tie_is_not_counted_as_a_move():
    """The helpers, on inputs whose right answer is known by hand."""
    import numpy as np
    a = np.array([-1.0, -res.TIE_TOL / 10, 0.0, res.TIE_TOL / 10, 2.0])
    assert res._neg(a) == 1 and res._pos(a) == 1
    assert res._ties(a) == 3 and res._untied(a) == 2
    assert res._neg(a) + res._pos(a) == res._untied(a)


def test_two_houses_cannot_say_which_of_them_moved():
    """The arithmetic that `SIDE_MIN_HOUSES` exists for, measured rather than asserted.

    Moving the consensus from the midpoint of the extremes to the median across house medians
    was supposed to end the degeneracy that made the top and the bottom gap one number. It ends
    it at three houses. At two the median IS the midpoint, so the identity returns intact for
    the plurality of cells, and §8.4's two columns would carry the same statistic twice on a
    third of their evidence while looking like a decomposition.

    Lowering the constant is therefore not a robustness check, and this test is what makes that
    fact executable: it recomputes the gaps at the two-house bar and shows they coincide.
    """
    import numpy as np
    import population as pop
    assert res.SIDE_MIN_HOUSES == 3, "the identification bar moved; re-read the argument first"

    d, c = pop.panel()
    keep = set(zip(c[c.guarded].company, c[c.guarded].dt))
    m = pop.comparable(d).dropna(subset=["dt"])
    hm = m.groupby(["company", "dt", "house"]).pps.median().reset_index()
    hm = hm[[k in keep for k in zip(hm.company, hm.dt)]]
    g = (hm.groupby(["company", "dt"]).pps
           .agg(["min", "max", "median", "count"]).reset_index())
    g = g[g["count"] >= 2]
    up, dn = g["max"] / g["median"] - 1, 1 - g["min"] / g["median"]

    # A cell where every house agrees has both gaps at zero, so the two sides trivially match
    # and the sign test drops it as a tie either way. Unanimity is not the degeneracy this
    # guards, so the comparison is made on cells that carry a spread at all.
    spread = (up.abs() > res.TIE_TOL) | (dn.abs() > res.TIE_TOL)

    pair = g["count"] == 2
    share = float(pair.mean())
    assert (pair & spread).sum() > 500, f"only {int((pair & spread).sum())} live two-house cells"
    assert np.allclose(up[pair], dn[pair]), (
        "two-house cells no longer collapse the two sides onto one number. Either the "
        "consensus changed or the gaps did; if the degeneracy is really gone, "
        "SIDE_MIN_HOUSES has lost its reason and the docstring is now wrong.")
    # The share is quoted in `_house_gaps`; pin it so the prose cannot drift off the data.
    assert 0.35 < share < 0.45, f"two-house cells are {share:.1%}, not the 39.5% quoted"

    # At three houses the two gaps still coincide when the three prices happen to sit in
    # arithmetic progression. That residual is 3.9% and it is the SAME 3.9% at exactly three
    # houses and at four or more, which is what says it is a coincidence between prices rather
    # than a property of the estimator: a structural identity would not be flat in house count.
    trio = (g["count"] >= res.SIDE_MIN_HOUSES) & spread
    apart = float((~np.isclose(up[trio], dn[trio])).mean())
    assert apart > 0.90, (
        f"only {apart:.1%} of three-house-plus cells with a spread separate the two sides; "
        f"the bar is not buying the identification it was raised for")

    def _same(mask) -> float:
        return float(np.isclose(up[mask], dn[mask]).mean())

    three, more = trio & (g["count"] == 3), trio & (g["count"] > 3)
    assert abs(_same(three) - _same(more)) < 0.03, (
        f"the residual coincidence is {_same(three):.1%} at three houses against "
        f"{_same(more):.1%} above three. Flat in house count is the whole argument that it is "
        f"prices landing in arithmetic progression; a gap here means the estimator itself is "
        f"still collapsing the two sides and the bar has been raised to the wrong number.")

    # And the shipped frame really is the restricted one, not this wider frame.
    gaps = res._house_gaps()
    assert (gaps["count"] >= res.SIDE_MIN_HOUSES).all()
    assert len(gaps) == int((g["count"] >= res.SIDE_MIN_HOUSES).sum())


def test_the_side_decomposition_survives_only_at_the_round():
    """The claim §8.4 makes, in the shape it makes it: one side, one anchor.

    Committed as a test rather than left to the registry because the registry pins each number
    on its own and has no opinion about the ORDERING that carries the argument — that the top
    house's move at the round beats every placebo, and that the bottom house's does not clear
    the same bar at the round it is measured on.
    """
    t = res.two_sided().set_index("offset_months")
    at = t.loc[0]
    assert at.top_p_sign < 0.001, f"the top-house result at the round is {at.top_p_sign:.4f}"
    assert at.bottom_p_sign > 0.05, (
        f"the bottom-house result at the round is now {at.bottom_p_sign:.4f}; §8.4 is written "
        f"on it NOT clearing five percent, so the prose has to move before this test does")
    for off in (-6, 6, 12):
        r = t.loc[off]
        assert r.top_p_sign > 0.05 and r.bottom_p_sign > 0.05, (
            f"a placebo anchor at {off:+d} months now shows a side moving "
            f"(top {r.top_p_sign:.3f}, bottom {r.bottom_p_sign:.3f})")
        assert at.top_p_sign < r.top_p_sign / 100, (
            f"the round no longer separates from the {off:+d}-month placebo by two orders")

    # One placebo leans the paper's way on its own — 14 of 22 at six months before, 64% — so
    # §8.4 quotes the three pooled instead. That pooling has to be the three and not the four:
    # including the round would fold the result into its own control.
    st = res.stats().set_index("statistic").value
    pn, pu = st["twosided_placebo_top_narrowed"], st["twosided_placebo_top_untied"]
    assert pn == t.loc[[-6, 6, 12]].top_narrowed.sum(), "the pooled count is not the placebos"
    assert pu == t.loc[[-6, 6, 12]].top_untied.sum()
    assert pn != pn + t.loc[0].top_narrowed, "sanity: the round contributes a nonzero count"
    assert pu > 60, f"the pooled placebo rests on only {pu} untied anchors"
    assert abs(pn / pu - 0.5) < 0.005, (
        f"the pooled placebos are {pn}/{pu} = {pn/pu:.4f}. §8.4 calls this 'a coin to four "
        f"decimal places'; move the prose before this test.")
