"""Harvest every Level-3 private mark in the SEC bulk Form N-PORT data sets.

`src/nport_fetch.py` searches EDGAR for one company at a time and stops after eighteen
filings, so it can only find companies already on a list and can miss most of the funds
holding them. This module reverses that: the SEC's Division of Economic and Risk Analysis
publishes every disseminated N-PORT filing as a quarterly flat-file data set, so companies
are discovered from the filings and coverage is whatever the filings contain.

Keeps the rows a private-company mark can come from — fair value Level 3, equity,
denominated in shares — and joins each to its filing date, fund series and registrant.
The restricted-security flag is carried as a column, not applied as a filter; filers
disagree about it for the same security.
SEC data is public domain; the declared User-Agent follows SEC fair access.

Output: data/nport_population_marks.csv.gz, one row per (filing, holding).

Run:  python3 src/nport_bulk.py                 # every quarter from 2019Q4
      python3 src/nport_bulk.py 2026q1 2026q2   # named quarters only
Interrupted runs resume: quarters already in the output are skipped.
"""
from __future__ import annotations

import io
import ssl
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import certifi
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "nport_population_marks.csv.gz"
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"     # SEC requires a real UA
URL = "https://www.sec.gov/files/dera/data/form-n-port-data-sets/{q}_nport.zip"

# A python.org install on macOS ships without provisioned root certificates, so point at
# the certifi bundle rather than turning verification off.
CTX = ssl.create_default_context(cafile=certifi.where())

QUARTERS = [q for q in (f"{y}q{i}" for y in range(2019, 2027) for i in (1, 2, 3, 4))
            if "2019q4" <= q <= "2026q2"]

TABLES = ["SUBMISSION.tsv", "REGISTRANT.tsv", "FUND_REPORTED_INFO.tsv", "FUND_REPORTED_HOLDING.tsv"]
HOLD_COLS = ["ACCESSION_NUMBER", "ISSUER_NAME", "ISSUER_TITLE", "ISSUER_LEI", "ISSUER_CUSIP",
             "BALANCE", "UNIT", "CURRENCY_VALUE", "CURRENCY_CODE", "PERCENTAGE", "ASSET_CAT",
             "ISSUER_TYPE", "INVESTMENT_COUNTRY", "IS_RESTRICTED_SECURITY", "FAIR_VALUE_LEVEL"]


def fetch(q: str) -> bytes:
    req = urllib.request.Request(URL.format(q=q), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=900, context=CTX) as r:
        return r.read()


def select_private(hold: pd.DataFrame) -> pd.DataFrame:
    """The rows a private-company mark can come from.

    Level 3 is the fair-value hierarchy tier for inputs that are not observable, which is
    where a private holding has to sit. EC/EP are common and preferred equity. NS means
    the balance is a share count, without which price per share is undefined — principal
    amounts and "other units" cannot be divided into a per-share price.

    The restricted-security flag is deliberately NOT a filter. Filers disagree about it
    for the same security: on 2026-04-30 Fidelity reported Revolut as restricted and ARK
    reported the identical holding as unrestricted. Filtering on it therefore selects on a
    reporting habit rather than on economics, and it does so unevenly across houses — for
    Revolut it removed the one family that disagreed and turned a 35% cross-family spread
    into zero. The flag is carried through as a column so the sensitivity can be measured.
    """
    return hold[(hold.FAIR_VALUE_LEVEL == "3")
                & (hold.ASSET_CAT.isin(["EC", "EP"]))
                & (hold.UNIT == "NS")].copy()


def price_per_share(m: pd.DataFrame) -> pd.DataFrame:
    """Attach numeric balance, value and implied price per share; drop unusable rows."""
    m = m.copy()
    m["balance"] = pd.to_numeric(m.BALANCE, errors="coerce")
    m["val_usd"] = pd.to_numeric(m.CURRENCY_VALUE, errors="coerce")
    m = m[m.balance.gt(0) & m.val_usd.gt(0)]
    m["pps"] = m.val_usd / m.balance
    return m


def quarter(q: str) -> pd.DataFrame:
    t0 = time.time()
    with zipfile.ZipFile(io.BytesIO(fetch(q))) as z:
        names = {n.split("/")[-1]: n for n in z.namelist()}
        missing = [t for t in TABLES if t not in names]
        if missing:
            raise RuntimeError(f"{q}: data set is missing {missing}")

        with z.open(names["FUND_REPORTED_HOLDING.tsv"]) as fh:
            hold = pd.read_csv(fh, sep="\t", dtype=str, low_memory=False, usecols=HOLD_COLS)
        priv = select_private(hold)
        del hold

        with z.open(names["SUBMISSION.tsv"]) as fh:
            sub = pd.read_csv(fh, sep="\t", dtype=str,
                              usecols=["ACCESSION_NUMBER", "SUB_TYPE", "REPORT_DATE", "FILING_DATE"])
        with z.open(names["REGISTRANT.tsv"]) as fh:
            reg = pd.read_csv(fh, sep="\t", dtype=str,
                              usecols=["ACCESSION_NUMBER", "CIK", "REGISTRANT_NAME"])
        with z.open(names["FUND_REPORTED_INFO.tsv"]) as fh:
            inf = pd.read_csv(fh, sep="\t", dtype=str,
                              usecols=["ACCESSION_NUMBER", "SERIES_NAME", "SERIES_ID", "NET_ASSETS"])

    m = (priv.merge(sub, on="ACCESSION_NUMBER", how="left")
             .merge(reg, on="ACCESSION_NUMBER", how="left")
             .merge(inf, on="ACCESSION_NUMBER", how="left"))
    m = m[m.SUB_TYPE.isin(["NPORT-P", "NPORT-P/A"])]
    m = price_per_share(m)
    m["src_quarter"] = q

    print(f"  {q}: {len(m):,} private marks · {m.ISSUER_NAME.nunique():,} issuers · "
          f"{m.SERIES_ID.nunique():,} funds · {m.CIK.nunique():,} registrants "
          f"· {time.time() - t0:.0f}s", flush=True)
    return m


def already_have() -> set[str]:
    if not OUT.exists():
        return set()
    try:
        return set(pd.read_csv(OUT, usecols=["src_quarter"], dtype=str).src_quarter.unique())
    except Exception:
        return set()


def main(qs: list[str]) -> None:
    have = already_have()
    if have:
        print(f"resuming; {len(have)} quarter(s) already harvested", flush=True)
    for q in qs:
        if q in have:
            continue
        for attempt in range(3):
            try:
                df = quarter(q)
                # Append per quarter: peak memory is one quarter, and an interrupted run
                # costs one quarter rather than the whole harvest.
                df.to_csv(OUT, mode="a", header=not OUT.exists(), index=False,
                          compression="gzip")
                del df
                break
            except Exception as e:
                print(f"  {q}: attempt {attempt + 1} failed: {str(e)[:90]}", flush=True)
                time.sleep(10)
        else:
            print(f"  {q}: giving up", flush=True)

    if OUT.exists():
        a = pd.read_csv(OUT, dtype=str, low_memory=False)
        print(f"\n{OUT.name}: {len(a):,} marks · {a.src_quarter.nunique()} quarters · "
              f"{a.ISSUER_NAME.nunique():,} issuer strings · {a.REPORT_DATE.nunique()} report dates",
              flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or QUARTERS)
