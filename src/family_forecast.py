"""NEW RESULT (gaps #2): which mutual-fund FAMILY's pre-IPO N-PORT mark best predicts the
realized IPO price? Harvests every fund's last pre-IPO Level-3 mark for the 7 fund-held
exits, maps registrant -> family, and ranks families by |mark/IPO - 1|.
Network (SEC, public domain). Run:
  SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())") python3 src/family_forecast.py
Writes data/ipo_premarks_byfund.csv and prints the family-accuracy table.
"""
import urllib.request
import urllib.parse
import urllib.error
import ssl
import io
import gzip
import re
import json
import time
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from statistics import median
import certifi

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context(cafile=certifi.where())
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"

# company -> (FTS query, issuer regex, IPO offer price/sh, pre-IPO report-period prefix)
EXITS = {
    "Instacart": ("Maplebear", r"maplebear|instacart", 30.0, "2023-06"),
    "Reddit": ("Reddit", r"\breddit\b", 34.0, "2024-01"),
    "Chime": ("Chime", r"\bchime\b", 27.0, "2025-04"),
    "Figma": ("Figma", r"\bfigma\b", 33.0, "2025-04"),
    "ServiceTitan": ("ServiceTitan", r"servicetitan", 71.0, "2024-09"),
    "Klaviyo": ("Klaviyo", r"\bklaviyo\b", 30.0, "2023-06"),
    "Circle": ("Circle", r"circle internet", 31.0, "2025-04"),
}
FAM = [("fidelity", "Fidelity"), ("rowe", "T. Rowe Price"), ("alger", "Alger"),
       ("clearbridge", "ClearBridge"), ("legg mason", "ClearBridge"),
       ("new economy", "American Funds"), ("europacific", "American Funds"),
       ("american funds", "American Funds"), ("capital world", "American Funds"),
       ("nuveen", "Nuveen"), ("winslow", "Nuveen"), ("blackrock", "BlackRock"),
       ("morgan stanley", "Morgan Stanley"), ("baron", "Baron"), ("franklin", "Franklin"),
       ("jpmorgan", "JPMorgan"), ("j.p. morgan", "JPMorgan"), ("wellington", "Wellington"),
       ("vanguard", "Vanguard"), ("destiny", "Destiny Tech100"), ("principal", "Principal")]


def family(reg):
    r = (reg or "").lower()
    for k, v in FAM:
        if k in r:
            return v
    return (reg or "?")[:22]


def get(u, j=False):
    for a in range(5):
        try:
            rq = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                                    "Accept": "application/json" if j else "*/*"})
            r = urllib.request.urlopen(rq, timeout=60, context=CTX)
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
            time.sleep(0.12)
            return json.loads(b) if j else b
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503) and a < 4:
                time.sleep(2)
                continue
            raise


def marks_for(comp, q, rgx, per, max_pages=25, max_downloads=80):
    """Return [(registrant, pps)] for every fund holding comp at Level 3 in period `per`.

    v2 (2026-07-02): PAGINATES the EDGAR full-text search (the v1 single-page `from=0` was
    the reason Figma/Klaviyo/Circle came back empty — those names are now PUBLIC, so
    thousands of post-IPO NPORT-P filings mention them and the pre-IPO period-matching
    filings sit far beyond the first 100 hits) and dedupes by accession. Downloads only
    period-matching filings, so deep pagination stays cheap."""
    out, seen, downloads = [], set(), 0
    pat = re.compile(rgx, re.I)
    for page in range(max_pages):
        data = get(f"https://efts.sec.gov/LATEST/search-index?q=%22{urllib.parse.quote(q)}%22"
                   f"&forms=NPORT-P&from={page * 100}", j=True)
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break
        for h in hits:
            s = h.get("_source", {})
            if not s.get("period_ending", "").startswith(per) or downloads >= max_downloads:
                continue
            cik = (s.get("ciks") or ["0"])[0]
            adsh = s.get("adsh") or h["_id"].split(":")[0]
            if adsh in seen:
                continue
            seen.add(adsh)
            downloads += 1
            acc = adsh.replace("-", "")
            try:
                b = get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/primary_doc.xml")
            except Exception:
                continue
            reg = ""
            for _, el in ET.iterparse(io.BytesIO(b), events=("end",)):
                t = el.tag.split("}")[-1]
                if t in ("seriesName", "regName") and not reg:
                    reg = (el.text or "").strip()
                if t == "invstOrSec":
                    d = {c.tag.split("}")[-1]: (c.text or "").strip() for c in el}
                    if pat.search(d.get("name", "") + " " + d.get("title", "")) and d.get("fairValLevel") == "3":
                        try:
                            out.append((reg, round(float(d["valUSD"]) / float(d["balance"]), 2)))
                        except (ValueError, ZeroDivisionError, KeyError):
                            pass
                    el.clear()
        if downloads >= max_downloads:
            break
    return out



# Everything below writes `data/ipo_premarks_byfund.csv` and reaches EDGAR to do it, and it
# used to run on import. Importing this module — which anything that walks `src/` does, an
# IDE indexing the package, a doc tool, an audit script enumerating constants — silently
# performed a live harvest and overwrote a committed input to §7. It happened: an audit that
# imported every module rewrote the file, and the fresh harvest disagreed with the committed
# one (eighteen T. Rowe series against twenty-two), so an accidental import moved a number
# the paper prints. A harvested input has to be produced deliberately or not at all.
def main() -> None:
    rows, fam_err = [], {}
    for comp, (q, rgx, ipo, per) in EXITS.items():
        ms = marks_for(comp, q, rgx, per)
        byfam = {}
        for reg, pps in ms:
            byfam.setdefault(family(reg), []).append(pps)
        print(f"\n{comp} (IPO ${ipo}, {per}):")
        for fam, ps in sorted(byfam.items(), key=lambda kv: median(kv[1])):
            m = median(ps)
            err = m / ipo - 1
            print(f"   {fam:18} ${m:>7.2f}  err {err:+6.0%}  (n={len(ps)})")
            rows.append({"company": comp, "family": fam, "mark_pps": m, "ipo_pps": ipo,
                         "err_pct": round(err * 100, 1), "n_funds": len(ps)})
            fam_err.setdefault(fam, []).append(abs(err))

    with open(ROOT / "data" / "ipo_premarks_byfund.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["company", "family", "mark_pps", "ipo_pps", "err_pct", "n_funds"])
        w.writeheader()
        w.writerows(rows)

    print("\n=== FAMILY FORECAST ACCURACY (median |mark/IPO - 1| across exits) ===")
    for fam, es in sorted(fam_err.items(), key=lambda kv: median(kv[1])):
        print(f"   {fam:18} median |err| {median(es):5.0%}   (exits: {len(es)})")
    print(f"\nwrote data/ipo_premarks_byfund.csv ({len(rows)} family-company marks)")



if __name__ == "__main__":
    main()
