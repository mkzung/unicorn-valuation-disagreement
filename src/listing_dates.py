"""When did each company in the panel start trading? Read off its own EDGAR filing history.

P4 needs a listing date per name and §7.1 currently takes its dates from the press. Both
can be served from the filings, and the previous round did it by hand for five names —
Form 8-A12B, the registration of a security on a national exchange, pulled from EDGAR
full-text search. Five names is a validation, not a sensor. This module is the sensor: the
submissions API returns every filing a CIK has ever made, so the same question can be asked
of every cluster in the panel and answered without a browser.

The rule is mechanical, and it is stated before the exceptions because the exceptions are
what make it worth writing down.

    listing = the earliest exchange registration this CIK filed while it carried this
              company's name

Both halves of that sentence exist because dropping either one gives a wrong date on a
real name in this panel.

WHAT GOES WRONG WITHOUT "EARLIEST"
A company files 8-A12B again when it changes exchange. Palantir has two, September 2020
for the direct listing and November 2024 for the move from NYSE to Nasdaq. Taking the
latest puts the event four years late.

WHAT GOES WRONG WITHOUT "WHILE IT CARRIED THIS COMPANY'S NAME"
A company that comes to market by merging into a listed shell never files an 8-A12B of its
own: the shell's registration is already there and the operating company inherits it. Under
"earliest 8-A12B" DraftKings dates to 10 May 2019, which is the day Diamond Eagle
Acquisition Corp went public — a year before DraftKings existed as a public company. EDGAR
records the transition rather than hiding it: CIK 1772757 carried the name Diamond Eagle
until 24 April 2020 and DraftKings from the 27th, and the successor registration, Form
8-K12B, was filed on the 29th. Reading the name eras is what tells the two apart, and the
same reading gets Aurora Innovation right, where the predecessor was Reinvent Technology
Partners Y and no successor form was filed at all — the name change on 3 November 2021 is
the whole record, and Aurora's stock began trading the next day.

WHAT GOES WRONG WITHOUT PAGING THE ARCHIVE
`filings.recent` in the submissions JSON is capped. For a company that files often the
listing has rolled off it: Airbnb returns no 8-A12B at all from `recent`, and DoorDash
returns September 2023 — a later re-registration — while its December 2020 listing sits in
the archived pages. Both errors are silent, and one of them is thirty-four months.

WHAT GOES WRONG STARTING FROM A TICKER
A ticker is a current-state key and this panel is historical. BIRD today resolves to
Smartbird, Inc., which is the same CIK Allbirds always had under a later name, so that one
survives; DKNG resolves to CIK 1883685, a holding company created in the 2022
reorganisation that has never filed an exchange registration at all. Every CIK below is
therefore pinned in the table rather than looked up, and each is checkable against the
accession the fetch records.

THE CHECK THAT CAN FAIL
A pinned CIK, an era rule and a hand override are three ways to attach the wrong date to a
name, so the date is checked against something the paper already has: the last report date
on which the company appears as a Level-3 private holding. `validate()` prints the distance
between the two, and it earns its place by having caught a wrong CIK in this table's own
first draft — 1876431 was pinned for Circle from memory and belongs to Prenetics Global,
whose registration sat 1,049 days from where Circle's marks stop.

The distances separate rather than tail off. Most names land inside a quarter, the widest
of them 82 days, and the next one after that is 258 — so the threshold is read off the data
instead of chosen, and the three names outside it are outside for one nameable reason: they
listed long after mutual funds stopped holding enough of them to make a cell. Grab's two
cells end sixteen months before it listed, ServiceTitan's twenty-six.

Run:  python3 src/listing_dates.py            # re-fetch from EDGAR, rewrite the table
      python3 src/listing_dates.py --check    # offline: read the table and validate it
"""
from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path

import certifi
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "data" / "listing_dates.csv"
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"     # SEC requires a real UA
SUB = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
CTX = ssl.create_default_context(cafile=certifi.where())

# Exchange registrations. 8-A12B registers a class on a national exchange, which covers an
# underwritten IPO and a direct listing alike; 8-K12B is the successor-issuer filing a
# company makes when it inherits a registration, which is the de-SPAC's equivalent.
# Amendments are excluded: DraftKings' 8-A12B/A of June 2020 amends the shell's 2019
# registration and dates neither event.
FORMS = ("8-A12B", "8-A12G", "8-K12B")

# key -> (CIK, era override or None, note). The CIK is pinned because a ticker lookup is a
# current-state map; the override names which era of a renamed registrant the panel's
# cluster refers to, and is only needed where the same CIK carried the company's name twice.
CANDIDATES: dict[str, tuple[int | None, str | None, str]] = {
    "ROW:33217":                   (1559720, None, "Airbnb"),
    "NM:PALANTIR":                 (1321655, None, "direct listing; second 8-A12B in 2024 is the Nasdaq move"),
    "NM:UIPATH":                   (1734722, None, ""),
    "NM:SWEETGREEN":               (1477815, None, ""),
    "NM:RIVIAN AUTOMOTIVE":        (1874178, None, ""),
    "NM:HONEST":                   (1530979, None, ""),
    "NM:TOAST":                    (1650164, None, ""),
    "NM:DOORDASH":                 (1792789, None, "2023 re-registration is the one `recent` returns"),
    "NM:OUTSET MEDICAL":           (1484612, None, "filed as Home Dialysis Plus until 2015"),
    "NM:DOXIMITY":                 (1516513, None, ""),
    "NM:ALLBIRDS":                 (1653909, None, "renamed Smartbird after the panel window; same CIK"),
    "NM:WARBY PARKER":             (1504776, None, "direct listing; filed as JAND, Inc."),
    "NM:XIAOJU KUAIZHI":           (1764757, None, "Didi Global; ADSs registered on the NYSE"),
    "NM:DRAFTKINGS":               (1772757, "DraftKings Inc.",
                                    "de-SPAC into Diamond Eagle; the 2019 8-A12B is the shell's"),
    "NM:AURORA INNOVATION":        (1828108, "Aurora Innovation, Inc.",
                                    "de-SPAC into Reinvent Technology Partners Y"),
    "NM:VROOM":                    (1580864, None, ""),
    "NM:GRAB":                     (1855612, None, "de-SPAC into Altimeter Growth"),
    "NM:MAPLEBEAR DBA INSTACART":  (1579091, None, "Maplebear Inc."),
    # CIK pinned from the ticker file rather than from memory: 1876431 is Prenetics Global,
    # whose 8-A12B of May 2022 the check rejected at 1,049 days from the panel exit.
    "NM:CIRCLE INTERNET FINANCIAL": (1876042, None, ""),
    "NM:CAVA":                     (1639438, None, ""),
    "NM:SERVICETITAN":             (1638826, None, ""),
    # Two names that belong in the table precisely because the sensor cannot date them, and
    # a table that only holds its successes is a table that hides its coverage.
    "NM:ROOFOODS":                 (None, None, "Deliveroo listed on the LSE; no SEC registration exists"),
    "NM:ANT":                      (None, None, "the 2020 listing was pulled; the company is still private"),
}

# One quarter, and the number is read rather than picked: the distances run 3, 8, 8, 9, 11,
# 15, 16, 21, 25, 29, 34, 55, 57, 63, 66, 76, 76, 82 days and then jump to 258, so every
# threshold from 83 to 257 selects the same eighteen names. A previous round quoted a
# fortnight. That was true of the five names then pulled by hand and false of the panel —
# the claim moved as soon as the sample stopped being the sample that was easy to pull.
ANCHOR_TOLERANCE = 92


def _get(url: str) -> dict:
    time.sleep(0.15)                                   # SEC fair access
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
        return json.loads(r.read())


def filing_history(cik: int) -> tuple[dict, pd.DataFrame]:
    """Every filing a CIK has made, `recent` plus the archived pages.

    The paging is the point. `recent` holds a fixed number of filings, so for an active
    filer the listing is not in it, and the failure is silent rather than empty: DoorDash's
    `recent` contains an 8-A12B, just not the one from December 2020.
    """
    j = _get(SUB.format(cik=cik))
    parts = [j["filings"]["recent"]]
    for f in j["filings"].get("files", []):
        parts.append(_get("https://data.sec.gov/submissions/" + f["name"]))
    rows = [(d, f, a) for p in parts
            for d, f, a in zip(p["filingDate"], p["form"], p["accessionNumber"])]
    return j, pd.DataFrame(rows, columns=["date", "form", "accession"]).drop_duplicates()


def name_eras(j: dict) -> dict[str, str]:
    """name -> the earliest date this CIK carried it.

    EDGAR dates the transitions, which is what makes the de-SPAC case mechanical rather
    than a judgement: the registrant stops being the shell on a recorded day. The current
    name gets the day the last *different* name ended, because a registrant that re-files
    its own unchanged name appears in `formerNames` as its own predecessor — Airbnb does,
    and treating that entry as a transition dates Airbnb's listing to this year.
    """
    former = j.get("formerNames", [])
    eras: dict[str, str] = {}
    for f in former:
        eras[f["name"]] = min(eras.get(f["name"], "9999"), f["from"][:10])
    cur = j["name"]
    handover = max((f["to"][:10] for f in former if f["name"] != cur), default="0001-01-01")
    eras[cur] = min(eras.get(cur, "9999"), handover)
    return eras


def resolve(key: str, cik: int, era_override: str | None) -> dict:
    """The rule, applied to one company.

    The default floor is the beginning of time: take the earliest exchange registration the
    CIK ever filed. That is right wherever the company has always been itself, and wrong in
    exactly one situation — a registrant that used to be somebody else — so the override
    names the era instead of the default silently guessing at one. Passing a date rather
    than a name sets the floor directly, which is what a registration that never led to
    trading needs.
    """
    j, f = filing_history(cik)
    eras = name_eras(j)
    if era_override and era_override[:2].isdigit():
        era = ("(from " + era_override + ")", era_override)
    elif era_override:
        era = (era_override, eras[era_override])
    else:
        era = ("(any)", "0001-01-01")
    reg = f[f.form.isin(FORMS) & (f.date >= era[1])].sort_values("date")
    if len(reg):
        r = reg.iloc[0]
        mech = "exchange registration" if r.form.startswith("8-A") else "successor registration"
        out = {"listing_date": r.date, "form": r.form, "accession": r.accession,
               "mechanism": mech}
    else:
        # No registration filed under this name: the company inherited one, and the day it
        # became the registrant is the only date EDGAR carries. Aurora is the case.
        out = {"listing_date": era[1], "form": "", "accession": "",
               "mechanism": "successor name"}
    # The name to print is the one the registrant carried on the day it listed. Today's name
    # is wrong for a company since renamed — Allbirds files as Smartbird now — and the
    # oldest is wrong for one renamed before listing, as Outset Medical was.
    at = max((n for n, s in eras.items() if s <= out["listing_date"]),
             key=lambda n: eras[n], default=j["name"])
    return {"key": key, "cik": cik, "company": at, "edgar_name": j["name"],
            "era_name": era[0], "era_from": era[1], **out}


def fetch() -> pd.DataFrame:
    rows = []
    for key, (cik, era, note) in CANDIDATES.items():
        if cik is None:
            rows.append({"key": key, "cik": "", "company": "", "edgar_name": "",
                         "era_name": "", "era_from": "", "listing_date": "", "form": "",
                         "accession": "", "mechanism": "no SEC registration", "note": note})
            continue
        r = resolve(key, cik, era)
        r["note"] = note
        rows.append(r)
    return pd.DataFrame(rows)


def load() -> pd.DataFrame:
    d = pd.read_csv(OUT, dtype=str).fillna("")
    return d


def dates() -> dict[str, pd.Timestamp]:
    """key -> listing date, for the names the sensor could date."""
    d = load()
    d = d[d.listing_date != ""]
    return {r.key: pd.Timestamp(r.listing_date) for _, r in d.iterrows()}


def validate() -> pd.DataFrame:
    """Each listing date against the last date its company appears as a private holding.

    Two independent things are being checked at once, which is why one column can settle
    both: a wrong CIK, a wrong era or a wrong form would put the date somewhere the panel
    does not support, and equally a panel exit that is nowhere near the listing means the
    exit cannot stand in for the listing on the names where no filing was pulled.
    """
    import population as pop
    _, c = pop.panel()
    g = c[c.guarded]
    rows = []
    for _, r in load().iterrows():
        s = g[g.company == r.key]
        last = s.dt.max() if len(s) else pd.NaT
        gap = ((pd.Timestamp(r.listing_date) - last).days
               if r.listing_date and pd.notna(last) else None)
        rows.append({"key": r.key, "company": r.company,
                     "listing_date": r.listing_date, "form": r.form,
                     "mechanism": r.mechanism, "cells": len(s),
                     "last_cell": last.date().isoformat() if pd.notna(last) else "",
                     "gap_days": gap,
                     "validated": gap is not None and abs(gap) <= ANCHOR_TOLERANCE})
    return pd.DataFrame(rows).sort_values("listing_date")


def summary() -> dict:
    v = validate()
    ok = v[v.validated]
    return {
        "candidates": len(v),
        "dated": int((v.listing_date != "").sum()),
        "validated": len(ok),
        "worst_validated_gap": int(ok.gap_days.abs().max()),
        "closest_rejected_gap": int(v[~v.validated & v.gap_days.notna()].gap_days.abs().min()),
        "de_spac": int((v.mechanism.isin(["successor registration", "successor name"])).sum()),
    }


def main() -> None:
    if "--check" not in sys.argv:
        d = fetch()
        d.to_csv(OUT, index=False)
        print(f"fetched {len(d)} companies from EDGAR -> {OUT.relative_to(ROOT)}")
    v = validate()
    print("listing dates against the last date each company is held as a private mark")
    print(v.to_string(index=False))
    s = summary()
    print(f"\n  {s['dated']} of {s['candidates']} dated from filings, {s['validated']} land "
          f"within {ANCHOR_TOLERANCE} days of the panel exit")
    print(f"  worst validated gap {s['worst_validated_gap']} days · closest rejected "
          f"{s['closest_rejected_gap']} days — the two groups do not touch")
    print(f"  {s['de_spac']} came to market through a shell, where the 8-A12B belongs to the "
          f"predecessor and is correctly not used")


if __name__ == "__main__":
    main()
