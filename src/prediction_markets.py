"""
Prediction markets — the fourth public signal (forward-looking).

Polymarket (Nasdaq Private Market-resolved) and Kalshi now price private-company
IPO timing, IPO order, and IPO closing-market-cap brackets. This script treats
those quoted probabilities as public, dated facts and computes OUR derived
metrics:

  (1) cross-venue / cross-contract DISAGREEMENT on the same underlying event
      (the valuation-disagreement thesis showing up in the forward signal); and
  (2) the forward market's implied debut valuation vs each name's last private
      round and Forge secondary estimate (does the forward signal sit above or
      below the headline?) — tying sec. 4.7 back to sec. 4.1/4.3/4.6.

Every figure carries platform + as-of date + source in data/prediction_markets.csv.
These are dated readings of young, thinly-traded markets (launched 2026-05-19),
not a continuous feed — see the limitations in paper/draft.md.

Run: python3 src/prediction_markets.py
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PM = pd.read_csv(ROOT / "data" / "prediction_markets.csv")
PANEL = pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")


def _p(company: str, contract_substr: str) -> float:
    """The implied probability (%) of the row whose contract contains a substring."""
    m = PM[(PM.company == company)
           & (PM.contract.str.contains(contract_substr, case=False, regex=False))]
    if m.empty:
        raise KeyError(f"{company} / '{contract_substr}' not found")
    return float(pd.to_numeric(m.implied_prob_pct, errors="coerce").iloc[0])


def exceedance_curve(company: str):
    """Sorted (cap $B, P(debut cap >= cap)%) points from the closing-mktcap rows."""
    m = PM[(PM.company == company) & (PM.metric_type == "closing_mktcap_ge")].copy()
    m["reference_busd"] = pd.to_numeric(m.reference_busd, errors="coerce")
    m["implied_prob_pct"] = pd.to_numeric(m.implied_prob_pct, errors="coerce")
    m = m.dropna(subset=["reference_busd", "implied_prob_pct"]).sort_values("reference_busd")
    return m.reference_busd.values, m.implied_prob_pct.values


def interp_prob(caps, probs, x: float) -> float:
    """P(debut cap >= x), linearly interpolated in the exceedance curve (probs
    are decreasing in cap). Clipped to the observed range."""
    return float(np.interp(x, caps, probs, left=probs[0], right=probs[-1]))


def implied_median_cap(caps, probs) -> float:
    """Cap at which the exceedance probability crosses 50% (the implied median
    debut market cap). Interpolated on the decreasing curve."""
    order = np.argsort(probs)            # np.interp needs increasing x
    return float(np.interp(50.0, probs[order], caps[order]))


def order_gap() -> float:
    """Cross-venue gap in P[Anthropic IPOs first]: Polymarket (late June) minus
    Kalshi's implied value (100 - its 'OpenAI first' price, launch week)."""
    return _p("Anthropic", "IPOs before OpenAI") - (100 - _p("OpenAI", "IPOs before Anthropic"))


def launchweek_openai_gap() -> float:
    """Kalshi 'announce in 2026' minus Polymarket 'complete by year-end' (launch week)."""
    return _p("OpenAI", "announces IPO in 2026") - _p("OpenAI", "by year-end 2026")


def main() -> None:
    print("=" * 78)
    print("PREDICTION MARKETS — fourth public signal (forward-looking)")
    print(f"{len(PM)} contract-readings | platforms: {', '.join(sorted(PM.platform.unique()))} | "
          f"as-of {PM.as_of.min()} .. {PM.as_of.max()}")
    print("=" * 78)
    for co, g in PM.groupby("company"):
        print(f"\n[{co}]")
        for r in g.itertuples():
            pv = pd.to_numeric(r.implied_prob_pct, errors="coerce")
            prob = "" if pd.isna(pv) else f"{float(pv):>5.1f}%"
            print(f"  {r.platform:<10} {prob:>6}  {r.contract}  ({r.as_of})")

    # ---- (1) cross-venue / cross-contract disagreement ----------------------- #
    print("\n" + "-" * 78)
    print("(1) THE FORWARD SIGNAL ALSO DISAGREES — across venues and contract designs")
    print("-" * 78)
    poly_anthropic_first = _p("Anthropic", "IPOs before OpenAI")
    kalshi_openai_first = _p("OpenAI", "IPOs before Anthropic")
    print(f"  IPO ORDER (P[Anthropic first]):  Polymarket {poly_anthropic_first:.0f}%  vs  "
          f"Kalshi {100 - kalshi_openai_first:.0f}%  ->  {order_gap():+.0f}-pt venue gap")
    print(f"     (Kalshi 2026-05-21 priced OpenAI-first {kalshi_openai_first:.0f}%, PRE Anthropic's "
          f"Jun-1 S-1; Polymarket 2026-06-27 POST-filing — venue + timing, stated honestly)")
    kw = launchweek_openai_gap()
    print(f"\n  OpenAI IPO IN 2026 (launch week):  Kalshi 'announce' {_p('OpenAI','announces IPO in 2026'):.0f}%  "
          f"vs  Polymarket 'complete' {_p('OpenAI','by year-end 2026'):.0f}%  ->  {kw:+.0f}-pt gap")
    print("     (part DEFINITIONAL — announce vs complete — part genuine; matches Prediction News '59 points')")
    print("\n  DIRECTION agrees, LEVEL disagrees: on 2026-06-26 delay reports OpenAI IPO-timing odds fell on")
    print("  BOTH venues at once — same 'co-move in direction, differ in level' pattern as the fund marks.")

    # ---- (2) forward implied valuation vs the headline ----------------------- #
    print("\n" + "-" * 78)
    print("(2) DOES THE FORWARD MARKET SIT ABOVE OR BELOW THE HEADLINE?")
    print("-" * 78)
    for co in ["Anthropic", "OpenAI"]:
        headline = float(PANEL.loc[co, "headline_val_busd"])
        forge = float(PANEL.loc[co, "forge_val_busd"])
        caps, probs = exceedance_curve(co)
        line = f"  {co:<9} last round ${headline:,.0f}B | Forge ${forge:,.0f}B |"
        if len(caps) >= 2:
            med = implied_median_cap(caps, probs)
            line += (f" P(debut >= last round) ~ {interp_prob(caps, probs, headline):.0f}% | "
                     f"implied MEDIAN debut cap ~ ${med:,.0f}B ({med/headline:.1f}x last round)")
        else:
            line += f" P(val >= $900B by year-end) {_p(co, '>= $900B'):.0f}% (vs ${headline:,.0f}B round)"
        print(line)
    print("\n  => In 2026 the forward market prices the top AI names AT or ABOVE their last private round,")
    print("     a right-skewed debut-cap distribution — same 'headline-as-floor' as sec. 4.1 / 4.3 / 4.6.")

    _figure()
    print("\nsaved figures/prediction_markets.png")


def _figure() -> None:
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5.2))

    caps, probs = exceedance_curve("Anthropic")
    headline_a = float(PANEL.loc["Anthropic", "headline_val_busd"])
    med_a = implied_median_cap(caps, probs)
    axA.plot(caps, probs, "o-", color="#2c3e50", lw=2, zorder=3)
    for x, y in zip(caps, probs):
        axA.annotate(f"${x/1000:.2f}T\n{y:.0f}%", (x, y), fontsize=8,
                     xytext=(6, 6), textcoords="offset points")
    axA.axvline(headline_a, color="#c0392b", ls="--", lw=1.4,
                label=f"last round / Forge ≈ ${headline_a:,.0f}B")
    axA.axhline(50, color="grey", ls=":", lw=1)
    axA.scatter([med_a], [50], color="#27ae60", zorder=5, s=60)
    axA.annotate(f"implied median debut cap\n≈ ${med_a/1000:.2f}T  ({med_a/headline_a:.1f}× last round)",
                 (med_a, 50), fontsize=8.5, color="#1e7e34",
                 xytext=(8, -28), textcoords="offset points")
    axA.set_xscale("log")
    axA.set_xlabel("IPO closing market cap, $B (log)")
    axA.set_ylabel("Polymarket implied P(debut cap ≥ x)  (%)")
    axA.set_title("A. Forward market prices Anthropic's debut\nABOVE its last private round (2026-06-27)")
    axA.set_ylim(0, 100)
    axA.legend(loc="upper right", fontsize=8)
    axA.grid(alpha=0.3, which="both")

    labels = ["P[Anthropic\nIPOs first]", "OpenAI IPO\nin 2026"]
    poly_vals = [_p("Anthropic", "IPOs before OpenAI"), _p("OpenAI", "by year-end 2026")]
    kalshi_vals = [100 - _p("OpenAI", "IPOs before Anthropic"), _p("OpenAI", "announces IPO in 2026")]
    x = np.arange(len(labels))
    w = 0.36
    axB.bar(x - w/2, poly_vals, w, label="Polymarket", color="#2980b9", edgecolor="black")
    axB.bar(x + w/2, kalshi_vals, w, label="Kalshi", color="#e67e22", edgecolor="black")
    for xi, v in zip(x - w/2, poly_vals):
        axB.annotate(f"{v:.0f}%", (xi, v), ha="center", va="bottom", fontsize=9)
    for xi, v in zip(x + w/2, kalshi_vals):
        axB.annotate(f"{v:.0f}%", (xi, v), ha="center", va="bottom", fontsize=9)
    axB.set_xticks(x)
    axB.set_xticklabels(labels)
    axB.set_ylabel("implied probability (%)")
    axB.set_ylim(0, 100)
    axB.set_title("B. The same event, priced differently across venues\n"
                  "(Kalshi 'announce' vs Polymarket 'complete' contracts)")
    axB.legend(fontsize=9)
    axB.grid(axis="y", alpha=0.3)
    axB.annotate("≈59-pt\ngap", (1, (kalshi_vals[1] + poly_vals[1]) / 2),
                 ha="center", fontsize=8, color="#7f4f24",
                 bbox=dict(boxstyle="round,pad=0.2", fc="#fdf2e9", ec="#7f4f24"))

    plt.tight_layout()
    fig.savefig(ROOT / "figures" / "prediction_markets.png", dpi=150)


if __name__ == "__main__":
    main()
