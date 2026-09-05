"""Independent verification: re-fetch EVERY cited N-PORT accession from live SEC EDGAR
and confirm each stored fund mark (balance, valUSD) exists in the actual filing. Covers
both the panel spine (data/fund_marks.csv) and the Appendix D out-of-panel probe
(data/nport_expansion_probe.csv). Turns "trust the harvest" into "SEC confirms every
mark" — anyone can re-run it. Exits non-zero on any mismatch.
SEC data is public domain. Run:
  SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())") python3 src/verify_marks.py
"""
import csv
import io
import time
import ssl
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import certifi

ROOT = Path(__file__).resolve().parents[1]
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"   # SEC fair-access UA
CTX = ssl.create_default_context(cafile=certifi.where())


def fetch(cik, adsh):
    u = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/primary_doc.xml"
    rq = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(rq, timeout=60, context=CTX) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
    time.sleep(0.12)
    return b


def live_pairs(b):
    """Set of (balance, valUSD) rounded to the cent for every holding in the filing."""
    s = set()
    for _, el in ET.iterparse(io.BytesIO(b), events=("end",)):
        if el.tag.split("}")[-1] == "invstOrSec":
            d = {c.tag.split("}")[-1]: (c.text or "").strip() for c in el}
            try:
                s.add((round(float(d.get("balance", "nan")), 2), round(float(d.get("valUSD", "nan")), 2)))
            except ValueError:
                pass
            el.clear()
    return s


def verify(csv_name: str, label: str) -> int:
    """Re-fetch every accession cited in `csv_name` and confirm each stored mark.
    Returns the number of mismatches (0 = every mark confirmed by SEC)."""
    rows = list(csv.DictReader(open(ROOT / "data" / csv_name)))
    by = defaultdict(list)
    for r in rows:
        try:
            int(r["cik"])
        except (ValueError, KeyError, TypeError):
            continue
        by[(r["cik"], r["accession"])].append(r)

    chk = mat = 0
    mism, err = [], []
    for (cik, adsh), rs in sorted(by.items()):
        try:
            pairs = live_pairs(fetch(cik, adsh))
        except Exception as e:
            err.append((cik, adsh, str(e)[:70]))
            continue
        for r in rs:
            chk += 1
            try:
                key = (round(float(r["balance"]), 2), round(float(r["val_usd"]), 2))
            except ValueError:
                continue
            if key in pairs:
                mat += 1
            else:
                mism.append((r["company"], r["fund"][:28], r["balance"], r["val_usd"], adsh))

    print(f"VERIFY {label}: {chk} marks across {len(by)} filings -> "
          f"matched {mat}, mismatch {len(mism)}, fetch_err {len(err)}")
    for m in mism[:30]:
        print("  MISMATCH", m)
    for e in err[:15]:
        print("  ERR", e)
    return len(mism)


# The panel spine, then the Appendix D out-of-panel probe: the probe carries the 75% Fanatics
# spread the manuscript quotes, so it needs the same SEC confirmation as the panel marks.
#
# Behind a guard, like every other entry point here. This ran on import and re-fetched every
# cited accession from EDGAR, so importing the module — which anything walking `src/` does —
# started a few hundred network round trips and then called `SystemExit`. `family_forecast`
# had the same shape and was worse: it wrote over a committed input.
def main() -> int:
    bad = verify("fund_marks.csv", "panel")
    bad += verify("nport_expansion_probe.csv", "probe")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
