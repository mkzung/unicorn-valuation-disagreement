"""
N-PORT fund-mark TIME SERIES — the markup/markdown/re-markup trajectory.

Companion to src/fund_marks.py (cross-section). Input: data/fund_marks_timeseries.csv
(from src/nport_timeseries.py). For each tracer fund we have the blended implied
price/share it disclosed for a private unicorn EACH QUARTER, 2019-2026.

Two questions, both public-domain:
  (1) Within a fund, how did the mark move across the cycle? -> peak (2021-22),
      drawdown (2022-23 reset), recovery (2024-26 AI rebound).
  (2) Across funds holding the SAME name, do they AGREE on the DIRECTION of re-marking,
      even though the cross-section shows they disagree on the LEVEL at a point in time?

Data hygiene (each documented, reproducible):
  - SpaceX is EXCLUDED from the per-share trajectory: a 10:1 split (Feb 2022) coincided
    with funds holding different share classes, so its per-share path is not cleanly
    comparable (same reason src/fund_marks.py drops it cross-sectionally). Rows are kept
    in the CSV as public facts; only the indexed analysis excludes it.
  - SPLIT ADJUSTMENT: a consecutive-quarter price ratio in ~[1/11..1/9] or [9..11] is a
    share-count restatement, not a valuation move (Discord restated 10:1 in 2026); each
    fund series is made continuous by accumulating the inverse factor.
  - UNIT OUTLIERS: after split adjustment, a point >4x off its own fund-series median is a
    filing/unit artifact (e.g. a T. Rowe OpenAI line at $7.70 while ARK marked it $652)
    and is dropped. The 4x band is wide enough to preserve the real 2022 writedowns
    (Databricks fell ~4.7x peak-to-trough; that is kept).

Run: python3 src/fund_marks_timeseries.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_PERSHARE = {"SpaceX"}          # multi-class + 2022 split -> per-share not comparable
SPLIT_LO, SPLIT_HI = 9.0, 11.0         # ~10:1 share-count restatement band
OUTLIER_K = 4.0                        # drop a point >K x off its fund-series median


def qlabel(d):
    y, m = int(d[:4]), int(d[5:7])
    return f"{y}Q{(m - 1) // 3 + 1}"


def load():
    df = pd.read_csv(ROOT / "data" / "fund_marks_timeseries.csv")
    df["pps"] = pd.to_numeric(df["pps"], errors="coerce")
    df["quarter"] = df["report_date"].map(qlabel)
    # one mark per (company, fund, quarter): keep the latest report_date in that quarter
    df = (df.sort_values("report_date")
            .drop_duplicates(["company", "fund", "quarter"], keep="last"))
    return df


def split_adjust(series):
    """series: pd.Series of pps indexed by sorted quarter. Remove ~10:1 share-count
    restatements so the price path is continuous; return the adjusted Series."""
    v = series.values.astype(float)
    factor = np.ones(len(v))
    cum = 1.0
    for i in range(1, len(v)):
        r = v[i] / v[i - 1]
        if SPLIT_LO <= r <= SPLIT_HI:          # 10x jump up = post-restatement scale up
            cum /= round(r)
        elif 1 / SPLIT_HI <= r <= 1 / SPLIT_LO:  # 10x drop = 10:1 split
            cum *= round(1 / r)
        factor[i] = cum
    adj = v * factor
    # renormalise so the most recent observation keeps its real reported scale
    adj = adj / factor[-1]
    return pd.Series(adj, index=series.index)


def clean_company(co, g):
    """Return tidy (quarter, fund, pps) for one company: split-adjusted, outliers dropped."""
    out = []
    for fund, fg in g.groupby("fund"):
        s = fg.set_index("quarter")["pps"].sort_index()
        s = split_adjust(s)
        med = s.median()
        s = s[(s <= OUTLIER_K * med) & (s >= med / OUTLIER_K)]   # drop unit junk
        for q, p in s.items():
            out.append({"company": co, "fund": fund, "quarter": q, "pps": p})
    return pd.DataFrame(out)


def cycle_metrics(med):
    """med: Series of cross-fund median pps indexed by sorted quarter -> cycle stats, using
    the standard MAXIMUM-DRAWDOWN decomposition so a name that recovered to a NEW high
    (Stripe, OpenAI) still surfaces its 2022-23 reset rather than reporting a 0% drawdown."""
    q = list(med.index)
    first_q, first = q[0], med.iloc[0]
    last_q, last = q[-1], med.iloc[-1]
    dd = med / med.cummax() - 1                  # drawdown from the running peak at each point
    trough_q = dd.idxmin(); trough = med[trough_q]
    peak_q = med.loc[:trough_q].idxmax(); peak = med[peak_q]   # the peak that preceded it
    return {
        "n_q": len(q), "first_q": first_q, "first": first,
        "peak_q": peak_q, "peak": peak,
        "trough_q": trough_q, "trough": trough, "last_q": last_q, "last": last,
        "run_up_pct": (peak / first - 1) * 100 if first else np.nan,
        "drawdown_pct": (trough / peak - 1) * 100,           # = max drawdown
        "recovery_pct": (last / trough - 1) * 100,
        "net_pct": (last / first - 1) * 100 if first else np.nan,
    }


def comovement(tidy):
    """For each co-held name with >=4 overlapping quarters between a fund pair, the median
    pairwise correlation of (log) mark LEVELS and of QoQ log-CHANGES. Co-movement is the
    cross-fund time-series counterpart to the cross-section's level disagreement: funds can
    differ on the level yet re-mark in step -- WHERE their holding windows overlap."""
    rows = []
    for co, g in tidy.groupby("company"):
        wide = g.pivot_table(index="quarter", columns="fund", values="pps").sort_index()
        if wide.shape[1] < 2:
            continue
        lvl = np.log(wide); chg = lvl.diff()
        funds = list(wide.columns)
        lcs, ccs = [], []
        for i in range(len(funds)):
            for j in range(i + 1, len(funds)):
                a, b = lvl[funds[i]], lvl[funds[j]]
                m = a.notna() & b.notna()
                if m.sum() >= 4:
                    lcs.append(a[m].corr(b[m]))
                    ca, cb = chg[funds[i]], chg[funds[j]]
                    m2 = ca.notna() & cb.notna()
                    if m2.sum() >= 4:
                        ccs.append(ca[m2].corr(cb[m2]))
        if lcs:
            rows.append({"company": co, "n_funds": len(funds),
                         "level_rho": np.median(lcs),
                         "change_rho": np.median(ccs) if ccs else np.nan,
                         "max_overlap_pairs": len(lcs)})
    return pd.DataFrame(rows).sort_values("level_rho", ascending=False) if rows else pd.DataFrame()


def main():
    df = load()
    tidy = pd.concat([clean_company(co, g) for co, g in df.groupby("company")
                      if co not in EXCLUDE_PERSHARE], ignore_index=True)

    # cross-fund median path per company
    rows = []
    paths = {}
    for co, g in tidy.groupby("company"):
        med = g.groupby("quarter")["pps"].median().sort_index()
        paths[co] = (g, med)
        m = cycle_metrics(med)
        m["company"] = co
        m["n_funds"] = g["fund"].nunique()
        rows.append(m)
    R = pd.DataFrame(rows).set_index("company").sort_values("n_q", ascending=False)

    cols = ["n_funds", "n_q", "first_q", "first", "peak_q", "peak", "trough_q", "trough",
            "last_q", "last", "run_up_pct", "drawdown_pct", "recovery_pct", "net_pct"]
    print("=" * 92)
    print("N-PORT FUND-MARK TIME SERIES — cross-fund median price/share path, 2019–2026")
    print("  (split-adjusted; SpaceX excluded from per-share path; public-domain SEC marks)")
    print("=" * 92)
    with pd.option_context("display.width", 200, "display.max_columns", 30):
        print(R[cols].to_string(float_format=lambda x: f"{x:.1f}"))

    deep = R[R.n_q >= 10]
    print(f"\nWithin-fund cycle — names with >=10 quarters: {', '.join(deep.index)}")
    print(f"  median max drawdown (2022–23 reset): {deep.drawdown_pct.median():.0f}%")
    print(f"  median trough->latest recovery:      +{deep.recovery_pct.median():.0f}%")
    print(f"  drawdown troughs cluster in: {sorted(set(deep.trough_q))}")

    cm = comovement(tidy)
    print("\nCross-fund co-movement (funds that co-hold a name, >=4 overlapping quarters):")
    if not cm.empty:
        with pd.option_context("display.width", 160):
            print(cm.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
        db = cm[cm.company == "Databricks"]
        if not db.empty:
            print(f"  Databricks (deepest overlap, {int(db.n_funds.iloc[0])} funds): level rho="
                  f"{db.level_rho.iloc[0]:.2f}, QoQ-change rho={db.change_rho.iloc[0]:.2f} — funds "
                  f"re-mark in step over time though the cross-section shows they differ on level.")
        print("  Honest caveat: co-movement needs overlap; staggered entrants (Discord) track loosely.")

    R[cols].to_csv(ROOT / "data" / "fund_marks_timeseries_summary.csv")
    print("\nwrote data/fund_marks_timeseries_summary.csv")
    _figure(paths, R)


def _figure(paths, R):
    """Small multiples: each deep name's per-fund marks (thin) + cross-fund median (bold),
    log y, with the 2021-22 peak and 2022-23 trough marked."""
    feat = R[R.n_q >= 10].sort_values("n_q", ascending=False).index.tolist()
    n = len(feat)
    ncol = 2
    nrow = (n + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(15, 4.7 * nrow), squeeze=False)
    allq = sorted({q for co in feat for q in paths[co][1].index})

    for k, co in enumerate(feat):
        ax = axes[k // ncol][k % ncol]
        g, med = paths[co]
        for fund, fg in g.groupby("fund"):
            s = fg.set_index("quarter")["pps"].reindex(allq)
            ax.plot(range(len(allq)), s.values, marker="o", ms=4, lw=1.6,
                    alpha=0.65, label=fund.replace(" Fund", "").replace(" Growth", ""))
        ax.plot([allq.index(q) for q in med.index], med.values, color="black",
                lw=2.4, zorder=5, label="cross-fund median")
        m = R.loc[co]
        for qq, mk, c in [(m.peak_q, "peak", "#c0392b"), (m.trough_q, "trough", "#2471a3")]:
            ax.axvline(allq.index(qq), color=c, ls="--", lw=1, alpha=0.7)
        ax.set_title(f"{co}  ·  {int(m.n_funds)} fund(s), {int(m.n_q)} q  ·  "
                     f"peak→trough {m.drawdown_pct:.0f}%, recovery +{m.recovery_pct:.0f}%",
                     fontsize=12)
        ax.set_yscale("log")
        ax.tick_params(labelsize=10)
        ax.set_ylabel("implied $/share (log)", fontsize=11)
        step = max(1, len(allq) // 8)
        ax.set_xticks(range(0, len(allq), step))
        ax.set_xticklabels([allq[i] for i in range(0, len(allq), step)], rotation=45, fontsize=10)
        ax.grid(alpha=0.25, which="both")
        # legend BELOW the panel (outside the data) so it never overlaps the lines
        ax.legend(fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.26),
                  ncol=min(g["fund"].nunique() + 1, 3), frameon=False,
                  handlelength=1.7, columnspacing=1.3, borderpad=0.2)
    for k in range(n, nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")

    fig.suptitle("How mutual funds re-marked the same private companies, 2019–2026\n"
                 "SEC N-PORT Level-3 fair-value marks · same security tracked quarterly · "
                 "dashed = cross-fund peak (red) / trough (blue)", fontsize=14)
    fig.subplots_adjust(hspace=0.92, wspace=0.22, top=0.93, bottom=0.04, left=0.07, right=0.97)
    fig.savefig(ROOT / "figures" / "fund_marks_timeseries.png", dpi=200, bbox_inches="tight")
    print("saved figures/fund_marks_timeseries.png")


if __name__ == "__main__":
    main()
