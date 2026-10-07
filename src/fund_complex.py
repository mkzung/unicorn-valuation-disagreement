"""Which registrants are the same fund house.

A registrant on Form N-PORT is a legal trust, not a fund complex. The largest houses each
file these marks under dozens of separate registrant CIKs — the counts live in
`src/paper_numbers.py`, not here, because a number in a docstring is a number no guard
reads. The
population panel originally counted each of those as a family, so a company held by two
Fidelity trusts cleared a bar meant to require two independent valuation opinions — and
those two trusts, sharing one valuation committee, agree by construction. Measured
agreement was inflated as a result.

The paper documents the mechanism itself: sub-advised funds across several
variable-insurance trusts, run by different insurers, carried Instacart into its listing at
T. Rowe Price's identical mark to the cent (§7.1). Section 5 was treating those trusts as
separate houses.

RULES ARE VERIFIED, NOT REMEMBERED. Every entry below was checked against the series names
the registrant actually files, because a wrong merge here fabricates agreement and a wrong
split fabricates disagreement — and disagreement is this paper's dependent variable. Two
rules were dropped at that step: `IVY FUNDS` files "Delaware Ivy ..." series, so it belongs
to Macquarie and not, as assumed, to Invesco; and `Variable Insurance Products Fund II`
files "VIP Contrafund Portfolio", which is Fidelity's.

One house is deliberately NOT merged. Franklin Templeton bought Putnam in 2024, but the
panel starts in 2019, and a static rule would backdate the merger over four years of
filings during which the two ran separate valuation processes. Putnam holds a rounding error's worth of
the cell value, so leaving it alone costs nothing and keeps the rule honest. The same
question applies to merges the map does make — Legg Mason (2020), Eaton Vance (2021),
the Ivy trusts (2021) — and it was measured rather than waved through: their combined
pre-acquisition exposure is a fraction of one percent of the value in the reported cells,
so a static map costs less than the machinery a date-aware one would need.

The map FAILS CLOSED. A registrant that matches nothing keeps its own identity and counts
as its own house, so anything missing makes the correction smaller, never larger. Shared
series trusts that host unrelated advisers — `Professionally Managed Portfolios` files both
Boston Common and Osterweis funds — are deliberately left unmapped for the same reason.

Run:  python3 src/fund_complex.py     (prints coverage and the largest complexes)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# (pattern, complex). Matched in order against the upper-cased registrant name, first hit
# wins, so put the specific brand ahead of any looser rule that could swallow it.
RULES: list[tuple[str, str]] = [
    # Fidelity. "Variable Insurance Products Fund [II-V]" carries VIP portfolios and is FMR's.
    (r"^FIDELITY\b", "Fidelity"),
    (r"^VARIABLE INSURANCE PRODUCTS FUND", "Fidelity"),
    # T. Rowe Price, with and without the point.
    (r"^T\.? ?ROWE PRICE\b", "T. Rowe Price"),
    # BlackRock, including the iShares ETF trusts.
    (r"^BLACK ?ROCK\b", "BlackRock"),
    (r"^ISHARES\b", "BlackRock"),
    # Capital Group's American Funds file under the fund's own name with no house brand,
    # so each one has to be named. Verified individually against the series they file.
    (r"^AMERICAN FUNDS\b", "Capital Group"),
    (r"^(?:THE )?GROWTH FUND OF AMERICA\b", "Capital Group"),
    (r"^(?:THE )?INCOME FUND OF AMERICA\b", "Capital Group"),
    (r"^(?:THE )?BOND FUND OF AMERICA\b", "Capital Group"),
    (r"^(?:THE )?INVESTMENT COMPANY OF AMERICA\b", "Capital Group"),
    (r"^(?:THE )?NEW ECONOMY FUND\b", "Capital Group"),
    # EuroPacific Growth Fund files under its own abbreviation as well as its full name,
    # and only the full name was mapped. The short one was left as a house of its own,
    # so Capital Group was counted twice in nine cells — including one of §4.3's ten
    # names. Found from the other side, in the N-CSR schedules, where the same fund turns
    # up beside Capital Group on one Canva lot and reads as a second opinion.
    (r"^EUPAC FUND\b", "Capital Group"),
    (r"^NEW WORLD FUND\b", "Capital Group"),
    (r"^SMALLCAP WORLD FUND\b", "Capital Group"),
    (r"^AMERICAN HIGH INCOME TRUST\b", "Capital Group"),
    (r"^CAPITAL INCOME BUILDER\b", "Capital Group"),
    (r"^CAPITAL WORLD\b", "Capital Group"),
    (r"^EUROPACIFIC GROWTH FUND\b", "Capital Group"),
    (r"^AMCAP FUND\b", "Capital Group"),
    (r"^FUNDAMENTAL INVESTORS\b", "Capital Group"),
    (r"^WASHINGTON MUTUAL INVESTORS\b", "Capital Group"),
    # Invesco absorbed the AIM trusts; the series are named "Invesco ...".
    (r"^INVESCO\b", "Invesco"),
    (r"^AIM \b", "Invesco"),
    # Franklin Templeton, plus the Legg Mason affiliates it acquired in 2020.
    (r"^FRANKLIN\b", "Franklin Templeton"),
    (r"^TEMPLETON\b", "Franklin Templeton"),
    (r"^LEGG MASON\b", "Franklin Templeton"),
    (r"^CLEARBRIDGE\b", "Franklin Templeton"),
    (r"^WESTERN ASSET\b", "Franklin Templeton"),
    (r"^ROYCE\b", "Franklin Templeton"),
    # Macquarie: Delaware Funds, and the Ivy trusts it took over (series read "Delaware Ivy").
    (r"^DELAWARE\b", "Macquarie"),
    # `^IVY FUNDS` missed two of them: "Ivy High Income Opportunities Fund" and "Ivy
    # Variable Insurance Portfolios" both file "Delaware Ivy ..." series.
    (r"^IVY\b", "Macquarie"),
    (r"^MACQUARIE\b", "Macquarie"),
    # Morgan Stanley, including Eaton Vance / Calvert / Parametric.
    (r"^MORGAN STANLEY\b", "Morgan Stanley"),
    (r"^EATON VANCE\b", "Morgan Stanley"),
    (r"^CALVERT\b", "Morgan Stanley"),
    (r"^PARAMETRIC\b", "Morgan Stanley"),
    # Nuveen and its TIAA parent.
    (r"^NUVEEN\b", "Nuveen"),
    (r"^TIAA\b", "Nuveen"),
    # PGIM is Prudential's asset manager.
    (r"^PRUDENTIAL\b", "PGIM"),
    (r"^PGIM\b", "PGIM"),
    # Everything below files under one recognisable brand.
    (r"^PIMCO\b", "PIMCO"),
    (r"^VANGUARD\b", "Vanguard"),
    (r"^JPMORGAN\b|^J\.?P\.? MORGAN\b", "JPMorgan"),
    (r"^ALGER\b", "Alger"),
    (r"^BARON\b", "Baron"),
    (r"^ARK\b", "ARK"),
    (r"^NEUBERGER BERMAN\b", "Neuberger Berman"),
    (r"^COHEN & STEERS\b", "Cohen & Steers"),
    (r"^JANUS\b", "Janus Henderson"),
    (r"^PRINCIPAL\b", "Principal"),
    (r"^VOYA\b", "Voya"),
    (r"^LINCOLN\b", "Lincoln"),
    (r"^BRIGHTHOUSE\b", "Brighthouse"),
    (r"^MASSMUTUAL\b|^MML\b", "MassMutual"),
    (r"^FS \b|^FS[A-Z]*\b", "FS Investments"),
    (r"^METROPOLITAN WEST\b|^TCW\b", "TCW"),
    (r"^STEPSTONE\b", "StepStone"),
    (r"^FPA\b", "FPA"),
    (r"^VALIC\b", "VALIC"),
    (r"^JNL\b", "Jackson"),
    (r"^PENN SERIES\b", "Penn Mutual"),
    (r"^AB \b|^ALLIANCEBERNSTEIN\b", "AllianceBernstein"),
    (r"^GOLDMAN SACHS\b", "Goldman Sachs"),
    (r"^WELLS FARGO\b|^ALLSPRING\b", "Allspring"),
    (r"^HARTFORD\b", "Hartford"),
    (r"^JOHN HANCOCK\b", "John Hancock"),
    (r"^COLUMBIA\b|^AMERIPRISE\b", "Columbia Threadneedle"),
    (r"^DWS\b|^DEUTSCHE\b", "DWS"),
    (r"^SEI \b", "SEI"),
    (r"^SCHWAB\b|^CHARLES SCHWAB\b", "Schwab"),
    (r"^DODGE & COX\b", "Dodge & Cox"),
    (r"^HARBOR\b", "Harbor"),
    (r"^THRIVENT\b", "Thrivent"),
    (r"^TRANSAMERICA\b", "Transamerica"),
    (r"^GUGGENHEIM\b|^RYDEX\b", "Guggenheim"),
    (r"^VIRTUS\b", "Virtus"),
    (r"^AMERICAN CENTURY\b", "American Century"),
    (r"^ARTISAN\b", "Artisan"),
    (r"^WILLIAM BLAIR\b", "William Blair"),
    (r"^DAVIS\b|^SELECTED AMERICAN SHARES\b|^SELECTED FUNDS\b", "Davis"),
    # Added after a second pass over the registrants the map left as singletons, each
    # confirmed against the series it files rather than from the name alone.
    (r"^DFA\b|^DIMENSIONAL\b", "Dimensional"),
    (r"^ABRDN\b|^ABERDEEN\b", "abrdn"),
    (r"^DOUBLELINE\b", "DoubleLine"),
    (r"^FIRST TRUST\b|^FT \b", "First Trust"),
    (r"^BNY\b|^DREYFUS\b", "BNY Mellon"),
    # Found by `population.duplicate_books`, which looks for one holding reported twice: the
    # same company, the same report date, the same share count AND the same value to the cent
    # under two different house labels. Two independent committees do not land on identical
    # figures fifty-four times, and every rule here was then confirmed the way the rest were,
    # against the series each registrant files.
    #   Apollo Senior Floating Rate and Apollo Tactical Income file "Apollo ..." series
    (r"^APOLLO\b", "Apollo"),
    #   AllianzGI Convertible & Income Fund and Fund II file "AllianzGI ..." series
    (r"^ALLIANZGI\b", "AllianzGI"),
    #   Tekla Healthcare Investors and Tekla Life Sciences Investors file their own names
    (r"^TEKLA\b", "Tekla"),
    #   Gabelli's trusts file "Gabelli ..." series. GDL Fund carries the same book and is
    #   deliberately NOT mapped: its series is "GDL Fund" and nothing in what it files says
    #   Gabelli, so merging it would be remembering rather than verifying.
    (r"^GABELLI\b", "Gabelli"),
    #   Putnam's own trusts, including George Putnam Balanced Fund. This is Putnam becoming
    #   one house, not Putnam joining Franklin — the 2024 acquisition stays unmapped for the
    #   reason given above.
    (r"\bPUTNAM\b", "Putnam"),
]

_COMPILED = [(re.compile(p), name) for p, name in RULES]


def normalise(name: str) -> str:
    """Upper-case, collapse whitespace, drop a leading article."""
    s = re.sub(r"\s+", " ", str(name).strip().upper())
    return re.sub(r"^THE ", "", s)


def confirmations(d: pd.DataFrame, unit: str = "house") -> int:
    """How many independent opinions a set of rows carries. Houses, never registrants.

    Three metrics in a row have been built in this repository whose first version counted
    registrants: §5's original panel, the N-CSR agreement table, and the split detector. Each
    time the number came out two to four times too high, and each time it was caught by someone
    reading the output rather than by the code. A registrant is a legal trust and a house files
    under dozens of them, so the default is wrong in a direction that manufactures agreement.

    This exists so the next metric does not have to rediscover that. Pass `unit="CIK"` only to
    reproduce a registrant-level bound deliberately, the way §5 quotes one.
    """
    if unit not in {"house", "CIK", "fund"}:
        raise ValueError(f"independence is counted in houses, funds or CIKs, not {unit!r}")
    if unit == "house" and "house" not in d.columns:
        d = d.assign(house=add_complex(d))
    return int(d[unit].nunique())


def complex_of(registrant_name: str) -> str:
    """The fund complex a registrant belongs to, or the registrant itself when unknown."""
    s = normalise(registrant_name)
    for pat, name in _COMPILED:
        if pat.search(s):
            return name
    return s


def add_complex(d: pd.DataFrame) -> pd.Series:
    """Vectorised `complex_of` over a frame carrying REGISTRANT_NAME.

    Registrants are resolved per distinct name rather than per row: there are three orders
    of magnitude more rows than distinct names, so the loop runs over the names and the
    result is mapped back.
    """
    names = d.REGISTRANT_NAME.fillna("")
    lookup = {n: complex_of(n) for n in names.unique()}
    return names.map(lookup)


if __name__ == "__main__":
    import population as pop

    d, c = pop.panel()
    x = pop.comparable(d)
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    x = x[[k in keys for k in zip(x.company, x.dt)]].copy()
    x["complex"] = add_complex(x)

    mapped = x[x.REGISTRANT_NAME.map(lambda n: complex_of(n) != normalise(n))]
    print(f"registrant names in the cells : {x.REGISTRANT_NAME.nunique():,}")
    print(f"distinct registrant CIKs      : {x.CIK.nunique():,}")
    print(f"distinct complexes            : {x['complex'].nunique():,}")
    print(f"rows matched to a named house : {len(mapped)/len(x)*100:.1f}%")
    print(f"NAV matched to a named house  : {mapped.val_usd.sum()/x.val_usd.sum()*100:.1f}%\n")

    top = (x.groupby("complex").agg(nav=("val_usd", "sum"), ciks=("CIK", "nunique"))
             .sort_values("nav", ascending=False).head(15))
    print(f"{'complex':24s} {'NAV $B':>8s} {'registrant CIKs collapsed':>26s}")
    for name, r in top.iterrows():
        print(f"  {name[:22]:22s} {r.nav/1e9:8.1f} {int(r.ciks):26d}")
