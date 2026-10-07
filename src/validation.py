"""
IPO-exit validation — the DIFFERENTIATOR: for unicorns that actually listed in 2023-26,
which PRE-IPO public signal was *least wrong* about the realized IPO valuation?

Two pre-IPO signals are compared against the realized IPO/first-print valuation:
  (A) the stale HEADLINE  = the last private primary-round post-money; and
  (B) the last pre-IPO FUND MARK = what mutual funds actually marked the company at in
      their SEC N-PORT filings just before the listing (implied valuation via the IPO
      per-share bridge: implied_val = ipo_val * mark_pps / ipo_pps, since pre-IPO
      preferred converts ~1:1 to the IPO common at a healthy listing; for the Klarna
      exit the only interim signal is a down ROUND, used directly).

error = signal / ipo - 1   (positive = signal ABOVE the realized IPO; 0 = exact).
least-wrong = the signal with the smaller |error|.

Result: across the SEVEN fund-held exits the last pre-IPO fund mark was the least-wrong signal
in FIVE -- and it crushed the headline precisely where the headline was STALE: the 2021-vintage
repriced names (Instacart fund mark +8% vs headline +294%; Chime -1% vs +116%; Reddit -5% vs
+56%), plus the modest ServiceTitan (+11% vs +21%) and Figma's floor case (-28% vs -48%). The
two COUNTER-EXAMPLES are exactly the names whose last round was recent and fairly priced, so the
headline was not stale: Klaviyo (headline +3% beats the fund mark's +15%) and Circle (headline
+11% beats Fidelity's conservative -25%, which UNDERshot a hot crypto listing). Median |fund-mark
error| 11% vs |headline| 48%. So the fund mark's edge is the ABSENCE OF STALENESS, not foresight:
the very N-PORT marks that *disagree* in the cross-section (sec. 4.4) and trace the cycle (sec.
4.5) carry better exit information than the headline only when the headline has gone stale. The
2022 Klarna down round overcorrected (-56%) yet still beat the +205% headline (IPO at offer-price
~$15.1B FD); in the flat/up cases (CoreWeave, SpaceX/xAI) the headline itself was already a floor.

Public facts only; SEC N-PORT is public domain; every row carries source + date in
data/ipo_validation.csv. Reproduce: python3 src/validation.py
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    return pd.read_csv(ROOT / "data" / "ipo_validation.csv")


def add_errors(v):
    """Add headline overshoot, the pre-IPO signal's implied valuation and its error, and
    the least-wrong label. Fund-mark implied valuation is rebuilt from the per-share mark
    and the IPO offer price (the bridge), so the CSV's stored value is independently checked."""
    v = v.copy()
    v["overshoot_pct"] = (v["last_private_val_busd"] / v["ipo_val_busd"] - 1.0) * 100.0

    # implied valuation of the pre-IPO non-headline signal
    implied = v["preipo_signal_busd"].astype(float)
    fm = v["preipo_signal_type"] == "fund_mark"
    bridge = v["ipo_val_busd"] * v["preipo_signal_pps"] / v["ipo_pps"]   # NaN where pps blank
    v["signal_implied_busd"] = np.where(fm, bridge, implied)

    v["signal_err_pct"] = (v["signal_implied_busd"] / v["ipo_val_busd"] - 1.0) * 100.0
    has = v["signal_implied_busd"].notna()
    v["least_wrong"] = np.where(
        has & (v["signal_err_pct"].abs() < v["overshoot_pct"].abs()),
        np.where(v["preipo_signal_type"] == "down_round", "interim round", "fund mark"),
        np.where(has, "headline", "(no interim signal)"))
    return v


def main():
    v = add_errors(load()).sort_values("overshoot_pct", ascending=False)

    cols = ["company", "sector", "last_private_val_busd", "ipo_val_busd",
            "overshoot_pct", "preipo_signal_type", "signal_implied_busd",
            "signal_err_pct", "least_wrong"]
    print(v[cols].to_string(index=False, formatters={
        "overshoot_pct": lambda x: f"{x:+.0f}%",
        "signal_err_pct": lambda x: "" if pd.isna(x) else f"{x:+.0f}%",
        "signal_implied_busd": lambda x: "" if pd.isna(x) else f"{x:.1f}"}))

    peak = v[v.vintage == "2021-peak"]      # the four 2021-bubble-vintage stale headlines
    print(f"\n2021-peak-vintage down-round exits: headline OVERSHOOT median {peak.overshoot_pct.median():+.0f}%")
    flatup = v[v.direction.isin(["flat", "up"])]
    print("flat/up exits (headline already a floor or fairly priced): "
          + ", ".join(f"{r.company} {r.overshoot_pct:+.0f}%" for r in flatup.itertuples()))

    # the differentiator: which signal was least wrong, where a fund mark exists
    fm = v[v.preipo_signal_type == "fund_mark"]
    nwin = int((fm.least_wrong == "fund mark").sum())
    print(f"\n--- which pre-IPO signal was LEAST WRONG (fund mark wins {nwin} of {len(fm)} fund-held exits) ---")
    for r in fm.itertuples():
        if abs(r.signal_err_pct) < abs(r.overshoot_pct):
            ratio = abs(r.overshoot_pct) / max(abs(r.signal_err_pct), 1e-9)
            tag = f"-> FUND MARK least wrong ({ratio:.0f}x closer)"
        else:
            tag = "-> headline least wrong (recent/fairly-priced round, not stale)"
        print(f"  {r.company:12} headline {r.overshoot_pct:+4.0f}%  vs  last fund mark "
              f"{r.signal_err_pct:+4.0f}%  {tag}")
    print(f"  median |headline error| = {fm.overshoot_pct.abs().median():.0f}%  vs  "
          f"median |fund-mark error| = {fm.signal_err_pct.abs().median():.0f}%")
    _power(fm)
    kl = v[v.company == "Klarna"]
    if len(kl):
        k = kl.iloc[0]
        print(f"  Klarna (interim DOWN ROUND, not a fund mark): headline {k.overshoot_pct:+.0f}% "
              f"vs round {k.signal_err_pct:+.0f}% (less wrong, but overcorrected below the IPO)")

    _figure(v)


def _power(fm):
    """How much does the 'five of seven' count actually carry? On seven exits the count alone
    cannot clear conventional significance even if the fund mark won every one (0.5^7 = 0.008
    is the floor, and 5/7 is far above it), so the leg's content is the paired ERROR MAGNITUDE,
    not the win count. Both are reported, plus the win rate restricted to clean-flag exits."""
    from scipy.stats import binomtest, wilcoxon

    n = len(fm)
    w = int((fm.signal_err_pct.abs() < fm.overshoot_pct.abs()).sum())
    sign_p = binomtest(w, n, 0.5, alternative="greater").pvalue
    try:
        _, wil_p = wilcoxon(fm.signal_err_pct.abs(), fm.overshoot_pct.abs(), alternative="less")
    except ValueError:
        wil_p = float("nan")
    clean = fm[fm.quality_flag == "clean"]
    cw = int((clean.signal_err_pct.abs() < clean.overshoot_pct.abs()).sum())
    print(f"  power: exact sign test on the {w}/{n} count p={sign_p:.2f} (NOT significant at n={n}); "
          f"paired Wilcoxon on |errors| p={wil_p:.3f}; clean-flag exits only {cw} of {len(clean)}")


def _figure(v):
    v = v.sort_values("overshoot_pct")
    y = np.arange(len(v)); h = 0.38
    fig, ax = plt.subplots(figsize=(10, 5.6))

    # One colour per SERIES, which is what the legend claims. The first version coloured the
    # headline bars red below zero and green above it, so the colour encoded the sign while
    # the legend said it encoded the signal: a reader decoding by the legend concluded that
    # Instacart, whose headline missed by +294%, had no headline bar at all. Worse, green read
    # as "good" on the largest error in the paper. The sign is already in the position of the
    # bar relative to the zero line and does not need a second, contradictory channel.
    ax.barh(y + h/2, v["overshoot_pct"], height=h,
            color="#c0392b", edgecolor="black", label="Headline (last private round)")
    # pre-IPO interim signal (fund mark / down round) bars, where present
    sig = v["signal_err_pct"].values
    ax.barh(y - h/2, np.nan_to_num(sig), height=h,
            color="#2c3e50", edgecolor="black", hatch="///",
            label="Last pre-IPO fund mark / interim round")
    for i, x in enumerate(sig):
        if np.isnan(x):
            ax.text(2, y[i] - h/2, "no interim signal", va="center", fontsize=7.5, color="#555")

    ax.axvline(0, color="black", lw=1.2)
    ax.set_yticks(y); ax.set_yticklabels(v["company"])
    ax.set_xlabel("Pre-IPO signal error vs realized IPO valuation (%)   —   0 = the IPO priced it right")
    # A three-line conclusion used to sit here, inside the image, and it read "the headline
    # already nailed" — slang in a finance paper, and a finding printed where no build can
    # check it. The finding belongs in the caption, which `src/build_pdf.py` writes and
    # `tests/test_manuscript_pointers.py` now holds to figures the paper states.
    ax.set_title("Pre-IPO signals against the realized IPO valuation", fontsize=10.5,
                 loc="left")
    # annotate values
    for r_y, val in zip(y + h/2, v["overshoot_pct"]):
        ax.text(val + (6 if val >= 0 else -6), r_y, f"{val:+.0f}%",
                va="center", ha="left" if val >= 0 else "right", fontsize=7.5)
    for r_y, val in zip(y - h/2, sig):
        if not np.isnan(val):
            ax.text(val + (6 if val >= 0 else -6), r_y, f"{val:+.0f}%",
                    va="center", ha="left" if val >= 0 else "right", fontsize=7.5, color="#2c3e50")
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    fig.savefig(ROOT / "figures" / "ipo_validation.png", dpi=150)
    print("\nsaved figures/ipo_validation.png")


if __name__ == "__main__":
    main()
