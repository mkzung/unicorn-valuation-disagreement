#!/usr/bin/env python3
"""What the headline median is made of: coverage, and the calendar.

Separate from `src/population.py` on purpose. The drafted registration pins that file, along
with `robustness.py`, `validation.py` and `sector_specification_curve.py`, and claims the
registered tests run unchanged. Everything here was written after review, in answer to a
referee who recomputed the panel by house count, so it is post-hoc by construction and saying
so is worth more than the convenience of one import. The registered file stays byte-identical
and `tests/test_registration_pin.py` can keep checking that it has.

Nothing in here changes a number the paper already stated. It decomposes one.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop


def _house_marks(d: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    """One row per house per reported cell: the house's median mark, on the guarded panel.

    Three functions below opened with this same six lines, and they had already drifted:
    two dropped non-positive prices before grouping and one checked after sorting instead.
    The difference is invisible until a filer reports a zero, and then two of the module's
    numbers move and the third does not. One definition, one place.
    """
    g = c[c.guarded]
    key = set(zip(g.company, g.dt))
    fam = pop.comparable(d).groupby(["company", "dt", "house"]).pps.median().reset_index()
    fam = fam[[k in key for k in zip(fam.company, fam.dt)]]
    return fam[fam.pps > 0]


def pairwise_spread(d: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    """The cell's disagreement scored between two houses at a time, not end to end.

    `spread_pct` is a maximum over a minimum, so it can only grow as more houses are added.
    The appendix on the event study says so, and uses it to defend that section, where the
    house count is equal either side of the round. Section 5 never applied the argument to
    itself, and it has to: the panel is not one coverage regime. Two-house cells are the
    largest group in it and much the narrowest.

    This is the size-invariant companion. The median over all house pairs in the cell of the
    absolute log price difference, returned as a percentage so it reads on the same scale as
    the end-to-end spread. Drawing two houses at random and asking how far apart they are
    cannot grow mechanically with how many houses there are.

    What it does instead was not what I expected, which is why the paper prints it rather than
    mentioning it. It does not flatten the gradient, it inverts it. A widely held company has
    one or two houses far from the rest and a crowd that agrees; a three-house company is three
    ways apart. The two statistics answer different questions and the paper needs both: the
    range of opinion is what an allocator holding the extremes faces, and the typical pair is
    what a reader imagines on being told two houses disagree. Every value is in
    `src/paper_numbers.py`.
    """
    fam = _house_marks(d, c)
    rows = []
    for (co, dt), s in fam.groupby(["company", "dt"]):
        p = np.sort(s.pps.values)
        if len(p) < 2:
            continue
        lp = np.log(p)
        pw = [abs(lp[i] - lp[j]) for i, j in itertools.combinations(range(len(p)), 2)]
        rows.append({"company": co, "dt": dt, "n_fams": len(p),
                     "pairwise_pct": float((np.exp(np.median(pw)) - 1) * 100),
                     "spread_pct": float((p[-1] / p[0] - 1) * 100)})
    return pd.DataFrame(rows)


def coverage_gradient(d: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    """One row per house-count band: what the headline is made of.

    Bands are 2, 3, 4, 5 and six-or-more. Past five the cells thin out and a band per integer
    would report noise; pooling the tail keeps the last band larger than the one before it.
    """
    u = pairwise_spread(d, c)
    g = c[c.guarded].set_index(["company", "dt"])
    u = u.assign(nav=[float(g.nav.get((a, b), np.nan)) for a, b in zip(u.company, u.dt)])
    u["band"] = u.n_fams.clip(upper=6)
    out = u.groupby("band").agg(
        cells=("n_fams", "size"),
        companies=("company", "nunique"),
        median_spread=("spread_pct", "median"),
        median_pairwise=("pairwise_pct", "median"),
        above_24=("spread_pct", lambda s: float((s > 24).mean() * 100)),
        nav_busd=("nav", lambda s: float(s.sum() / 1e9)),
    ).reset_index()
    return out


def calendar_path(c: pd.DataFrame) -> pd.DataFrame:
    """Disagreement by report year, with the two things that could explain it away.

    A paper about dispersion over twenty-seven quarters printed no calendar path at all. The
    path is neither flat nor composition: the median trebles from its trough while the mean
    number of houses per cell falls monotonically, which is the direction that shrinks a
    maximum over a minimum rather than growing it. The three-house-and-up columns remove the
    coverage mixture entirely and the shape survives.

    The trough is the event study aggregated over the calendar. In a year when nearly every
    company sits close to a fresh round there is a price, and the houses agree about it.
    """
    g = c[c.guarded].copy()
    g["year"] = pd.to_datetime(g.dt).dt.year
    out = g.groupby("year").agg(
        cells=("spread_pct", "size"),
        median_spread=("spread_pct", "median"),
        mean_houses=("n_fams", "mean"),
    )
    out["median_3plus"] = g[g.n_fams >= 3].groupby("year").spread_pct.median()
    out["cells_3plus"] = g[g.n_fams >= 3].groupby("year").spread_pct.size()
    return out.reset_index()

def quiet_cells(d: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    """The cells of `population.staleness` where no house moved, as a frame rather than a count.

    `staleness` returns counts. This needs the keys, and `population.py` is pinned by the
    registration, so the selection is rebuilt here from the same public pieces and the same
    two constants. Rebuilt logic can drift from the original silently, which is the whole
    hazard, so `test_the_quiet_rebuild_matches_the_pinned_one` asserts this returns exactly
    as many cells as `staleness` counts.
    """
    x = pop.comparable(d)
    h = (x.groupby(["company", "house", "dt"], as_index=False)
           .agg(pps=("pps", "median"))
           .sort_values(["company", "house", "dt"]))
    prev = h.groupby(["company", "house"])
    h["prev_pps"] = prev.pps.shift(1)
    h["gap"] = (h.dt - prev.dt.shift(1)).dt.days
    h["judge"] = h.gap.le(pop.MAX_GAP_DAYS) & h.prev_pps.notna()
    h["moved"] = h.judge & ((h.pps / h.prev_pps - 1).abs() > pop.REMARK_TOL)

    g = c[c.guarded]
    keys = set(zip(g.company, g.dt))
    h = h[[k in keys for k in zip(h.company, h.dt)]]
    per = (h.groupby(["company", "dt"])
             .agg(nh=("house", "nunique"), njudge=("judge", "sum"), nmoved=("moved", "sum"))
             .reset_index())
    cell = g.merge(per, on=["company", "dt"])
    return cell[(cell.njudge == cell.nh) & (cell.nmoved == 0)]


def fully_named_cells(d: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    """Cells where every filing names a series letter and they all name the same one."""
    all_rows = pop.comparable(d)
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    all_rows = all_rows[[k in keys for k in zip(all_rows.company, all_rows.dt)]].copy()
    all_rows["ser"] = pop.series_letters(all_rows)
    agg = all_rows.groupby(["company", "dt"]).agg(
        n_letters=("ser", lambda s: len(set().union(*s)) if len(s) else 0),
        rows=("ser", "size"),
        named_rows=("ser", lambda s: int((s.map(len) > 0).sum())),
    ).reset_index()
    t = c[c.guarded].merge(agg, on=["company", "dt"])
    return t[(t.n_letters == 1) & (t.named_rows == t.rows)]


def no_move_one_letter(d: pd.DataFrame, c: pd.DataFrame) -> dict:
    """The cell where neither escape is available: same security, and nobody moved.

    Two objections are made to the wide cells in which no house repriced. One is staleness,
    which the standing itself answers. The other is composition — the cells no filing
    describes are the widest group in the panel, so an unmoved wide cell could be two share
    classes rather than one disagreement. Each subsample answers one objection and neither
    answers both.

    Their intersection answers both at once, and it is small by construction: it needs every
    filer to name the letter AND every house to have stood pat with a judgeable previous
    observation. The count is what it is. An empty intersection is reported as empty, because
    the reason to build this was to find out rather than to have something to print.
    """
    q = quiet_cells(d, c)
    f = fully_named_cells(d, c)
    key = set(zip(f.company, f.dt))
    both = q[[k in key for k in zip(q.company, q.dt)]]
    wide = both[both.spread_pct > 24]
    return {
        "quiet": len(q), "fully_named": len(f), "both": len(both),
        "both_companies": int(both.company.nunique()),
        "both_median": float(both.spread_pct.median()) if len(both) else float("nan"),
        "both_above_24": len(wide),
        "both_nonzero": int((both.spread_pct > pop.IDENTICAL).sum()),
        "widest": float(both.spread_pct.max()) if len(both) else float("nan"),
        "wide_nav_busd": float(wide.nav.sum() / 1e9) if len(wide) else 0.0,
    }


def pair_vs_company(d: pd.DataFrame, c: pd.DataFrame, min_companies: int = 3) -> dict:
    """Is disagreement a trait of the company, or of the pair of houses that hold it?

    Section 6.1 says company: between-company differences are 58.8% of the variance in log
    spread and a company predicts its own next observation. Appendix G.3 says the deviation of
    a house from consensus is itself persistent, and holdings are sticky, so the same cells
    could be reporting that WHICH HOUSES argue is stable rather than which companies are
    argued about. Those are different claims — a property of the asset against a property of a
    pair of valuers — and §6.1's control does not separate them.

    This does. Each observation is one pair of houses in one cell and the absolute log
    difference between their marks. The variance of that is attributed to company identity and
    to pair identity in turn.

    The naive comparison favours the pair and it is an artifact worth spelling out, because it
    is the trap this test exists to avoid falling into. Most house pairs are rare: a pair seen
    on one company is that company wearing a different label, so pair identity silently absorbs
    company identity and comes out ahead. Requiring a pair to appear on at least
    `min_companies` distinct companies breaks the encoding, and the ordering reverses. Both
    shares are reported at both restrictions, so a reader can see the artifact rather than be
    told about it.

    Neither number is a variance decomposition in the additive sense — the two groupings are
    not orthogonal and the shares do not sum to one. Each is the share of total variance that
    the group means alone reproduce, which is the same statistic §6.1 already reports.
    """
    fam = _house_marks(d, c)

    rows = []
    for (co, dt), s in fam.groupby(["company", "dt"]):
        marks = sorted(zip(s.house, np.log(s.pps.values)))
        for (h1, l1), (h2, l2) in itertools.combinations(marks, 2):
            rows.append({"company": co, "dt": dt, "pair": f"{h1} | {h2}",
                         "absdiff": abs(l1 - l2)})
    pw = pd.DataFrame(rows)

    def share(df: pd.DataFrame, col: str) -> float:
        grand = df.absdiff.mean()
        total = float(((df.absdiff - grand) ** 2).sum())
        if total <= 0:
            return float("nan")
        means = df.groupby(col).absdiff.transform("mean")
        return float(((means - grand) ** 2).sum() / total)

    spread = pw.groupby("pair").company.nunique()
    wide = pw[pw.pair.isin(spread[spread >= min_companies].index)]
    return {
        "observations": len(pw), "companies": int(pw.company.nunique()),
        "pairs": int(pw.pair.nunique()),
        "company_share": share(pw, "company"), "pair_share": share(pw, "pair"),
        "pairs_on_several_companies": int(wide.pair.nunique()),
        "observations_kept": len(wide),
        "company_share_restricted": share(wide, "company"),
        "pair_share_restricted": share(wide, "pair"),
    }


OUTLIER_DRAWS, OUTLIER_SEED = 2000, 20260827

# Two houses count as equally far from the rest when their absolute deviations are within this
# of each other, in log points. Never `==`, for the reason the rest of this project never uses
# it on a float, and the reason is sharper here than usual.
#
# The tie-break was made deterministic by sorting on the house name, which fixed the order of
# rows and did nothing about the CONTENTS of the tie set. Exact equality asks whether two
# `np.log` results agree to the last bit, and libm builds disagree there: the same code on the
# same data found 286 tie cells on macOS and 292 on Linux. Medians and ratios do not notice a
# swapped pair. `repeat_pct` does, because it is a chain — the outlier of one cell is compared
# against the outlier of the next — so six flipped ties compounded into 66.309 against 66.644,
# seven times the registered tolerance, and the first public CI run on ubuntu would have opened
# red on the line the paper prints.
#
# The value is not a judgement. Gaps between the largest deviation in a cell and the others
# were counted, all 8,772 of them: 110 sit below 1e-11 log points, which is floating-point
# noise on identical marks, 60 sit at 1e-9 or above, which is a real difference, and the band
# between is EMPTY. Any epsilon inside that gap gives the same answer, so this one is chosen
# from the middle of it and `test_the_tie_epsilon_sits_in_an_empty_band` fails if the gap
# closes.
TIE_EPS = 1e-10


def _outlier_rows(fam: pd.DataFrame):
    """One row per cell that has a dissenter, plus the counters the house table needs.

    A seam, so a test can hand this three or four prices and check which house it names. The
    only probe that reached it before was the whole panel, and on the whole panel every
    tie-break rule agrees often enough that a wrong one still looks right: shuffling the input
    rows cannot move the answer, because the caller groups and this sorts, so the test that
    tried it passed with the bug restored.
    """
    rows, present, expected, chosen, side = [], {}, {}, {}, {}
    unanimous = 0
    for (co, dt), s in fam.groupby(["company", "dt"]):
        # Sorted by house name before anything else. `argmax` returns the FIRST maximum, so
        # two houses equally far from the others are separated by whichever way the last bits
        # of `np.log` fell, and that is not the same on every libm. An independent replication
        # of this function differed by one pair and four tenths of a point for exactly that
        # reason. The name is arbitrary but it is the same everywhere.
        s = s.sort_values("house", kind="stable")
        v, houses = s.pps.values, list(s.house.values)
        k = len(v)
        if k < 3:
            continue
        devs = [np.log(v[i] / np.median(np.delete(v, i))) * 100 for i in range(k)]
        # A cell whose houses all file the same price has no outlier, and 244 of them do not.
        # Naming one anyway hands the name-sort an arbitrary house, and that house then enters
        # the persistence chain as an identity — which is both meaningless and the place the
        # platform sensitivity was worst, because the choice among identical marks is decided
        # entirely by which logarithm rounded which way. No dissenter, no observation.
        mag = np.abs(devs)
        if mag.max() <= TIE_EPS:
            unanimous += 1
            continue
        # Every house within TIE_EPS of the largest deviation is tied for it, and the first by
        # name wins. `argmax` alone takes the first maximum by bit-equality, which is a
        # different set of houses on a different libm.
        i = int(next(j for j in range(k) if mag.max() - mag[j] <= TIE_EPS))
        rest = np.log(np.delete(v, i))
        pw = [abs(a - b) for a, b in itertools.combinations(rest, 2)]
        # The WIDEST pair among the houses the outlier leaves, not their median pair. The
        # claim being made is that they agree, so the conservative reading is the right one:
        # even the two furthest apart of them are this close.
        rows.append({"company": co, "dt": dt, "houses": houses, "out": houses[i],
                     "dev": devs[i],
                     "rest_spread": (np.exp(max(pw)) - 1) * 100 if pw else 0.0})
        for h in houses:
            present[h] = present.get(h, 0) + 1
            expected[h] = expected.get(h, 0.0) + 1.0 / k
        chosen[houses[i]] = chosen.get(houses[i], 0) + 1
        side.setdefault(houses[i], []).append(devs[i] > 0)
    return rows, present, expected, chosen, side, unanimous


def outlier_structure(d: pd.DataFrame, c: pd.DataFrame, min_cells: int = 100) -> dict:
    """A wide cell is a consensus plus an outlier. Is the outlier a house, or a coincidence?

    The pairwise statistic inverts the coverage gradient, which says the wide cells are not
    fans of opinion but crowds with one house away from them. That is a structural claim about
    what disagreement IS, and it has a consequence that can be tested: if the away-house is the
    same house next quarter, disagreement is a standing position rather than an accident of
    the date.

    The outlier in a cell is the house furthest, in absolute log price, from the median of the
    OTHER houses. Leave-one-out, because a house compared against a consensus it is itself
    inside cannot be far from it, and with three houses the middle one is zero by construction.
    Cells need three houses for the comparison to mean anything.

    Persistence is measured only where a repeat was possible: the previous cell's outlier has
    to still be in the current cell, or the question is whether the house is present rather
    than whether it is out. The null is not a constant, because a cell of three offers a one in
    three chance and a cell of six a one in six, so it is drawn: the outlier of each cell is
    resampled uniformly from the houses actually in it.

    The house table is a rate against its OWN baseline for the same reason the panel median
    needed Table 6. A house that appears in three-house cells is the outlier a third of the
    time by chance; one in six-house cells, a sixth. `ratio` is observed over expected and is
    the only column that compares houses to each other.
    """
    rows, present, expected, chosen, side, unanimous = _outlier_rows(_house_marks(d, c))
    if not rows:
        raise ValueError("no cell carries three houses; the outlier is undefined here")
    o = pd.DataFrame(rows).sort_values(["company", "dt"])

    pairs = []
    for _co, s in o.groupby("company"):
        s = s.reset_index(drop=True)
        for j in range(1, len(s)):
            if s.loc[j - 1, "out"] in s.loc[j, "houses"]:
                pairs.append((s.loc[j - 1, "out"], s.loc[j, "out"], s.loc[j, "houses"]))
    # A panel with no company observed twice has no persistence to measure. `np.mean([])`
    # is a nan and a warning, and the permutation would draw two thousand empty samples to
    # produce more of them, so the empty case is answered rather than computed.
    if pairs:
        repeat = float(np.mean([a == b for a, b, _ in pairs]) * 100)
        rng = np.random.default_rng(OUTLIER_SEED)
        null = np.array([np.mean([prev == rng.choice(hs) for prev, _, hs in pairs]) * 100
                         for _ in range(OUTLIER_DRAWS)])
    else:
        repeat, null = float("nan"), np.array([float("nan")])

    tab = pd.DataFrame({"cells": pd.Series(present), "outlier": pd.Series(chosen),
                        "expected": pd.Series(expected)}).fillna(0)
    tab = tab[tab.cells >= min_cells].copy()
    tab["rate"] = tab.outlier / tab.cells * 100
    tab["baseline"] = tab.expected / tab.cells * 100
    tab["ratio"] = tab.outlier / tab.expected
    tab["above"] = [float(np.mean(side.get(h, [np.nan])) * 100) for h in tab.index]
    tab = tab.sort_values("ratio", ascending=False)

    return {
        "cells": len(o),
        # The denominator this dropped, so the reader can put it back. These are cells
        # where three or more houses file one price, which is the herding regime §4.3
        # names, and they carry no direction to report.
        "unanimous_cells": unanimous,
        # Arithmetic, not log points. `dev` is a log ratio times a hundred, and the paper's
        # every other spread is `exp(x) - 1`; printing 18.23 beside `rest_spread`'s 0.35 put
        # two scales behind one per-cent sign in one sentence. The median is taken in logs,
        # where it is a median of the quantity that is symmetric, and converted after.
        "outlier_dev": float((np.exp(o.dev.abs().median() / 100) - 1) * 100),
        "outlier_dev_log_points": float(o.dev.abs().median()),
        "rest_spread": float(o.rest_spread.median()),
        "above_pct": float((o.dev > 0).mean() * 100),
        "pairs": len(pairs), "repeat_pct": repeat,
        "null_mean": float(null.mean()), "null_max": float(null.max()),
        # `nan >= nan` is False, so an empty panel used to report p = 0.0 — a perfect
        # result from no observations. It reports nan now, which is what it has.
        "null_p": float((null >= repeat).mean()) if pairs else float("nan"),
        "houses": len(tab), "ratio_min": float(tab.ratio.min()),
        "ratio_max": float(tab.ratio.max()),
        "table": tab,
    }


def main() -> None:
    """Everything this module computes, in the order §5.1 and §6 use it."""
    d, c = pop.panel()
    print("coverage gradient\n")
    print(coverage_gradient(d, c).round(2).to_string(index=False))
    print("\ncalendar\n")
    print(calendar_path(c).round(2).to_string(index=False))
    print("\ncompany identity against house-pair identity\n")
    for k, v in pair_vs_company(d, c).items():
        print(f"  {k:34s} {v if isinstance(v, int) else round(v, 4)}")
    print("\nno house moved and every filing names one letter\n")
    for k, v in no_move_one_letter(d, c).items():
        print(f"  {k:34s} {v if isinstance(v, int) else round(v, 4)}")
    print("\nwhat an outlier is, and whether it is a house\n")
    ol = outlier_structure(d, c)
    for k, v in ol.items():
        if k != "table":
            print(f"  {k:34s} {v if isinstance(v, int) else round(v, 4)}")
    print()
    print(ol["table"].round(2).to_string())


if __name__ == "__main__":
    main()
