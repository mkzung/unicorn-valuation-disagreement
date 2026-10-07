"""Round dates from Form D, and the check that decides whether they can be used.

The paper replaced press-sourced listing dates with filings (`src/listing_dates.py`). Round
dates are the other press-sourced quantity, and they gate everything that wants to know
where a company sits in a re-pricing cycle. Form D is the filing: an issuer selling
securities under Regulation D files a notice of exempt offering, and the notice carries the
date of first sale.

The SEC publishes it the same way it publishes N-PORT — quarterly flat files rather than a
search index, so companies are discovered from the filings instead of from a list.

WHAT THIS MODULE PRODUCES, AND WHAT IT DOES NOT
It produces a validation and a coverage measurement. It does NOT produce a round date the
paper quotes, because whether these dates are usable is exactly the question, and the answer
is measured here rather than assumed. `validate()` prints the distance from each Form D
first-sale date to the press date the panel already carries, for the names where both exist.
The threshold, if there is one, comes off the shape of that distribution — the same rule the
listing dates were held to, where the distances separated cleanly into two groups.

THREE THINGS THE DOWNLOAD RECIPE HAS TO GET RIGHT
The URL cannot be templated. Files sit under two different paths — `structureddata` for most
of the history and `datastandardsinnovation` for the newest quarter — and older ones carry a
`_0` suffix that newer ones do not. The index page is the only reliable list, so it is
fetched and parsed rather than guessed at, which also means a new quarter needs no code
change. The archive starts in 2008 but is nearly empty until late 2009: the 2008 zips are
tens of kilobytes against megabytes later, because electronic Form D only became mandatory
in March 2009.

WHAT COVERAGE MEANS HERE, AND WHY IT IS MEASURED FIRST
Not every round files a Form D. A Section 4(a)(2) placement does not, and neither does a
Reg S offering sold entirely offshore. So the share of known rounds with a matching filing
is not a diagnostic of this code, it is the sample size of anything built on it, and
`coverage()` reports it. The same goes for the fields: REVENUERANGE permits "Decline to
Disclose" and a covariate nobody fills in is not a covariate.

Run:  python3 src/form_d.py           # fetch every quarter, rebuild the extract
      python3 src/form_d.py --check   # offline: read the extract and validate it
"""
from __future__ import annotations

import io
import re
import ssl
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import certifi
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import entity_resolution as er

OUT = ROOT / "data" / "form_d_offerings.csv.gz"
STATS = ROOT / "data" / "form_d_coverage.csv"
INDEX = "https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets"
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"     # SEC requires a real UA
CTX = ssl.create_default_context(cafile=certifi.where())

SUB_COLS = ["ACCESSIONNUMBER", "FILING_DATE", "SIC_CODE", "SUBMISSIONTYPE", "TESTORLIVE"]
ISS_COLS = ["ACCESSIONNUMBER", "IS_PRIMARYISSUER_FLAG", "CIK", "ENTITYNAME", "ENTITYTYPE",
            "JURISDICTIONOFINC", "YEAROFINC_VALUE_ENTERED",
            "ISSUER_PREVIOUSNAME_1", "ISSUER_PREVIOUSNAME_2", "ISSUER_PREVIOUSNAME_3",
            "EDGAR_PREVIOUSNAME_1", "EDGAR_PREVIOUSNAME_2", "EDGAR_PREVIOUSNAME_3"]
OFF_COLS = ["ACCESSIONNUMBER", "INDUSTRYGROUPTYPE", "INVESTMENTFUNDTYPE", "IS40ACT",
            "REVENUERANGE", "ISAMENDMENT", "PREVIOUSACCESSIONNUMBER", "SALE_DATE",
            "YETTOOCCUR", "ISEQUITYTYPE", "TOTALOFFERINGAMOUNT", "TOTALAMOUNTSOLD"]


def _get(url: str) -> bytes:
    time.sleep(0.15)                                   # SEC fair access
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
        return r.read()


def quarters() -> dict[str, str]:
    """quarter -> download URL, read off the SEC's own index page.

    Parsed rather than templated: the path prefix changed once and the filename suffix
    changed twice over the archive, so any pattern written down today is a pattern that
    breaks on some quarter.
    """
    html = _get(INDEX).decode("utf-8", "replace")
    out = {}
    for href, q in re.findall(r'href="(/files/[^"]*form-d-data-sets/(\d{4}q\d)_d(?:_\d)?\.zip)"',
                              html):
        out.setdefault(q, "https://www.sec.gov" + href)
    return dict(sorted(out.items()))


def _table(z: zipfile.ZipFile, name: str, cols: list[str]) -> pd.DataFrame:
    member = next(n for n in z.namelist() if n.upper().endswith(name))
    d = pd.read_csv(io.BytesIO(z.read(member)), sep="\t", dtype=str,
                    on_bad_lines="skip", low_memory=False)
    keep = [c for c in cols if c in d.columns]
    return d[keep]


def quarter_frame(url: str) -> pd.DataFrame:
    """One quarter, joined on the accession number, primary issuer only.

    A filing can name several issuers — a fund complex raising for many vehicles at once —
    and only the primary one is the company the offering belongs to.
    """
    z = zipfile.ZipFile(io.BytesIO(_get(url)))
    sub = _table(z, "FORMDSUBMISSION.TSV", SUB_COLS)
    iss = _table(z, "ISSUERS.TSV", ISS_COLS)
    off = _table(z, "OFFERING.TSV", OFF_COLS)
    iss = iss[iss.IS_PRIMARYISSUER_FLAG.fillna("").str.upper().str.startswith("Y")]
    return sub.merge(iss, on="ACCESSIONNUMBER").merge(off, on="ACCESSIONNUMBER")


def fetch(qs: dict[str, str] | None = None) -> pd.DataFrame:
    qs = qs or quarters()
    frames = []
    for q, url in qs.items():
        try:
            f = quarter_frame(url)
        except Exception as e:
            print(f"  {q}: FAILED {e}")
            continue
        f["src_quarter"] = q
        frames.append(f)
        print(f"  {q}: {len(f):>6} offerings")
    return pd.concat(frames, ignore_index=True)


def names(d: pd.DataFrame) -> pd.Series:
    """Normalised issuer name, the same normaliser the mark panel resolves on."""
    return d.ENTITYNAME.fillna("").map(lambda s: er.norm_name(s))


def flag(col: pd.Series) -> pd.Series:
    """The boolean columns are spelled `true`/`false`, and assuming `Y`/`N` returns silence.

    The first version of `coverage` filtered amendments with `startswith("N")` and reported
    that the archive contains no original offerings at all — a filter that matches nothing
    reads exactly like a data set that contains nothing. Hence a shared parser, and a test
    that asserts the vocabulary.
    """
    return col.fillna("").astype(str).str.strip().str.lower().isin(["true", "y", "yes", "1"])


def coverage(d: pd.DataFrame) -> pd.DataFrame:
    """The two facts that decide whether anything can be built on this.

    Reported as counts and shares over every live original offering, because a fill rate is
    only meaningful against the population it is a fill rate of.
    """
    live = d[d.TESTORLIVE.fillna("LIVE").str.upper() == "LIVE"]
    orig = live[~flag(live.ISAMENDMENT)]
    eq = orig[flag(orig.ISEQUITYTYPE)]
    rev = orig.REVENUERANGE.fillna("").str.strip()
    rows = [
        ("offerings, all rows", len(d)),
        ("offerings, live", len(live)),
        ("offerings, live originals (not amendments)", len(orig)),
        ("of those, equity offerings", len(eq)),
        ("with a first-sale date", int(orig.SALE_DATE.notna().sum())),
        ("flagged first sale yet to occur", int(flag(orig.YETTOOCCUR).sum())),
        ("REVENUERANGE answered at all", int((rev != "").sum())),
        ("REVENUERANGE declines to disclose", int(rev.str.contains("Decline", case=False).sum())),
        ("REVENUERANGE gives a usable bucket",
         int(((rev != "") & ~rev.str.contains("Decline", case=False)).sum())),
        ("issuer declares itself a pooled fund",
         int((orig.INDUSTRYGROUPTYPE.fillna("").str.contains("Pooled", case=False)
              | flag(orig.IS40ACT)).sum())),
        ("distinct issuer CIKs", int(orig.CIK.nunique())),
    ]
    t = pd.DataFrame(rows, columns=["fact", "n"])
    t["share_of_live_originals"] = (t.n / max(len(orig), 1) * 100).round(2)
    return t


def panel_names() -> dict[str, str]:
    """The press-dated companies to validate against: normalised name -> company."""
    p = pd.read_csv(ROOT / "data" / "valuation_panel.csv")
    return {er.norm_name(c): c for c in p.company}


# An SPV raising to buy one company's stock files its own Form D and puts the company's name
# in the issuer field: "Anthropic Series D NMJFF Apr 2024 a Series of CGF2021 LLC", "Stripe
# Inc Stock May 2024 a Series of CGF2021 LLC", "Kraken Series A, a Series of Providence
# Venture Capital, LLC". Its first-sale date is the date the SPV raised, not the date the
# company did. Section 5 excludes exactly these vehicles from the mark panel for the same
# reason, one field over: a price per unit in a feeder is not the company's price per share.
VEHICLE = r"\bA SERIES OF\b|\bSERIES OF\b.*\bLLC\b|\bSPV\b|CO-?INVEST|\bFUND\b\s|\bFEEDER\b"


def is_vehicle(d: pd.DataFrame) -> pd.Series:
    txt = d.ENTITYNAME.fillna("").str.upper()
    return (txt.str.contains(VEHICLE, regex=True)
            | d.INDUSTRYGROUPTYPE.fillna("").str.contains("Pooled", case=False)
            | flag(d.IS40ACT))


def match(d: pd.DataFrame) -> pd.DataFrame:
    """Offerings whose issuer name matches a company the panel carries a press date for."""
    want = panel_names()
    n = names(d)
    m = d[n.isin(want)].copy()
    m["company"] = n[n.isin(want)].map(want)
    m["vehicle"] = is_vehicle(m)
    return m


def validate(m: pd.DataFrame | None = None) -> pd.DataFrame:
    """Each company's Form D first sale against the press date the panel already carries.

    The press date is a month for most rows, so the comparison is made at month granularity
    and the distance is in months, not days. Being coarser than the listing check is a
    property of the press source, not of Form D.
    """
    if m is None:
        m = load()
    p = pd.read_csv(ROOT / "data" / "valuation_panel.csv")
    press = {r.company: str(r.headline_date) for _, r in p.iterrows()}
    live = m[(m.TESTORLIVE.fillna("LIVE").str.upper() == "LIVE")
             & ~flag(m.ISAMENDMENT) & m.SALE_DATE.notna()
             & ~m.vehicle.astype(str).str.lower().isin(["true"])].copy()
    live["sale"] = pd.to_datetime(live.SALE_DATE, errors="coerce")
    rows = []
    for co, g in live.groupby("company"):
        want = press.get(co, "")
        pm = pd.Period(want[:7], "M") if re.match(r"^\d{4}-\d{2}", want) else None
        g = g.dropna(subset=["sale"])
        if g.empty:
            continue
        # The offering closest in time to the press date, and the latest one, because which
        # of the two a reader should want is the question the distribution answers.
        if pm is not None:
            g = g.assign(gap=[(pd.Period(s, "M") - pm).n for s in g.sale])
            best = g.iloc[g.gap.abs().argmin()]
        else:
            best = g.sort_values("sale").iloc[-1]
        rows.append({"company": co, "press": want,
                     "closest_first_sale": best.sale.date().isoformat(),
                     "gap_months": int(best.gap) if pm is not None else None,
                     "latest_first_sale": g.sale.max().date().isoformat(),
                     "offerings": len(g), "cik": best.CIK,
                     "entity": best.ENTITYNAME,
                     "revenue_range": best.get("REVENUERANGE", "")})
    if not rows:
        return pd.DataFrame(columns=["company", "press", "closest_first_sale", "gap_months",
                                     "latest_first_sale", "offerings", "cik", "entity",
                                     "revenue_range"])
    return pd.DataFrame(rows).sort_values("company").reset_index(drop=True)


def load() -> pd.DataFrame:
    return pd.read_csv(OUT, dtype=str, low_memory=False)


def main() -> None:
    if "--check" not in sys.argv:
        qs = quarters()
        print(f"index lists {len(qs)} quarters, {min(qs)} to {max(qs)}")
        d = fetch(qs)
        cov = coverage(d)
        cov.to_csv(STATS, index=False)
        m = match(d)
        m.to_csv(OUT, index=False)
        print(f"\n{len(d):,} offerings harvested; {len(m):,} matched to a panel company")
        print(f"wrote {OUT.relative_to(ROOT)} and {STATS.relative_to(ROOT)}")
    cov = pd.read_csv(STATS)
    print("\ncoverage of the harvest")
    print(cov.to_string(index=False))
    v = validate()
    print(f"\nfirst-sale date against the press date, {len(v)} of the panel's companies")
    print(v[["company", "press", "closest_first_sale", "gap_months", "latest_first_sale",
             "offerings", "entity"]].to_string(index=False))
    if v.gap_months.notna().any():
        g = v.gap_months.dropna().abs()
        print(f"  |gap| median {g.median():.0f} months · inside 1 month {int((g <= 1).sum())} "
              f"of {len(g)} · inside 3 months {int((g <= 3).sum())}")


if __name__ == "__main__":
    main()
