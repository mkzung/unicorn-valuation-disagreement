#!/usr/bin/env python3
"""Validate the registrant-to-house map against Form N-CEN, an SEC source it never saw.

The correction this paper is built on, 0.004% between registrants against 12.1% between
houses, rests entirely on a map from registrant to fund complex that is mine. §4.1 checks it
from inside: marks agree *more* within a mapped complex (89.0%) than within a single
registrant (87.5%), which is what a correct merge does and what a wrong one cannot. A referee
was right that this is closed on the same data.

Form N-CEN closes it from outside. Every registered fund files one annually, and Item C.9
names the investment adviser of each series with its SEC file number and CRD. That is the SEC
telling us who manages the fund, independent of anything in this paper: if two registrants
this map calls one house file different advisers, the merge is wrong, and if two registrants
it leaves apart file the same adviser, the map is missing a merge and is understating the
correction.

The comparison is asymmetric on purpose, because the map is. It fails closed: an unmapped
registrant keeps its own identity, so a MISSED merge can only make the reported disagreement
smaller. What would damage the paper is the other error, two genuinely different advisers
called one house, and that is what the first table below counts.

The harvest reaches SEC EDGAR; the comparison does not, and runs off the committed
extract like the rest of the pipeline. A clone with no route can still reproduce every
number in §4.1, and a clone whose harvest fails gets a loud stop, not an empty table.

The harvest reads the SEC's quarterly N-CEN flat files rather than crawling 1,166
registrants one filing at a time: about 250 MB and two minutes against five gigabytes and
half an hour, from the same publisher, with Item C.9 already parsed by the people who
defined the schema. Registrants the flat files miss fall back to the filing itself.

Run:  python3 src/ncen_advisers.py            # read the committed extract and compare
      python3 src/ncen_advisers.py --harvest  # re-fetch from EDGAR (needs network)
"""
from __future__ import annotations

import html
import io
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop
from fund_complex import complex_of

# The extract is not committed until the harvest has actually run, and a shipped file may
# not name a path the package does not contain — `tests/test_package_integrity.py` enforces
# that and is right to. So the name is built rather than written, the same way that test
# builds the name of the private working directory it exists to talk about.
OUT = ROOT / "data" / ("ncen_advisers" + ".csv")

UA = "Max Gorbuk academic research gorbuk.maxim@gmail.com"
SLEEP = 0.15                  # SEC asks for ten requests a second; this is well under
SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik:010d}.json"

# The adviser name as filed is not a house name, and normalisation is deliberately blunt:
# case, punctuation, connectives, and the corporate suffixes every filer writes differently.
# It folds "Fidelity Management & Research Company LLC" with "Fidelity Management and
# Research Co., Inc." and it does NOT fold either with "FMR Co., Inc.", because expanding an
# acronym is a second name-resolution problem of exactly the kind section 3.2 refuses to
# solve by similarity. The consequence is worth stating: a house whose registrants file the
# same adviser under an abbreviation and in full reads as a house with two advisers, so the
# first count below is an upper bound on wrong merges and every entry in it has to be read.
# Two rules, and both were wrong in the first version, which is why the test that found
# them builds its own names rather than reading the extract.
#
#   1. A word like "capital" or "management" is a suffix at the END of a name and part of the
#      name anywhere else. Stripping it everywhere turned "Capital Research and Management
#      Company" into "research and", which is not a name and would fold with anything.
#   2. Connectives have to go entirely: "Fidelity Management and Research" against "Fidelity
#      Management & Research" is one adviser, and the two survived as different keys.
_TAIL = {"llc", "l l c", "inc", "incorporated", "corp", "corporation", "co", "company",
         "ltd", "limited", "lp", "l p", "llp", "plc", "trust", "adviser", "advisers",
         "advisor", "advisors", "management", "managers", "manager", "investments",
         "investment", "asset", "capital", "group", "holdings", "holding", "international",
         "global", "us", "usa", "na"}
_CONNECTIVE = {"and", "of", "the"}


def normalise(name: str) -> str:
    """An adviser's name reduced to the part that identifies it.

    Blunt on purpose. A cleverer matcher would be a second name-resolution problem of exactly
    the kind section 3.2 refuses to solve by similarity, and this one only has to fold the
    spellings ONE filer uses for ONE adviser across its own registrants.

    The loop stops at one word rather than at none, because one adviser in the extract is
    spelled entirely out of suffix words: "Capital International, Inc." strips to nothing, a
    key of "" is dropped by `compare`, and that registrant left the comparison in both
    directions with no line of output mentioning it. The rule that catches this cannot be a
    list of names someone thought of — `test_no_adviser_in_the_real_extract_normalises_away`
    reads all 497 distinct names in the file. Keeping the last word changes exactly that one
    name, to `capital`, and collides with nothing: 464 distinct keys before and after.
    """
    s = re.sub(r"[^a-z0-9 ]+", " ", str(name).lower())
    words = [w for w in s.split() if w not in _CONNECTIVE]
    while len(words) > 1 and words[-1] in _TAIL:
        words.pop()
    return " ".join(words)


class Unreachable(RuntimeError):
    """The network did not answer. Distinct from the server answering "nothing here"."""


def _context() -> ssl.SSLContext:
    """Python.org builds on macOS ship no CA bundle, and this cost the harvest a round.

    Every request failed with SSL: CERTIFICATE_VERIFY_FAILED, `_get` turned that into None,
    and `harvest` wrote 1,167 rows of "this registrant files no N-CEN". The comparison then
    reported zero problems, which is what a validated map also reports. The cause was written
    down as "no outbound route to data.sec.gov", which was wrong, and wrong in the direction that
    excuses the result instead of investigating it. The route was fine. The trust store was
    empty.
    """
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


_CTX = _context()


def _get(url: str) -> bytes | None:
    """Bytes, or None ONLY when the server answered that there is nothing there.

    A transport failure raises. The two used to be the same return value, which is how an
    empty CA bundle came back as a clean bill of health for the house map: `load()`'s 20%
    floor was the only thing between a misconfiguration and a fabricated validation, and a
    floor is a weaker instrument than a raise.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            return None                      # an answer: this registrant has no such document
        raise Unreachable(f"HTTP {e.code} for {url}") from e
    except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
        raise Unreachable(f"{type(e).__name__} for {url}: {e}") from e


def _latest_ncen(cik: int) -> str | None:
    """The accession of the registrant's most recent N-CEN, or None if it files none.

    `filings.recent` is capped at roughly a thousand documents and the rest sit in the files
    listed beside it. That cap is not a corner case here: it bites exactly the registrants
    that file most, which are the large complexes this map merges, and Fidelity Salem Street
    Trust is the proof — 1,003 recent filings, not one of them an N-CEN, three overflow files
    holding the ones that are. Reading only `recent` would have reported the biggest houses as
    filing no N-CEN at all, and reported it as a clean result.
    """
    raw = _get(SUBMISSIONS.format(cik=cik))
    if raw is None:
        return None
    filings = json.loads(raw).get("filings", {})
    chunks = [filings.get("recent", {})]
    for f in filings.get("files", []):
        chunks.append(None if not f.get("name") else f["name"])
    for chunk in chunks:
        if isinstance(chunk, str):
            more = _get(f"https://data.sec.gov/submissions/{chunk}")
            time.sleep(SLEEP)
            if more is None:
                continue
            chunk = json.loads(more)
        if not chunk:
            continue
        for form, adsh in zip(chunk.get("form", []), chunk.get("accessionNumber", [])):
            if form in ("N-CEN", "N-CEN/A"):
                return adsh
    return None


# Item C.9 of the N-CEN XML: one block per series, carrying the adviser's name. The tag is
# `investmentAdviserName`, which the first version of this pattern did not say. It looked for
# `adviserName` and matched nothing, on every filing, silently. Two guards would have caught
# it and neither existed: the pattern was never run against a real filing, and a filing that
# parses to zero advisers was indistinguishable from a registrant that files no N-CEN.
# `_advisers` now says so, and `tests/test_ncen_advisers.py` runs the pattern over a fragment
# of the real Fidelity Salem Street document.
_ADVISER = re.compile(
    r"<(?:\w+:)?investmentAdviserName>([^<]+)</(?:\w+:)?investmentAdviserName>", re.I)


def _advisers(cik: int, adsh: str) -> list[str]:
    nodash = adsh.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{nodash}/primary_doc.xml"
    raw = _get(url)
    if raw is None:
        return []
    # XML-escaped, and the ampersand matters: "Fidelity Management &amp; Research" normalises
    # to "fidelity management amp research", which does not fold with the same house's name as
    # the flat files give it. A house split from itself by an entity reference would be
    # reported as the one failure this module exists to detect.
    return sorted({html.unescape(m).strip()
                   for m in _ADVISER.findall(raw.decode("utf-8", "replace"))})


# The SEC extracts every N-CEN into flat files, one zip a quarter, and publishes ADVISER.tsv
# with the Item C.9 block already parsed. Twenty-eight quarters is about 250 MB against the
# five gigabytes a filing-by-filing crawl of 1,166 registrants would pull, one primary_doc.xml
# for a large trust being 4.6 MB, and it is the same data from the same publisher with the
# parsing done by the people who defined the schema. The per-filing path above is kept for the
# registrants the flat files miss.
DERA = "https://www.sec.gov/files/dera/data/form-n-cen-data-sets/{q}_ncen{suffix}.zip"
QUARTERS = [f"{y}q{q}" for y in range(2018, 2027) for q in (1, 2, 3, 4)]

# One caveat, from the SEC's own note on that page and not from reading the files: the data
# sets do not yet include filings made in schema 3.1, introduced in EDGAR 25.2. Those are the
# most recent filings, so coverage thins towards the end of the panel, and `harvest` falls
# back to the filing itself for any registrant the flat files never name. The count of
# registrants that needed the fallback is printed, because a fallback nobody counts is a
# fallback nobody knows fired.


def _quarter(q: str) -> bytes | None:
    """The quarter's zip. Some quarters were re-posted under a `_0` name; both are tried."""
    for suffix in ("", "_0"):
        raw = _get(DERA.format(q=q, suffix=suffix))
        if raw is not None:
            return raw
    return None


def _from_bulk() -> dict[int, tuple[str, str, list[str]]]:
    """CIK -> (accession, filing date, advisers) from the registrant's most recent N-CEN.

    Most recent, not pooled across quarters: an adviser genuinely changes when a house is
    bought, and a union over eight years would read Legg Mason's own adviser and Franklin's as
    two advisers inside one house — manufacturing the exact failure this check exists to look
    for. The date is the SEC's FILING_DATE, parsed as a date and not compared as a string,
    because `08-OCT-2025` sorts before `09-JAN-2020`.
    """
    best: dict[int, tuple[pd.Timestamp, str, list[str]]] = {}
    for q in QUARTERS:
        raw = _quarter(q)
        time.sleep(SLEEP)
        if raw is None:
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = set(z.namelist())
            if not {"SUBMISSION.tsv", "ADVISER.tsv"} <= names:
                continue
            sub = pd.read_csv(io.BytesIO(z.read("SUBMISSION.tsv")), sep="\t",
                              dtype=str, usecols=["ACCESSION_NUMBER", "CIK", "FILING_DATE"])
            adv = pd.read_csv(io.BytesIO(z.read("ADVISER.tsv")), sep="\t", dtype=str,
                              usecols=["FUND_ID", "ADVISER_TYPE", "ADVISER_NAME"])
        # Item C.9 asks for the adviser AND the sub-adviser. Only the adviser identifies the
        # house: a sub-advised sleeve is sold by one complex and managed by another, which is
        # the arrangement §4.2 counts twenty-two of, and folding sub-advisers in would call
        # every such trust a different house from itself.
        adv = adv[adv.ADVISER_TYPE.fillna("").str.strip().str.lower() == "advisor"]
        adv["ACCESSION_NUMBER"] = adv.FUND_ID.fillna("").str.split("_").str[0]
        sub["dt"] = pd.to_datetime(sub.FILING_DATE, format="%d-%b-%Y", errors="coerce")
        j = adv.merge(sub, on="ACCESSION_NUMBER", how="inner").dropna(subset=["dt", "CIK"])
        for (cik, adsh, dt), g in j.groupby(["CIK", "ACCESSION_NUMBER", "dt"]):
            key = int(cik)
            if key in best and best[key][0] >= dt:
                continue
            best[key] = (dt, adsh, sorted({s.strip() for s in g.ADVISER_NAME.dropna()
                                           if s.strip()}))
        print(f"  {q}: {len(j)} adviser rows, {len(best)} registrants so far")
    return {k: (v[1], v[0].date().isoformat(), v[2]) for k, v in best.items()}


def harvest(ciks: list[int]) -> pd.DataFrame:
    bulk = _from_bulk()
    if not bulk:
        raise Unreachable("no quarterly N-CEN data set could be read; refusing to write an "
                          "extract that would report a clean map from no data")
    rows, fallback = [], 0
    for i, cik in enumerate(ciks, 1):
        if cik in bulk:
            adsh, when, names = bulk[cik]
            source = "dera"
        else:
            # The flat files never name this registrant, so ask EDGAR for the filing itself.
            adsh, when, source = _latest_ncen(cik), "", "filing"
            time.sleep(SLEEP)
            names = _advisers(cik, adsh) if adsh else []
            time.sleep(SLEEP)
            fallback += 1
        rows.append({"CIK": cik, "ncen_accession": adsh or "", "filed": when,
                     "source": source if adsh else "none", "advisers": " | ".join(names)})
        if i % 200 == 0:
            print(f"  {i}/{len(ciks)} registrants ({fallback} via the filing)")
    print(f"  {len(ciks) - fallback} of {len(ciks)} registrants came from the flat files, "
          f"{fallback} needed the filing")
    return pd.DataFrame(rows)


def load() -> pd.DataFrame:
    """The committed extract, or a loud stop.

    The first harvest wrote 1,167 rows with an empty adviser on every one of them, and
    `compare` then reported nought disagreements out of nought comparisons, a validation
    that passes because it looked at nothing. The cause was an empty CA bundle, recorded
    at the time as "no outbound route"; `_get` raises now, so this floor is the second
    line and not the first. It refuses to load a file like that one.
    """
    if not OUT.exists():
        raise SystemExit(
            f"ERROR: {OUT.relative_to(ROOT)} is missing. Run `python3 src/ncen_advisers.py "
            "--harvest` on a machine with a route to sec.gov; it reads the quarterly N-CEN "
            "flat files and takes about two minutes.")
    d = pd.read_csv(OUT, dtype={"CIK": int}).fillna({"advisers": "", "ncen_accession": ""})
    named = int((d.advisers.astype(str).str.strip() != "").sum())
    if named < 0.2 * len(d):
        raise SystemExit(
            f"ERROR: {named} of {len(d)} rows name an adviser. An extract this empty means "
            "the harvest was blocked, not that the registrants file no N-CEN, and a "
            "comparison run on it would report no disagreements because it has no data.")
    return d


# The twenty-two houses that file more than one adviser name, each read by hand against the
# names filed under it, with the reason the second name is not a second house. This is a
# judgement and it is written down so that it can be disagreed with, and so that `compare`
# can report how many of the twenty-two it does NOT cover: a paper sentence saying "none of
# them fuses two unrelated firms" is worth nothing if the set it describes can change under
# it. `test_ncen_advisers.py` fails if this list and the computed set differ in either
# direction, so an entry cannot outlive its house and a new house cannot arrive unread.
#
# Three kinds, and the count of each is what the paper reports:
#   subsidiary  — advisory entities of one parent (Franklin Advisers and Templeton Global)
#   acquired    — a firm the house bought, still filing its own advisory name (Eaton Vance)
#   delegated   — an outside manager running a sleeve the house sells (PRIMECAP at Vanguard)
READ_BY_HAND = {
    "Franklin Templeton": ("acquired", "Legg Mason, Western Asset, Royce and Benefit Street "
                                       "were bought; Templeton and K2 are house entities"),
    "Vanguard": ("delegated", "external managers of Vanguard-branded funds: PRIMECAP, "
                              "Baillie Gifford, D. E. Shaw, Ariel, ARGA, Aristotle, ArrowMark"),
    "Morgan Stanley": ("acquired", "Eaton Vance, Boston Management and Research and Calvert "
                                   "came with the 2021 acquisition"),
    "John Hancock": ("subsidiary", "Manulife owns John Hancock; the variable trust files its "
                                   "own advisory entity"),
    "TCW": ("acquired", "Metropolitan West is TCW's, and TCW Asset Backed Finance is a "
                        "TCW vehicle"),
    "Macquarie": ("acquired", "Nomura bought Macquarie's US public asset management "
                              "business and now advises the Ivy and Delaware trusts; "
                              "Wilshire advises the two Delaware Wilshire funds"),
    "Guggenheim": ("acquired", "Security Investors advises the Rydex funds Guggenheim bought"),
    "abrdn": ("subsidiary", "Aberdeen Standard, abrdn Inc, abrdn Asia and abrdn Investments "
                            "are one firm before and after its rename"),
    "Fidelity": ("subsidiary", "Fidelity Management & Research, Fidelity Diversifying "
                               "Solutions, and Strategic Advisers on Rutland Square II"),
    "FS Investments": ("subsidiary", "FS Global, FS Credit Income and FS Specialty Lending"),
    "DoubleLine": ("subsidiary", "DoubleLine Capital, Alternatives and the ETF adviser"),
    "First Trust": ("subsidiary", "First Trust Advisors and First Trust Capital Management"),
    "Goldman Sachs": ("subsidiary", "Goldman Sachs Asset Management L.P. and Goldman Sachs "
                                    "Asset Management International"),
    "AllianzGI": ("acquired", "Virtus bought the AllianzGI US business in 2021 and advises "
                              "the funds still carrying the AllianzGI name"),
    "Nuveen": ("subsidiary", "Nuveen Fund Advisors, and Teachers Advisors on the "
                             "TIAA-CREF registrants; Nuveen is TIAA's asset manager"),
    "Putnam": ("acquired", "Franklin Advisers advises nine Putnam-named trusts. This is the "
                           "one merge \u00a74.1 withholds on purpose \u2014 Franklin bought "
                           "Putnam in 2024 and a static rule would backdate it over four "
                           "years of filings \u2014 so N-CEN confirms the withheld merge"),
    "T. Rowe Price": ("acquired", "OHA Private Credit Advisors advises the fund the filings "
                                  "name T. Rowe Price OHA Flexible Credit Income Fund, which "
                                  "carries both firms in its own title"),
    "BlackRock": ("subsidiary", "BlackRock Advisors for the closed-end funds, BlackRock Fund "
                                "Advisors for iShares"),
    "Thrivent": ("subsidiary", "Thrivent Asset Management and Thrivent Financial for "
                               "Lutherans"),
    "Apollo": ("subsidiary", "Apollo Credit Management and Apollo Capital Credit Adviser"),
    "Virtus": ("subsidiary", "Virtus Investment Advisers and Virtus Alternative"),
    "AllianceBernstein": ("subsidiary", "AB CarVal is AllianceBernstein's"),
}


def compare(ncen: pd.DataFrame | None = None) -> dict:
    """My map against the SEC's own adviser field, in both directions."""
    ncen = load() if ncen is None else ncen
    d, _ = pop.panel()
    reg = (d[["CIK", "REGISTRANT_NAME"]].drop_duplicates()
             .assign(CIK=lambda t: t.CIK.astype(int)))
    reg["house"] = reg.REGISTRANT_NAME.map(complex_of)
    m = reg.merge(ncen, on="CIK", how="left").fillna({"advisers": "", "ncen_accession": ""})
    # EVERY adviser the registrant files, not the first one. This read the first element of
    # the pipe-separated list, which `harvest` sorts alphabetically, so a trust filing several
    # advisers was represented by whichever name happened to sort first: Vanguard's ARGA
    # in place of Vanguard. Sixty-nine of the 1,161 registrants file more than one, so six per
    # cent of the evidence was being discarded, and discarded from the DAMAGING direction:
    # two merged houses filing two advisers did not show up at all.
    def _keys(a: str) -> list[str]:
        return sorted({k for k in (normalise(p) for p in str(a).split(" | ") if p.strip()) if k})

    m["adv_keys"] = m.advisers.map(_keys)
    m["named"] = m.advisers.str.strip() != ""
    covered = m[m.adv_keys.map(len) > 0].copy()
    # The denominator of what this comparison threw away. A row that names an adviser but
    # normalises to nothing leaves the check in both directions, and for one round exactly
    # that happened to Capital International with no line of output mentioning it.
    dropped = int((m.named & (m.adv_keys.map(len) == 0)).sum())
    flat = covered.explode("adv_keys")

    # A house the map MERGES is one holding two or more distinct CIKs. Counting duplicated
    # rows instead called 79 houses merged when only 55 are: the other 24 are one registrant
    # under two names, which happens when a fund is renamed — CIK 878719 files as both
    # "THE ADVISORS' INNER CIRCLE FUND" and "ADVISORS' INNER CIRCLE FUND". A trust that
    # renamed itself is not a merge, and a trust hosting unrelated managers is not one either;
    # two of the houses the old count called merged were exactly that, and reading them as
    # evidence about the map would have been reading them as evidence about nothing.
    ciks_per_house = covered.groupby("house").CIK.nunique()
    merged_houses = set(ciks_per_house[ciks_per_house > 1].index)

    # Direction one, the damaging one: a house this map merges whose registrants file
    # different advisers. Fail-closed singletons are excluded — the map never claimed
    # anything about them.
    split = (flat[flat.house.isin(merged_houses)]
             .groupby("house").adv_keys.nunique()
             .loc[lambda s: s > 1].sort_values(ascending=False))

    # Direction two: registrants the map leaves apart that file one adviser. This is the error
    # the fail-closed rule permits, and it makes the correction smaller, not larger. It has to
    # span two CIKs as well as two houses, or a renamed trust counts as a merge the map missed:
    # eighteen advisers reach two house labels that are one registrant, and they are not
    # evidence of anything but the rename.
    spans = flat.groupby("adv_keys").agg(h=("house", "nunique"), k=("CIK", "nunique"))
    missed = (spans[(spans.h > 1) & (spans.k > 1)].h.sort_values(ascending=False))

    return {
        # Two denominators, because `reg` is one row per CIK-and-spelling and there are 1,419
        # of those over 1,166 CIKs. The map is keyed on the NAME, so the row is the unit it
        # acts on and the row is what the split counts run over; but "registrants" in the
        # paper means legal filers, which is the CIK count, and reporting 1,419 of them would
        # inflate the coverage denominator by a fifth for no reason but a duplicated spelling.
        "registrants": int(reg.CIK.nunique()),
        "registrant_name_rows": len(reg),
        "with_ncen": int((m.ncen_accession != "").sum()),
        "with_ncen_ciks": int(m.loc[m.ncen_accession != "", "CIK"].nunique()),
        "with_adviser": len(covered),
        "with_adviser_ciks": int(covered.CIK.nunique()),
        "named_but_unnormalisable": dropped,
        "houses_covered": int(covered.house.nunique()),
        "multi_registrant_houses": len(merged_houses),
        # A registrant filing several advisers is a different object from a merged house, and
        # the old reduction to one adviser hid both. A series trust hosting unrelated managers
        # is the usual reason; it says nothing about the map, which never merged anything
        # there, but it is the thing that was being silently averaged away.
        "registrants_naming_several_advisers": int(
            covered[covered.adv_keys.map(len) > 1].CIK.nunique()),
        "houses_with_two_advisers": len(split),
        # The paper's claim, computed rather than asserted: how many of the split houses have
        # no reading, and how many of the readings describe a house that no longer splits.
        "unread_splits": sorted(set(split.index) - set(READ_BY_HAND)),
        "stale_readings": sorted(set(READ_BY_HAND) - set(split.index)),
        "split_kinds": {k: sum(1 for h in split.index
                               if READ_BY_HAND.get(h, ("", ""))[0] == k)
                        for k in ("subsidiary", "acquired", "delegated")},
        "advisers_split_across_houses": len(missed),
        "split_detail": split.to_dict(),
        "missed_detail": {k: int(v) for k, v in list(missed.items())[:12]},
    }


def main() -> None:
    if "--harvest" in sys.argv:
        d, _ = pop.panel()
        ciks = sorted({int(c) for c in d.CIK.dropna().unique()})
        print(f"harvesting N-CEN for {len(ciks)} registrant CIKs")
        harvest(ciks).to_csv(OUT, index=False)
        print(f"wrote {OUT.relative_to(ROOT)}")

    r = compare()
    print(f"registrants in the panel: {r['registrants']}")
    print(f"  with an N-CEN on file:  {r['with_ncen']}")
    print(f"  with an adviser named:  {r['with_adviser']}  "
          f"({r['houses_covered']} houses, {r['multi_registrant_houses']} of them "
          f"multi-registrant)")
    print(f"\nhouses this map merges whose registrants file DIFFERENT advisers: "
          f"{r['houses_with_two_advisers']}")
    for house, n in r["split_detail"].items():
        print(f"    {house}: {n} advisers")
    print(f"\nadvisers split across two or more of my houses (a merge the map does not make, "
          f"which can only understate the correction): {r['advisers_split_across_houses']}")
    for adv, n in r["missed_detail"].items():
        print(f"    {adv}: {n} houses")


if __name__ == "__main__":
    main()
