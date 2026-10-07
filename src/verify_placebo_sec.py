#!/usr/bin/env python3
"""Online re-verification of the Level-1 placebo (Appendix D) against live SEC EDGAR.

The placebo's claim: two mutual funds from DIFFERENT families mark five shared
*public* (Level-1) securities at the identical price per share, on a common report
date — five they both hold, not an exhaustive intersection of the two portfolios — so the
cross-fund dispersion the paper documents for *private*
(Level-3) marks is a property of private-valuation discretion, not of fund
reporting. `data/level1_placebo.csv` records those marks; this script re-pulls the
two source NPORT-P filings from EDGAR and confirms, to the cent, that

  * each filing is the fund the CSV names, for report date 2026-03-31;
  * each of the five shared securities is carried at fairValLevel == 1; and
  * each price/share (valUSD / balance) equals the CSV value, identically across
    the two families (cross-family spread 0.00%).

This is the ONLY check in the repo that touches the network, so it is deliberately
kept OUT of the offline `src/reproduce.py` pipeline and its CI. Run it by hand to
re-audit the placebo against primary sources:

    python3 src/verify_placebo_sec.py            # exits non-zero on any mismatch

EDGAR stores a filing under the *registrant* CIK (not the accession-number's filer
prefix), so the registrant CIK is recorded per row below; SEC fair-access headers
(declared User-Agent, polite spacing) are honored.
"""
from __future__ import annotations

import io
import ssl
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"  # SEC requires a real UA
ARCH = "https://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/primary_doc.xml"

# accession -> registrant CIK under which EDGAR archives the filing (verified via
# EDGAR full-text search 2026-06-28; the accession's 0000035402-/0001099263- filer
# prefix is NOT the archive path CIK).
REGISTRANT_CIK = {
    "0000035402-26-003312": "24238",    # Fidelity Contrafund
    "0001099263-26-006586": "902259",   # T. Rowe Price Blue Chip Growth Fund, Inc.
}


def _ssl_ctx() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:                                  # pragma: no cover
        return ssl.create_default_context()


def _fetch(url: str, ctx: ssl.SSLContext, tries: int = 4) -> bytes:
    last = None
    for k in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
        try:
            with urllib.request.urlopen(req, timeout=70, context=ctx) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                return raw
        except Exception as e:
            last = e
            time.sleep(2 + 2 * k)
    raise RuntimeError(f"fetch failed after {tries} tries: {url} ({last})")


def _marks_by_cusip(raw: bytes, cusips: set[str]) -> tuple[dict, dict]:
    """Return (header, {cusip: (fairValLevel, price_per_share)}) from one NPORT-P."""
    hdr, found = {}, {}
    for _ev, el in ET.iterparse(io.BytesIO(raw), events=("end",)):
        tag = el.tag.split("}")[-1]
        if tag in ("regName", "seriesName", "repPdDate") and tag not in hdr:
            hdr[tag] = (el.text or "").strip()
        elif tag == "invstOrSec":
            d = {c.tag.split("}")[-1]: (c.text or "").strip() for c in el}
            if d.get("cusip") in cusips:
                bal = float(d.get("balance") or "nan")
                val = float(d.get("valUSD") or "nan")
                found[d["cusip"]] = (d.get("fairValLevel", ""), val / bal if bal else float("nan"))
            el.clear()
    return hdr, found


def main() -> int:
    df = pd.read_csv(ROOT / "data" / "level1_placebo.csv")
    cusips = set(df.cusip.astype(str))
    ctx = _ssl_ctx()
    ok = True
    per_security_prices: dict[str, set] = {c: set() for c in cusips}

    for adsh, g in df.groupby("accession"):
        cik = REGISTRANT_CIK.get(adsh)
        fund = g.fund.iloc[0]
        if not cik:
            print(f"  [{fund}] no registrant CIK on file for {adsh} — SKIP")
            ok = False
            continue
        raw = _fetch(ARCH.format(cik=cik, adsh=adsh.replace("-", "")), ctx)
        hdr, found = _marks_by_cusip(raw, cusips)
        date_ok = hdr.get("repPdDate") == g.report_date.iloc[0]
        print(f"[{fund}]  cik={cik}  series={hdr.get('seriesName', '')!r}  "
              f"repPdDate={hdr.get('repPdDate', '')} ({'ok' if date_ok else 'MISMATCH'})")
        ok &= date_ok
        for _, row in g.iterrows():
            cu = str(row.cusip)
            if cu not in found:
                print(f"    {row.security:22s} cusip {cu}  NOT FOUND in filing  ***")
                ok = False
                continue
            lvl, pps = found[cu]
            cell_ok = (lvl == "1") and abs(pps - float(row.price_per_share)) < 0.005
            per_security_prices[cu].add(round(pps, 2))
            print(f"    {row.security:22s} L{lvl} pps={pps:.2f}  (csv {row.price_per_share})  "
                  f"{'OK' if cell_ok else '*** MISMATCH ***'}")
            ok &= cell_ok
        time.sleep(0.5)

    # cross-family identity: each security must have collapsed to a single price
    spreads = {c: (max(v) / min(v) - 1) * 100 for c, v in per_security_prices.items() if v}
    worst = max(spreads.values()) if spreads else 0.0
    print(f"\ncross-family spread across the {len(spreads)} shared public names: "
          f"max {worst:.4f}%  (claim: 0.00%)")
    ok &= worst < 1e-6

    print("\nRESULT:", "PLACEBO VERIFIED vs live SEC ✓" if ok else "FAILED ***")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
