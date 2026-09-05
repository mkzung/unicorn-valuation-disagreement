"""
Unicorn Valuation Disagreement — headline (last primary round) vs Forge secondary estimate.
Public-data fact compilation; Forge figures cited with attribution (Forge Global, via its
published estimates). Computes OUR derived metric: the secondary-to-headline gap.

Run: python3 src/analyze.py
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Behind a guard. This module's body ran on import, and two of the things it does are not
# harmless: it prints a table, and it writes two figures into `figures/`. Both belong to a leg
# cut to a second paper, and both were deliberately deleted from the repository — so importing
# this module put back a file `test_the_figures_directory_holds_exactly_what_the_paper_cites`
# exists to keep out. Found by importing it.
def main() -> None:
    df = pd.read_csv(ROOT / "data" / "valuation_panel.csv")

    # OUR derived metric: secondary-to-headline gap (positive = Forge secondary ABOVE last round)
    df["gap_pct"] = (df["forge_val_busd"] / df["headline_val_busd"] - 1.0) * 100.0
    df["sign"] = np.where(df["gap_pct"] >= 0, "above", "below")

    clean = df[df["quality_flag"] == "clean"].copy()

    def summarize(name, d):
        print(f"\n=== {name} (n={len(d)}) ===")
        print(f"  median gap: {d['gap_pct'].median():+.1f}%   mean: {d['gap_pct'].mean():+.1f}%")
        print(f"  above headline: {(d['gap_pct']>=0).sum()}   below: {(d['gap_pct']<0).sum()}")
        print(f"  range: {d['gap_pct'].min():+.1f}% ({d.loc[d.gap_pct.idxmin(),'company']})"
              f"  to {d['gap_pct'].max():+.1f}% ({d.loc[d.gap_pct.idxmax(),'company']})")

    summarize("CLEAN primary-round subset", clean)
    summarize("FULL panel (incl. flagged)", df)

    print("\n--- by sector (clean) ---")
    print(clean.groupby("sector")["gap_pct"].agg(["count", "median"]).round(1).to_string())

    print("\n--- per company (sorted) ---")
    print(df.sort_values("gap_pct", ascending=False)
          [["company","sector","headline_val_busd","forge_val_busd","gap_pct","quality_flag"]]
          .to_string(index=False, formatters={"gap_pct": lambda x: f"{x:+.1f}%"}))

    # ---- Figure 1: gap bar chart ----
    d = df.sort_values("gap_pct")
    colors = ["#c0392b" if g < 0 else "#27ae60" for g in d["gap_pct"]]
    hatch = ["//" if q != "clean" else "" for q in d["quality_flag"]]
    fig, ax = plt.subplots(figsize=(12, 7.5))
    bars = ax.barh(d["company"], d["gap_pct"], color=colors, edgecolor="black", linewidth=0.6)
    for b, h in zip(bars, hatch):
        if h:
            b.set_hatch(h)
    ax.axvline(0, color="black", lw=1)
    ax.set_xlabel("Forge secondary estimate vs last headline round  (%)")
    ax.set_title("Unicorn valuation disagreement, June 2026\nSecondary above (green) / below (red) the last primary round; hatched = flagged headline", fontsize=12)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    fig.savefig(ROOT / "figures" / "gap_chart.png", dpi=200, bbox_inches="tight")
    print("\nsaved figures/gap_chart.png")

    # ---- Figure 2: headline vs forge log-log ----
    fig2, ax2 = plt.subplots(figsize=(13, 13))
    ax2.scatter(df["headline_val_busd"], df["forge_val_busd"],
                c=["#c0392b" if g < 0 else "#27ae60" for g in df["gap_pct"]], s=55, edgecolor="black", zorder=3)
    lim = [0.7, 1300]   # wide enough to include the deep-discount names (Forge ~$1B) and the mega-caps
    ax2.plot(lim, lim, "k--", alpha=0.6, label="parity (secondary = headline)")
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlim(lim); ax2.set_ylim(lim)
    ax2.set_xlabel("Last headline round valuation  ($B, log)")
    ax2.set_ylabel("Forge secondary estimate  ($B, log)")
    ax2.set_title("Headline vs secondary, June 2026")
    ax2.legend(loc="upper left"); ax2.grid(alpha=0.3, which="both")
    # Non-overlapping labels: adjustText repels the labels off each other and the points,
    # with thin leader lines back to each marker. Falls back to a plain offset if the
    # library is unavailable, so reproduce.py never hard-fails on a missing optional dep.
    _texts = [ax2.text(r["headline_val_busd"], r["forge_val_busd"], r["company"], fontsize=7)
              for _, r in df.iterrows()]
    try:
        from adjustText import adjust_text
        # iter_lim is what makes this figure reproducible. Left to itself adjustText stops on a
        # one-second wall-clock budget, so the labels land wherever the machine happened to get
        # to and the PNG differs on every run; a fixed iteration count removes the clock.
        adjust_text(_texts, ax=ax2, expand=(2.0, 2.8), force_text=(1.0, 1.8),
                    only_move={"text": "xy", "static": "xy"}, iter_lim=400,
                    arrowprops=dict(arrowstyle="-", color="0.6", lw=0.5))
    except Exception as _e:
        print(f"  (adjustText unavailable: {_e}; using plain offsets)")
        for t, (_, r) in zip(_texts, df.iterrows()):
            t.set_fontsize(7)
            t.set_position((r["headline_val_busd"] * 1.05, r["forge_val_busd"]))
    plt.tight_layout()
    fig2.savefig(ROOT / "figures" / "headline_vs_forge.png", dpi=200, bbox_inches="tight")
    print("saved figures/headline_vs_forge.png")



if __name__ == "__main__":
    main()
