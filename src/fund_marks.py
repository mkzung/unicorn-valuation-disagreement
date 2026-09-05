"""
N-PORT cross-fund dispersion: do different mutual funds mark the SAME private
unicorn security at the SAME fair value? Independent, public-domain (SEC) signal,
the spine of the paper. Input: data/fund_marks.csv (from src/nport_fetch.py).

OUR derived metric: for each company, the spread in the implied price-per-share
(valUSD / balance) across funds that disclose a Level-3 mark, holding the report
date fixed so the spread reflects DISAGREEMENT, not differing fiscal quarter-ends.

Guards (each a documented, reproducible filter):
  - keep only Level-3, restricted, equity (EC/EP), share-denominated (units=NS) marks;
  - drop SPV / fund-of-fund wrappers ("...LLC (economic exposure to ...)"), whose
    per-unit price is not the issuer's per-share price;
  - drop unit-convention outliers (a fund stating shares on a 10:1 basis -> pps 10x
    the company median); these are measurement artifacts, not valuation views;
  - auto-flag companies whose funds hold securities at internally very different
    prices (multiple share classes, e.g. SpaceX/Discord) -> per-share not comparable;
  - report dispersion CONDITIONAL on the modal report date.

Run: python3 src/fund_marks.py
"""
import re
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

# Fund house behind each FUND name (marks cluster by house -> the "valuation policy" effect).
# This map keys on the fund; `src/fund_complex.py` keys on the REGISTRANT for the population
# panel. Two maps are needed because the two harvests carry different identifying fields, but
# they must name the same house the same way, so the labels here follow that module.
#
# Four funds used to fall through to "Other" because the pattern missed how the filing spells
# them: "T.Rowe Price Large Cap Growth Portfolio" has no space after the point, iShares is
# BlackRock's ETF brand, EUPAC is how EuroPacific is abbreviated, and Fidelity's sector funds
# file as "Select ... Portfolio". None of the published figures moves when they are corrected
# -- "Other" is already excluded from every family statistic -- but a catch-all that pools
# unrelated houses is a trap the next panel expansion would spring.
FAMILIES = [
    ("Fidelity", r"Fidelity|Contrafund|\bVIP\b|Select \w+ Portfolio"),
    ("Alger", r"Alger"),
    ("T. Rowe Price", r"T\.\s?Rowe"),
    ("BlackRock", r"BlackRock|iShares"),
    ("Capital Group",
     r"AMCAP|New Economy|Growth Fund of America|Washington Mutual|"
     r"Investment Company of America|EuroPacific|EUPAC|SMALLCAP"),
    ("Franklin Templeton", r"Franklin|ClearBridge|Legg Mason|Western Asset"),
    ("Neuberger Berman", r"Neuberger"),
    ("ARK", r"\bARK\b"),
    ("Nuveen", r"Nuveen|Winslow"),
    ("Baron", r"Baron"),
    ("Morgan Stanley", r"Morgan Stanley|Insight"),
    ("Coatue", r"Coatue"),
    ("Fundrise", r"Fundrise"),
    ("Robinhood", r"Robinhood"),
    ("Destiny", r"Destiny"),
    ("Wellington", r"Wellington"),
    # Four houses this list did not name and `fund_complex` — the map the population panel
    # runs on — does. They surfaced on the Epic Games row of the dispersion figure, where
    # four of the seven holders were pooled into one grey "Other" and the only name in the
    # panel with no attributable point at all. Pooling unrelated houses in a catch-all is
    # what the comment above this list warns about, and it had already happened.
    #
    # Lincoln sits before AllianceBernstein deliberately: "LVIP AllianceBernstein Large Cap
    # Growth Fund" is a Lincoln Variable Insurance Products trust sub-advised by AB, and the
    # Level-3 fair value is the trust's valuation designee's, not the sub-adviser's. The two
    # do not agree on Epic Games ($504.62 against $594.26), which is the same evidence §4.2
    # uses in the other direction: one house, one number.
    ("Lincoln", r"^LVIP\b|Lincoln Variable"),
    ("AllianceBernstein", r"^AB\b|AllianceBernstein"),
    ("First Trust", r"^First Trust\b|^FT "),
    ("Voya", r"^Voya\b"),
    ("Grandeur Peak", r"Grandeur Peak"),
    ("MFS", r"\bMFS\b"),
    ("Private Shares Fund", r"Private Shares Fund"),
]
WRAPPER = re.compile(r"exposure|invested in|DXYZ|MWAM|Snowpoint|ARTIST EDGE|PARTNERS|, LLC \(|LP \(", re.I)

# Companies whose funds hold NON-COMPARABLE securities across different legal
# entities or share classes, so a cross-fund per-share comparison is apples-to-
# oranges. SpaceX is caught automatically by the within-fund class-mix detector
# (its funds hold several SpaceX classes inside one filing). ByteDance must be
# added by hand: each fund holds a SINGLE security, so the within-fund detector
# cannot see that the holders split across the Douyin Co Ltd vs ByteDance Ltd
# legal entities AND across common (Series E-1, ~$253) vs convertible-preferred
# (Series E, ~$386) classes — verified by inspecting the raw N-PORT marks
# (2026-06-27). Reported as a finding (opacity), not silently dropped.
CROSS_CLASS_EXCLUDE = {"ByteDance"}


def family(name):
    for fam, pat in FAMILIES:
        if re.search(pat, str(name), re.I):
            return fam
    return "Other"


def load():
    df = pd.read_csv(ROOT / "data" / "fund_marks.csv")
    df["bal"] = pd.to_numeric(df.balance, errors="coerce")
    df["val"] = pd.to_numeric(df.val_usd, errors="coerce")
    df["pps"] = df.val / df.bal
    m = df[(df.fair_val_level == 3) & (df.units == "NS") & (df.bal > 0)
           & (df.asset_cat.isin(["EC", "EP"]))].copy()
    m = m[~m.issuer_name.astype(str).str.contains(WRAPPER)]
    m["family"] = m.fund.map(family)
    return m


def fund_price_table(m):
    """One blended price per (company, fund, report_date) = total value / total shares,
    plus the within-fund price ratio (class-mix detector)."""
    g = m.groupby(["company", "fund", "family", "report_date"])
    tab = g.apply(lambda x: pd.Series({
        "pps": x.val.sum() / x.bal.sum(),
        "within_fund_ratio": x.pps.max() / x.pps.min() if x.pps.min() > 0 else np.nan,
        "n_sec": len(x),
    }), include_groups=False).reset_index()
    return tab


def main():
    m = load()
    tab = fund_price_table(m)

    # class-mix flag: companies where >20% of funds hold securities at >1.5x internal spread
    classmix = (tab.assign(mix=tab.within_fund_ratio > 1.5)
                .groupby("company").mix.mean())
    mixed = set(classmix[classmix > 0.20].index)
    auto_mixed = sorted(mixed)
    mixed |= CROSS_CLASS_EXCLUDE          # manual: cross-fund entity/class splits (ByteDance)

    # unit-convention outliers: pps far from the company median
    med = tab.groupby("company").pps.transform("median")
    tab["unit_ok"] = (tab.pps <= 3 * med) & (tab.pps >= med / 3)
    dropped = tab[~tab.unit_ok]

    print("=" * 78)
    print("N-PORT CROSS-FUND DISPERSION  —  Level-3 fair-value marks, 2025Q4–2026Q1")
    print("=" * 78)
    print(f"clean marks: {len(m)} holdings | {m.fund.nunique()} funds | {m.company.nunique()} companies")
    print(f"excluded from per-share comparison (non-comparable classes/entities): {sorted(mixed)}"
          f"  [auto within-fund class-mix: {auto_mixed}; manual entity/class split: {sorted(CROSS_CLASS_EXCLUDE)}]")
    if len(dropped):
        print(f"unit-convention outliers dropped: {len(dropped)} "
              f"({', '.join(dropped.company + '/' + dropped.family)})")

    clean = tab[tab.unit_ok & ~tab.company.isin(mixed)].copy()

    # dispersion conditional on the modal report date (kills the timing confound)
    print("\n--- cross-fund dispersion, conditional on modal report date ---")
    rows = []
    for co, s in clean.groupby("company"):
        md = s.report_date.mode().iloc[0]
        sd = s[s.report_date == md]
        if len(sd) < 2:
            continue
        v = sd.pps.values
        rows.append({
            "company": co, "date": md, "n_funds": len(sd),
            "min": v.min(), "median": np.median(v), "max": v.max(),
            "maxmin": v.max() / v.min(),
            "spread_pct": (v.max() / v.min() - 1) * 100,
            "cv_pct": v.std(ddof=1) / v.mean() * 100,
            "n_families": sd.family.nunique(),
        })
    R = pd.DataFrame(rows).sort_values("spread_pct", ascending=False)
    with pd.option_context("display.width", 170):
        print(R.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    big = R[R.n_funds >= 5]
    print(f"\ncompanies with >=5 same-date funds: {len(big)}")
    print(f"  median cross-fund spread (max/min): {big.maxmin.median():.2f}x "
          f"= {(big.maxmin.median() - 1) * 100:.0f}%")
    print(f"  widest: {R.iloc[0]['company']} {R.iloc[0]['spread_pct']:.0f}% "
          f"({R.iloc[0]['n_funds']:.0f} funds, {R.iloc[0]['n_families']:.0f} families, {R.iloc[0]['date']})")
    herd = big[big.spread_pct < 5]
    print(f"  'herd to last round' (<5% spread): {', '.join(sorted(herd.company))}")

    R.to_csv(ROOT / "data" / "fund_marks_dispersion.csv", index=False)
    print("\nwrote data/fund_marks_dispersion.csv")

    _figure(clean, R, big)


def _figure(clean, R, big):
    """Strip plot: each fund's mark as % deviation from its company's same-date median.
    One row per company (>=5 same-date funds); colored by fund family."""
    cos = big.sort_values("spread_pct").company.tolist()
    # Colour is the only channel carrying the house identity, so it has to decode. The first
    # version indexed a hand-typed family list into `tab20` and fell back to plain grey for
    # anything not on the list. Two of the panel's houses are spelled "Franklin Templeton" and
    # "Neuberger Berman" in the data against "Franklin" and "Neuberger" on the list, so both
    # rendered grey; `tab20`'s fifteenth and sixteenth entries are grey and light grey, which
    # took Robinhood and Destiny; and the legend ended up with four grey dots, three of them
    # the same tone. On Gusto the reader cannot tell which house sits at −25%.
    #
    # So: the families come from the data, the palette is the qualitative one that has no grey
    # in it, grey is reserved for the "Other" bucket alone, and a family with no colour raises
    # instead of quietly becoming a fourth grey.
    # A referee could not separate Fidelity from Robinhood on the printed figure: `tab10` is
    # not colourblind-safe, and its pink and its brown converge under deuteranopia, which is
    # the most common form. The Okabe-Ito set is eight hues chosen to stay distinct under all
    # three types; grey is not one of them, which suits the "Other" bucket keeping it.
    OKABE_ITO = ["#0072b2", "#e69f00", "#009e73", "#d55e00",
                 "#cc79a7", "#56b4e9", "#f0e442", "#000000"]
    fams = [f for f in sorted(clean.family.dropna().unique()) if f != "Other"]
    hues = OKABE_ITO
    marks = ["o", "s", "^", "D", "v", "P", "X", "*", "<"]
    fam_color = {f: hues[i % len(hues)] for i, f in enumerate(fams)}
    fam_marker = {f: marks[(i // len(hues)) % len(marks)] for i, f in enumerate(fams)}
    fam_color["Other"], fam_marker["Other"] = "#9e9e9e", "o"
    missing = sorted(set(clean.family.dropna()) - set(fam_color))
    assert not missing, f"no colour assigned to {missing}"
    # Nine hues and nine markers give 81 combinations, and the two indices advance at
    # different rates, so the pairs are distinct — while both list lengths stay as they are.
    # A future edit to either list could collide two houses onto one glyph, which is the
    # failure this whole block exists to remove, so it is asserted rather than reasoned about.
    pairs = [(fam_color[f], fam_marker[f]) for f in fam_color]
    assert len(set(pairs)) == len(pairs), "two families share a colour and a marker"

    fig, ax = plt.subplots(figsize=(10, 0.62 * len(cos) + 1.8))
    seen = set()
    for y, co in enumerate(cos):
        md = R[R.company == co].iloc[0]["date"]
        s = clean[(clean.company == co) & (clean.report_date == md)]
        center = s.pps.median()
        for _, r in s.iterrows():
            dev = (r.pps / center - 1) * 100
            lbl = r.family if r.family not in seen else None
            seen.add(r.family)
            ax.scatter(dev, y, s=70, color=fam_color[r.family],
                       marker=fam_marker[r.family],
                       edgecolor="black", linewidth=0.5, zorder=3, label=lbl)
        sp = (s.pps.max() / s.pps.min() - 1) * 100
        ax.annotate(f"{int(s.fund.nunique())} funds · spread {sp:.0f}%",
                    (max((s.pps.max()/center-1)*100, 2) + 1.5, y), va="center", fontsize=8, color="#555")
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(range(len(cos)))
    ax.set_yticklabels(cos)
    ax.set_xlabel("Each fund's Level-3 mark vs the cross-fund median for that company, same quarter  (%)")
    # No in-image title: the figure caption in the paper carries it (and matches Table 4's
    # phrasing — each company read at its OWN modal report date), so a title here would be
    # a second copy that could drift from the first.
    # The "n funds · spread x%" annotations are placed in data coordinates to the right of the
    # widest point, so the axis has to be widened for them or the top row's label runs off the
    # canvas. Measured from the widest annotation rather than guessed at a margin fraction.
    lo, hi = ax.get_xlim()
    ax.set_xlim(lo, hi + 0.28 * (hi - lo))
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=7, ncol=2, framealpha=0.9, title="fund family")
    plt.tight_layout()
    fig.savefig(ROOT / "figures" / "fund_marks_dispersion.png", dpi=150)
    print("saved figures/fund_marks_dispersion.png")


if __name__ == "__main__":
    main()
