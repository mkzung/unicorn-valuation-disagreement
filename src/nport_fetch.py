"""
N-PORT fund-mark extractor (BEDROCK / spine leg) — SEC public-domain data.

Pulls the quarterly Level-3 fair-value marks that registered mutual funds disclose
for their PRIVATE unicorn holdings in Form NPORT-P, via EDGAR full-text search.
SEC data is public domain; we respect SEC fair-access (declared User-Agent, <=5 req/s).

Pipeline:
  1. EDGAR full-text search (efts.sec.gov) for each target inside NPORT-P filings.
     The endpoint returns 100 hits/page; `from=N` paginates. (Server-side date
     filtering 500s on this endpoint, so the fetch pages a few times and ranks by file_date.)
  2. For the most recent distinct funds, download the filing's primary_doc.xml and
     STREAM-parse <invstOrSec> entries (iterparse, memory-bounded) whose issuer name
     matches the target (alias-aware: SpaceX files as "SPACE EXPLORATION TECHNOLOGIES").
  3. Keep private equity marks (fairValLevel=3, isRestrictedSec=Y, units=NS, assetCat in
     {EC,EP}); record fund (seriesName), report period (repPdDate), shares (balance),
     fair value (valUSD), pctVal. Implied price/share = valUSD / balance.
  4. Write data/fund_marks.csv -> enables cross-fund dispersion (same company/series,
     multiple funds) and the time path of marks.

Run:  python3 src/nport_fetch.py              # default target list
      python3 src/nport_fetch.py Databricks Stripe
"""
import math
import sys
import time
import csv
import io
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"   # SEC requires a real UA
SEARCH = "https://efts.sec.gov/LATEST/search-index?q=%22{q}%22&forms=NPORT-P&from={frm}"
ARCH = "https://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/primary_doc.xml"
ROOT = Path(__file__).resolve().parents[1]

# Target -> (full-text query string that appears IN filings, regex matching the issuer name).
# The query is what we search EDGAR for; the regex is what we accept inside the XML
# (word-boundaried to avoid false hits like "Ramp" -> "Rampart").
TARGETS = {
    "Databricks":  ("Databricks",                      r"\bdatabricks\b"),
    "Stripe":      ("Stripe",                          r"\bstripe\b"),
    "Anthropic":   ("Anthropic",                       r"\banthropic\b"),
    "OpenAI":      ("OpenAI",                           r"\bopenai\b"),
    "Anduril":     ("Anduril",                          r"\banduril\b"),
    "Ramp":        ("Ramp Business",                    r"\bramp\b"),
    "Epic Games":  ("Epic Games",                       r"\bepic games\b"),
    "Canva":       ("Canva",                            r"\bcanva\b"),
    "SpaceX":      ("Space Exploration Technologies",   r"\bspace exploration\b|\bspacex\b"),
    "Discord":     ("Discord",                          r"\bdiscord\b"),
    "Fanatics":    ("Fanatics",                         r"\bfanatics\b"),
    "Rippling":    ("Rippling",                         r"\brippling\b"),
    # --- v0.8 expansion: broadly fund-held names verified still-private (>=2 sources, 2026-06-27) ---
    "ByteDance":   ("ByteDance",  r"\bbytedance\b"),
    "Plaid":       ("Plaid",      r"\bplaid\b"),
    "Revolut":     ("Revolut",    r"\brevolut\b"),
    "Gusto":       ("Gusto",      r"\bgusto\b|\bzenpayroll\b"),
}

PAGES_PER_CO = 3          # 100 hits/page -> up to 300 candidate filings ranked by date
MAX_FILINGS_TRIED = 18    # cap filing downloads per company (SEC courtesy + runtime)
TARGET_FUNDS = 14         # stop once this many distinct funds have produced a mark
SLEEP = 0.15              # ~6.7 req/s ceiling, polite vs SEC's 10 req/s limit


def _get(url, as_json=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Encoding": "gzip, deflate",
        "Accept": "application/json" if as_json else "*/*"})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            import gzip
            raw = gzip.decompress(raw)
    time.sleep(SLEEP)                       # rate-limit courtesy (real, not dead code)
    return json.loads(raw) if as_json else raw


def search(query):
    """Return candidate NPORT-P filings mentioning `query`, ranked newest-first."""
    seen, hits = set(), []
    for p in range(PAGES_PER_CO):
        try:
            data = _get(SEARCH.format(q=urllib.parse.quote(query), frm=p * 100), as_json=True)
        except Exception as e:
            print(f"    search page {p} failed: {e}")
            break
        page = data.get("hits", {}).get("hits", [])
        if not page:
            break
        for h in page:
            s = h.get("_source", {})
            adsh = s.get("adsh") or h["_id"].split(":")[0]
            if adsh in seen:
                continue
            seen.add(adsh)
            hits.append({
                "cik": (s.get("ciks") or ["0"])[0],
                "adsh": adsh,
                "fund_display": "; ".join(s.get("display_names", [])),
                "file_date": s.get("file_date", ""),
                "period_ending": s.get("period_ending", ""),
            })
        if len(page) < 100:
            break
    hits.sort(key=lambda x: x["file_date"], reverse=True)               # newest first
    return hits


# Header fields (appear before holdings in the doc) and per-holding fields we keep.
HDR = {"repPdDate", "regName", "seriesName", "seriesId", "totAssets"}


def fetch_marks(cik, adsh, label, name_re):
    """Stream-parse one NPORT-P; yield matching private-equity marks."""
    url = ARCH.format(cik=int(cik), adsh=adsh.replace("-", ""))
    raw = _get(url)
    hdr, rows = {}, []
    pat = re.compile(name_re, re.I)
    for _ev, el in ET.iterparse(io.BytesIO(raw), events=("end",)):
        tag = el.tag.split("}")[-1]
        if tag in HDR and tag not in hdr:
            hdr[tag] = (el.text or "").strip()
        elif tag == "invstOrSec":
            d = {c.tag.split("}")[-1]: (c.text or "").strip() for c in el}
            blob = (d.get("name", "") + " " + d.get("title", ""))
            if pat.search(blob):
                rows.append(d)
            el.clear()                                                   # bound memory
    out = []
    for d in rows:
        # Keep only Level-3 private marks (as the module docstring states). This also
        # drops public-company namesakes that the text query collides with — e.g. the
        # Japanese listed company PLAID, Inc. (TSE 4165) held by international small-cap
        # funds at Level 2, vs the US private Plaid fintech we target.
        if d.get("fairValLevel") != "3":
            continue
        try:
            bal = float(d.get("balance") or "nan")
            val = float(d.get("valUSD") or "nan")
        except ValueError:
            bal, val = float("nan"), float("nan")
        pps = val / bal if bal and not math.isnan(bal) and bal != 0 else ""
        out.append({
            "company": label,
            "issuer_name": d.get("name", ""),
            "fund": hdr.get("seriesName") or hdr.get("regName", ""),
            "registrant": hdr.get("regName", ""),
            "series_id": hdr.get("seriesId", ""),
            "cik": int(cik),
            "accession": adsh,
            "report_date": hdr.get("repPdDate", ""),
            "units": d.get("units", ""),
            "balance": d.get("balance", ""),
            "val_usd": d.get("valUSD", ""),
            "price_per_share": f"{pps:.4f}" if pps != "" else "",
            "pct_val": d.get("pctVal", ""),
            "asset_cat": d.get("assetCat", ""),
            "fair_val_level": d.get("fairValLevel", ""),
            "restricted": d.get("isRestrictedSec", ""),
            "cusip": d.get("cusip", ""),
        })
    return out


COLS = ["company", "issuer_name", "fund", "registrant", "series_id", "cik",
        "accession", "report_date", "units", "balance", "val_usd",
        "price_per_share", "pct_val", "asset_cat", "fair_val_level",
        "restricted", "cusip"]


def _pull_company(label):
    """Fetch the newest distinct-fund marks for one company; return list of row dicts."""
    query, name_re = TARGETS.get(label, (label, r"\b" + re.escape(label.lower()) + r"\b"))
    print(f"\n[{label}]  q=\"{query}\"")
    hits = search(query)
    print(f"  {len(hits)} candidate filings; pulling newest distinct funds...")
    rows, funds_with_marks, tried = [], set(), 0
    for h in hits:
        if len(funds_with_marks) >= TARGET_FUNDS or tried >= MAX_FILINGS_TRIED:
            break
        tried += 1
        try:
            marks = fetch_marks(h["cik"], h["adsh"], label, name_re)
        except Exception as e:
            print(f"    skip {h['adsh']}: {e}")
            continue
        if not marks:
            continue
        fund = marks[0]["fund"] or marks[0]["registrant"] or h["adsh"]
        if fund in funds_with_marks:                                     # one filing per fund
            continue
        funds_with_marks.add(fund)
        rows.extend(marks)
        n_eq = sum(1 for m in marks if m["fair_val_level"] == "3")
        print(f"    {h['file_date']}  {marks[0]['report_date']}  {fund[:42]:42} "
              f"{len(marks)} hit(s), {n_eq} L3")
    print(f"  -> {len(funds_with_marks)} funds with marks")
    return rows


def main(labels, out_path=None, append=False):
    """Resumable: writes each company's marks immediately; skips companies already in CSV."""
    out = Path(out_path) if out_path else ROOT / "data" / "fund_marks.csv"
    done = set()
    if out.exists() and append:
        with open(out) as f:
            done = {r["company"] for r in csv.DictReader(f)}
    if not out.exists() or not append:                                   # fresh file w/ header
        with open(out, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=COLS).writeheader()
        done = set()
    for label in labels:
        if label in done:
            print(f"\n[{label}] already in CSV — skip")
            continue
        rows = _pull_company(label)
        if rows:                                                         # append atomically per company
            with open(out, "a", newline="") as f:
                csv.DictWriter(f, fieldnames=COLS).writerows(rows)
            print(f"    appended {len(rows)} rows -> {out.name}")
    with open(out) as f:
        n = sum(1 for _ in f) - 1
    print(f"\nCSV now holds {n} marks -> {out}")


if __name__ == "__main__":
    args = sys.argv[1:]
    append = "--append" in args
    args = [a for a in args if a != "--append"]
    out_path = None
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    main(args or list(TARGETS), out_path=out_path, append=append)
