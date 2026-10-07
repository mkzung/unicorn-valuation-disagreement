"""
Appendix C.4 coverage map — which of the four public signals sees which company.
Visualises the complementarity thesis: the signals overlap on very few names, so
the four-way triangulation is non-redundant. Reads only the existing per-signal
data files; writes data/coverage_matrix.csv + figures/coverage_matrix.png.

`coverage()` is import-safe (pure compute, no writes/plots) so src/paper_numbers.py
can pin the counts; the figure + CSV are produced by main().

Run: python3 src/coverage_matrix.py
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _canon(n):
    return {"SpaceX-xAI": "SpaceX"}.get(n, n)


def signal_universes():
    """The four public-signal company sets, each from its own production data file."""
    sec = set(pd.read_csv(ROOT / "data/valuation_panel.csv").company.map(_canon))        # §7.2
    ipo = set(pd.read_csv(ROOT / "data/ipo_validation.csv").company.map(_canon))         # §7.1
    disp = pd.read_csv(ROOT / "data/fund_marks_dispersion.csv")
    xf = set(disp[disp.n_funds >= 5].company.map(_canon))                                 # §4.3 (>=5 funds)
    pm = pd.read_csv(ROOT / "data/prediction_markets.csv")
    pmset = set(pm[pm.company != "cross"].company.map(_canon))                            # Appendix C.3
    return [("Secondary\n(Forge)", sec), ("IPO exit", ipo),
            ("Cross-fund\n(N-PORT)", xf), ("Prediction\nmarket", pmset)]


def coverage():
    """Return (signals, sorted rows, counts) — pure, no side effects."""
    signals = signal_universes()
    names = sorted(set().union(*[s for _, s in signals]))
    rows = [(nm, [nm in s for _, s in signals], sum(nm in s for _, s in signals)) for nm in names]
    rows.sort(key=lambda r: (-r[2], next((i for i, c in enumerate(r[1]) if c), 99), r[0]))
    counts = {"union": len(names),
              "single": sum(1 for r in rows if r[2] == 1),
              "multi": sum(1 for r in rows if r[2] > 1),
              "triple": sum(1 for r in rows if r[2] >= 3)}
    return signals, rows, counts


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    signals, rows, c = coverage()
    pd.DataFrame([{"company": nm, "secondary": int(cov[0]), "ipo_exit": int(cov[1]),
                   "cross_fund": int(cov[2]), "prediction_mkt": int(cov[3]), "n_signals": k}
                  for nm, cov, k in rows]).to_csv(ROOT / "data/coverage_matrix.csv", index=False)

    colors = ["#2c7fb8", "#d95f0e", "#31a354", "#756bb1"]
    fig, ax = plt.subplots(figsize=(7.4, max(6.0, 0.27 * len(rows))))
    for y, (nm, cov, k) in enumerate(rows):
        if k > 1:
            ax.add_patch(Rectangle((-0.03, y - 0.05), 4.06, 0.96, fc="#fff3d6",
                                   ec="0.55", lw=0.7, ls=":", zorder=0))
        for x, on in enumerate(cov):
            if on:
                ax.add_patch(Rectangle((x + 0.04, y), 0.92, 0.86, color=colors[x], alpha=0.92, zorder=2))
    ax.set_xlim(-0.05, 4.05)
    ax.set_ylim(len(rows), -0.6)
    ax.set_xticks([i + 0.5 for i in range(4)])
    ax.set_xticklabels([s[0] for s in signals], fontsize=9.5)
    ax.set_yticks([y + 0.43 for y in range(len(rows))])
    ax.set_yticklabels([r[0] for r in rows], fontsize=7.4)
    ax.xaxis.tick_top()
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Four-signal coverage map: which public signal sees which company\n"
                 "%d distinct names · %d seen by one signal only · %d by more than one "
                 "· only Anthropic & OpenAI by three" % (c["union"], c["single"], c["multi"]),
                 fontsize=9.5, pad=24)
    plt.tight_layout()
    fig.savefig(ROOT / "figures/coverage_matrix.png", dpi=200, bbox_inches="tight")
    print("saved figures/coverage_matrix.png + data/coverage_matrix.csv")
    print("union=%(union)d single=%(single)d multi=%(multi)d triple=%(triple)d" % c)
    print("multi-signal:", [(r[0], r[2]) for r in rows if r[2] > 1])


if __name__ == "__main__":
    main()
