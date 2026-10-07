"""What the funds paid, and when — from the schedule of investments in N-CSR.

Two rounds of sensor work have now replaced press-sourced quantities with filings: listing
dates from Form 8-A12B, and an attempt at round dates from Form D that failed its own
validation because the largest private rounds are placed under Section 4(a)(2) and leave no
Reg D trace. This module looks one document type sideways, at the funds rather than the
issuers.

Regulation S-X requires the schedule of investments to disclose, for each restricted
security, the date it was acquired and what it cost. N-PORT carries neither — its holdings
table has balance, value, fair-value level and a restricted flag, and stops. The annual and
semi-annual reports carry both, and they carry them for exactly the private positions this
paper is built on.

WHAT THAT BUYS THAT THE PAPER DOES NOT HAVE
Cost divided by shares is an entry price per share, filed by the buyer. Set against the mark
in the same filing it gives a markup over cost; set against another fund's entry it says
whether two houses bought the same thing on the same day. That last one is the sharpest
available form of §4.3's house-policy finding: where two houses entered on the same date at
the same price and now carry different marks, the spread cannot be entry, vintage, share
class or units, because all four are disclosed and identical.

WHAT COST IS NOT
It is the fund's entry, which is a round price only when the entry was a purchase in a round.
ARK's Databricks position cost $400,000 for 27,922 shares — fourteen dollars a share against
a mark of seventy-two — because the position arrived through the MosaicML acquisition in
stock, which the filing says in a footnote. So agreement across independent funds is not a
nicety here, it is the test: a genuine round close shows the same date and the same price in
several filings at once, and an inherited or secondary position does not.

HOW THE COLUMNS ARE FOUND, AND WHY IT IS NOT BY POSITION
The first version of this module read the three numbers after the acquisition date as
shares, cost and value, which is the order Regulation S-X lists them in and the order ARK
uses. Capital Group prints cost, value and percent of net assets, with no share count in the
row at all — it lives in the main schedule, over a position that can span several lots — so
the same code returned Anthropic at $4.18 a share against a mark of zero. The header is now
read and the columns placed by where each label appears in it. One filer calibrated and
generalised is the error, and the fix is three filers with three different layouts.

That difference decides what is computable. A markup, value over cost, needs no share count
and is available on every row. An entry price per share needs one and is available on the
minority of filers who print it beside the cost.

FIVE WAYS THE HARVEST GOES WRONG, ALL SEEN
  the schedule is not in the primary document  ARK puts it in the N-CSR itself; other filers
      attach the annual report as a separate file in the same accession. Reading only the
      primary document silently halves the sample, the same shape of error as reading only
      `filings.recent` and dating DoorDash's listing to 2023.
  the semi-annual report is a different form  N-CSRS, not N-CSR. Searching one form type
      finds one half of the filings.
  the position is held through a vehicle  the shares and cost are then the SPV's, restated
      or not depending on the filer, which is §5's wrapper problem one document over.
  the name is not the company  the same false-match risk every name join in this repository
      carries, and the reason a row is kept only when the security title matches a target
      pattern rather than merely containing a word.
  a registrant is not a house  Alger Funds and Alger Institutional Funds file separately and
      hold one opinion between them; so do New Economy Fund and Capital World Growth &
      Income. Counting registrants as independent views is the error §5 spends a section
      correcting, so the same complex map is applied here.

Run:  python3 src/ncsr_acquisitions.py            # fetch and rebuild the extract
      python3 src/ncsr_acquisitions.py --check    # offline: read the extract and validate
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import sys
import threading
import time
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

import certifi
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import fund_complex as fx

OUT = ROOT / "data" / "ncsr_acquisitions.csv"
UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"     # SEC requires a real UA
CTX = ssl.create_default_context(cafile=certifi.where())
FTS = "https://efts.sec.gov/LATEST/search-index?q={q}&forms={f}&from={frm}"
ARCH = "https://www.sec.gov/Archives/edgar/data/{cik}/{adsh}"

FORMS = ("N-CSR", "N-CSRS")        # annual and semi-annual; both carry the schedule
# The second phrase every query carries. It is the parser's own gate — `MARKER` below — asked
# of the index instead of the document, and it is what let the cap go. Searching the company
# name alone returns 1,491 N-CSRs mentioning Discord, nearly all of them the English word;
# requiring the schedule's column header too leaves 206, and those are the ones a downloader
# would have kept anyway. Both spellings, because the index matches tokens and "dates" is not
# "date": Discord splits 179 to 27 across the two, Anthropic 71 to 15.
#
# A prefilter that is not a superset of the harvest it replaces is a silent sample cut, so
# `validate_prefilter` checks the containment directly against the last extract.
MARKER_PHRASES = ("acquisition date", "acquisition dates")
PAGES = 30                         # 100 hits a page; a stop, not a cap — the largest query
                                   # returns 285. Paging ends when a page comes back short.
MAX_DOC_MB = 40                    # a schedule lives in an HTML document, not a 200 MB one.
                                   # Measured on the wire, so a gzipped document larger than
                                   # this still gets through — which is the intent, since the
                                   # limit exists to bound the download rather than the parse.
WORKERS = 4                        # concurrent document fetches. SEC's published fair-access
                                   # ceiling is ten requests a second and this run sits three
                                   # orders below it; the constraint is courtesy, not rate.
                                   # Single-file, the harvest ran at eight documents a minute
                                   # against 25 MB annual reports, which is a wall-clock
                                   # problem and nothing else.
RETRIES = 4                        # EDGAR returns a 500 under sustained load, and an hour of
                                   # fetches will meet several. Retried with backoff rather
                                   # than skipped: a dropped document is a dropped row, and
                                   # a harvest that silently shrinks under load is one whose
                                   # sample size measures SEC's mood.

# The §4.3 names, with the pattern a row's security title must match. Deliberately the same
# targets `src/nport_fetch.py` uses, so the two sources are asked about the same companies.
TARGETS = {
    "Anthropic":  (r"\banthropic\b",),
    "Databricks": (r"\bdatabricks\b",),
    "Discord":    (r"\bdiscord\b",),
    "Epic Games": (r"\bepic games\b",),
    "OpenAI":     (r"\bopenai\b|\bopen ai\b",),
    "SpaceX":     (r"\bspace exploration\b|\bspacex\b",),
    "Stripe":     (r"\bstripe\b",),
    "Anduril":    (r"\banduril\b",),
    "Canva":      (r"\bcanva\b",),
    "Revolut":    (r"\brevolut\b",),
}

# Numeric first, because that is what every filer in the sample writes, and a month name
# second, because the next one will not. `load` parses whatever this matches with
# format="mixed", so a spelling that reaches the CSV also reaches the lot key.
MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
DATE = re.compile(rf"\d{{1,2}}/\d{{1,2}}/\d{{2,4}}|(?:{MONTHS})[a-z]*\.? ?\d{{1,2}},? ?\d{{4}}", re.I)

# "Series J" and "Class L" are the same thing written twice: Robinhood files "Series L
# Preferred Stock" where Capital Group files "Class L". The letter is what makes a lot a lot,
# and without it a shared acquisition date is necessary but not sufficient — two houses could
# have bought different tranches into one close, and the markup gap would be a class artifact
# rather than a policy difference.
# The same pattern `round_dates` reads, from the module both can import. This copy used to
# be its own and narrower — no SER, no CL, no full stop, one digit — and the two modules
# read the two document types this paper CALIBRATES AGAINST EACH OTHER. It matched every
# N-CSR title identically today, which is the state a divergence hides in.
import population as _pop
# The currency sign is sometimes its own cell and sometimes glued to the number, and the
# percent sign is glued to the last column. A pattern that allows neither drops the
# largest Anthropic lot in the Capital Group filing and keeps the two beside it.
MONEY = re.compile(r"^\$?\(?-?[\d,]+(\.\d+)?\)?\s*%?$")
# "Acquisition <br/>Date" is one label with a line break inside it, so the marker has to
# tolerate markup between the two words. ARK writes it that way and a whitespace-only
# pattern finds nothing in the one filing this module was calibrated against.
MARKER = re.compile(r"acquisition(?:\s|<[^>]*>)+dates?", re.I)

# The columns a schedule of investments can carry beside the acquisition date, and the words
# filers use for them. Order is not assumed: the header is read and the columns are placed by
# where each word appears in it, because the two layouts in front of me disagree.
#   ARK        Acquisition Date · Shares/Principal/Units · Cost · Value
#   Capital    Acquisition date(s) · Cost (000) · Value (000) · Percent of net assets
# The second has no share count in the same row at all — it lives in the main schedule, over
# a position that may span several acquisition lots — so cost per share is simply not
# available there. Cost and value are, and a markup needs no share count.
COLUMN_WORDS = [("acq", r"acquisition\s+dates?"), ("shares", r"shares?\b|units?\b|principal"),
                ("cost", r"cost\b"), ("value", r"value\b"),
                ("pct", r"percent|% of net|percentage")]
THOUSANDS = re.compile(r"\(000")
HEADER_GAP = 35        # characters; labels are adjacent, a security title is not
# Days between two report periods still called near-simultaneous. Filers keep different
# fiscal year-ends, so an exact match is rare: one lot in this harvest has two houses at the
# same period. A month is one step of the reporting grid and is quoted as a widening, never
# as a match.
NEAR_PERIOD = 31


# Ten companies searched against the same filers means the same annual report is fetched ten
# times, and these documents run to tens of megabytes. The cache is keyed on the URL, lives
# outside the repository and is never read by anything that produces a number — it only
# decides whether a byte comes from SEC or from disk.
CACHE = Path(os.environ.get("NCSR_CACHE", "/tmp/ncsr_cache"))


def _get(url: str, as_json: bool = False, max_bytes: int | None = None):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = CACHE / (hashlib.sha1(url.encode()).hexdigest() + (".json" if as_json else ".bin"))
    if key.exists():
        raw = key.read_bytes()
        return json.loads(raw) if as_json else raw
    last = None
    for attempt in range(RETRIES):
        time.sleep(0.15 + attempt * 2)                  # SEC fair access, then backoff
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept-Encoding": "gzip, deflate"})
        try:
            with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
                # Checked before the body is read, not after: the point of a size limit is
                # not to spend the bandwidth. A filer who staples a 200 MB exhibit into the
                # accession should cost one header, not one download.
                size = int(r.headers.get("Content-Length") or 0)
                if max_bytes and size > max_bytes:
                    raise ValueError(f"document is {size / 1e6:.0f} MB")
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
        except ValueError:
            raise
        except Exception as e:
            last = e
            continue
        # Written to a private name and renamed, because four threads share this directory
        # and a reader that opens a half-written file gets a truncated document rather than
        # an error. Rename is atomic within a filesystem.
        tmp = key.with_suffix(f".{os.getpid()}.{threading.get_ident()}.part")
        tmp.write_bytes(raw)
        tmp.replace(key)
        return json.loads(raw) if as_json else raw
    raise last                                                          # type: ignore[misc]


def search(company: str, form: str) -> list[dict]:
    """Every filing of one form type whose schedule of investments names the company.

    Both marker spellings, unioned. The hit is a DOCUMENT, not an accession — `_id` is
    `accession:filename` — and that filename is the document the phrase was found in, which
    is the one worth downloading. Reading it off the index removes the accession listing and
    the two speculative document fetches that used to stand in for it: three requests a
    filing became one, and that, not patience, is what paid for dropping the cap.
    """
    hits, seen = [], set()
    for phrase in MARKER_PHRASES:
        q = urllib.parse.quote(f'"{company}" "{phrase}"')
        for p in range(PAGES):
            try:
                d = _get(FTS.format(q=q, f=form, frm=p * 100), True)
            except Exception as e:
                print(f"    search failed: {e}")
                break
            page = d.get("hits", {}).get("hits", [])
            for h in page:
                s = h.get("_source", {})
                adsh, _, doc = h["_id"].partition(":")
                if (adsh, doc) in seen:
                    continue
                seen.add((adsh, doc))
                hits.append({"cik": (s.get("ciks") or ["0"])[0], "adsh": adsh, "doc": doc,
                             "filer": "; ".join(s.get("display_names", []))[:60],
                             "file_date": s.get("file_date", ""),
                             # The date the marks are AS OF, which is not the date they were
                             # filed. An annual report for a year ended in December and a
                             # semi-annual for the six months ended in April can reach EDGAR
                             # four months apart and value the same position five months
                             # apart.
                             "period": s.get("period_ending", ""), "form": form})
            if len(page) < 100:
                break
    return sorted(hits, key=lambda x: x["file_date"], reverse=True)


def document_url(hit: dict) -> str:
    """The document the index matched, addressed directly.

    The earlier version listed the accession and tried its two largest HTML files, because
    the primary document is often a cover page and the schedule is stapled on as a separate
    exhibit. Both facts are still true; the index just already knows which file it is.
    """
    return ARCH.format(cik=int(hit["cik"]), adsh=hit["adsh"].replace("-", "")) + "/" + hit["doc"]


def strip_tags(html: str) -> str:
    import html as H
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)))


TABLE_OPEN = re.compile(r"<table\b", re.I)
TABLE_CLOSE = re.compile(r"</table\s*>", re.I)


def table_blocks(html: str) -> list[tuple[int, str]]:
    """The document's outermost tables, each one complete.

    Handing pandas a whole annual report and asking for its tables costs tens of seconds a
    document, and at 2,400 documents that is the difference between a harvest that finishes
    and one that does not. Handing it one table at a time costs nothing, but only if the
    slice is a whole table: cutting at the marker is what the earlier version refused to do,
    and it was right to, because the marker sits inside a header cell.

    EDGAR nests tables inside tables for layout, so the closing tag is tracked by depth
    rather than by the next match. A regex pair without the counter closes the outer table at
    the inner one's `</table>` and truncates the schedule at its first row.
    """
    out, i = [], 0
    while (m := TABLE_OPEN.search(html, i)):
        depth, pos, end = 0, m.start(), None
        while True:
            o = TABLE_OPEN.search(html, pos + 1)
            c = TABLE_CLOSE.search(html, pos + 1)
            if not c:                       # unterminated table: nothing further to find
                return out
            if o and o.start() < c.start():
                depth, pos = depth + 1, o.start()
            elif depth:
                depth, pos = depth - 1, c.start()
            else:
                end = c.end()
                break
        out.append((m.start(), html[m.start():end]))
        i = end
    return out


def header_spec(text: str) -> tuple[list[str], bool]:
    """Which column is which, read off the header rather than assumed.

    Returns the column kinds in the order the filer prints them and whether the money columns
    are in thousands. Assuming the order instead is what put Anthropic at $4.18 a share in the
    first version of this module: Capital Group's three numbers are cost, value and percent of
    net assets, not shares, cost and value.
    """
    head = text[:300]
    pos = {}
    for kind, pat in COLUMN_WORDS:
        m = re.search(pat, head, re.I)
        if m:
            pos[kind] = m.start()
    ordered = sorted(pos.items(), key=lambda kv: kv[1])
    # Header labels sit next to each other; the first row of data does not. Capital Group's
    # first security is "Anthropic, PBC, Class G-1, preferred shares", and without this the
    # word "shares" in a company's own security title is read as a fifth column heading and
    # every row is then dropped for having too few numbers.
    kinds = []
    for i, (kind, at) in enumerate(ordered):
        if i and at - ordered[i - 1][1] > HEADER_GAP:
            break
        kinds.append(kind)
    return kinds, bool(THOUSANDS.search(head))


def _num(cell: str) -> float | None:
    c = cell.replace(",", "").replace("$", "").replace("%", "").strip()
    neg = c.startswith("(") and c.endswith(")")
    c = c.strip("()")
    try:
        v = float(c)
    except ValueError:
        return None
    return -v if neg else v


def header_for(block_at: int, block_len: int, marks: list[tuple[int, tuple]]) -> tuple | None:
    """Which of a document's headers governs one table.

    A header inside the table governs that table, because that is where filers put it. A table
    with no header of its own takes the nearest one above it, because Capital Group splits the
    header into a table of its own. Neither is a guess about layout; both are read off the file.

    Applying the file's first "acquisition date" header to every table was the earlier rule, and
    it put Anthropic's Class F lot at minus a hundred percent against four filers who had it at
    +77.991332. Both bugs it caused are written up under "Two parser bugs" in
    `notes/ncsr_acquisition_validation.md`.
    """
    inside = [k for at, k in marks if block_at <= at < block_at + block_len]
    if inside:
        return inside[0]
    above = [k for at, k in marks if at < block_at]
    return above[-1] if above else None


def rows_from(doc: str, patterns: dict[str, str]) -> list[dict]:
    """Schedule rows for the target companies, parsed against the header that governs each."""
    import io
    html = _get(doc, max_bytes=MAX_DOC_MB * 1_000_000).decode("utf-8", "replace")
    marks = [(m.start(), header_spec(strip_tags(html[m.start():m.start() + 6000])))
             for m in MARKER.finditer(html)]
    if not marks:
        return []
    # Whole tables, and only the ones that name a target. Rows without an acquisition date are
    # dropped below, which is what keeps the main schedule's own rows for the same company out.
    any_target = re.compile("|".join(patterns.values()), re.I)
    tables = []
    for at, block in table_blocks(html):
        if not any_target.search(strip_tags(block)):
            continue
        spec = header_for(at, len(block), marks)
        if spec is None:
            continue
        kinds, thousands = spec
        if "acq" not in kinds or "cost" not in kinds or "value" not in kinds:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                parsed = pd.read_html(io.StringIO(block))
            except ValueError:
                continue
        tables += [(t, kinds[kinds.index("acq") + 1:], thousands) for t in parsed]
    out = []
    for t, after, thousands in tables:
        scale = 1000.0 if thousands else 1.0
        for _, r in t.astype(str).iterrows():
            cells = [c.strip() for c in r.tolist() if c and c.lower() != "nan"]
            if not cells:
                continue
            label = cells[0]
            company = next((c for c, pat in patterns.items()
                            if re.search(pat, label, re.I)), None)
            if company is None:
                continue
            dated = [c for c in cells if DATE.search(c)]
            nums = [_num(c) for c in cells if not DATE.search(c) and MONEY.match(c)]
            nums = [v for v in nums if v is not None]
            if not dated or len(nums) < len(after):
                continue
            got = dict(zip(after, nums[:len(after)]))
            cost = got.get("cost", 0.0) * scale
            value = got.get("value", 0.0) * scale
            if cost <= 0 or value < 0:
                continue
            dates = DATE.findall(dated[0])
            row = {"company": company, "security": label[:70],
                   "acquired": dates[0], "acquired_last": dates[-1],
                   "lots_spanned": len(dates), "cost": cost, "value": value,
                   "markup_pct": (value / cost - 1) * 100,
                   "shares": got.get("shares"), "in_thousands": thousands, "doc": doc}
            row["cost_per_share"] = (cost / row["shares"]
                                     if row.get("shares") else None)
            row["mark_per_share"] = (value / row["shares"]
                                     if row.get("shares") else None)
            out.append(row)
    return out


def _one(company: str, pat: str, form: str, h: dict) -> list[dict]:
    doc = document_url(h)
    got = rows_from(doc, {company: pat})
    for g in got:
        g.update(filer=h["filer"], cik=h["cik"], adsh=h["adsh"],
                 form=form, file_date=h["file_date"], period=h["period"])
    return got


def fetch() -> pd.DataFrame:
    from concurrent.futures import ThreadPoolExecutor

    rows, skipped = [], 0
    for company, (pat,) in TARGETS.items():
        for form in FORMS:
            hits = search(company, form)
            print(f"  {company:12} {form:7} {len(hits):4} documents", flush=True)
            with ThreadPoolExecutor(max_workers=WORKERS) as pool:
                futures = {pool.submit(_one, company, pat, form, h): h for h in hits}
                for f, h in futures.items():
                    try:
                        rows += f.result()
                    except Exception as e:
                        skipped += 1
                        print(f"    {h['doc']}: {type(e).__name__} {e}")
    # Reported, not swallowed. A harvest that loses documents to transport errors and says
    # nothing has a sample size set by the network, and the count is the only way to tell
    # that from a sample size set by the filings.
    print(f"  documents that could not be read: {skipped}")
    # One filer can match a company in two documents of one accession — the annual report and
    # the N-CSR wrapper that repeats it. The row is the same row twice.
    key = ["company", "security", "acquired", "cost", "value", "adsh"]
    d = pd.DataFrame(rows).drop_duplicates(subset=key, ignore_index=True)
    # Sorted because the pool returns in completion order, and a file whose row order depends
    # on which download finished first is a file that changes when the network does.
    return d.sort_values(key, kind="mergesort", ignore_index=True)


def validate_prefilter(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Does the phrase prefilter still contain every filing the harvest actually used?

    The check that makes `MARKER_PHRASES` an optimisation rather than a sample cut. It asks
    EDGAR for the prefiltered accession set and looks for the accessions in the committed
    extract that are not in it. Anything missing is a document whose header the index and the
    parser read differently, and the phrase list has to grow to cover it.
    """
    d = pd.read_csv(OUT) if d is None else d
    out = []
    for company in sorted(d.company.unique()):
        found = set()
        for form in FORMS:
            found |= {h["adsh"] for h in search(company, form)}
        used = set(d.loc[d.company == company, "adsh"])
        out.append({"company": company, "prefiltered": len(found), "used": len(used),
                    "missed": len(used - found), "which": ",".join(sorted(used - found))})
    return pd.DataFrame(out)


def load() -> pd.DataFrame:
    d = pd.read_csv(OUT)
    # Two-digit years are half the file — "12/17/24" beside "12/17/2024" for the same lot
    # at two filers — and the default parser returns NaT for them without saying so. That
    # dropped sixteen of thirty-six rows out of the agreement table, including every row
    # that made a lot cross-filer, which is the one thing the table exists to show.
    d["acq"] = pd.to_datetime(d.acquired, errors="coerce", format="mixed")
    d["per"] = pd.to_datetime(d.period, errors="coerce")
    assert d.acq.notna().all(), f"unparsed dates: {sorted(set(d.acquired[d.acq.isna()]))}"
    # A filer is a registrant and a house files under several. Alger Funds and Alger
    # Institutional Funds are one house; so are New Economy Fund and Capital World Growth &
    # Income. Counting registrants as independent opinions is the error §5 spends a section
    # correcting, and it would be the same error here.
    d["house"] = fx.add_complex(d.rename(columns={"filer": "REGISTRANT_NAME"}))
    d["series"] = _pop.extract_series(d.security)
    # The same wrapper rule §4.3 applies to the marks, applied here to the security title.
    # A position held through an SPV reports the vehicle's cost and the vehicle's value, so
    # its markup is the vehicle's markup. Reported rather than dropped, because for a
    # cost-to-value ratio the vehicle may be the right unit — but the two modules have to
    # answer "who is the holder" the same way, and that is what this column makes checkable.
    import fund_marks as fm
    d["wrapper"] = d.security.str.contains(fm.WRAPPER, regex=True, na=False)
    return d


def coverage(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """What the harvest can and cannot answer, before anything is asked of it.

    The share column is the one that decides. ARK reports shares beside cost, so an entry
    price per share exists; Capital Group and Destiny report the restricted lot as cost and
    value only, with the share count living in the main schedule over a position that may
    span several lots. A markup needs no share count and is available on every row; an entry
    price needs one and is available on a minority.
    """
    d = load() if d is None else d
    has_shares = d.shares.notna()
    rows = [("schedule rows", len(d)),
            ("companies", d.company.nunique()),
            ("filers", d.cik.nunique()),
            ("rows carrying a share count", int(has_shares.sum())),
            ("rows with an entry price per share", int((d.cost_per_share.notna()).sum())),
            ("rows whose lot spans several dates", int((d.lots_spanned > 1).sum())),
            ("rows naming a series or class", int(d.series.notna().sum())),
            ("rows held through a vehicle (§4.3's wrapper rule)", int(d.wrapper.sum())),
            ("filings reported in thousands", int(d[d.in_thousands].adsh.nunique()))]
    t = pd.DataFrame(rows, columns=["fact", "n"])
    t["share_pct"] = (t.n / max(len(d), 1) * 100).round(1)
    return t


def agreement(d: pd.DataFrame | None = None, tol: int = 0) -> pd.DataFrame:
    """Do independent houses carry one lot differently AT THE SAME VALUATION DATE?

    The unit is (company, acquisition date, period), not (company, acquisition date). A
    markup is value over cost as of the report period the filing covers, so two houses
    reporting one lot from an annual report for a December year-end and a semi-annual for an
    April half-year are answering at two different dates. The previous version of this
    function keyed on the acquisition date alone and filtered on how far apart the filings
    were *filed*, which is not the same thing: a December annual and an April semi-annual
    reach EDGAR 119 days apart and value the position five months apart.

    What that error cost is on the record. Three cross-house markup gaps of 8 to 12 points
    were published from this module; every one of them was a house's own revaluation between
    periods. Alger carries Databricks Series J at +105.4% as of 31 December 2025 and +85.9%
    as of 30 April 2026 — 19.5 points, from one house, on one lot.

    THE SERIES IS PART OF THE KEY, NOT A COLUMN BESIDE IT
    It was a column beside it until the harvest grew, and at forty filings the difference did
    not show. At four hundred it does: Canva's 4 November 2021 date carries Series A, A-3 and
    A-4 at six houses, and pooling them produced a 462-point "gap" between two different
    securities. Two houses can buy different tranches into one close at different prices, so
    a shared acquisition date is necessary and not sufficient. Rows with no letter at all are
    kept as their own group rather than pooled with the lettered ones, because an unlabelled
    row is unknown, not equal.

    `tol` widens the match to periods within that many days, for the near-simultaneous
    comparison the exact match is too strict to make at this sample size.
    """
    d = load() if d is None else d
    d = d.dropna(subset=["acq", "per"])
    d = d.assign(_ser=d.series.fillna(""))
    rows = []
    for (co, acq, ser), g in d.groupby(["company", "acq", "_ser"]):
        for per, gp in g.groupby("per"):
            near = g[(g.per - per).abs() <= pd.Timedelta(days=tol)] if tol else gp
            # Per BOOK, not per house label: seven sub-advised sleeves of one manager are one
            # opinion, and taking the range over house labels reports the sleeve structure.
            hm = books_of(near)
            rows.append({"company": co, "acquired": acq.date().isoformat(),
                         "period": per.date().isoformat(),
                         "houses": near.house.nunique(), "registrants": near.cik.nunique(),
                         "rows": len(near), "series": ser, "one_series": bool(ser),
                         "books": shared_books(near),
                         "period_span_days": int((near.per.max() - near.per.min()).days),
                         "wrappers": int(near.wrapper.sum()),
                         "markup_lo": float(hm.min()), "markup_hi": float(hm.max()),
                         "markup_gap_pts": float(hm.max() - hm.min()) if len(hm) > 1 else None})
    t = pd.DataFrame(rows).drop_duplicates(subset=["company", "acquired", "series", "period"])
    return t.sort_values(["houses", "company", "period"],
                         ascending=[False, True, True]).reset_index(drop=True)


def shared_books(g: pd.DataFrame) -> int:
    """How many INDEPENDENT books are behind a group of rows, as against how many house labels.

    Start from houses, and join two houses when they file a cost and a value that agree to the
    dollar. Books are the connected components of that. Cost is a fact about one purchase by
    one buyer, so when it repeats across sponsors the second row is a sub-advised sleeve of the
    first rather than a second opinion.

    Starting from rows instead of houses over-counts in the other direction: two funds of one
    house holding different amounts have different costs, and would read as two books. A house
    is the floor of independence in this repository, and the merge can only go up from there.

    The Canva lot that forced both halves of that rule — seven sponsors at one cost, and the
    same seven at a second cost — is under "House labels are not books" in
    `notes/ncsr_acquisition_validation.md`. §5's panel has a milder version of the same problem
    and `population.duplicate_books` measures it there.
    """
    return len(set(map(frozenset, _books(g).values())))


def _books(g: pd.DataFrame) -> dict:
    """House -> the set of houses it shares a book with. One copy, two callers.

    Two houses are joined when they file a cost and a value agreeing to the dollar, and a book
    is a connected component of that relation. `shared_books` counts the components and
    `books_of` groups by them; the loop was written out twice, identically, which is one
    definition of "independent book" with two places to change it.
    """
    comp = {h: {h} for h in g.house.unique()}
    for _, x in g.groupby(["cost", "value"]):
        hs = set(x.house)
        if len(hs) < 2:
            continue
        merged = set().union(*(comp[h] for h in hs))
        for h in merged:
            comp[h] = merged
    return comp


def books_of(g: pd.DataFrame) -> pd.Series:
    """Median markup per independent book, for the gap `agreement` reports."""
    comp = _books(g)
    key = g.house.map(lambda h: "|".join(sorted(comp[h])))
    return g.groupby(key).markup_pct.median()


def series_j(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """The Databricks Series J rows, with the ratio the entry-price argument rests on.

    Kept as a function rather than as a paragraph because the argument is arithmetic: four
    filers, four cost bases, one value-over-cost ratio at 31 December 2025, and two of the four
    disclosing the share count that turns that ratio into $92.50 in and $190.00 out.
    `notes/ncsr_acquisition_validation.md` carries the reading, including the version of it that
    rested on the zero at the start and was wrong.
    """
    d = load() if d is None else d
    j = d[(d.company == "Databricks") & (d.series == "J")].copy()
    j["ratio"] = j.value / j.cost
    j["entry_pps"] = j.cost / j.shares
    j["mark_pps"] = j.value / j.shares
    cols = ["filer", "house", "acquired", "period", "cost", "value", "ratio",
            "shares", "entry_pps", "mark_pps"]
    return j.loc[j.period.isin(["2024-12-31", "2025-06-30", "2025-12-31"]), cols] \
            .sort_values(["period", "cost"]).round(6).reset_index(drop=True)


def house_drift(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """One house, one lot, across periods — the quantity the old key was measuring by mistake.

    It is worth reporting in its own right. §4.2 says that within a house the mark is one
    number, and this second source says so to four decimal places across registrants; what it
    adds is that the statement holds AT A DATE. Between report dates the same house moves the
    same lot by nine to twenty points.
    """
    d = load() if d is None else d
    d = d.dropna(subset=["acq", "per"])
    rows = []
    for (co, acq, house), g in d.groupby(["company", "acq", "house"]):
        pm = g.groupby("per").markup_pct.median()
        if len(pm) < 2:
            continue
        rows.append({"company": co, "acquired": acq.date().isoformat(), "house": house,
                     "periods": len(pm), "first": pm.index.min().date().isoformat(),
                     "last": pm.index.max().date().isoformat(),
                     "markup_first": float(pm.iloc[0]), "markup_last": float(pm.iloc[-1]),
                     "drift_pts": float(pm.max() - pm.min())})
    return pd.DataFrame(rows).sort_values("drift_pts", ascending=False).reset_index(drop=True)


def within_house(d: pd.DataFrame | None = None, single_lot: bool = True) -> pd.DataFrame:
    """One house, one lot, one period, several registrants — §4.2 in a second source.

    Single-lot rows only, and that restriction is the difference between a counterexample and
    an artifact. A row whose `lots_spanned` is two carries a blended cost over two purchases,
    and two funds of one house that bought different amounts on each date have different
    blends — so their markups differ by construction, the same way a price per share is
    incomparable without a share basis. Capital Group's Stripe Class B row, acquired over 6
    May 2021 and 24 August 2023, is the case: it produced a 13.8-point within-house spread
    that reads like a policy difference and is arithmetic. On single-lot rows the largest
    within-house spread in this harvest is 1.2 points and the median is four ten-thousandths;
    the same filer's single-lot Series BB-1 row at one period reads 192.4876% against
    192.4992%. Pass `single_lot=False` to see the blended rows and what they do.
    """
    d = load() if d is None else d
    d = d.dropna(subset=["acq", "per"])
    if single_lot:
        d = d[d.lots_spanned == 1]
    rows = []
    for (co, acq, house, per), g in d.groupby(["company", "acq", "house", "per"]):
        if g.cik.nunique() < 2:
            continue
        rows.append({"company": co, "acquired": acq.date().isoformat(),
                     "period": per.date().isoformat(), "house": house,
                     "registrants": g.cik.nunique(),
                     "spread_pts": float(g.markup_pct.max() - g.markup_pct.min())})
    return pd.DataFrame(rows).sort_values("spread_pts", ascending=False).reset_index(drop=True)


def nport_markup(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Markup over a disclosed entry price, at the report dates §5 already fixes.

    The reviewer's route out of the fiscal-year trap, and it works because cost does not move.
    An entry price is a fact about a purchase; only the mark is a fact about a date. So the
    cost comes from N-CSR — any period, wherever the filer prints a share count beside it —
    and the mark comes from N-PORT on a common report date, where the discipline of holding
    the date fixed is already implemented in §5. No coincidence of fiscal year is required.

    What that yields and what it does not is worth being exact about. It yields a LEVEL the
    paper cannot compute today: how far above its own disclosed entry a house carries a
    position, quarter by quarter. It does not yield a new cross-house test, and the reason is
    algebra rather than coverage — if two houses bought the same lot at one price, dividing
    both marks by that price leaves their ratio unchanged, so the markup GAP between houses at
    a fixed date is exactly the mark spread §5 already reports. Cost adds the level, not the
    dispersion.

    Coverage is the binding constraint and it is arithmetic: 26 usable cost rows over two
    houses, of which one, ARK, files N-PORT at all.
    """
    import reconcile_versions as rv
    import population as pop
    d = load() if d is None else d
    cost = d[(d.cost_per_share > 0) & (d.lots_spanned == 1) & (~d.wrapper)]
    if cost.empty:
        return pd.DataFrame()
    _, keymap = rv.joint_resolution()
    marks = pop.comparable(pop.load_marks())
    rows = []
    for (co, house), g in cost.groupby(["company", "house"]):
        key = keymap.get(co)
        if key is None:
            continue
        m = marks[(marks.company == key) & (marks.house == house)]
        if m.empty:
            continue
        entry = float(g.cost_per_share.median())
        for dt, gm in m.groupby("dt"):
            pps = float(gm.pps.median())
            rows.append({"company": co, "house": house, "report_date": dt.date().isoformat(),
                         "entry_pps": entry, "mark_pps": pps,
                         "markup_pct": (pps / entry - 1) * 100,
                         "lots": len(g), "funds": int(gm.fund.nunique())})
    t = pd.DataFrame(rows).sort_values(["company", "report_date"]).reset_index(drop=True)
    if t.empty:
        return t
    # A share basis that changes mid-series makes the level unreadable, and the series says
    # so itself: ARK's SpaceX mark steps from $185 to $1,017 between two report dates and
    # Discord's from $289 to $26. Neither is a revaluation. The test is the same 4x ratio
    # §5 uses on class artifacts, applied between consecutive marks of one house on one
    # company, and a company carrying one anywhere is flagged throughout rather than in the
    # quarter it happens — the entry price is on one side of the break and the marks are on
    # both.
    step = t.groupby(["company", "house"]).mark_pps.apply(
        lambda x: (x / x.shift()).dropna())
    broken = {co for (co, _), r in step.groupby(level=[0, 1]) if (r.max() > 4 or r.min() < 0.25)}
    t["basis_break"] = t.company.isin(broken)
    return t


def markup(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Value over cost, per lot — §4.3's question with the entry disclosed.

    Two filers holding the same company from the same date at the same cost and carrying
    different values is a statement about house policy that nothing else in this paper can
    make, because entry, vintage, class and units are all on the page and all equal.
    """
    d = load() if d is None else d
    return d[["company", "acquired", "filer", "cost", "value", "markup_pct",
              "cost_per_share", "form", "adsh"]].sort_values(["company", "acquired"])


def main() -> None:
    if "--check" not in sys.argv:
        d = fetch()
        if d.empty:
            raise SystemExit("nothing parsed — the schedule layout or the search has changed")
        d.to_csv(OUT, index=False)
        print(f"\n{len(d)} schedule rows -> {OUT.relative_to(ROOT)}")
    d = load()
    print("\ncoverage")
    print(coverage(d).to_string(index=False))

    a = agreement(d)
    labels, books = a[a.houses > 1], a[a.books > 1]
    print(f"\n{len(a)} lot-period-series. Two or more house LABELS at the same valuation date: "
          f"{len(labels)}; two or more independent BOOKS: {len(books)}. The difference is "
          f"sub-advised sleeves — seven insurance trusts filing one manager's cost to the "
          f"dollar are one opinion, and `shared_books` merges them.")
    tight = int((books.markup_gap_pts <= 0.01).sum())
    print(f"  {tight} of {len(books)} agree to within a hundredth of a point; median gap "
          f"{books.markup_gap_pts.median():.4f}, largest {books.markup_gap_pts.max():.2f}")
    print(books.sort_values("markup_gap_pts", ascending=False).head(8)[
        ["company", "acquired", "period", "series", "houses", "books",
         "markup_lo", "markup_hi", "markup_gap_pts"]].round(4).to_string(index=False))

    # The one comparison in this repository where nothing is left to explain a gap. What
    # establishes the common entry price is the year end, not the zero at the start: a fresh
    # position marked at what it cost prints 0.0000 whatever it cost, so that row is consistent
    # with any pair of entry prices. Four different bases printing one ratio is not.
    print("\nDatabricks Series J: four cost bases, one ratio at the year end")
    print(series_j(d).to_string(index=False))
    print("  76/37 = 2.0540540540... Three of the four are that exactly; the fourth rounds its "
          "filed value to the dollar.")
    print("  Both Brighthouse rows print a share count, and both give $92.50 in and $190.00 out "
          "— so the ratio is a disclosed price pair rather than an inferred one, and the two "
          "Alger rows reproduce it on bases ten and thirteen times larger.")
    print("  Trust II acquired on 21 January 2025 at the same $92.50, so December and January "
          "are two closings of one round at one price.")
    print("  Against that entry, the 30 June marks imply $119.19 a share at Alger and $108.18 at "
          "Brighthouse. One entry, one date, eleven dollars apart — and the same number to nine "
          "decimals in December. A basis difference cannot open and then close.")

    near = agreement(d, tol=NEAR_PERIOD)
    nm = near[near.books > 1]
    print(f"\nwidened to periods within {NEAR_PERIOD} days: {len(nm)} lot-period-series")
    print(nm[["company", "acquired", "period", "series", "books", "markup_gap_pts",
              "period_span_days"]].head(12).round(3).to_string(index=False))

    hd = house_drift(d)
    print(f"\none house, one lot, between periods: {len(hd)} series, "
          f"median drift {hd.drift_pts.median():.1f} points, largest {hd.drift_pts.max():.0f}")
    print(hd.head(6).round(1).to_string(index=False))

    wh = within_house(d)
    wb = within_house(d, single_lot=False)
    print(f"\none house, one lot, ONE period, several registrants: {len(wh)} single-lot cases, "
          f"largest spread {wh.spread_pts.max():.2f} points, median "
          f"{wh.spread_pts.median():.4f}")
    print(f"  including blended rows the largest becomes {wb.spread_pts.max():.1f} points, "
          f"which is the blend and not a house")
    print(wh.head(4).round(4).to_string(index=False))

    nm = nport_markup(d)
    if not nm.empty:
        ok = nm[~nm.basis_break]
        print(f"\nmarkup over a disclosed entry, at N-PORT report dates: {len(nm)} rows, "
              f"{nm.company.nunique()} companies, {nm.house.nunique()} house(s)")
        print(f"  {len(ok)} rows on {ok.company.nunique()} companies survive the share-basis "
              f"check; {sorted(set(nm[nm.basis_break].company))} are flagged and dropped")
        print(ok.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
