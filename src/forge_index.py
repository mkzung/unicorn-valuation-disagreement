"""
Forge Private Market Index (^FPMI) vs the N-PORT fund-mark cycle — the
secondary-market corroboration of the fund-mark trajectory (paper section 4.6).

Two INDEPENDENT public signals of late-stage private value across 2021-2026:
  (1) Forge FPMI — an equal-weighted secondary-market index of ~75 actively-traded
      private companies (Forge Data LLC; secondary trades + IOIs). We do NOT
      republish Forge's table; we take Forge's own PUBLISHED index level and
      trailing returns (facts/estimates, attributed) and derive dated anchor
      levels -> data/forge_index.csv. Compliance: single-source-with-attribution
      is the sanctioned treatment for a proprietary index (notes/compliance_audit.md);
      every anchor carries its source + derivation; no automated scraping in the
      pipeline (the CSV is hand-entered from Forge-published figures).
  (2) N-PORT fund marks — the equal-weighted cross-fund MEDIAN price/share path
      we built in src/fund_marks_timeseries.py from SEC filings (public domain).

The test of the paper's thesis along the cycle: do two signals built from
completely different data-generating processes (secondary transactions vs
mutual-fund Level-3 model marks) trace the SAME markup -> markdown -> re-markup?

HONEST SCOPE. The FPMI anchors are coarse (annual trailing-return points + the
2025-26 recovery sampled quarterly), so the corroboration is at the level of
cycle SHAPE and drawdown/recovery MAGNITUDE, not a tick-by-tick correlation. The
FPMI 2021 anchor predates the true cycle peak, so its drawdown is a LOWER BOUND.

Run: python3 src/forge_index.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import fund_marks_timeseries as ts

ROOT = Path(__file__).resolve().parents[1]

# the deep names with a full 2021->2026 cross-fund path and an obs at the 2021Q4 anchor
INDEX_NAMES = ["Databricks", "Stripe", "Canva", "Discord"]
ANCHOR_Q = "2021Q4"          # rebase the fund-mark index to 100 here
END_Q = "2026Q1"             # last quarter with the constant-4 composition present


def _qorder(q):
    y, n = int(q[:4]), int(q[5])
    return y * 4 + (n - 1)


def load_fpmi():
    f = pd.read_csv(ROOT / "data" / "forge_index.csv")
    f["date"] = pd.to_datetime(f["date"])
    return f.sort_values("date").reset_index(drop=True)


def fund_mark_index():
    """Equal-weighted index of the cross-fund MEDIAN price/share for INDEX_NAMES,
    rebased to 100 at ANCHOR_Q. Each name's median path is forward-filled only
    WITHIN its active window (a quarterly mark persists until the next filing); the
    index at quarter q is the equal-weighted mean of the names active at q."""
    df = ts.load()
    tidy = pd.concat([ts.clean_company(co, g) for co, g in df.groupby("company")
                      if co in INDEX_NAMES], ignore_index=True)

    meds = {}
    for co, g in tidy.groupby("company"):
        meds[co] = g.groupby("quarter")["pps"].median().sort_index()

    allq = sorted({q for s in meds.values() for q in s.index}, key=_qorder)
    allq = [q for q in allq if _qorder(ANCHOR_Q) <= _qorder(q) <= _qorder(END_Q)]

    rebased = {}
    for co, s in meds.items():
        s = s.sort_index(key=lambda idx: idx.map(_qorder))
        # forward-fill within the active window only
        active = [q for q in allq if _qorder(s.index.min()) <= _qorder(q) <= _qorder(s.index.max())]
        ss = s.reindex(sorted(set(list(s.index) + active), key=_qorder)).ffill()
        ss = ss.reindex(active)
        if ANCHOR_Q in ss.index and pd.notna(ss.get(ANCHOR_Q)):
            rebased[co] = ss / ss[ANCHOR_Q] * 100.0

    idx = pd.DataFrame(rebased).reindex(allq)
    n_present = idx.notna().sum(axis=1)
    index = idx.mean(axis=1)                      # equal-weighted across names active at q
    index = index[n_present >= 3]                 # require >=3 of 4 for a clean composition
    return index, idx, n_present


def cycle_from_path(level: pd.Series):
    """Max-drawdown decomposition for a level series (index = ordered labels)."""
    peak_run = level.cummax()
    dd = level / peak_run - 1
    trough_lbl = dd.idxmin(); trough = level[trough_lbl]
    pre = level.loc[:trough_lbl]
    peak_lbl = pre.idxmax(); peak = level[peak_lbl]
    return {
        "first": level.iloc[0], "first_lbl": level.index[0],
        "peak": peak, "peak_lbl": peak_lbl,
        "trough": trough, "trough_lbl": trough_lbl,
        "last": level.iloc[-1], "last_lbl": level.index[-1],
        "drawdown_pct": (trough / peak - 1) * 100,
        "recovery_pct": (level.iloc[-1] / trough - 1) * 100,
    }


def main():
    fpmi = load_fpmi()
    flevel = pd.Series(fpmi.fpmi_level.values, index=fpmi.date)
    fc = cycle_from_path(flevel)

    fmi, parts, n_present = fund_mark_index()
    mc = cycle_from_path(fmi)

    print("=" * 90)
    print("FORGE FPMI (secondary index)  vs  N-PORT FUND-MARK INDEX  — same cycle? (section 4.6)")
    print("=" * 90)
    print("\nForge FPMI anchor path (Forge Data LLC, published level + trailing returns; coarse):")
    for d, lv, bs in zip(fpmi.date.dt.date, fpmi.fpmi_level, fpmi.basis):
        print(f"  {d}   {lv:7.2f}   {bs}")
    print(f"\n  FPMI peak-region {fc['peak_lbl'].date()} {fc['peak']:.1f} -> trough-region "
          f"{fc['trough_lbl'].date()} {fc['trough']:.1f}: drawdown {fc['drawdown_pct']:.0f}% "
          f"(LOWER BOUND — 2021 anchor predates the true peak)")
    print(f"  FPMI trough -> latest {fc['last_lbl'].date()} {fc['last']:.1f}: "
          f"recovery +{fc['recovery_pct']:.0f}%")

    print(f"\nFund-mark equal-weighted index ({len(INDEX_NAMES)} deep names {INDEX_NAMES}, "
          f"rebased {ANCHOR_Q}=100):")
    print(fmi.round(1).to_string())
    print(f"\n  fund-mark index peak {mc['peak_lbl']} {mc['peak']:.1f} -> trough "
          f"{mc['trough_lbl']} {mc['trough']:.1f}: drawdown {mc['drawdown_pct']:.0f}%")
    print(f"  fund-mark index trough -> latest {mc['last_lbl']} {mc['last']:.1f}: "
          f"recovery +{mc['recovery_pct']:.0f}%")

    # descriptive cross-signal correlation on matched dates (coarse -> caveated, not headline)
    qdate = {"2023Q2": "2023-06-24", "2025Q2": "2025-06-24",
             "2025Q4": "2025-12-31", "2026Q1": "2026-03-31"}
    pairs = []
    for q, d in qdate.items():
        if q in fmi.index and pd.Timestamp(d) in flevel.index:
            pairs.append((flevel[pd.Timestamp(d)], fmi[q]))
    corr = np.nan
    if len(pairs) >= 3:
        a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
        corr = np.corrcoef(a, b)[0, 1]
    print(f"\nMatched-date level correlation (n={len(pairs)} coarse points, DESCRIPTIVE only): "
          f"rho={corr:.2f}")
    print("  -> Both signals: a ~50% drawdown into 2023 and a ~2-3x recovery by 2026.")
    print("     Corroboration is cycle SHAPE + MAGNITUDE, not tick-by-tick (FPMI anchors are coarse).")

    out = pd.DataFrame({"fund_mark_index": fmi})
    out.to_csv(ROOT / "data" / "forge_vs_fundmarks.csv")
    print("\nwrote data/forge_vs_fundmarks.csv")
    _figure(flevel, fc, fmi, mc)
    return fc, mc, corr


def _figure(flevel, fc, fmi, mc):
    """Overlay both signals rebased to 100 at ~end-2021, on a shared date axis."""
    fig, ax = plt.subplots(figsize=(10, 5.6))

    # FPMI rebased to its first anchor = 100
    fr = flevel / flevel.iloc[0] * 100
    ax.plot(fr.index, fr.values, marker="o", ms=8, lw=2.4, color="#1f77b4",
            label="Forge FPMI (secondary index, Forge Data LLC) — anchors", zorder=5)
    for d, v in fr.items():
        ax.annotate(f"{v:.0f}", (d, v), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=8, color="#1f77b4")

    # fund-mark index: quarter labels -> approx quarter-end dates for a shared x-axis
    qend = {q: pd.Timestamp(f"{q[:4]}-{ {1:'03-31',2:'06-30',3:'09-30',4:'12-31'}[int(q[5])] }")
            for q in fmi.index}
    fx = [qend[q] for q in fmi.index]
    ax.plot(fx, fmi.values, marker="s", ms=4, lw=2.0, color="#d62728",
            label=f"N-PORT fund-mark index (equal-wt, {len(INDEX_NAMES)} names) — quarterly", zorder=4)

    ax.axhline(100, color="grey", ls=":", lw=1)
    ax.set_yscale("log")
    ax.set_ylabel("index, rebased to 100 at end-2021 (log scale)")
    ax.set_xlabel("")
    ax.set_title("Two independent public signals trace the same private-market cycle, 2021–2026\n"
                 "Forge secondary-market index vs SEC N-PORT mutual-fund Level-3 marks "
                 "(both rebased; FPMI anchors coarse)", fontsize=11)
    note = (f"FPMI: drawdown {fc['drawdown_pct']:.0f}% (lower bound) → recovery +{fc['recovery_pct']:.0f}%\n"
            f"Fund marks: drawdown {mc['drawdown_pct']:.0f}% → recovery +{mc['recovery_pct']:.0f}%")
    ax.annotate(note, xy=(0.015, 0.97), xycoords="axes fraction", va="top", fontsize=8.5,
                bbox=dict(boxstyle="round", fc="#f6f6f6", ec="#bbb"))
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    ax.grid(alpha=0.25, which="both")
    plt.tight_layout()
    fig.savefig(ROOT / "figures" / "forge_vs_fundmarks.png", dpi=150)
    print("saved figures/forge_vs_fundmarks.png")


if __name__ == "__main__":
    main()
