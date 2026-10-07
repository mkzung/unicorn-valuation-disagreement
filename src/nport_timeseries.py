"""
N-PORT fund-mark TIME SERIES (markup/markdown trajectory) — SEC public-domain data.

The cross-section (src/nport_fetch.py + src/fund_marks.py) shows funds disagree about
the SAME private security at one point in time. This script adds the orthogonal axis:
how a given fund re-marked the SAME private company QUARTER BY QUARTER across the
2019-2026 cycle (the 2021 peak -> 2022-24 reset -> 2025-26 AI rebound).

Method (per "tracer" fund-series, chosen for deep, public N-PORT history):
  1. EDGAR series-level browse (browse-edgar, output=atom) lists every NPORT-P filing
     for that one fund series across its whole history -> (filing_date, accession).
     (Series-level, so we download ONE filing per fund per quarter, not the whole trust.)
  2. Download each filing's primary_doc.xml, stream-parse <invstOrSec>, and for every
     target company held in that filing compute the blended implied price/share,
     Sigma(valUSD)/Sigma(balance), over its Level-3 / restricted / share-denominated
     (units=NS) equity (EC/EP) holdings -- exactly the per-(fund,date) price that
     src/fund_marks.py compares across funds, now tracked over time.
  3. One download yields every target the fund holds that quarter (efficient).

Output: data/fund_marks_timeseries.csv  (company, fund, series_id, cik, accession,
filing_date, report_date, n_sec, tot_balance, tot_val_usd, pps).  Public domain; each
row locates its SEC filing. SpaceX is kept (within-fund path is comparable; the
multi-share-class caveat only bites CROSS-fund per-share comparison, src/fund_marks.py).

Resumable: writes per (company, series) immediately; skips pairs already in the CSV.
Run:  python3 src/nport_timeseries.py                 # all tracers
      python3 src/nport_timeseries.py --append        # resume / extend
      python3 src/nport_timeseries.py --only Baron     # restrict to tracers matching a string
"""
import math
import sys
import re
import io
import csv
import time
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"   # SEC requires a real UA
BROWSE = ("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={bid}"
          "&type=NPORT-P&dateb=&owner=include&count=100&output=atom")
ARCH = "https://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/primary_doc.xml"
ROOT = Path(__file__).resolve().parents[1]
SLEEP = 0.13                                            # polite vs SEC's 10 req/s

# Reuse the cross-section's wrapper guard so an SPV / "economic exposure" line never
# contaminates a fund's direct-holding blended price.
# One definition of "this row is a wrapper, not the issuer's own security", in `fund_marks`.
# This module kept a second and it was four patterns short — no PARTNERS, no ", LLC (", no
# "LP (" — so the two harvests disagreed about which rows are SPV sleeves. It costs nothing
# on the committed panel, where neither pattern drops a row, and that is exactly the state a
# divergence hides in until the panel changes.
import fund_marks as _fm
WRAPPER = _fm.WRAPPER

# Company -> issuer-name regex (word-boundaried; aliases for filing names).
CO_RE = {
    "Databricks": r"\bdatabricks\b",
    "Stripe":     r"\bstripe\b",
    "Anthropic":  r"\banthropic\b",
    "OpenAI":     r"\bopenai\b",
    "Anduril":    r"\banduril\b",
    "Epic Games": r"\bepic games\b",
    "Canva":      r"\bcanva\b",
    "SpaceX":     r"\bspace exploration\b|\bspacex\b",
    "Discord":    r"\bdiscord\b",
}

# Tracer fund-series chosen for deep public N-PORT history. Each: a stable series (or
# the CIK for single-series interval funds like ARK Venture), the trust CIK for the
# Archives URL, a display label, and the target companies it has held.
# browse_id = series id (S0000...) where the trust files many series; else the CIK.
TRACERS = [
    # company-rich interval/closed-end funds (one download -> many names)
    {"browse": "1905088",     "cik": "1905088", "label": "ARK Venture Fund",
     "cos": ["Databricks", "OpenAI", "Epic Games", "Discord"]},
    # Fidelity Contrafund: deepest big-fund history (2019->), Stripe/Discord/SpaceX
    {"browse": "S000006037",  "cik": "24238",   "label": "Fidelity Contrafund",
     "cos": ["Stripe", "Discord", "SpaceX"]},
    # Fidelity Blue Chip Growth: OpenAI/Anthropic/Databricks/SpaceX
    {"browse": "S000007195",  "cik": "754510",  "label": "Fidelity Blue Chip Growth Fund",
     "cos": ["OpenAI", "Anthropic", "Databricks", "SpaceX"]},
    # T. Rowe Price Global Stock: Canva/Databricks/OpenAI/Anduril
    {"browse": "S000001497",  "cik": "313212",  "label": "T. Rowe Price Global Stock Fund",
     "cos": ["Canva", "Databricks", "OpenAI", "Anduril"]},
    # Alger Focus Equity: Anthropic/Databricks (the cross-section's low-mark family)
    {"browse": "S000009201",  "cik": "911415",  "label": "Alger Focus Equity Fund",
     "cos": ["Anthropic", "Databricks"]},
    # SpaceX deep path (2019->) via Baron, the longest-running public window on SpaceX
    {"browse": "S000022521",  "cik": "1217673", "label": "Baron Focused Growth Fund",
     "cos": ["SpaceX"]},
    {"browse": "S000000588",  "cik": "1217673", "label": "Baron Partners Fund",
     "cos": ["SpaceX"]},
    # --- v0.12: cross-FAMILY tracers so the single-fund cycle names (Stripe, Canva,
    # Epic Games) gain a second/third family's mark path -> the Appendix C.1 "re-mark in step"
    # (direction-agreement) claim can be tested across families, not just on Databricks.
    # series_id + trust CIK taken straight from data/fund_marks.csv (no guessing).
    # Franklin Growth Fund (Franklin family): Stripe + Canva — NEW family for both.
    {"browse": "S000006755",  "cik": "38721",   "label": "Franklin Growth Fund",
     "cos": ["Stripe", "Canva"]},
    # New Economy Fund (American Funds / Capital Group): Stripe — NEW family.
    {"browse": "S000009598",  "cik": "719608",  "label": "New Economy Fund",
     "cos": ["Stripe"]},
    # T. Rowe Price Communications & Technology: Canva + Epic Games (cross-family vs ARK on Epic).
    {"browse": "S000002101",  "cik": "910671",  "label": "T. Rowe Price Communications & Technology Fund",
     "cos": ["Canva", "Epic Games"]},
    # T. Rowe Price Global Technology: Epic Games (within-family replication + extra Epic depth).
    {"browse": "S000002085",  "cik": "1116626", "label": "T. Rowe Price Global Technology Fund",
     "cos": ["Epic Games"]},
]

COLS = ["company", "fund", "series_id", "cik", "accession", "filing_date",
        "report_date", "n_sec", "tot_balance", "tot_val_usd", "pps"]


def _get(url, raw=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    with urllib.request.urlopen(req, timeout=45) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
    time.sleep(SLEEP)
    return b if raw else b.decode("utf-8", "replace")


def history(browse_id):
    """Every NPORT-P filing for one series (or interval-fund CIK): [(filing_date, accession)]."""
    x = _get(BROWSE.format(bid=browse_id))
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
        acc = re.search(r"<accession-n[a-z\-]*>([^<]+)<", e)
        fd = re.search(r"<filing-date>([^<]+)<", e)
        if acc and fd:
            out.append((fd.group(1), acc.group(1)))
    return out


def parse_filing(cik, accession, cos):
    """Stream-parse one NPORT-P; return (report_date, {company: blended-mark dict}).
    Blended mark = Sigma(valUSD)/Sigma(balance) over Level-3 restricted NS EC/EP holdings."""
    raw = _get(ARCH.format(cik=int(cik), adsh=accession.replace("-", "")), raw=True)
    pats = {c: re.compile(CO_RE[c], re.I) for c in cos}
    repd = ""
    agg = {c: {"bal": 0.0, "val": 0.0, "n": 0} for c in cos}
    for _, el in ET.iterparse(io.BytesIO(raw), events=("end",)):
        tag = el.tag.split("}")[-1]
        if tag == "repPdDate" and not repd:
            repd = (el.text or "").strip()
        elif tag == "invstOrSec":
            d = {c.tag.split("}")[-1]: (c.text or "").strip() for c in el}
            blob = d.get("name", "") + " " + d.get("title", "")
            # Same holding definition as the cross-section (src/fund_marks.py): directly-held
            # Level-3, share-denominated (units=NS) common/preferred equity. We do NOT filter on
            # isRestrictedSec -- it is filed inconsistently for the same private names (ARK marks
            # them "N", most funds "Y"), so it is not a reliable screen and the cross-section omits it.
            if (d.get("fairValLevel") == "3" and d.get("units") == "NS"
                    and d.get("assetCat") in ("EC", "EP")
                    and not WRAPPER.search(blob)):
                for c, pat in pats.items():
                    if pat.search(blob):
                        try:
                            bal = float(d.get("balance") or "nan")
                            val = float(d.get("valUSD") or "nan")
                        except ValueError:
                            bal = val = float("nan")
                        if not math.isnan(bal) and not math.isnan(val) and bal > 0:
                            agg[c]["bal"] += bal
                            agg[c]["val"] += val
                            agg[c]["n"] += 1
            el.clear()
    marks = {}
    for c, a in agg.items():
        if a["n"] and a["bal"] > 0:
            marks[c] = {"report_date": repd, "n_sec": a["n"],
                        "tot_balance": a["bal"], "tot_val_usd": a["val"],
                        "pps": a["val"] / a["bal"]}
    return repd, marks


def run(only=None, append=False, out_path=None):
    """Resumable at FILING granularity: each filing's marks flush to disk immediately,
    and already-harvested (fund, accession) filings are skipped, so a run interrupted by
    the shell time ceiling resumes exactly where it stopped. `append` is implied whenever
    the CSV already exists; pass it explicitly to be safe."""
    out = Path(out_path) if out_path else ROOT / "data" / "fund_marks_timeseries.csv"
    seen = set()                                          # (fund, accession) already on disk
    if out.exists():
        with open(out) as f:
            seen = {(r["fund"], r["accession"]) for r in csv.DictReader(f)}
    else:
        with open(out, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=COLS).writeheader()

    def flush(rows):
        with open(out, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=COLS).writerows(rows)

    for t in TRACERS:
        if only and only.lower() not in t["label"].lower():
            continue
        print(f"\n[{t['label']}]  series/CIK {t['browse']}  targets={t['cos']}")
        hist = history(t["browse"])
        todo = [(fd, acc) for fd, acc in hist if (t["label"], acc) not in seen]
        print(f"  {len(hist)} NPORT-P filings, {hist[-1][0] if hist else '?'} -> "
              f"{hist[0][0] if hist else '?'}  ({len(todo)} new)")
        got = dict.fromkeys(t["cos"], 0)
        for fd, acc in todo:
            try:
                _repd, marks = parse_filing(t["cik"], acc, t["cos"])
            except Exception as e:
                print(f"    skip {acc}: {e}")
                continue
            rows = [{"company": c, "fund": t["label"], "series_id": t["browse"],
                     "cik": t["cik"], "accession": acc, "filing_date": fd,
                     "report_date": m["report_date"], "n_sec": m["n_sec"],
                     "tot_balance": f"{m['tot_balance']:.4f}",
                     "tot_val_usd": f"{m['tot_val_usd']:.2f}",
                     "pps": f"{m['pps']:.4f}"} for c, m in marks.items()]
            if rows:
                flush(rows)                                            # survive interruption
                for c in marks:
                    got[c] += 1
            seen.add((t["label"], acc))
        for c in t["cos"]:
            print(f"    {c:11} -> +{got[c]} new quarterly marks")
    with open(out) as f:
        n = sum(1 for _ in f) - 1
    print(f"\nCSV now holds {n} time-series marks -> {out}")


if __name__ == "__main__":
    args = sys.argv[1:]
    append = "--append" in args
    only = None
    if "--only" in args:
        only = args[args.index("--only") + 1]
    run(only=only, append=append)
