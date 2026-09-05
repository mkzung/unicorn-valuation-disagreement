#!/usr/bin/env python3
"""The three figures the body's own results need, drawn from the production code.

A referee counted what the paper shows: seventy-two pages, three figures, and not one of
them a picture of a result the paper leads with. The event study is the paper's only
dynamic and lived entirely in a table; the one lot that closes every deflationary reading
was a paragraph of prices; the decomposition that bounds the headline was two numbers in a
sentence. All three are shapes, and a shape belongs in a picture.

  round_event_study    §8: between-house spread by month around a round, and the step at
                       the round against the three shifted anchors that do not have one.
  databricks_series_j  §2.1: two houses carrying one lot from a disclosed common entry
                       price, apart at the midpoint and identical at the year end.
  series_decomposition §3.3 and Appendix C.5: what holding the security fixed takes out of
                       the median, what it leaves in the tail, and the half of the
                       population the test cannot reach at all.

Nothing here is typed in. Every value is read from the committed panels or recomputed by
the module that owns it, so a figure cannot drift away from the prose the way a caption can.
The entry price in the second one is divided out of a filed cost and a filed share count
rather than copied from the text, and the run stops if the lot has more than one.

Three rules these follow and the three older figures did not, all of them a referee's:
  - no caption baked into the image. The caption is the caption; a picture carrying its own
    is two captions that disagree the moment one is edited.
  - no section number inside a PNG. Section numbers move; pixels do not.
  - no conclusion inside the axes. The reader is shown the shape and told what it means
    underneath, in text a build can check.

Run:  python3 src/paper_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop

FIGDIR = ROOT / "figures"

# One ink, one accent, one muted pair, used the same way in all three. The pair is chosen
# from a colourblind-safe set rather than from the default cycle: the older dispersion
# figure put Fidelity and Robinhood on two pinks a deuteranope cannot separate.
INK = "#1a1a1a"
ACCENT = "#c1272d"
BLUE = "#08519c"
PALE = "#9ecae1"
GREY = "#8c8c8c"
FAINT = "#d9d9d9"

# Type sizes shared across the three, because a journal reads them on facing pages.
plt.rcParams.update({
    "font.size": 9.5, "axes.titlesize": 10.5, "axes.labelsize": 9.5,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})

# The two bands the step compares, as §8.2 defines them. Written once so the shading and
# the statistic cannot end up describing different months.
PRE, POST = (-3, -1), (0, 2)


def _stat(s: pd.DataFrame, name: str) -> float:
    row = s[s.statistic == name]
    if row.empty:
        raise SystemExit(f"ERROR: {name!r} is not in the committed event-study statistics")
    return float(row.value.iloc[0])


def event_study() -> Path:
    """The profile around a round, and the step the shifted anchors do not reproduce."""
    prof = pd.read_csv(ROOT / "data" / "round_event_study.csv")
    s = pd.read_csv(ROOT / "data" / "round_event_study_stats.csv")

    fig = plt.figure(figsize=(13.2, 5.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.7, 1], height_ratios=[3.4, 1],
                          hspace=0.14, wspace=0.3)
    ax = fig.add_subplot(gs[0, 0])
    axn = fig.add_subplot(gs[1, 0], sharex=ax)
    axr = fig.add_subplot(gs[:, 1])

    m = prof.m.to_numpy()
    w = prof.within_company_median.to_numpy()

    # Colour carries the comparison rather than the sign of the month: the two shaded bands
    # are what the step is a difference between, and everything outside them is context.
    def band(x: int) -> str:
        if PRE[0] <= x <= PRE[1]:
            return PALE
        if POST[0] <= x <= POST[1]:
            return ACCENT
        return FAINT

    ax.bar(m, w, color=[band(x) for x in m], width=0.8, zorder=3)
    ax.axhline(0, color=INK, lw=0.9, zorder=4)
    ax.axvspan(PRE[0] - 0.5, PRE[1] + 0.5, color=PALE, alpha=0.16, zorder=1)
    ax.axvspan(POST[0] - 0.5, POST[1] + 0.5, color=ACCENT, alpha=0.10, zorder=1)
    top = max(w) * 1.18
    ax.set_ylim(min(w) * 1.25, top)
    ax.text(sum(PRE) / 2, top * 0.9, "before", ha="center", fontsize=9, color=BLUE)
    ax.text(sum(POST) / 2, top * 0.9, "after", ha="center", fontsize=9, color=ACCENT)
    ax.set_ylabel("median deviation from the company's\nown median spread (points)")
    ax.set_title("A. Each company measured against its own norm", loc="left")
    ax.tick_params(labelbottom=False)

    axn.bar(m, prof.cells, color=GREY, width=0.8, zorder=3)
    axn.set_xticks(range(-6, 13, 2))
    axn.set_ylabel("cells", color=GREY)
    axn.set_xlabel("months to the nearest non-first dated round")
    axn.tick_params(axis="y", colors=GREY, labelsize=8)
    axn.set_ylim(0, prof.cells.max() * 1.3)

    # ---- right: the same estimator, anchor moved ---------------------------------------
    # All four rows are `placebo_<offset>`, the round being the zero offset, so the picture
    # compares one design against itself rather than a step statistic against a placebo one.
    rows = [("the round", "+0"), ("6 months\nbefore", "-6"),
            ("6 months\nafter", "+6"), ("12 months\nafter", "+12")]
    labels, meds, notes = [], [], []
    for label, off in rows:
        med = _stat(s, f"placebo_{off}_step_pts")
        neg = _stat(s, f"placebo_{off}_negative")
        unt = _stat(s, f"placebo_{off}_untied")
        p = _stat(s, f"placebo_{off}_p_sign")
        labels.append(label)
        meds.append(med)
        notes.append(f"{neg:.0f} of {unt:.0f} negative,  "
                     + (f"p={p:.4f}" if p < 0.01 else f"p={p:.2f}"))
    y = np.arange(len(labels))[::-1]
    axr.barh(y, meds, color=[ACCENT] + [PALE] * 3, height=0.34, zorder=3)
    axr.axvline(0, color=INK, lw=0.9, zorder=4)
    # A zero bar draws nothing and three invisible bars read as three missing rows, so the
    # anchors that return exactly zero get a tick at zero instead.
    for yy, med in zip(y, meds):
        if abs(med) < 1e-9:
            axr.plot([0], [yy], marker="|", ms=14, color=BLUE, zorder=5)
    span = max(abs(min(meds)), 0.5)
    for yy, note in zip(y, notes):
        axr.text(-span * 1.02, yy - 0.24, note, va="top", ha="left", fontsize=9.6,
                 color=INK)
    axr.set_yticks(y)
    axr.set_yticklabels(labels)
    axr.set_xlim(-span * 1.08, span * 0.36)
    axr.set_ylim(-0.62, len(labels) - 0.55)
    axr.set_xlabel("median step across the anchor (points)")
    axr.set_title("B. The same design with the anchor moved", loc="left")

    out = FIGDIR / "round_event_study.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def databricks_series_j() -> Path:
    """One lot, two books, three shared dates: apart in the middle, identical at the end."""
    a = pd.read_csv(ROOT / "data" / "ncsr_acquisitions.csv")
    j = a[a.company.str.contains("Databricks", case=False, na=False)
          & a.security.str.contains("Series J", na=False)].copy()
    j["house"] = np.where(j.filer.str.contains("Alger", case=False), "Alger",
                          np.where(j.filer.str.contains("Brighthouse", case=False),
                                   "Brighthouse", None))
    j = j[j.house.notna()]
    g = j.groupby(["house", "period"]).markup_pct.median().unstack(0).dropna()
    if len(g) < 3:
        raise SystemExit(f"ERROR: only {len(g)} shared period(s) for the Series J lot")

    sh = j[j.shares.notna() & (j.shares > 0)]
    entry = np.unique((sh.cost / sh.shares).round(2))
    if len(entry) != 1:
        raise SystemExit(f"ERROR: the lot no longer has one disclosed entry price: {entry}")
    entry = float(entry[0])

    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    x = np.arange(len(g))
    px = {h: entry * (1 + g[h].to_numpy() / 100) for h in ("Alger", "Brighthouse")}
    for house, colour, marker in (("Alger", ACCENT, "o"), ("Brighthouse", BLUE, "s")):
        ax.plot(x, px[house], color=colour, marker=marker, ms=7, lw=2, label=house, zorder=3)

    # One label where the two agree and two where they do not: a shared point labelled twice
    # is two numbers printed on top of each other, which is what the first version drew.
    for xx in x:
        hi, lo = px["Alger"][xx], px["Brighthouse"][xx]
        if abs(hi - lo) < 0.005:
            ax.annotate(f"both ${hi:,.2f}", (xx, hi), textcoords="offset points",
                        xytext=(0, 12), ha="center", fontsize=9.5, color=INK)
        else:
            ax.annotate(f"${hi:,.2f}", (xx, hi), textcoords="offset points",
                        xytext=(-12, 4), ha="right", fontsize=9.5, color=ACCENT)
            ax.annotate(f"${lo:,.2f}", (xx, lo), textcoords="offset points",
                        xytext=(-14, -13), ha="right", va="top", fontsize=9.5, color=BLUE)
            ax.annotate("", xy=(xx + 0.05, hi), xytext=(xx + 0.05, lo),
                        arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.2))
            ax.text(xx + 0.11, (hi + lo) / 2, f"${hi - lo:,.2f} a share", va="center",
                    fontsize=9.5, color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels([pd.Timestamp(p).strftime("%d %b %Y") for p in g.index])
    ax.set_ylabel("price per share implied by the filed markup ($)")
    ax.set_xlim(-0.45, len(g) - 0.4)
    ax.set_ylim(entry * 0.84, entry * 2.22)
    ax.axhline(entry, color=GREY, ls=":", lw=1.1, zorder=1)
    ax.text(len(g) - 0.45, entry * 1.02, "disclosed entry price", fontsize=9, color=GREY,
            ha="right")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.03, 0.99))

    fig.tight_layout()
    out = FIGDIR / "databricks_series_j.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def series_decomposition() -> Path:
    """What holding the security fixed removes, what it leaves, and what it cannot reach."""
    marks, cells = pop.panel()
    d = pop.series_composition(marks, cells)
    same = pop.same_series_spread(marks, cells)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.4),
                                   gridspec_kw={"width_ratios": [1, 1.3]})

    # Two decimals on the medians and one on the shares, because that is the precision the
    # paper prints for each. A figure showing 21.97% beside a sentence saying 22.0% is the
    # same number and reads as two.
    pairs = [("median spread", same["pooled_median"], same["median"], 2),
             ("share above 24%", same["pooled_above_24"], same["above_24"], 1)]
    x = np.arange(len(pairs))
    wid = 0.34
    before = [p[1] for p in pairs]
    after = [p[2] for p in pairs]
    axL.bar(x - wid / 2, before, wid, color=PALE, label="series ignored", zorder=3)
    axL.bar(x + wid / 2, after, wid, color=BLUE,
            label="one named series, two or more houses", zorder=3)
    for (_, b, a_, dp), xx in zip(pairs, x):
        axL.text(xx - wid / 2, b + 0.8, f"{b:.{dp}f}%", ha="center", fontsize=9, color=INK)
        axL.text(xx + wid / 2, a_ + 0.8, f"{a_:.{dp}f}%", ha="center", fontsize=9, color=INK)
    axL.set_xticks(x)
    axL.set_xticklabels([p[0] for p in pairs])
    axL.set_ylabel("per cent")
    axL.set_ylim(0, max(before) * 1.34)
    axL.legend(frameon=False, loc="upper left")
    axL.set_title(f"A. The same {same['cells']:,} cells, scored two ways", loc="left")

    # ---- right: where the test can run at all ------------------------------------------
    order = ["no filing names a letter", "one letter, some filings",
             "every filing names the same letter", "two or more letters named"]
    key = {"no filing names a letter": "unnamed", "one letter, some filings": "partial",
           "every filing names the same letter": "fully_named",
           "two or more letters named": "mixed"}
    meds = [d[key[o]]["median"] for o in order]
    ns = [d[key[o]]["cells"] for o in order]
    unreachable = [True, False, False, False]
    y = np.arange(len(order))[::-1]
    axR.barh(y, meds, color=[GREY if u else BLUE for u in unreachable], height=0.55,
             zorder=3)
    panel_median = same["panel_median"]
    axR.axvline(panel_median, color=ACCENT, ls="--", lw=1.2, zorder=4)
    axR.text(panel_median + 0.2, -0.72, f"whole panel, {panel_median:.2f}%", color=ACCENT,
             fontsize=9, va="bottom")
    for yy, med, n in zip(y, meds, ns):
        axR.text(med + 0.28, yy, f"{med:.2f}%   ({n:,} cells)", va="center", fontsize=9,
                 color=INK)
    axR.set_yticks(y)
    axR.set_yticklabels(order)
    axR.set_xlim(0, max(meds) * 1.5)
    axR.set_ylim(-0.9, len(order) - 0.45)
    axR.set_xlabel("median between-house spread (%)")
    axR.set_title("B. Where the test can run; grey is where it cannot", loc="left")

    fig.tight_layout()
    out = FIGDIR / "series_decomposition.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    for fn in (event_study, databricks_series_j, series_decomposition):
        out = fn()
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
