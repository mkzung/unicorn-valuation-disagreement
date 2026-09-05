"""Does between-house disagreement narrow when a company prices a round?

Item D, which has been deferred through four rounds of review for want of its inputs. Both are
now filings. `round_dates` dates a round from the first report month carrying a new series
letter, calibrated against N-CSR to within 35 days on fourteen of fifteen pairs.
`split_events` dates the restatement windows in which a share count is being redefined and a
spread means something else.

THE HYPOTHESIS, STATED SO IT CAN LOSE
A priced round is the one moment a private company has something like an observable price. If
disagreement between houses is uncertainty about value, it should be smallest just after a round
and widen as the round recedes. If it is instead a standing difference in method — which is what
§6.2 concludes from the stood-pat cells — the round should do nothing.

FOUR THINGS THAT WOULD MAKE A NULL RESULT UNINTERPRETABLE, AND WHAT IS DONE ABOUT EACH
Resolution. Both dates are reporting months, so event time is counted in months and no claim is
made inside one.

Composition. §6.1 finds that disagreement is a trait of the company rather than of the date, so
a pooled profile mostly measures which companies happen to sit in which bin. Every spread is
demeaned within its own company before anything is averaged, and the pooled version is printed
beside it so the difference is visible rather than asserted.

Restatement. A cell in which one house has restated a split and another has not carries a spread
that is the split factor, and `split_events` says where those are. They are dropped.

Power. A null with no power is not evidence, so `null()` randomises the event dates within each
company's own observed dates and re-runs the whole profile, which gives the distribution the
statistic would have if rounds were placed at random inside the same panel.

Run:  python3 src/round_event_study.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop
import round_dates as rdt
import split_events as se

OUT = ROOT / "data" / "round_event_study.csv"
STATS = ROOT / "data" / "round_event_study_stats.csv"

PRE_MONTHS, POST_MONTHS = 6, 12
# The bands the discontinuity is measured across. Narrow and adjacent on purpose: a monotone
# trend contributes only its slope over five months, a jump at zero contributes all of itself.
PRE_BAND, POST_BAND = (-3, -1), (0, 2)
NEAR, FAR = 3, 12       # the first design's bands, kept so its result stays reproducible
SEED, DRAWS = 20260807, 400

# Every count in this module is decided by the sign of a difference of two medians, and a tie
# is a real category here: when a company's pre-band and post-band medians are the same cell
# value, the step is genuinely zero and the sign test must not count it. Exact `== 0` was doing
# that job, and it is the wrong test. Two runs of the same pipeline over the same inputs put
# one widest-selection event on either side of zero — 65 negatives in the committed data, 64
# after a rebuild — because `post.median() - pre.median()` arrives at zero by different
# arithmetic paths and lands an ULP away from it. The reported count and its p-value moved
# with it, which is a number in the paper changing for no reason in the world.
#
# TIE_TOL sits between the two scales, and both are measured rather than assumed. In the widest
# selection the panel produces nine exact zeros, one value at 1.1e-14 (the ULP artifact this is
# for), and then nothing until 3.1e-8, which is a real if tiny difference between two cells. So
# the gap the tolerance has to fall inside spans 1e-14 to 3e-8, and it is narrower than it looks
# from the units: these are percentage points, but a difference of medians inherits the precision
# of the marks, not of the percentages. `tests/test_round_event_study.py` asserts the clearance on
# both sides against the live distribution, so the constant cannot quietly start swallowing a real
# step if the panel changes.
TIE_TOL = 1e-9


def _neg(a) -> int:
    """Steps that are negative by more than tie tolerance."""
    return int((np.asarray(a, dtype=float) < -TIE_TOL).sum())


def _pos(a) -> int:
    return int((np.asarray(a, dtype=float) > TIE_TOL).sum())


def _untied(a) -> int:
    return int((np.abs(np.asarray(a, dtype=float)) > TIE_TOL).sum())


def _ties(a) -> int:
    return int((np.abs(np.asarray(a, dtype=float)) <= TIE_TOL).sum())


def _months(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a.dt.year - b.dt.year) * 12 + (a.dt.month - b.dt.month)


def cells_around_rounds(non_first_only: bool = True) -> pd.DataFrame:
    """Guarded cells tagged with months to the nearest dated round, before it or after it.

    TWO CHANGES THAT THE FIRST VERSION'S NULL FORCED, BOTH FROM THE REVIEWER
    The first version anchored on the most recent round and looked only forward, and its
    phase-randomised null could not tell "just after a round" from "early in the observation
    window". The reason is not noise. **A company enters this panel because a fund bought it in
    a round**, so for the FIRST round, months-since-round and months-since-entry are collinear
    by construction, and any anchor early in the window reproduces the profile.

    `non_first_only` drops each company's first dated round. For a company already in the panel,
    the next round is not the reason it is there, so the anchor moves while the window does not.

    The window is symmetric. A mechanism that says "a round resolves disagreement" predicts a
    DISCONTINUITY at zero — wide before, narrow after. The confound predicts a monotone trend
    and no step. Looking only forward cannot separate those; looking both ways can.
    """
    _, c = pop.panel()
    g = c[c.guarded].copy()
    r = rdt.first_seen()
    r = _ranked(r[r.dated][["company", "series", "first_dt"]])
    if r.empty:
        return pd.DataFrame()
    if non_first_only:
        r = r[r["rank"] > 1]
    r = r.drop_duplicates(["company", "first_dt"], keep="first")
    if r.empty:
        return pd.DataFrame()
    # `merge_asof` rather than a row loop: it is the same "most recent round at or before this
    # date" question, done once. The loop it replaces also read `cell.dt` inside `iterrows`,
    # where `.dt` is pandas' datetime accessor and not the column — an attribute error that a
    # differently named column would have turned into a silent wrong answer.
    left = g[["company", "dt", "spread_pct", "n_funds", "nav"]].sort_values("dt")
    right = r.rename(columns={"first_dt": "round_dt"})[["company", "round_dt"]] \
             .sort_values("round_dt")
    # `nearest`, not `backward`: the window is symmetric now, so a cell three months before a
    # round belongs to that round rather than to the one a year earlier.
    d = pd.merge_asof(left, right, left_on="dt", right_on="round_dt", by="company",
                      direction="nearest").dropna(subset=["round_dt"])
    if d.empty:
        return d
    d["m"] = _months(d.dt, d.round_dt)
    d = d[(d.m >= -PRE_MONTHS) & (d.m <= POST_MONTHS)]
    # A cell inside a restatement window carries the split factor rather than an opinion.
    ev = se.events()
    bad = set()
    for _, e in ev.iterrows():
        lo = pd.Timestamp(e.first_dt) - pd.Timedelta(days=se.WINDOW_MONTHS * 31)
        hi = pd.Timestamp(e.last_dt) + pd.Timedelta(days=se.WINDOW_MONTHS * 31)
        bad |= {(e.company, t) for t in d.dt.unique() if lo <= t <= hi}
    d["in_restatement"] = [(co, t) in bad for co, t in zip(d.company, d.dt)]
    return d[~d.in_restatement].reset_index(drop=True)


def profile(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Median spread by months since the last round, pooled and demeaned within company."""
    d = cells_around_rounds() if d is None else d
    if d.empty:
        return d
    d = d.copy()
    d["dev"] = d.spread_pct - d.groupby("company").spread_pct.transform("median")
    return (d.groupby("m")
              .agg(cells=("spread_pct", "size"), companies=("company", "nunique"),
                   pooled_median=("spread_pct", "median"),
                   within_company_median=("dev", "median")).reset_index())


def step(d: pd.DataFrame | None = None) -> dict:
    """The discontinuity at zero: the three months before a round against the three after.

    This is the statistic the symmetric window buys. Bands are adjacent and narrow so that a
    smooth trend in event time contributes only its slope across five months while a jump at the
    round contributes all of itself. Paired inside the company for the reason `test` gives.
    """
    d = cells_around_rounds() if d is None else d
    if d.empty:
        return {"companies": 0, "underpowered": True}
    pre = d[d.m.between(*PRE_BAND)].groupby("company").spread_pct.median()
    post = d[d.m.between(*POST_BAND)].groupby("company").spread_pct.median()
    both = pre.index.intersection(post.index)
    if len(both) < 3:
        return {"companies": len(both), "underpowered": True}
    diff = (post[both] - pre[both]).to_numpy()
    res = wilcoxon(diff, alternative="less")
    return {"companies": len(both), "cells": len(d),
            "median_pre": float(pre[both].median()), "median_post": float(post[both].median()),
            "step_pts": float(np.median(diff)),
            "narrower_after": _neg(diff), "ties": _ties(diff),
            "p_one_sided": float(res.pvalue),
            # The sign test is reported beside the signed-rank one because the phase null on the
            # median step is degenerate: with a random anchor the two bands draw from the same
            # distribution, most companies' paired difference is exactly zero, and the median
            # across companies is therefore zero in almost every draw. "Nought of four hundred"
            # then means only that the observed step is negative and the null never is. A count
            # of companies has a proper null that does not collapse.
            "p_sign": float(binomtest(_neg(diff), _untied(diff),
                                      alternative="greater").pvalue)
            if _untied(diff) else float("nan"),
            "untied": _untied(diff), "underpowered": False}


def test(d: pd.DataFrame | None = None) -> dict:
    """Near a round against far from one, paired inside each company.

    The first design's statistic, kept so its result stays reproducible beside the new one.
    Paired because the alternative is a between-company comparison, and §6.1 has already shown
    that between-company variance is most of the variance.
    """
    d = cells_around_rounds() if d is None else d
    if d.empty:
        return {"companies": 0}
    near = d[d.m.between(0, NEAR)].groupby("company").spread_pct.median()
    far = d[d.m >= FAR].groupby("company").spread_pct.median()
    both = near.index.intersection(far.index)
    if len(both) < 3:
        return {"companies": len(both), "cells": len(d),
                "companies_near": int(near.size), "companies_far": int(far.size),
                "underpowered": True}
    diff = (near[both] - far[both]).to_numpy()
    res = wilcoxon(diff, alternative="less")
    return {"companies": len(both), "cells": len(d),
            "median_near": float(near[both].median()),
            "median_far": float(far[both].median()),
            "median_diff_pts": float(np.median(diff)),
            "narrower_near": _neg(diff), "ties": _ties(diff),
            "p_one_sided": float(res.pvalue), "underpowered": False}


def null(d: pd.DataFrame | None = None, draws: int = DRAWS, stat=None) -> dict:
    """The same statistic with the round dates shuffled inside each company's own dates.

    This is the check that decides whether a null result means anything. If rounds placed at
    random reproduce the observed difference, the design cannot see the effect and the null is
    about the design. The randomisation stays inside the company so the company trait §6.1
    documents is held fixed.
    """
    d = cells_around_rounds() if d is None else d
    if d.empty:
        return {"draws": 0}
    stat = stat or test
    key = "step_pts" if stat is step else "median_diff_pts"
    obs = stat(d)
    if obs.get("underpowered"):
        return {"draws": 0, "underpowered": True}
    rng = np.random.default_rng(SEED)
    stats = []
    for _ in range(draws):
        s = d.copy()
        # Reassign each company's round date to one of the report dates it actually has, so the
        # shuffled design has the same coverage and the same gaps as the real one.
        pick = {co: rng.choice(x.dt.unique()) for co, x in s.groupby("company")}
        s["round_dt"] = s.company.map(pick)
        s["m"] = _months(s.dt, s.round_dt)
        s = s[(s.m >= -PRE_MONTHS) & (s.m <= POST_MONTHS)]
        t = stat(s)
        if not t.get("underpowered"):
            stats.append(t[key])
    stats = np.array(stats)
    return {"draws": len(stats), "observed": obs[key],
            "null_median": float(np.median(stats)) if len(stats) else float("nan"),
            "null_p05": float(np.quantile(stats, 0.05)) if len(stats) else float("nan"),
            "share_at_least_as_extreme":
                float((stats <= obs[key]).mean()) if len(stats) else float("nan")}


def new_series_share(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """At the round month, how much of the cell is the freshly priced series?

    The objection this answers is that the trough at zero could be arithmetic: if a cell in the
    round month consisted only of funds that had just bought at the round price, they would agree
    because they had all paid the same, and nothing about valuation would follow. They do not.
    The new series is a median 28% of the rows and is never the whole cell, so the convergence is
    over the company's whole position rather than over the security that has just traded.
    """
    d = cells_around_rounds() if d is None else d
    marks = pop.comparable(pop.load_marks()).dropna(subset=["dt"]).copy()
    marks["series"] = pop.extract_series(marks.ISSUER_TITLE)
    r = _one_row_per_anchor(rdt.first_seen().pipe(lambda t: t[t.dated]))
    key = r.set_index(["company", "first_dt"]).series.to_dict()
    rows = []
    for co, dt in d[d.m == 0][["company", "round_dt"]].drop_duplicates().itertuples(index=False):
        ser = key.get((co, dt))
        cell = marks[(marks.company == co) & (marks.dt == dt)]
        if ser is None or cell.empty:
            continue
        new = cell.series.eq(ser)
        rows.append({"company": co, "dt": dt, "series": ser, "rows": len(cell),
                     "share_new_series": float(new.mean()),
                     "houses": cell.house.nunique()})
    return pd.DataFrame(rows)


def cell_width(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Does the cell get wider across the round? A range statistic grows with n if it does.

    The spread is max over min of house medians, so it rises mechanically with the number of
    houses compared. If a round brought new buyers in, cells after it would be wider by
    composition and the step would be part arithmetic. The reviewer asked for this before
    anything else, which is the right instinct: it is the first question a referee who knows
    what a range statistic does will ask.
    """
    d = cells_around_rounds() if d is None else d
    if d.empty:
        return d
    _, c = pop.panel()
    hz = c[c.guarded][["company", "dt", "n_fams", "n_funds"]]
    w = d.merge(hz, on=["company", "dt"], how="left", suffixes=("", "_c"))
    return (w.groupby("m")
              .agg(cells=("n_fams", "size"), median_houses=("n_fams", "median"),
                   median_funds=("n_funds_c", "median")).reset_index())


def width_test(d: pd.DataFrame | None = None) -> dict:
    """Houses per cell before the round against after, so the non-result has a p-value."""
    from scipy.stats import mannwhitneyu
    d = cells_around_rounds() if d is None else d
    _, c = pop.panel()
    hz = c[c.guarded][["company", "dt", "n_fams"]]
    w = d.merge(hz, on=["company", "dt"], how="left")
    pre, post = w[w.m < 0].n_fams.dropna(), w[w.m >= 0].n_fams.dropna()
    return {"median_houses_pre": float(pre.median()), "median_houses_post": float(post.median()),
            "distinct_month_medians": int(cell_width(d).median_houses.nunique()),
            "mwu_p": float(mannwhitneyu(pre, post).pvalue)}


def rebuild_rate(d: pd.DataFrame | None = None) -> dict:
    """How fast disagreement comes back after a round, in points a month.

    The second dynamic quantity in the paper, beside the -62%/+171% cycle. Each company's
    within-company deviation is regressed on months zero to twelve and the median slope across
    companies is reported, because a pooled regression would weight the companies with the most
    cells and those are the widely held names.

    A slope is a trend, and a trend is exactly what the phase null reproduces for the near-far
    statistic, so this one has to clear the same null to be worth quoting.
    """
    d = cells_around_rounds() if d is None else d
    if d.empty:
        return {"companies": 0, "underpowered": True}
    x = d[d.m >= 0].copy()
    x["dev"] = x.spread_pct - x.groupby("company").spread_pct.transform("median")
    slopes = []
    for _co, g in x.groupby("company"):
        if g.m.nunique() < 3:
            continue
        slopes.append(np.polyfit(g.m.to_numpy(float), g.dev.to_numpy(float), 1)[0])
    if len(slopes) < 5:
        return {"companies": len(slopes), "underpowered": True}
    s = np.array(slopes)
    return {"companies": len(s), "median_slope_pts_per_month": float(np.median(s)),
            "rising": _pos(s),
            "p_sign": float(binomtest(_pos(s), len(s), alternative="greater").pvalue),
            "underpowered": False}


def rebuild_null(d: pd.DataFrame | None = None, draws: int = DRAWS) -> dict:
    """The slope under random anchors. A trend that any anchor makes is not a round effect."""
    d = cells_around_rounds() if d is None else d
    obs = rebuild_rate(d)
    if obs.get("underpowered"):
        return {"draws": 0, "underpowered": True}
    rng = np.random.default_rng(SEED)
    stats = []
    for _ in range(draws):
        s = d.copy()
        pick = {co: rng.choice(x.dt.unique()) for co, x in s.groupby("company")}
        s["round_dt"] = s.company.map(pick)
        s["m"] = _months(s.dt, s.round_dt)
        s = s[(s.m >= -PRE_MONTHS) & (s.m <= POST_MONTHS)]
        r = rebuild_rate(s)
        if not r.get("underpowered"):
            stats.append(r["median_slope_pts_per_month"])
    a = np.array(stats)
    return {"draws": len(a), "observed": obs["median_slope_pts_per_month"],
            "null_median": float(np.median(a)) if len(a) else float("nan"),
            "null_p95": float(np.quantile(a, 0.95)) if len(a) else float("nan"),
            "share_at_least_as_extreme":
                float((a >= obs["median_slope_pts_per_month"]).mean()) if len(a) else float("nan")}


def _ranked(f: pd.DataFrame) -> pd.DataFrame:
    """Company-series pairs in date order, with a DENSE rank over each company's anchor dates.

    Stable sort and dense rank, both for the same reason: two series of one company can share
    a first report month. Quicksort would order them arbitrarily and `rank(method="first")`
    would then hand rank 1 to whichever came out on top, so a first round would be admitted to
    the non-first event list on a coin flip that is not even reproducible between runs.
    """
    r = f.sort_values(["company", "first_dt"], kind="mergesort").copy()
    r["rank"] = r.groupby("company").first_dt.rank(method="dense")
    return r


def _one_row_per_anchor(r: pd.DataFrame) -> pd.DataFrame:
    """Drop each company's first anchor, then keep one row per surviving anchor.

    An event is an anchor date, not a series letter. Two letters can first appear in the same
    report month — High Street Holdco has sixteen on one date, Radar Topco nine — and the step
    measured at each of them is the same number computed from the same cells, because the only
    thing the loop below uses from the row is `first_dt`. Left as separate rows, 683 non-first
    rows become 516 anchors' worth of information counted 683 times, and `binomtest` reads the
    copies as independent draws.

    Ranking has to be dense for the same reason. With `method="first"` a company whose two
    earliest letters share a date has one of them ranked 1 (dropped as the first round) and the
    other ranked 2 (kept as a later one), which is a first round entering the event list.
    """
    r = _ranked(r)
    r = r[r["rank"] > 1]
    return r.drop_duplicates(["company", "first_dt"], keep="first")


def event_steps(offset_months: int = 0, min_rounds: int = 1) -> pd.DataFrame:
    """The step at each individual round, rather than one step per company.

    The design the reviewer named as the next version, and the one that answers the standing
    caveat about 31 companies. A company with several dated non-first rounds carries the anchor
    to several places inside its own window, so a company-level time trend cannot produce a step
    at each of them; it can only produce one wherever the window happens to start.

    `offset_months` shifts every anchor by a fixed number of months. At zero this is the real
    design. At six it is a placebo that keeps the calendar month, the market conditions and the
    company's own filing rhythm and removes only the event, which is a tighter answer to
    "companies raise when the market is open" than any randomisation can give: a null moves the
    anchor to a random time, a shifted anchor moves it to a time the company chose plus a
    constant.
    """
    _, c = pop.panel()
    g = c[c.guarded][["company", "dt", "spread_pct"]]
    r = _one_row_per_anchor(rdt.first_seen().pipe(lambda t: t[t.dated]))
    keep = r.groupby("company").size()
    r = r[r.company.isin(keep[keep >= min_rounds].index)]
    ev = se.events()
    pad = pd.Timedelta(days=se.WINDOW_MONTHS * 31)
    bad: dict[str, list] = {}
    for _, e in ev.iterrows():
        bad.setdefault(e.company, []).append(
            (pd.Timestamp(e.first_dt) - pad, pd.Timestamp(e.last_dt) + pad))
    by_company = dict(tuple(g.groupby("company")))
    rows = []
    for co, ser, rd in r[["company", "series", "first_dt"]].itertuples(index=False):
        anchor = rd + pd.DateOffset(months=offset_months)
        s = by_company.get(co)
        if s is None or s.empty:
            continue
        s = s.copy()
        s["m"] = _months(s.dt, pd.Series(anchor, index=s.index))
        # Restatement windows out, same rule as the pooled design. `np.array` because `~` on a
        # bare list is a unary operator on a list and raises.
        if co in bad:
            drop = np.array([any(lo <= x <= hi for lo, hi in bad[co]) for x in s.dt])
            s = s[~drop]
        pre = s[s.m.between(*PRE_BAND)].spread_pct
        post = s[s.m.between(*POST_BAND)].spread_pct
        if pre.empty or post.empty:
            continue
        rows.append({"company": co, "series": ser, "round_dt": rd.date().isoformat(),
                     "anchor": anchor.date().isoformat(), "offset": offset_months,
                     "pre_cells": len(pre), "post_cells": len(post),
                     "pre": float(pre.median()), "post": float(post.median()),
                     "step_pts": float(post.median() - pre.median())})
    return pd.DataFrame(rows)


def multi_round(min_rounds: int = 2) -> dict:
    """The step measured at every round, and whether it repeats inside one company.

    A company-level trend gives one step per company at most. A round effect gives one at each
    round. `repeats` is the count of companies whose steps are negative at every one of their
    rounds, which is the quantity that separates the two and cannot be produced by a trend.
    """
    e = event_steps(0, min_rounds=min_rounds)
    if len(e) < 5:
        return {"events": len(e), "underpowered": True}
    by_co = e.groupby("company").step_pts
    repeats = int((by_co.max() < -TIE_TOL).sum())
    multi = int((by_co.size() >= 2).sum())
    res = wilcoxon(e.step_pts.to_numpy(), alternative="less")
    untied = _untied(e.step_pts)
    return {"events": len(e), "companies": int(e.company.nunique()),
            "companies_with_two_or_more": multi,
            "companies_negative_at_every_round": repeats,
            "median_step_pts": float(e.step_pts.median()),
            "negative_events": _neg(e.step_pts), "untied": untied,
            "p_signed_rank": float(res.pvalue),
            "p_sign": float(binomtest(_neg(e.step_pts), untied,
                                      alternative="greater").pvalue) if untied else float("nan"),
            "underpowered": False}


def placebo(offsets=(-6, 6, 12)) -> pd.DataFrame:
    """The same step at anchors the company chose plus a constant, where no round happened.

    If the step is calendar timing — companies raise when the market is open, and spreads are
    narrow when the market is open — a shifted anchor keeps the timing and should keep the step.
    If it is the round, the step should go with the round.
    """
    rows = []
    for k in (0,) + tuple(offsets):
        e = event_steps(k, min_rounds=1)
        if e.empty:
            continue
        untied = _untied(e.step_pts)
        rows.append({"offset_months": k, "events": len(e),
                     "companies": int(e.company.nunique()),
                     "median_step_pts": float(e.step_pts.median()),
                     "negative": _neg(e.step_pts), "untied": untied,
                     "p_sign": float(binomtest(_neg(e.step_pts), untied,
                                               alternative="greater").pvalue)
                     if untied else float("nan")})
    return pd.DataFrame(rows)


def _steps_for(rounds: pd.DataFrame, drop_restatement: bool = True,
               guarded: bool = True, min_cells: int = 1) -> np.ndarray:
    """Per-event steps under an arbitrary event selection. The ladder below varies the rules.

    One row per anchor, for the reason `_one_row_per_anchor` gives: every rung of the ladder is
    a sign test, and two letters sharing a report month give it the same step twice.
    """
    rounds = rounds.drop_duplicates(["company", "first_dt"], keep="first")
    _, c = pop.panel()
    cells = (c[c.guarded] if guarded else c)[["company", "dt", "spread_pct"]]
    by = dict(tuple(cells.groupby("company")))
    pad = pd.Timedelta(days=se.WINDOW_MONTHS * 31)
    bad: dict[str, list] = {}
    if drop_restatement:
        for _, e in se.events().iterrows():
            bad.setdefault(e.company, []).append(
                (pd.Timestamp(e.first_dt) - pad, pd.Timestamp(e.last_dt) + pad))
    out = []
    for co, rd in rounds[["company", "first_dt"]].itertuples(index=False):
        s = by.get(co)
        if s is None:
            continue
        s = s.copy()
        s["m"] = (s.dt.dt.year - rd.year) * 12 + (s.dt.dt.month - rd.month)
        if co in bad:
            s = s[~np.array([any(lo <= x <= hi for lo, hi in bad[co]) for x in s.dt])]
        pre = s[s.m.between(*PRE_BAND)].spread_pct
        post = s[s.m.between(*POST_BAND)].spread_pct
        if len(pre) < min_cells or len(post) < min_cells:
            continue
        out.append(post.median() - pre.median())
    return np.array(out)


def _score(a: np.ndarray) -> dict:
    if len(a) < 5:
        return {"events": len(a), "underpowered": True}
    un, neg = _untied(a), _neg(a)
    return {"events": len(a), "median_step_pts": float(np.median(a)), "negative": neg,
            "untied": un,
            "p_sign": float(binomtest(neg, un, alternative="greater").pvalue) if un else float("nan")}


def selection_ladder() -> pd.DataFrame:
    """How the step survives each filter being relaxed, and which one carries it.

    The reviewer could not reproduce the placebo table from a naive event list and found the step
    gone at a wider selection. He is right that it is sensitive to which events are admitted, and
    this prints the sensitivity rather than describing it. The funnel is 5,864 company-series
    pairs carrying a letter, 425 of them dated, 137 of those non-first, and 54 with guarded cells
    in both bands.

    Restatement windows and the guarded restriction turn out not to matter: dropping either moves
    the median by a tenth of a point and the p-value not at all. What carries the result is the
    two-house bar on the round DATE — and that bar was not chosen here. It was read off the N-CSR
    calibration two rounds earlier, where the eight one-house pairs missed the acquisition date by
    49 to 670 days. Admitting them does not add rounds, it adds anchors placed months from the
    event, and a misplaced anchor smears the step by construction.

    Which is what the last rows show: at the widest selection the sign survives at 58% negative
    and the magnitude does not. That is stated in the note as a limit, not explained away.
    """
    f = rdt.first_seen()
    allp, dat = _ranked(f), _ranked(f[f.dated])
    rows = [
        ("dated, non-first, restatement out, guarded", _score(_steps_for(dat[dat["rank"] > 1]))),
        ("  keep restatement windows", _score(_steps_for(dat[dat["rank"] > 1],
                                                         drop_restatement=False))),
        ("  all cells, not only guarded", _score(_steps_for(dat[dat["rank"] > 1], guarded=False))),
        ("  admit first rounds too", _score(_steps_for(dat))),
        ("  drop the two-house bar", _score(_steps_for(allp[allp["rank"] > 1]))),
        ("  drop it and keep restatement", _score(_steps_for(allp[allp["rank"] > 1],
                                                             drop_restatement=False))),
    ]
    return pd.DataFrame([{"selection": k, **v} for k, v in rows])


SIDE_MIN_HOUSES = 3     # not a filter: see below. Two opinions cannot say which one moved.


_CELLS: dict[str, pd.DataFrame] = {}


def _cell_prices() -> pd.DataFrame:
    """One row per guarded cell: the min, max, median and count of its house medians.

    Memoised on the panel's own cache key, the way `round_dates.first_seen` is and for the
    same reason. `_house_gaps` and `identified_cell_pct` both need it, and the first version
    of the second one recomputed the whole thing — a full resolve of every mark in the panel —
    to obtain a denominator it could have divided out of the frame already in hand.
    """
    key = pop._cache_key()
    if key not in _CELLS:
        _CELLS.clear()
        d, c = pop.panel()
        keep = set(zip(c[c.guarded].company, c[c.guarded].dt))
        m = pop.comparable(d).dropna(subset=["dt"])
        hm = m.groupby(["company", "dt", "house"]).pps.median().reset_index()
        hm = hm[[k in keep for k in zip(hm.company, hm.dt)]]
        _CELLS[key] = (hm.groupby(["company", "dt"]).pps
                         .agg(["min", "max", "median", "count"]).reset_index())
    return _CELLS[key].copy()


def _house_gaps() -> pd.DataFrame:
    """Per cell, how far the top and the bottom house sit from the median house.

    The consensus has to be the MEDIAN across house medians rather than the midpoint of the
    extremes. Under a midpoint the two gaps are the same number by algebra — both are half the
    spread over the midpoint — so a decomposition built on one reports the spread twice and
    reads as two findings. The first version did exactly that and was caught only because both
    sides printed identical statistics to four decimals.

    The median repairs that at three houses or more, and NOT at two, which is where this
    measurement went wrong the second time. With two opinions the median is the midpoint, so
    the identity comes straight back for the 39.5% of guarded cells that hold exactly two
    houses. `tests/test_round_event_study.py` measures the identity at two and its absence at
    three so that lowering `SIDE_MIN_HOUSES` fails rather than quietly restoring it.

    The bar is an identification limit, not a robustness choice. Deciding whether the high
    house came down or the low house came up requires somebody to have stayed put, and two
    houses leave nobody in the middle: every movement of one is a movement of the other in the
    only coordinate system available. The total gap in `stats()` is unaffected — it never
    asks which side moved — so this constant governs `two_sided` alone.
    """
    g = _cell_prices()
    g = g[g["count"] >= SIDE_MIN_HOUSES].copy()
    g["up_gap"] = g["max"] / g["median"] - 1
    g["dn_gap"] = 1 - g["min"] / g["median"]
    return g


def identified_cell_pct() -> float:
    """Share of two-house-or-more cells on which asking WHICH side moved is answerable.

    Quoted in §8.4 as the price the identification bar charges, and computed here rather than
    divided out by hand in the manuscript so that it moves when the panel does.
    """
    n = _cell_prices()["count"]
    return float((n >= SIDE_MIN_HOUSES).sum() / (n >= 2).sum() * 100)


def two_sided(offsets=(0, -6, 6, 12)) -> pd.DataFrame:
    """Which side of the cell moves at the round, and whether it moves at a shifted anchor.

    The objection §8.7 concedes is that a price arriving and good news arriving are the same
    event. News moves every house the same way: all revise toward the new price, and the cell
    narrows because the laggards catch up. It cannot push the most OPTIMISTIC house down. A
    price existing pulls from both ends, so a fall in the upper gap is the half of the
    movement a one-sided story does not produce.

    That is what this returns, and only that. The top house comes down at the round and at no
    shifted anchor. The bottom house's move is in the same direction and does not clear five
    percent, so the finding is an asymmetry rather than a pair of findings, and the manuscript
    reports it as one. Reading the weaker column as confirmation would be reading a p of 0.09
    as a result because the column beside it is small.

    Selecting the top house selects partly on its own error, which is the regression to the
    mean §11.3 refuses to read as reversion, and it would narrow the upper gap at any date.
    The shifted anchors are the answer: mean reversion does not know where the rounds are.
    """
    a = _one_row_per_anchor(rdt.first_seen().pipe(lambda t: t[t.dated]))[["company", "first_dt"]]
    by = dict(tuple(_house_gaps().groupby("company")))
    out = []
    for off in offsets:
        rows = []
        for co, rd in a.itertuples(index=False):
            s = by.get(co)
            if s is None:
                continue
            anchor = rd + pd.DateOffset(months=off)
            s = s.copy()
            s["m"] = (s.dt.dt.year - anchor.year) * 12 + (s.dt.dt.month - anchor.month)
            pre, post = s[s.m.between(*PRE_BAND)], s[s.m.between(*POST_BAND)]
            if pre.empty or post.empty:
                continue
            rows.append((float(post.up_gap.median() - pre.up_gap.median()),
                         float(post.dn_gap.median() - pre.dn_gap.median())))
        e = pd.DataFrame(rows, columns=["d_up", "d_dn"])
        rec = {"offset_months": off, "events": len(e)}
        for side, col in (("top", "d_up"), ("bottom", "d_dn")):
            x = e[col].to_numpy() if len(e) else np.zeros(0)
            untied = int((np.abs(x) > TIE_TOL).sum())
            narrowed = int((x < -TIE_TOL).sum())
            rec[f"{side}_narrowed"] = narrowed
            rec[f"{side}_untied"] = untied
            rec[f"{side}_p_sign"] = (float(binomtest(narrowed, untied, alternative="greater")
                                           .pvalue) if untied else float("nan"))
        out.append(rec)
    return pd.DataFrame(out)


def up_down() -> pd.DataFrame:
    """The step in rounds that raised the price and in rounds that cut it.

    The endogeneity the placebo cannot reach is that a company chooses when to raise. If houses
    converge because the news is good, the step should live in the up rounds. If they converge
    because a price now exists, it should be in both. The split is on the median price per share
    across the round — a level, not a spread, so it is not the dependent variable in disguise.
    """
    _, c = pop.panel()
    g = c[c.guarded][["company", "dt", "spread_pct"]]
    d, _ = pop.panel()
    m = pop.comparable(d).dropna(subset=["dt"])
    px = m.groupby(["company", "dt"]).pps.median().reset_index()
    f = rdt.first_seen()
    r = _one_row_per_anchor(f[f.dated])
    by_g = dict(tuple(g.groupby("company")))
    by_p = dict(tuple(px.groupby("company")))
    rows = []
    for co, rd in r[["company", "first_dt"]].itertuples(index=False):
        s, q = by_g.get(co), by_p.get(co)
        if s is None or q is None:
            continue
        s = s.copy()
        s["m"] = (s.dt.dt.year - rd.year) * 12 + (s.dt.dt.month - rd.month)
        pre, post = s[s.m.between(*PRE_BAND)].spread_pct, s[s.m.between(*POST_BAND)].spread_pct
        qq = q.copy()
        qq["m"] = (qq.dt.dt.year - rd.year) * 12 + (qq.dt.dt.month - rd.month)
        p0, p1 = qq[qq.m.between(*PRE_BAND)].pps, qq[qq.m.between(*POST_BAND)].pps
        if pre.empty or post.empty or p0.empty or p1.empty:
            continue
        rows.append({"company": co, "step_pts": float(post.median() - pre.median()),
                     "price_change_pct": float(p1.median() / p0.median() - 1) * 100})
    e = pd.DataFrame(rows)
    if e.empty:
        return e
    out = []
    for lab, sel in [("up rounds", e.price_change_pct > 0), ("down rounds", e.price_change_pct <= 0)]:
        out.append({"rounds": lab, **_score(e[sel].step_pts.to_numpy())})
    out.append({"rounds": "all", **_score(e.step_pts.to_numpy())})
    return pd.DataFrame(out)


def design_key() -> str:
    """A content hash of everything this study's numbers are a function of.

    Every statistic below takes eight to ten minutes to produce, which is too slow to run
    inside the manuscript guard, so `stats()` writes them to `data/round_event_study_stats.csv`
    and the guard pins the prose against that file. A committed artifact that the guard trusts
    is a staleness hole: the prose can agree perfectly with a number the code no longer
    produces. This closes it. The key is the sha256 of the source marks file — content, not
    mtime, because mtime is not preserved by a clone — folded together with the design
    constants of this module and of the two sensors it depends on. Change the panel or move a
    band and the key moves, and `test_the_committed_statistics_match_the_current_design` fails
    until the file is regenerated.
    """
    h = hashlib.sha256()
    with pop.MARKS.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    h.update(repr((PRE_MONTHS, POST_MONTHS, PRE_BAND, POST_BAND, NEAR, FAR, SEED, DRAWS,
                   rdt.MIN_HOUSES, rdt.TOLERANCE_DAYS,
                   se.MIN_K, se.MAX_K, sorted(se.CANONICAL_K), se.BALANCE_TOL,
                   se.VALUE_BAND, se.WINDOW_MONTHS, se.MIN_HOUSES)).encode())
    return h.hexdigest()[:16]


def stats(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Every scalar the manuscript quotes from this module, in one long table.

    One row per quoted number, so the registry can pin a prose token to a named statistic
    rather than to a position in a printout.
    """
    d = cells_around_rounds() if d is None else d
    first = cells_around_rounds(non_first_only=False)
    s, t, w = step(d), test(d), width_test(d)
    ns, rr, rn = new_series_share(d), rebuild_rate(d), rebuild_null(d)
    n_step, n_near = null(d, stat=step), null(d, stat=test)
    mr, pl, lad, ud = multi_round(), placebo(), selection_ladder(), up_down()
    rows = [
        ("cells", len(d)), ("companies", d.company.nunique()),
        ("cells_with_first_rounds", len(first)),
        ("companies_with_first_rounds", first.company.nunique()),
        ("cells_before", int((d.m < 0).sum())),
        ("companies_before", d[d.m < 0].company.nunique()),
        ("cells_after", int((d.m >= 0).sum())),
        ("companies_after", d[d.m >= 0].company.nunique()),
        ("step_companies", s["companies"]), ("step_median_pre", s["median_pre"]),
        ("step_median_post", s["median_post"]), ("step_pts", s["step_pts"]),
        ("step_narrower_after", s["narrower_after"]), ("step_untied", s["untied"]),
        ("step_p_sign", s["p_sign"]),
        ("step_null_share", n_step["share_at_least_as_extreme"]),
        ("nearfar_pts", t["median_diff_pts"]), ("nearfar_companies", t["companies"]),
        ("nearfar_p", t["p_one_sided"]),
        ("nearfar_null_share", n_near["share_at_least_as_extreme"]),
        ("round_month_cells", len(ns)),
        ("new_series_share_median", float(ns.share_new_series.median())),
        ("round_month_cells_all_new_series", int((ns.share_new_series > 0.999).sum())),
        ("width_houses_pre", w["median_houses_pre"]),
        ("width_houses_post", w["median_houses_post"]), ("width_mwu_p", w["mwu_p"]),
        ("width_distinct_month_medians", w["distinct_month_medians"]),
        ("rebuild_slope", rr["median_slope_pts_per_month"]),
        ("rebuild_companies", rr["companies"]), ("rebuild_rising", rr["rising"]),
        ("rebuild_p_sign", rr["p_sign"]), ("rebuild_null_median", rn["null_median"]),
        ("rebuild_null_share", rn["share_at_least_as_extreme"]),
        ("multi_events", mr["events"]), ("multi_companies", mr["companies"]),
        ("multi_companies_two_or_more", mr["companies_with_two_or_more"]),
        ("multi_step_pts", mr["median_step_pts"]),
        ("multi_negative", mr["negative_events"]), ("multi_untied", mr["untied"]),
        ("multi_p_sign", mr["p_sign"]),
        ("multi_companies_negative_every_round", mr["companies_negative_at_every_round"]),
    ]
    for _, r in pl.iterrows():
        k = f"placebo_{int(r.offset_months):+d}"
        rows += [(f"{k}_events", r.events), (f"{k}_companies", r.companies),
                 (f"{k}_step_pts", r.median_step_pts), (f"{k}_negative", r.negative),
                 (f"{k}_untied", r.untied), (f"{k}_p_sign", r.p_sign)]
    for i, r in lad.iterrows():
        k = f"ladder{i}"
        rows += [(f"{k}_events", r.events), (f"{k}_step_pts", r.median_step_pts),
                 (f"{k}_negative", r.negative), (f"{k}_untied", r.untied),
                 (f"{k}_p_sign", r.p_sign)]
    for _, r in ud.iterrows():
        k = "updown_" + r.rounds.split()[0]
        rows += [(f"{k}_events", r.events), (f"{k}_step_pts", r.median_step_pts),
                 (f"{k}_negative", r.negative), (f"{k}_untied", r.untied),
                 (f"{k}_p_sign", r.p_sign)]
    _ts = two_sided()
    rows += [("side_identified_cell_pct", identified_cell_pct()),
             ("side_two_house_cell_pct", 100.0 - identified_cell_pct())]
    # The three placebo anchors pooled. Reported because one of them, six months before the
    # round, leans the same way as the round at 14 of 22 and reads as a pre-trend on its own.
    # Pooled it is not one: the three together are a coin to four decimal places, which is a
    # stronger statement than three separate failures to clear a threshold.
    _pl = _ts[_ts.offset_months != 0]
    rows += [("twosided_placebo_top_narrowed", float(_pl.top_narrowed.sum())),
             ("twosided_placebo_top_untied", float(_pl.top_untied.sum()))]
    for _, r in _ts.iterrows():
        k = f"twosided_{int(r.offset_months):+d}"
        rows += [(f"{k}_events", r.events),
                 (f"{k}_top_narrowed", r.top_narrowed), (f"{k}_top_untied", r.top_untied),
                 (f"{k}_top_p_sign", r.top_p_sign),
                 (f"{k}_bottom_narrowed", r.bottom_narrowed),
                 (f"{k}_bottom_untied", r.bottom_untied),
                 (f"{k}_bottom_p_sign", r.bottom_p_sign)]
    out = pd.DataFrame(rows, columns=["statistic", "value"])
    out["value"] = out.value.astype(float)
    out.insert(0, "design_key", design_key())
    return out


def load_stats() -> pd.Series:
    """The committed statistics as a name -> value mapping, for the manuscript guard."""
    t = pd.read_csv(STATS)
    return t.set_index("statistic").value


def main() -> None:
    d = cells_around_rounds()
    first = cells_around_rounds(non_first_only=False)
    if d.empty:
        raise SystemExit("no guarded cell sits near a non-first dated round")
    p = profile(d)
    p.to_csv(OUT, index=False)
    print(f"non-first dated rounds only. guarded cells in [-{PRE_MONTHS}, +{POST_MONTHS}] "
          f"months of one: {len(d)} on {d.company.nunique()} companies "
          f"({len(first)} on {first.company.nunique()} if first rounds are kept)")
    print(f"  before the round: {int((d.m < 0).sum())} cells on "
          f"{d[d.m < 0].company.nunique()} companies; after: {int((d.m >= 0).sum())} on "
          f"{d[d.m >= 0].company.nunique()}")
    print("\nmonths to the nearest non-first round")
    print(p.round(2).to_string(index=False))

    s = step(d)
    if s.get("underpowered"):
        print(f"\nonly {s['companies']} companies have cells on both sides of zero — "
              "the step cannot be tested.")
    else:
        print(f"\nthe step at zero: months {PRE_BAND[0]}..{PRE_BAND[1]} against "
              f"{POST_BAND[0]}..{POST_BAND[1]}, paired within company, {s['companies']} companies")
        print(f"  median before {s['median_pre']:.2f}%, after {s['median_post']:.2f}%, "
              f"step {s['step_pts']:+.2f} points; narrower after in {s['narrower_after']} of "
              f"{s['untied']} untied, signed-rank p={s['p_one_sided']:.3f}, "
              f"sign test p={s['p_sign']:.4f}")
        n = null(d, stat=step)
        print(f"  phase-randomised null over {n['draws']} draws: median step "
              f"{n['null_median']:+.2f}, 5th percentile {n['null_p05']:+.2f}; the observed step "
              f"is matched or beaten by {n['share_at_least_as_extreme'] * 100:.0f}% of random "
              f"placements.")
        print("  A monotone trend contributes its slope across five months to both the observed "
              "step and the null; what survives the comparison is the jump.")
        print("  The null on the median step is degenerate — with a random anchor both bands "
              "draw from one distribution, most paired differences are exactly zero and the "
              "median across companies is zero in nearly every draw. So 0% means the observed "
              "step is negative and the null never is; the sign test is the one with a null "
              "that does not collapse.")
        ns = new_series_share(d)
        print(f"\n  the trough is not the newly traded security agreeing with itself: across "
              f"{len(ns)} round-month cells the new series is a median "
              f"{ns.share_new_series.median() * 100:.0f}% of the rows and the whole cell in "
              f"{int((ns.share_new_series > 0.999).sum())} of them.")

    t = test(d)
    if not t.get("underpowered"):
        nt = null(d, stat=test)
        print(f"\nthe first design's statistic on this sample, for comparison: near-far "
              f"{t['median_diff_pts']:+.2f} points on {t['companies']} companies, "
              f"p={t['p_one_sided']:.3f}, reproduced by "
              f"{nt['share_at_least_as_extreme'] * 100:.0f}% of random placements.")
    w = width_test(d)
    print(f"\ncell width across the round: median houses {w['median_houses_pre']:.1f} before "
          f"against {w['median_houses_post']:.1f} after, Mann-Whitney p={w['mwu_p']:.2f}; the "
          f"month-by-month medians take {w['distinct_month_medians']} distinct value(s) across "
          "the window. A range statistic grows with n, and n does not move here.")

    rr = rebuild_rate(d)
    if not rr.get("underpowered"):
        rn = rebuild_null(d)
        print(f"\nhow fast it comes back: median within-company slope "
              f"{rr['median_slope_pts_per_month']:+.2f} points a month over months 0..12 on "
              f"{rr['companies']} companies, rising in {rr['rising']}, sign p={rr['p_sign']:.4f}")
        print(f"  against the phase null: median slope {rn['null_median']:+.2f}, 95th percentile "
              f"{rn['null_p95']:+.2f}, matched or beaten by "
              f"{rn['share_at_least_as_extreme'] * 100:.0f}% of random placements.")

    mr = multi_round()
    if not mr.get("underpowered"):
        print(f"\nthe step measured at every round rather than once per company: "
              f"{mr['events']} rounds on {mr['companies']} companies, "
              f"{mr['companies_with_two_or_more']} of which carry two or more")
        print(f"  median step {mr['median_step_pts']:+.2f} points, negative at "
              f"{mr['negative_events']} of {mr['untied']} untied rounds, sign p="
              f"{mr['p_sign']:.4f}; negative at EVERY one of its rounds in "
              f"{mr['companies_negative_at_every_round']} companies")
        print("  A company-level trend gives at most one step per company. A round effect gives "
              "one at each round, and that is what repeats.")

    pl = placebo()
    if not pl.empty:
        print("\nplacebo: the same statistic at anchors the company chose plus a constant")
        print(pl.round(3).to_string(index=False))
        real = pl[pl.offset_months == 0]
        if len(real):
            print("  A shifted anchor keeps the calendar month, the market conditions and the "
                  "company's own filing rhythm, and removes only the event. If the step were "
                  "timing it would survive the shift.")

    print("\nhow the step survives each filter being relaxed")
    print(selection_ladder().round(4).to_string(index=False))
    print("  The two-house bar carries it, and that bar was read off the N-CSR calibration two "
          "rounds before this statistic existed: the eight one-house pairs there missed the "
          "acquisition date by 49 to 670 days. Admitting them adds anchors, not rounds.")

    ud = up_down()
    if not ud.empty:
        print("\nup rounds against down rounds, split on the median price per share")
        print(ud.round(4).to_string(index=False))

    st = stats(d)
    st.to_csv(STATS, index=False)
    print(f"\n  wrote {OUT.relative_to(ROOT)} and {STATS.relative_to(ROOT)} "
          f"({len(st)} statistics, design key {st.design_key.iat[0]})")


if __name__ == "__main__":
    main()
