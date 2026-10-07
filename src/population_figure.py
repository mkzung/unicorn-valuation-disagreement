"""Two views of the population panel: how often funds disagree, and where the money sits.

The manuscript's first ten companies were picked before the data were seen. Measured
between fund complexes rather than the legal trusts they file under, the population says
their median spread is close to typical rather than extreme; the figures are in
`src/paper_numbers.py`. Both panels below are the same guarded cells; they differ in what
they weight.

  left    the distribution of the spread itself, one point per cell. A sixth of the mass
          sits at exactly zero, so an ordinary histogram spends its range on an empty middle
          and a log axis cannot draw a zero at all. An ECDF keeps the zero atom visible as a
          step at the origin and still resolves a tail that runs into the hundreds.
  right   the same cells counted, and weighted by the dollars funds actually booked. The two
          weightings differ in both directions, which is the useful part: dollars are
          over-represented above the reference line the figure draws, while the very
          widest spreads sit among the smallest positions.

Reads the committed population panel; makes no network call.

Run:  python3 src/population_figure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop

OUT = ROOT / "figures" / "population_spread.png"

# Bucket edges and labels live in population.py, so this figure cannot drift away from
# Table 11. Only the display strings are local.
DISPLAY = {"identical": "0%\n(unanimous)", "0-10%": "0–10%", "10-24%": "10–24%",
           "24-50%": "24–50%", "50-100%": "50–100%", ">100%": ">100%"}

INK = "#1a1a1a"
BAR_LO = "#9ecae1"     # cells at or under the 24% line
BAR_HI = "#08519c"     # cells above it — where the paper says the money is
ACCENT = "#c1272d"


def panels() -> tuple[plt.Figure, dict]:
    _, c = pop.panel()
    g = c[c.guarded]
    s = g.spread_pct.to_numpy()
    nav = g.nav.to_numpy()

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.4))

    # ---- left: ECDF of the cell spread -------------------------------------------------
    xs = np.sort(s)
    ys = np.arange(1, len(xs) + 1) / len(xs) * 100
    axL.step(xs, ys, where="post", color=INK, lw=1.9)
    axL.set_xscale("symlog", linthresh=1.0)
    axL.set_xlim(-0.15, max(1200, xs.max()))
    axL.set_ylim(0, 100)
    axL.set_xlabel("spread between fund houses on one report date (%, symlog)")
    axL.set_ylabel("share of company-dates at or below (%)")

    at_zero = (s <= 1e-9).mean() * 100
    within_bp = (s <= 0.01).mean() * 100
    above24 = (s > 24).mean() * 100
    axL.axvline(24, color=ACCENT, ls="--", lw=1.3)
    # Above the curve rather than to the right of the rule: the space to the right is where
    # the linear inset goes, and the callout used to land on top of it.
    axL.annotate(f"the ten broadly-held names' median, 24%\n— {above24:.0f}% of cells exceed it",
                 xy=(24, 100 - above24), xytext=(1.9, 86),
                 color=ACCENT, fontsize=9.5, ha="left", va="center",
                 arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.1,
                                 connectionstyle="arc3,rad=0.15"))
    # The zero atom and the basis-point shoulder are the whole point of the panel, and on a
    # symlog axis they sit within a hair of each other. Mark both, with short arrows that do
    # not cross the curve.
    axL.plot([0], [at_zero], "o", ms=5.5, color=INK, zorder=5)
    # Sits well clear of the axis: at 15% the label used to start on top of the spine.
    axL.annotate(f"{at_zero:.0f}% of cells are unanimous",
                 xy=(0, at_zero), xytext=(0.9, 6), fontsize=9.5, color=INK,
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.1,
                                 connectionstyle="arc3,rad=-0.3"))
    axL.plot([0.01], [within_bp], "o", ms=5.5, color=INK, zorder=5)
    axL.annotate(f"{within_bp:.0f}% agree to within a basis point",
                 xy=(0.01, within_bp), xytext=(0.13, 70), fontsize=9.5, color=INK,
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.1,
                                 connectionstyle="arc3,rad=0.2"))
    axL.set_title("A. Between houses, disagreement is the normal state", loc="left",
                  fontsize=12, color=INK)
    axL.grid(alpha=0.25, lw=0.6)

    # The symlog axis compresses 0–1%, which is where the mass the panel is about actually
    # sits: the atom at zero and the shoulder inside a basis point are 28% of the cells and
    # about a centimetre of the axis. The inset reads that stretch on a linear scale, so the
    # two annotations above have somewhere to be checked rather than believed.
    # Bottom right: the only quadrant of this panel with nothing in it. Left of x=0.62 in
    # axes coordinates is the 24% rule and its callout, and the upper left is the
    # basis-point annotation.
    ins = axL.inset_axes([0.665, 0.10, 0.315, 0.30])
    ins.step(xs, ys, where="post", color=INK, lw=1.5)
    ins.set_xlim(0, 1.0)
    ins.set_ylim(0, 40)
    ins.axvline(0.01, color=INK, lw=0.8, ls=":")
    ins.tick_params(labelsize=7.5)
    ins.set_title("0–1%, linear", fontsize=8.5, color=INK, loc="left", pad=2)
    ins.grid(alpha=0.2, lw=0.5)
    for sp in ins.spines.values():
        sp.set_alpha(0.4)

    # ---- right: cells vs dollars, same buckets ------------------------------------------
    bk = pop.spread_buckets(g)
    cell_share = bk.cells_pct.to_numpy()
    nav_share = bk.nav_pct.to_numpy()
    labels = [DISPLAY[b] for b in bk.bucket]

    x = np.arange(len(labels))
    w = 0.4
    cols = [BAR_LO if e < 24 else BAR_HI for e in pop.BUCKET_EDGES[:-1]]
    axR.bar(x - w / 2, cell_share, w, color=cols, edgecolor=INK, lw=0.5)
    axR.bar(x + w / 2, nav_share, w, color=cols, edgecolor=INK, lw=0.5, hatch="///")
    # Colour already carries the 24% split, so the legend must not imply it also encodes the
    # count-vs-value contrast. Neutral swatches: these keys speak only to solid vs hatched.
    axR.legend(handles=[Patch(facecolor="#dddddd", edgecolor=INK, lw=0.5, label="company-dates"),
                        Patch(facecolor="#dddddd", edgecolor=INK, lw=0.5, hatch="///",
                              label="booked NAV")],
               frameon=False, fontsize=9.5, loc="upper right")
    for xi, (cell_pct, nav_pct) in enumerate(zip(cell_share, nav_share)):
        axR.text(xi - w / 2, cell_pct + 1.1, f"{cell_pct:.0f}", ha="center",
                 fontsize=9, color=INK)
        axR.text(xi + w / 2, nav_pct + 1.1, f"{nav_pct:.0f}", ha="center",
                 fontsize=9, color=INK)
    axR.set_xticks(x)
    axR.set_xticklabels(labels, fontsize=9)
    axR.set_ylabel("share of the population (%)")
    axR.set_ylim(0, max(cell_share.max(), nav_share.max()) * 1.22)
    axR.set_title("B. The same cells, weighted by the value booked", loc="left",
                  fontsize=12, color=INK)
    axR.grid(axis="y", alpha=0.25, lw=0.6)

    # The source line that used to be printed here is gone. It said what the LaTeX caption
    # says, one line above it on the page, so the two were a pair that would disagree the
    # first time either was edited — and a caption baked into a PNG cannot be edited at all
    # without rerunning the figure. The statistics it carried are returned below instead, and
    # the caption in `src/build_pdf.py` states them.
    hi = s > 24
    fig.tight_layout()
    return fig, {"at_zero": at_zero, "above24": above24,
                 "nav_hi": nav[hi].sum() / 1e9, "nav_all": nav.sum() / 1e9,
                 "cells": len(g), "companies": g.company.nunique()}


if __name__ == "__main__":
    fig, k = panels()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"{k['cells']:,} cells · {k['companies']:,} companies")
    print(f"  unanimous {k['at_zero']:.1f}% of cells · above 24% {k['above24']:.1f}%")
    print(f"  NAV in cells above 24%: ${k['nav_hi']:,.1f}B of ${k['nav_all']:,.1f}B "
          f"({k['nav_hi']/k['nav_all']*100:.1f}%)")
    print(f"  wrote {OUT.relative_to(ROOT)}")
