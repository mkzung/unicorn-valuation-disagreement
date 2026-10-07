"""Is the cross-family mark disagreement just staleness?

The §4.3 finding is that two fund families can carry the same private share at prices
tens of percent apart. The obvious deflationary reading is that this is not disagreement
at all but *staleness*: one house simply has not refreshed an old mark. This module tests
that reading three ways, all from the committed quarterly panel
(`data/fund_marks_timeseries.csv`, one Level-3 mark per fund-quarter).

  (1) REMARK RATE. For each family, the share of adjacent-quarter pairs in which its mark
      actually moves (|change| > 0.5%). A family that never refreshes would sit near zero.

  (2) THE DECISIVE TEST. Restrict to company-quarters in which EVERY family present moved
      its mark that quarter, so no mark in the cell can be stale by construction, and compare
      the cross-family spread there against the spread in all cells. Under the staleness
      reading the freshly-remarked cells should show a materially SMALLER spread.

  (3) LEVEL DEVIATION vs REMARK RATE. If staleness drove the spread, the family that
      refreshes least often should be the one sitting furthest from the cross-family median.

Outlier discipline follows the time-series leg: a company-quarter cell is dropped when the
highest family mark exceeds the lowest by more than 4x, the documented unit-convention /
share-class guard (Discord's ARK-vs-Fidelity cell is the one such case here).

Run: python3 src/mark_staleness.py
"""
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu

from fund_marks import family  # the paper's own family mapping

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "mark_staleness.csv"

REMARK_TOL = 0.005   # a mark "moved" if it changed by more than 0.5%
CLASS_GUARD = 4.0    # drop cells whose max/min family mark exceeds this (unit/class artifact)
FAVORED_SECTORS = {"AI", "Data/AI", "Defense"}          # the §7.2 pre-specified favored set
DEEP_DISCOUNT_SECTORS = {"Crypto", "Quantum", "Energy"}  # the fallen 2021-22 cohort


def load() -> pd.DataFrame:
    ts = pd.read_csv(ROOT / "data" / "fund_marks_timeseries.csv")
    ts["family"] = ts.fund.map(family)
    ts["q"] = pd.PeriodIndex(pd.to_datetime(ts.report_date), freq="Q")
    ts["pps"] = pd.to_numeric(ts.pps, errors="coerce")
    ts = ts.dropna(subset=["pps"])
    # one mark per (company, family, quarter): median across that family's funds
    fam_q = (ts.groupby(["company", "family", "q"], as_index=False)
               .agg(pps=("pps", "median"), n_funds=("fund", "nunique")))
    fam_q = fam_q.sort_values(["company", "family", "q"])
    prev = fam_q.groupby(["company", "family"])
    fam_q["prev_pps"] = prev.pps.shift(1)
    fam_q["prev_q"] = prev.q.shift(1)
    fam_q["adjacent"] = (fam_q.q - fam_q.prev_q).map(lambda d: getattr(d, "n", None)) == 1
    fam_q["remarked"] = (fam_q.pps / fam_q.prev_pps - 1).abs() > REMARK_TOL
    return fam_q


def remark_rates(fam_q: pd.DataFrame) -> pd.DataFrame:
    adj = fam_q[fam_q.adjacent]
    return (adj.groupby("family")
               .agg(pairs=("remarked", "size"), moved=("remarked", "sum"),
                    companies=("company", "nunique"))
               .assign(remark_rate=lambda d: (d.moved / d.pairs).round(3))
               .sort_values("remark_rate"))


def qualifies(g: pd.DataFrame) -> tuple[float, float] | None:
    """Whether a company-quarter is a cell this appendix will score, and its price range.

    Two families at least, a positive low, and a high no more than `CLASS_GUARD` above it.
    One function because it was two: `cells` and `level_deviation` each wrote the same three
    lines, so legs two and three of Appendix B ran on cell sets that were equal only because
    nobody had yet edited one of them. `test_shared_constants` cannot see this class — it
    matches module-level constant NAMES, and a predicate inlined twice inside one module has
    no name to match.

    Returns the (low, high) pair the caller needs anyway, so a caller cannot re-derive it
    differently, and `None` when the cell does not qualify.
    """
    if g.family.nunique() < 2:
        return None
    lo, hi = g.pps.min(), g.pps.max()
    if lo <= 0 or hi / lo > CLASS_GUARD:
        return None
    return float(lo), float(hi)


def cells(fam_q: pd.DataFrame) -> pd.DataFrame:
    """One row per company-quarter with >=2 families: the cross-family spread, and whether
    every family in the cell moved its mark that quarter.

    `judgeable` marks the cells where freshness can actually be determined — every family
    present has an observation in the immediately preceding quarter to compare against. A
    cell that opens a family's series carries no evidence either way and must not be scored
    as "stood pat"; the comparison in main() is therefore run on judgeable cells only."""
    rows = []
    for (co, q), g in fam_q.groupby(["company", "q"]):
        rng = qualifies(g)
        if rng is None:
            continue
        lo, hi = rng
        n_fam = g.family.nunique()
        known = g[g.adjacent]
        judgeable = len(known) == n_fam
        n_moved = int(known.remarked.sum()) if judgeable else -1
        rows.append({"company": co, "quarter": str(q), "n_families": n_fam,
                     "spread_pct": (hi / lo - 1) * 100,
                     "judgeable": judgeable,
                     "n_moved": n_moved,
                     "all_remarked": bool(judgeable and known.remarked.all()),
                     "none_remarked": bool(judgeable and n_moved == 0),
                     "families": ",".join(sorted(g.family))})
    return pd.DataFrame(rows).sort_values(["company", "quarter"])


def level_deviation(fam_q: pd.DataFrame) -> pd.DataFrame:
    """Each family's mark relative to the cross-family median of the same cell."""
    rows = []
    for (_co, _q), g in fam_q.groupby(["company", "q"]):
        if qualifies(g) is None:
            continue
        med = g.pps.median()
        for _, r in g.iterrows():
            rows.append({"family": r.family, "rel_dev_pct": (r.pps / med - 1) * 100})
    # An empty `rows` is a frame with no columns, and `groupby("family")` on one raises
    # "No group keys passed!" — a message that names neither this function nor the filter that
    # emptied it. It is reachable: `sensitivity` sweeps CLASS_GUARD down to 2.0, and a panel
    # narrow enough for that to remove every multi-family cell would report a pandas internal
    # instead of "nothing qualified". Say so in the shape the caller expects.
    d = pd.DataFrame(rows, columns=["family", "rel_dev_pct"])
    return (d.groupby("family").rel_dev_pct
             .agg(cells="size", mean_dev_pct="mean", median_dev_pct="median").round(2))


def sensitivity() -> dict:
    """The test rests on two thresholds I chose (what counts as a mark "moving", and the
    class guard) and on cells that are not independent (105 company-quarters over seven
    companies). Sweep both thresholds, and collapse the panel to one comparison per company
    so the clustering cannot carry the result."""
    global REMARK_TOL, CLASS_GUARD
    tol0, guard0 = REMARK_TOL, CLASS_GUARD
    out: dict = {"tol": [], "guard": []}
    try:
        for t in (0.001, 0.0025, 0.005, 0.01, 0.02, 0.05):
            REMARK_TOL = t
            ok = cells(load())
            ok = ok[ok.judgeable]
            fr, st = ok[ok.all_remarked], ok[~ok.all_remarked]
            out["tol"].append({"tol": t, "fresh": fr.spread_pct.median(),
                               "stale": st.spread_pct.median(),
                               "p": float(mannwhitneyu(fr.spread_pct, st.spread_pct,
                                                       alternative="less")[1])})
        REMARK_TOL = tol0
        for g in (2.0, 3.0, 4.0, 6.0, float("inf")):
            CLASS_GUARD = g
            ok = cells(load())
            ok = ok[ok.judgeable]
            fr, st = ok[ok.all_remarked], ok[~ok.all_remarked]
            out["guard"].append({"guard": g, "fresh": fr.spread_pct.median(),
                                 "stale": st.spread_pct.median(),
                                 "p": float(mannwhitneyu(fr.spread_pct, st.spread_pct,
                                                         alternative="less")[1])})
    finally:
        REMARK_TOL, CLASS_GUARD = tol0, guard0

    ok = cells(load())
    ok = ok[ok.judgeable]
    rows = []
    for co, g in ok.groupby("company"):
        fr, st = g[g.all_remarked], g[~g.all_remarked]
        if len(fr) and len(st):
            rows.append({"company": co, "n_fresh": len(fr), "med_fresh": fr.spread_pct.median(),
                         "n_stale": len(st), "med_stale": st.spread_pct.median()})
    by_co = pd.DataFrame(rows)
    out["by_company"] = by_co
    out["companies_fresh_wider"] = int((by_co.med_fresh > by_co.med_stale).sum())
    out["companies_compared"] = len(by_co)      # companies with cells of BOTH kinds
    out["n_companies"] = int(ok.company.nunique())
    out["n_cells"] = len(ok)
    return out


def coverage_and_drift(fam_q: pd.DataFrame) -> None:
    """Two facts the fund record supplies about its own limits: (a) the demand-unfavored panel
    names carry no fund marks at all, so the §7.2 sign-split cannot be re-run on marks; (b) on
    the one name whose headline round is old enough for marks to have moved since, the tracer
    drift and the Forge gap can be compared directly."""
    panel = pd.read_csv(ROOT / "data" / "valuation_panel.csv")
    marks = pd.read_csv(ROOT / "data" / "fund_marks.csv")
    held = set(marks.company)
    favored = panel.sector.isin(FAVORED_SECTORS)
    covered = panel.company.isin(held)
    print("\n=== COVERAGE: which side of the sector split does N-PORT see? ===")
    print(f"  demand-favored panel names : {int(favored.sum())}, of which "
          f"{int((favored & covered).sum())} carry an N-PORT mark")
    print(f"  the rest                   : {int((~favored).sum())}, of which "
          f"{int((~favored & covered).sum())} do "
          f"({', '.join(panel[~favored & covered].company)})")
    deep = panel.sector.isin(DEEP_DISCOUNT_SECTORS)
    print(f"  the deep-discount cohort (crypto/quantum/energy): {int(deep.sum())} names, of which "
          f"{int((deep & covered).sum())} carry a mark")

    print("\n=== DRIFT vs FORGE, where the round is old enough to have drifted ===")
    for _, r in panel.iterrows():
        g = fam_q[fam_q.company == r.company]
        if g.empty:
            continue
        try:
            rq = pd.Period(str(r.headline_date).replace("-", ""), freq="Q") if "Q" in str(r.headline_date) \
                else pd.Period(pd.to_datetime(str(r.headline_date) + "-01"), freq="Q")
        except Exception:
            continue
        at = g[g.q <= rq]
        if at.empty or (g.q.max() - at.q.max()).n < 4:   # need >=1 year of drift
            continue
        p0 = at[at.q == at.q.max()].pps.median()
        p1 = g[g.q == g.q.max()].pps.median()
        forge_gap = r.forge_val_busd / r.headline_val_busd - 1
        print(f"  {r.company:12} round {rq}  mark {p0:.2f} -> {p1:.2f} = {p1/p0-1:+.1%}"
              f"   |  Forge gap {forge_gap:+.1%}")


def main() -> None:
    fam_q = load()
    rates = remark_rates(fam_q)
    cl = cells(fam_q)
    dev = level_deviation(fam_q)

    print("=== (1) REMARK RATE BY FAMILY (adjacent quarters, |change| > 0.5%) ===")
    print(rates.to_string())
    adj = fam_q[fam_q.adjacent]
    overall = adj.remarked.mean()
    moved = (adj[adj.remarked].pps / adj[adj.remarked].prev_pps - 1).abs().median()
    print(f"\noverall remark rate: {overall:.3f}   "
          f"(range {rates.remark_rate.min():.2f}-{rates.remark_rate.max():.2f});  "
          f"median |move| when a mark moves: {moved:.3f}")

    ok = cl[cl.judgeable]
    fresh, rest = ok[ok.all_remarked], ok[~ok.all_remarked]
    print("\n=== (2) DECISIVE TEST: spread where every family just remarked ===")
    print(f"  multi-family cells          : {len(cl)}  (judgeable: {len(ok)}; "
          f"{len(cl) - len(ok)} open a family's series and carry no freshness evidence)")
    print(f"  all judgeable cells         : median spread {ok.spread_pct.median():.1f}%  (n={len(ok)})")
    print(f"  every family remarked       : median spread {fresh.spread_pct.median():.1f}%  (n={len(fresh)})")
    print(f"  at least one did not        : median spread {rest.spread_pct.median():.1f}%  (n={len(rest)})")
    if len(fresh) and len(rest):
        u, p = mannwhitneyu(fresh.spread_pct, rest.spread_pct, alternative="less")
        print(f"  one-sided MWU that fresh cells are SMALLER: U={u:.0f}, p={p:.3f}"
              f"  -> {'staleness supported' if p < 0.05 else 'staleness NOT supported'}")

    print("\n=== (3) LEVEL DEVIATION vs REMARK RATE ===")
    print(dev.join(rates.remark_rate).sort_values("remark_rate").to_string())

    s = sensitivity()
    print("\n=== (4) SENSITIVITY TO MY TWO THRESHOLDS, AND TO THE CLUSTERING ===")
    print("  remark tolerance   " + "  ".join(
        f"{r['tol']:.3g}:{r['fresh']:.1f}/{r['stale']:.1f}(p{r['p']:.2f})" for r in s["tol"]))
    print("  class guard        " + "  ".join(
        f"{r['guard']:.3g}:{r['fresh']:.1f}/{r['stale']:.1f}(p{r['p']:.2f})" for r in s["guard"]))
    print("  (each entry: fresh median % / stale median % (one-sided p))")
    print(f"\n  one comparison per company (the {s['n_cells']} cells span only "
          f"{s['n_companies']} companies):")
    print(s["by_company"].round(1).to_string(index=False))
    print(f"  companies where the freshly-remarked cells are WIDER: "
          f"{s['companies_fresh_wider']} of {s['companies_compared']}")

    quiet = ok[ok.none_remarked]
    print("\n=== (5) THE RIVAL STORY: is the disagreement only a repricing episode? ===")
    print("  Conditioning on 'every family moved' selects quarters with news. If the spread")
    print("  lived only in those episodes, quiet quarters would show none.")
    print(f"  quiet cells (nobody moved): n={len(quiet)}, median spread "
          f"{quiet.spread_pct.median():.1f}%, {(quiet.spread_pct > 5).mean():.0%} above 5%")
    print("  " + ", ".join(f"{r.company} {r.quarter} {r.spread_pct:.1f}%"
                           for r in quiet.itertuples()))
    print("  -> too few to settle it; reported as an open question, not as support.")

    coverage_and_drift(fam_q)

    cl.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.relative_to(ROOT)}  ({len(cl)} cells)")


if __name__ == "__main__":
    main()
