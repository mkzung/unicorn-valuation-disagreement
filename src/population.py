"""Cross-fund disagreement over the whole Level-3 population, not ten chosen names.

The first version reported a median cross-family spread across ten companies chosen before
the data were seen. The population answers a different question, and answers it between
fund HOUSES rather than between the legal trusts a filing names. The claim worth making
turns out not to be that funds disagree but that disagreement is a stable property of
particular companies.

No result figure appears anywhere in this file. Every number the paper quotes from here is
recomputed and pinned in `src/paper_numbers.py`, which is the only place a reader should
have to trust; a docstring restating a result goes stale in silence, because no guard reads
one. `tests/test_docstrings_carry_no_results.py` keeps it that way.

Definitions, all computed from `data/nport_population_marks.csv.gz`:
  cell           a company on one report date with >=5 funds across >=2 fund COMPLEXES
  family mark    the median price per share among one complex's funds
  complex        the fund house, not the legal trust. A house files under dozens of
                 registrant CIKs, and trusts inside one house share a valuation committee,
                 so counting registrants as families both lowers the independence bar and
                 inflates measured agreement (`src/fund_complex.py`)
  spread         max/min family mark - 1, so a house filing many funds cannot inflate it
  guard          cells whose extreme family marks differ by more than 4x are flagged and
                 excluded from every reported figure, the same rule the first version used;
                 they stay in the written file, so a median over the raw rows will differ

Three kinds of row are excluded from price comparison, all for the same reason: the price
they carry is not the company's price per share. Feeder vehicles quote a price per unit in
the feeder. Russian issuers sit at Level 3 by sanction rather than by being venture backed;
every other domicile stays. Contingent value rights, escrow lines, subscription rights,
warrants and lock-up dummies are claims on or against a company rather than shares in it,
and an issuer identifier joins them to the company's stock because the identifier names the
issuer while the price names the security (`is_claim`).

Run:  python3 src/population.py
"""
from __future__ import annotations

import re
import string
import sys
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, mannwhitneyu, spearmanr, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import entity_resolution as er
import fund_complex as fx

MARKS = ROOT / "data" / "nport_population_marks.csv.gz"
CELLS = ROOT / "data" / "population_cells.csv"
MIN_FUNDS, MIN_FAMS, CLASS_GUARD = 5, 2, 4.0
REMARK_TOL = 0.005                       # a mark "moved" when it changed by over 0.5%
SEED, DRAWS = 20260624, 200


def fund_key(d: pd.DataFrame) -> pd.Series:
    """Identify the fund, not the fund complex.

    A registrant CIK can host thirty series, so the registrant is the family and the
    series is the fund. Closed-end and interval funds file with no series identifier at
    all — a quarter of the rows here — so counting distinct SERIES_ID silently drops them
    and pushes real company-dates below the five-fund bar. Fall back to the registrant
    and series name, and to the registrant alone when the filing carries neither.
    """
    sid = d.SERIES_ID.fillna("").str.strip()
    name = d.SERIES_NAME.fillna("").str.strip()
    cik = d.CIK.fillna("").str.strip()
    # The separator has to be a character a filer cannot type into a series name. A pipe
    # is not: the full harvest contains one, and the assertion below caught it the first
    # time the unfiltered data ran through. ASCII unit separator cannot appear in the text.
    SEP = "\x1f"
    assert not name.str.contains(SEP, regex=False).any(), "series name contains the separator"
    fallback = np.where(name != "", cik + SEP + name, cik)
    return pd.Series(np.where(sid != "", sid, fallback), index=d.index)


def load_marks() -> pd.DataFrame:
    if not MARKS.exists():
        raise SystemExit(
            f"{MARKS.relative_to(ROOT)} is missing. It ships with the repository; if you "
            "have deleted it, rebuild with `python3 src/nport_bulk.py` (downloads about "
            "11 GB from SEC and takes roughly an hour).")
    d = pd.read_csv(MARKS, dtype=str, low_memory=False)
    d["pps"] = pd.to_numeric(d.pps, errors="coerce")
    d["val_usd"] = pd.to_numeric(d.val_usd, errors="coerce")
    d = d[d.pps.gt(0) & d.val_usd.gt(0)].copy()
    d["company"], d["label"], d["is_wrapper"] = er.resolve(d)
    d["house"] = fx.add_complex(d)
    d["fund"] = fund_key(d)
    d["dt"] = pd.to_datetime(d.REPORT_DATE, format="%d-%b-%Y", errors="coerce")
    return d


# Matched against the filing's security title and issuer name together, because filers put
# the instrument in either field. Word boundaries matter: ESC is an escrow line and ESCO is
# a company, RTS is a rights line and PARTS is not.
CLAIM_PATTERNS = {
    "cvr": r"\bCVR\b|CONTINGENT VALUE|CONTINGENT PAYMENT",
    "escrow": r"\bESCROW\b|\bESC\b|\bHOLDBACK\b",
    "right": r"\bRTS\b|\bRIGHTS?\b",
    "warrant": r"\bWARRANTS?\b|\bWTS\b|-?\bCW\d{2}\b",
    "lockup": r"LOCK ?-?UP",
    # Shares a merger releases only if a price target is met, a trust holding a lawsuit's
    # proceeds, and the placeholder line a filer books against a spin-off before the stock
    # exists. None is a share in a company, and all three joined the panel on the issuer's
    # identifier exactly as the CVRs did.
    "earnout": r"EARN ?-?OUT",
    "litigation": r"LITIGATION (?:TRUST|RECEIVABLE)",
    # Words that describe the BOOK ENTRY rather than the security. This is a different
    # category from the instruments above and a closed one: a filer writes DUMMY or
    # PLACEHOLDER when the position needs a line before the paper it stands for exists.
    # "ESCROW DUMMY" was caught two rounds ago and "FORESIGHT ENERGY LLC DUMMY EQUITY",
    # priced at $1.47 against $7.93 for the same company's real equity, was not, because
    # the pattern needed the word ESCROW beside it.
    "dummy": r"\bDUMMY\b|PLACEHOLDER",
    # A liquidating trust is a claim on what is left after a company is wound up, and the
    # panel had CMS Liquidating Trust fused with the common stock of Center for Medical
    # Science on the issuer name — a claim and a share under one key, which is the join
    # failure this filter exists for, one level below entity resolution.
    "liquidating": r"LIQUIDATING TRUST",
    # A SAFE is a promise of future equity with no share count, so a price per share
    # computed from it is a price per nothing.
    "safe": r"\bSAFE\b",
    # A contra position is the offsetting entry a corporate action leaves behind, and it is
    # a CVR by another name: the clusters carrying one are Abiomed, Albireo, 89bio, Poseida,
    # Verve — companies acquired with contingent consideration. The filer simply wrote
    # CONTRA instead of CVR, which is why the first version of this list missed them. Most
    # matched strings lead with the token; the rest carry it inside a filer's own note, as
    # in "BM TECHNOLOGIES CONTRA (CUSTOMERS BANCORP SPIN OFF IN LOCK UP PERIOD)", which is
    # why the pattern is a word boundary rather than an anchor.
    "contra": r"\bCONTRA\b",
}

# Tokens too short or too common to match on their own, so they are matched only where the
# same string also carries an expiry. That is the structural tell: an instrument that runs
# out has a date on it and a share in a company does not. The list is what
# `expiring_survivors()` turned up after the patterns above had been applied — RT and WT in
# the singular, single-name call options, RHTS, and the contingent payment right a filer
# abbreviates CPR. Matching them unconditionally would take Proterra's Series 5 preferred
# with them, whose title happens to carry the expiry of a physical certificate.
EXPIRING_PATTERNS = {
    "rt": r"\bRT\b", "wt": r"\bWT\b", "option": r"\bCALLS?\b|\bPUTS?\b",
    "rhts": r"\bRHTS\b", "cpr": r"\bCPR\b",
}
EXPIRY = r"\bEXP\b|EXPIR|\d{1,2}/\d{1,2}/\d{2,4}|\b\d{1,2}/\d{2}\b|\b\d{6}\b"

# What survives with an explicit expiry word on it, each read and kept deliberately. Pinned
# so that a re-harvest bringing a new spelling of a claim breaks the build instead of
# quietly widening the panel — which is how CVR, then escrow, then contra, then this round's
# warrants each got in. `tests/test_population.py` asserts the set.
EXPIRING_SURVIVORS = {
    'GRAF GLOBAL CORP UNIT EXP 053132 | GRAF GLOBAL CORP',
    'MAPLETREE COMMERICAL TRUST EXP 07NOV19 | MAPLETREE COMMERICAL TRUST EXP 07NOV19',
    'PROTERRA INC PFD USD SERIES 5 *PHYS CERTS 144A EXP 09/16/17* | PROTERRA INC PFD USD SERIES 5 *PHYS CERTS 144A EXP 09/16/17*',
    'SICHUAN EXP-H | SICHUAN EXPRESSWAY CO LTD',
    'STICHTING ADMKANRISTRET CI EXP | STICHTING ADMKANRISTRET CI EXP',
    'TC12K8DB1 | FRAMEEBRIDGE EXP FUND PAYMT PP',
}


def is_claim(d: pd.DataFrame) -> pd.Series:
    """Rows whose security is a claim on a company rather than a share in it.

    Entity resolution joins on the issuer's CUSIP or LEI, and both name the issuer, not the
    security. A contingent value right issued when a company was acquired, the escrow line
    left behind by a merger, a subscription right, a warrant and a lock-up dummy therefore
    land on the same company key as the stock — and their prices per unit have nothing to do
    with each other. Left in, they do to a cell exactly what fusing two companies would do,
    one level down: the reported quantity stops being two houses' opinion of one security.

    Read off the filings rather than imagined. The strings the regexes match include escrow
    lines a filer labels a dummy, rights lines carrying the issuer's own name with an RTS
    suffix, and put rights over shares still inside a listing lock-up.
    """
    txt = _title(d)
    hit = _any(txt, CLAIM_PATTERNS)
    short = _any(txt, EXPIRING_PATTERNS)
    return hit | (short & txt.str.contains(EXPIRY, regex=True, na=False))


def _any(txt: pd.Series, patterns: dict[str, str]) -> pd.Series:
    """True where a title matches any pattern — and False everywhere if there are none.

    `"|".join({}.values())` is the empty string, and `str.contains("")` is True for every row,
    so an empty pattern dictionary silently reclassifies the whole panel as claim instruments.
    Nothing empties these dictionaries in normal use; `correction_cost` does, to measure what
    one of them is worth, and it got the sign of its own answer backwards before this existed.
    """
    if not patterns:
        return pd.Series(False, index=txt.index)
    return txt.str.contains("|".join(patterns.values()), regex=True, na=False)


def _title(d: pd.DataFrame) -> pd.Series:
    return (d.ISSUER_TITLE.astype(str).str.upper() + " | "
            + d.ISSUER_NAME.astype(str).str.upper())


# Rows a filer left without an issuer name. The resolver clusters on what it is given, so
# they arrive as one company holding Allstar Coinvest, Chennai Super Kings Cricket and
# Lithium Technologies at once — a fusion of unrelated issuers rather than a company, and
# the one cluster in the panel that is an artifact of the *absence* of a name.
UNRESOLVED = "NM:UNKNOWN"


def price_outliers(d: pd.DataFrame, c: pd.DataFrame, floor: float = 0.05) -> pd.DataFrame:
    """Rows priced at a fraction of their own cell, under a title nobody else in it uses.

    The detector that does not need to know how an instrument is spelled. Every leak this
    filter has sprung — contingent value rights, escrow lines, contra positions, singular
    warrants, and now book-entry dummies — announced itself the same way: a price two orders
    of magnitude away from what the rest of the cell paid for the same issuer, carrying a
    title of its own. So the artifact is defined by what it does to the price rather than by
    the word the filer chose, which is the only version of this test that a sixth spelling
    cannot get past.

    It is a detector and not a filter, and the distinction is the whole safety of it. This
    paper measures disagreement; a rule that quietly dropped low marks would delete its own
    subject. What survives is listed, small, and decided one row at a time — `PRICE_OUTLIERS`
    records which are instruments and which are marks that houses really filed.
    """
    g = c[c.guarded]
    keys = set(zip(g.company, g.dt))
    x = d[[k in keys for k in zip(d.company, d.dt)]].copy()
    x["ti"] = x.ISSUER_TITLE.astype(str).str.upper().str.strip()
    out = []
    for (co, dt), grp in x.groupby(["company", "dt"]):
        med, modal = grp.pps.median(), grp.ti.mode().iloc[0]
        low = grp[(grp.pps <= floor * med) & (grp.ti != modal)]
        for _, r in low.iterrows():
            out.append({"company": co, "dt": dt, "title": r.ti, "modal": modal,
                        "pps": float(r.pps), "cell_median": float(med)})
    return pd.DataFrame(out, columns=["company", "dt", "title", "modal", "pps", "cell_median"])


# What the price detector leaves, each read against the filing and kept deliberately: six
# titles on five issuers, twelve rows in all. FOUR are a different security of the same
# issuer that the word list does not reach, and TWO are marks a house really filed. This
# comment had those two counts the other way round while the set below was right, which is
# the shape of comment that outlives the code it describes; `test_the_price_detector_..._
# split` now counts the set instead of trusting the sentence.
OTHER_SECURITY = {
    # A different security under the same issuer: preferred against common, and two
    # participating classes against the convertible the rest of the cell holds.
    ("NM:TRAVELPORT", "TRAVELPORT PREF EQ LX224848"),
    ("ROW:33117", "MAGIC LEAP INC PC SER B PP"),
    ("ROW:33117", "MAGIC LEAP INC PC SER C PP"),
    ("NM:EXIDE OLD", "EXIDE TECHNOLOGIES (PAR SHARE)"),
}
MARKS_THAT_STAND = {
    # Marks that stand. Epic Games at $1.00 against a $600 consensus is First Trust's filed
    # number, discussed in 5.12 and kept for the same reason the guard reports what it drops:
    # removing a mark because it is far from the others would delete the finding.
    ("NM:EPIC GAMES", "EPIC GAMES, INC."),
    ("NM:NOBLE 144A", "NOBLE GROUP LTD."),
}
# Splitting the two groups apart is the point: as one set with the split written only in a
# comment, nothing could disagree with the comment, and the comment was wrong.
PRICE_OUTLIERS = OTHER_SECURITY | MARKS_THAT_STAND


def expiring_survivors(d: pd.DataFrame) -> set[str]:
    """Rows that survive the claim filter while still carrying an expiry word.

    The detector that closed this round's leak, kept as a standing one. A spelling list is
    only ever as complete as the strings its author has read, and this asks the filings
    instead: anything left in the panel with EXP or EXPIR on it is either a claim the list
    still misses or a false positive worth naming. It returned ten strings when it was first
    run and four of them were instruments.
    """
    t = _title(d[~is_claim(d)])
    return set(t[t.str.contains(r"\bEXP\b|EXPIR", regex=True, na=False)])


def comparable(d: pd.DataFrame) -> pd.DataFrame:
    """Rows eligible for cross-family price comparison.

    Feeder vehicles are out because a price per unit in a feeder is not the company's
    price per share. Russian issuers are out because they sit at Level 3 for a reason that
    has nothing to do with venture valuation — sanctions closed the market that priced
    them — and their marks move with the freeze rather than with the company. Every other
    domicile stays: the private companies registered funds hold include British and
    Australian names, and dropping them would narrow the population by nationality rather
    than by anything economic. Claim instruments are out for the reason `is_claim` gives.

    Dropping feeders also drops their value from the NAV total, which understates exposure.
    The size of that understatement was measured rather than left as a worry: feeders hold
    well under a tenth of one percent of the booked value, so the choice costs nothing worth
    recovering.
    """
    return d[~d.is_wrapper & (d.INVESTMENT_COUNTRY != "RU") & ~is_claim(d)
             & (d.company != UNRESOLVED)]


def cells(d: pd.DataFrame, family: str = "house") -> pd.DataFrame:
    """Company-dates broad enough to measure disagreement on.

    `family` selects the unit two of which a cell must span. The default is the fund
    complex. Passing "CIK" reproduces the registrant-level panel the first version of this
    section reported; that version is quoted in the manuscript as the conservative bound,
    because splitting one house into thirty trusts can only make funds look more agreeable.
    """
    x = comparable(d)
    fam = x.groupby(["company", "dt", family]).pps.median().reset_index()
    agg = (fam.groupby(["company", "dt"])
              .agg(n_fams=(family, "nunique"), lo=("pps", "min"), hi=("pps", "max")).reset_index())
    breadth = (x.groupby(["company", "dt"])
                 .agg(n_funds=("fund", "nunique"), nav=("val_usd", "sum")).reset_index())
    c = agg.merge(breadth, on=["company", "dt"])
    c = c[(c.n_funds >= MIN_FUNDS) & (c.n_fams >= MIN_FAMS)].copy()
    c["spread_pct"] = (c.hi / c.lo - 1) * 100
    c["guarded"] = c.hi / c.lo <= CLASS_GUARD
    return c.sort_values(["company", "dt"]).reset_index(drop=True)


IDENTICAL, ONE_BP = 1e-9, 0.01
# Squared-log variance below this is floating-point noise, not disagreement (see house_policy).
VAR_FLOOR = 1e-12


def same_number(a, b):
    """Do two computed spreads state the same number, allowing for how they were computed?

    Nothing in this file may ask whether two floats are equal. Spreads arrive through
    `hi/lo - 1` and then a median, and that path leaves the last bits at the mercy of
    accumulation order: six of the paired comparisons in `staleness` sit at |difference|
    around 1e-14 and changed side between pandas 2.2.3 and 2.3.3, moving an integer count
    the manuscript printed. It is the third time this class has cost something — a variance
    tested against zero moved a count by 40, a knife-edge `tot > 0` moved another — so the
    rule is now a named function rather than a constant patched in at each site, and
    `tests/test_population.py` fails if any comparison lands in the band where the answer
    would depend on the release of a dependency.

    The tolerance is `IDENTICAL`, the same figure §5 already uses for "the same mark to the
    last digit", so this introduces no new threshold. It is absolute rather than relative
    because spreads are percentage points on one scale while the residue sits at the same
    order whatever the level: a relative rule of the same nominal size works out, at the
    spreads this panel carries, to within a small factor of the narrowest genuine difference
    in it — a tolerance that would swallow real data to save typing.

    How much room the absolute rule leaves is measured rather than asserted.
    `staleness` returns `narrowest_untied_gap`, the registry pins it, and
    `tests/test_population.py` fails if it ever approaches the tolerance.
    """
    return np.abs(np.asarray(a, float) - np.asarray(b, float)) <= IDENTICAL


# The panel cached on disk between processes, outside the repository so it never ships. Keyed on
# the source file's size and modification time, so a rebuilt `nport_population_marks.csv.gz`
# invalidates it rather than being silently ignored — a stale cache here would be a wrong number
# in every figure at once, which is worse than the minute it saves.
PANEL_CACHE = Path(os.environ.get("UVD_CACHE", ROOT / "_work" / "panel_cache"))


def _cache_key() -> str:
    st = MARKS.stat()
    return f"{int(st.st_mtime)}-{st.st_size}"


@lru_cache(maxsize=1)
def panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    """The marks and the cell table, built once per process and once per machine.

    Loading is not cheap — a gzipped file of a few hundred thousand rows, plus an
    entity-resolution pass over every issuer string — and several callers need the same two
    frames (this module, the figure, and the number registry the tests run). Without the
    in-process cache the registry alone rebuilt the panel four times.

    The disk half was added after a reader reported the registry and the event study running out
    of memory in one process on his machine: both hold the panel, and each stage rebuilding it
    from the gzip is what makes holding two copies expensive. Parquet is read back memory-mapped
    and the resolution pass does not run again.

    It is a cache and not an artifact. `_cache_key` is the source file's mtime and size, a miss
    rebuilds from source, and nothing in `data/` or the reported numbers depends on it existing.
    """
    key = _cache_key()
    m_path = PANEL_CACHE / f"marks-{key}.parquet"
    c_path = PANEL_CACHE / f"cells-{key}.parquet"
    if m_path.exists() and c_path.exists():
        try:
            return pd.read_parquet(m_path), pd.read_parquet(c_path)
        except Exception:
            pass          # a corrupt or half-written cache rebuilds rather than raising
    d = load_marks()
    c = cells(d)
    try:
        PANEL_CACHE.mkdir(parents=True, exist_ok=True)
        d.to_parquet(m_path, index=False)
        c.to_parquet(c_path, index=False)
    except Exception:
        pass          # no parquet engine, or a read-only checkout: the cache is optional
    return d, c


def correction_cost(d: pd.DataFrame | None = None) -> dict:
    """What §3.2's two newest corrections cost the panel, measured rather than remembered.

    The section used to say they cost twenty cells and moved the median by less than two
    tenths of a point. That was true of the panel it was written against and stopped being
    true twice since, silently, because the sentence was prose and nothing recomputed it.

    The two are the DUMMY/PLACEHOLDER class — a filer needs a line in the book before the
    paper it stands for exists — and the expiry test, which needs no vocabulary: an
    instrument that runs out carries a date and a share in a company does not.

    Switching them off means switching off module state, which is ugly, so it is done here
    once and restored, and the swap asserts that it changed something. A check that cannot fail is the
    mistake this repository has already made.
    """
    d = load_marks() if d is None else d
    base = cells(d)
    keep_pat, keep_exp = dict(CLAIM_PATTERNS), dict(EXPIRING_PATTERNS)
    before = int(is_claim(d).sum())
    globals()["CLAIM_PATTERNS"] = {k: v for k, v in keep_pat.items() if k != "dummy"}
    globals()["EXPIRING_PATTERNS"] = {}
    try:
        after = int(is_claim(d).sum())
        assert after < before, "the switch does nothing; the check is vacuous"
        loose = cells(d)
    finally:
        globals()["CLAIM_PATTERNS"] = keep_pat
        globals()["EXPIRING_PATTERNS"] = keep_exp
    g, gl = base[base.guarded], loose[loose.guarded]
    return {"rows_removed": before - after,
            "cells": len(g) - len(gl),
            "median_pts": float(g.spread_pct.median() - gl.spread_pct.median())}


def duplicate_books(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """One holding reported twice under two house labels.

    WHAT MAKES THIS DIFFERENT FROM AGREEMENT
    Two houses printing the same price per share is the paper's subject, not its problem —
    it is what anchoring to a round price looks like, and §5 measures how often it happens.
    Two houses printing the same price per share AND the same number of shares is something
    else. A share count is a fact about one portfolio. When it repeats, the second row is not
    a second opinion about the company; it is the first row seen through another registrant,
    which is what a sub-advised sleeve or an unmapped affiliate produces.

    WHY IT MATTERS AND WHY IT DOES NOT
    The panel's guard asks for five funds across two houses, and a cell whose second house is
    a copy of the first does not have two independent valuations behind it. So the count is a
    ceiling on how much of §5 could rest on duplicated evidence — and it is small: the number
    is in the registry, and the cells it touches are a low single-digit share of the guarded
    panel. It also earns its keep in the other direction, as a detector: five of the pairs it
    surfaced were registrants of one house that `fund_complex` had not merged, and those are
    now merged.

    Not every pair is an error. A sub-advised sleeve is legally a separate house that has
    bought its opinion from someone else, and merging those is a modelling choice with
    consequences for a dependent variable, so this reports rather than merges.
    """
    d = load_marks() if d is None else d
    m = comparable(d)
    m = m.assign(balance=pd.to_numeric(m.balance, errors="coerce"),
                 val_usd=pd.to_numeric(m.val_usd, errors="coerce"))
    m = m[(m.balance > 0) & (m.val_usd > 0)]
    g = (m.groupby(["company", "dt", "balance", "val_usd"])
           .agg(houses=("house", "nunique"), funds=("fund", "nunique"),
                who=("house", lambda s: " | ".join(sorted(set(s))))).reset_index())
    return g[g.houses > 1].sort_values(["company", "dt"], ignore_index=True)


def duplicate_book_summary() -> dict:
    d, c = panel()
    dup = duplicate_books(d)
    hit = set(zip(dup.company, dup.dt))
    g = c[c.guarded]
    touched = g[[(a, b) in hit for a, b in zip(g.company, g.dt)]]
    clean = g[[(a, b) not in hit for a, b in zip(g.company, g.dt)]]
    return {"duplicated_holdings": len(dup),
            "company_dates": int(dup.groupby(["company", "dt"]).ngroups),
            "guarded_cells_touched": len(touched),
            "guarded_cells_touched_pct": float(len(touched) / max(len(g), 1) * 100),
            # The robustness number: drop every cell a duplicated book touches and see
            # whether the headline moves. If it does, the headline was resting on copies.
            "median_spread_all": float(g.spread_pct.median()),
            "median_spread_clean": float(clean.spread_pct.median())}


def concentration(c: pd.DataFrame) -> dict:
    """The median alone would mislead in either direction, so the summary carries the shares
    that fix the shape of the distribution instead of one midpoint. Grouped by registrant the
    median rounds to zero and reads as "every fund agrees", which is what counting one house
    as thirty trusts does to a summary statistic; grouped by house it does not.

    `identical` uses a tolerance rather than equality because a family median over an even
    number of funds averages two marks, which can differ from a bitwise-equal comparison in
    the last place even when every filing states the same price.
    """
    g = c[c.guarded]
    hi = g[g.spread_pct > 24]
    return {
        "cells": len(g), "companies": g.company.nunique(),
        "median": float(g.spread_pct.median()),
        "identical_pct": float((g.spread_pct <= IDENTICAL).mean() * 100),
        "within_1bp_pct": float((g.spread_pct <= ONE_BP).mean() * 100),
        "p75": float(np.percentile(g.spread_pct, 75)),
        "p90": float(np.percentile(g.spread_pct, 90)),
        "share_above_24": float((g.spread_pct > 24).mean() * 100),
        "nav_busd": float(g.nav.sum() / 1e9),
        "nav_disagreeing_busd": float(hi.nav.sum() / 1e9),
        "nav_disagreeing_share": float(hi.nav.sum() / g.nav.sum() * 100),
    }


# Read off the paper's own thresholds, not chosen to look tidy: 0 is the unanimous mark, 24
# is the first version's headline median, 100 is a doubling. Buckets are LEFT-closed,
# [lo, hi) — stated because the manuscript table, the figure and the number registry each
# bucketed independently at first, and seven cells sitting exactly at 50% came out in
# different rows depending on which convention a caller happened to use.
BUCKET_EDGES = [0.0, 1e-9, 10.0, 24.0, 50.0, 100.0, np.inf]
BUCKET_LABELS = ["identical", "0-10%", "10-24%", "24-50%", "50-100%", ">100%"]


def spread_buckets(g: pd.DataFrame) -> pd.DataFrame:
    """The manuscript's Table 11, computed once so every consumer sees the same rows."""
    idx = np.digitize(g.spread_pct.to_numpy(), BUCKET_EDGES[1:-1], right=False)
    nav = g.nav.to_numpy()
    return pd.DataFrame([{
        "bucket": lab,
        "cells": int((idx == i).sum()),
        "cells_pct": float((idx == i).mean() * 100),
        "nav_busd": float(nav[idx == i].sum() / 1e9),
        "nav_pct": float(nav[idx == i].sum() / nav.sum() * 100),
    } for i, lab in enumerate(BUCKET_LABELS)])


def persistence(c: pd.DataFrame) -> dict:
    """Is disagreement a company characteristic or a quarter effect? Three readings:
    the between-company share of variance against a relabelling null, the company's own
    lag-1 autocorrelation, and that autocorrelation restricted to quarters in which the
    mark actually moved, so a stale mark cannot manufacture the persistence.

    The movement test watches the cell's highest family mark. That is a conservative
    proxy rather than a complete one: it registers when the top-marking house repriced and
    misses a quarter in which only a lower house moved. Tightening it to a per-family
    remark test would shrink the qualifying set, not the conclusion, since the restricted
    correlation already sits close to the unrestricted one."""
    g = c[c.guarded].dropna(subset=["dt"]).copy()
    rep = g.groupby("company").filter(lambda s: len(s) >= 4)
    if rep.empty:
        return {}
    rep = rep.assign(y=np.log1p(rep.spread_pct.clip(lower=0)))

    grand = rep.y.var(ddof=0)
    between = rep.groupby("company").y.transform("mean").var(ddof=0) / grand

    rng = np.random.default_rng(SEED)
    null = []
    for _ in range(DRAWS):
        sh = rep.assign(company=rep.groupby("dt").company.transform(
            lambda s: rng.permutation(s.values)))
        null.append(sh.groupby("company").y.transform("mean").var(ddof=0) / sh.y.var(ddof=0))

    pairs, moved = [], []
    for _, s in rep.groupby("company"):
        v, hi = s.spread_pct.values, s.hi.values
        for i in range(len(v) - 1):
            pairs.append((v[i], v[i + 1]))
            if abs(hi[i + 1] / hi[i] - 1) > REMARK_TOL:
                moved.append((v[i], v[i + 1]))

    def rho(p):
        a = np.array([q[0] for q in p]); b = np.array([q[1] for q in p])
        r, pv = spearmanr(a, b)
        return float(r), float(pv), len(p)

    r_all, p_all, n_all = rho(pairs)
    r_mv, p_mv, n_mv = rho(moved)
    med = rep.groupby("company").spread_pct.median()
    quiet, loud = med[med <= 0.5].index, med[med > 24].index
    # Two-sided on purpose. There is no prior about which way position size should cut,
    # and a one-sided test pointed the wrong way returns p=1 and settles nothing.
    nav_p, nav_ratio = float("nan"), float("nan")
    if len(quiet) and len(loud):
        ln = rep[rep.company.isin(loud)].nav
        qn = rep[rep.company.isin(quiet)].nav
        nav_p = float(mannwhitneyu(ln, qn, alternative="two-sided").pvalue)
        nav_ratio = float(ln.median() / qn.median()) if qn.median() else float("nan")
    return {
        "companies": int(rep.company.nunique()), "cells": len(rep),
        "between_share": float(between * 100),
        "null_median": float(np.median(null) * 100),
        "null_p95": float(np.percentile(null, 95) * 100),
        "rho_all": r_all, "p_all": p_all, "n_all": n_all,
        "rho_moved": r_mv, "p_moved": p_mv, "n_moved": n_mv,
        "n_quiet": len(quiet), "n_loud": len(loud), "nav_mwu_p": nav_p,
        "nav_ratio": nav_ratio,
    }


def size_effect_by_horizon(c: pd.DataFrame, horizons=(8, 16, 24, None)) -> pd.DataFrame:
    """Does high disagreement sit in small positions? The answer depends on how much of the
    panel you have, which is the reason this function exists rather than a single number.

    Reading the report dates in order and re-running the test on the first N reproduces the
    finding as it looked while the harvest was still running: strong and highly significant
    at two thirds of the panel, gone at the end. Anyone can replay the sequence, which is
    the only honest way to quote a result that dissolved.
    """
    g = c[c.guarded].dropna(subset=["dt"])
    dates = sorted(g.dt.unique())
    rows = []
    for n in horizons:
        sub = g if n is None else g[g.dt.isin(dates[:n])]
        rep = sub.groupby("company").filter(lambda s: len(s) >= 4)
        if rep.empty:
            continue
        med = rep.groupby("company").spread_pct.median()
        quiet, loud = med[med <= 0.5].index, med[med > 24].index
        if not len(quiet) or not len(loud):
            continue
        ln, qn = rep[rep.company.isin(loud)].nav, rep[rep.company.isin(quiet)].nav
        rows.append({
            "dates": len(dates) if n is None else n,
            "companies": int(rep.company.nunique()),
            "loud": len(loud), "quiet": len(quiet),
            "nav_ratio": float(ln.median() / qn.median()),
            "p": float(mannwhitneyu(ln, qn, alternative="two-sided").pvalue),
        })
    return pd.DataFrame(rows)


def house_policy(d: pd.DataFrame, c: pd.DataFrame, family: str = "house") -> dict:
    """The first version's sharpest structural claim, re-asked at scale: within a fund
    family the mark is one number, so the count of independent views is the count of
    families rather than the count of funds."""
    x = comparable(d)
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    x = x[[k in keys for k in zip(x.company, x.dt)]]
    within = x.groupby(["company", "dt", family]).pps.agg(["min", "max", "size"])
    within = within[within["size"] > 1]

    # A cell in which every fund files the same price has zero total variance, and the
    # between-family share is then 0/0. Gating on `tot > 0` looked like it excluded exactly
    # those, but summing squared deviations of identical logs lands anywhere in [0, 1e-25]
    # depending on the order pandas accumulates in, so 838 unanimous cells fell on one side
    # or the other of the test according to the pandas version, and the reported count moved
    # between two releases while nothing about the data changed. VAR_FLOOR is well
    # above that noise and far below any real disagreement: 1e-12 in squared log units is a
    # price difference around a millionth of a percent.
    eta = []
    for _, s in x.groupby(["company", "dt"]):
        if s[family].nunique() < 2 or len(s) < 3:
            continue
        y = np.log(s.pps.values)
        tot = ((y - y.mean()) ** 2).sum()
        if tot > VAR_FLOOR:
            fit = s.groupby(family).pps.transform(lambda v: np.log(v).mean()).values
            eta.append(((fit - y.mean()) ** 2).sum() / tot)
    return {
        "family_cells": len(within),
        "identical_pct": float((within["max"] / within["min"] <= 1.0001).mean() * 100),
        "eta2_median": float(np.median(eta)) if eta else float("nan"),
        "eta2_cells": len(eta),
    }


# WHAT NAMES A SERIES. One pattern, here, because three modules used to carry three and they
# disagreed. §2.3's copy stopped at [A-K] and dropped the numeric suffix, and both limits cost
# it real rows: Databricks Series L is a series this paper quotes by name and was invisible to
# the decomposition, and Series A-2 read as Series A, so two houses holding C-1 and C-3 of one
# company were scored as holding THE SAME named series — the composition the decomposition
# exists to strip out. Measured against this pattern that was 7,637 rows §2.3 could not see
# and 10,821 it named differently; against the pattern `round_dates` was reading, 4,502.
#
# The union reads A-Z with an optional -N suffix, keeps the bare-letter "X SHARES" form §2.3's
# copy already had, and takes the SER / CL abbreviations `round_dates` had. The `\b` after each
# abbreviation is what stops SERAPH matching SER + APH. It lives in this module because
# `round_dates` imports `ncsr_acquisitions`, so neither can define it for the other, and this
# module imports neither.
#
# DOUBLED LETTERS, because a single letter is not what the filings carry either. After Z the
# convention goes AA, BB, CC, and the panel has 150 rows of "SER AA", 66 of "SER BB" — one of
# them Stripe's Series BB-1, which §4.2 quotes by name — plus Series EE, DD, II and AA-9. A
# one-letter pattern reads none of them, which is the Databricks Series L defect recurring in
# the letters it was widened past. The error runs in the safe direction, since a row whose
# series goes unread joins the cells no filing describes and cannot manufacture a false
# same-series match, but the paper cannot quote a series its own decomposition is blind to.
#
# Exactly doubled, not any two letters: BX, CR1, PF2 and ACC-1 are not series, and III and IV
# are roman numerals in a fund's name. The alternation is written out rather than expressed as
# a backreference, which would need a capture group the three-branch extraction cannot use.
_DOUBLED = "|".join(c * 2 for c in string.ascii_uppercase)
_LETTER = rf"(?:{_DOUBLED}|[A-Z])(?:-?\d{{1,2}})?"
SERIES_RE = re.compile(
    rf"\bSER(?:IES)?\b\.?\s*({_LETTER})\b"
    rf"|\bCL(?:ASS)?\b\.?\s*({_LETTER})\b"
    rf"|\b({_LETTER})[- ]?(?:SHARES?|SHS)\b")


# Twenty-five letter-digit series are written both ways somewhere in the panel, and neither
# spelling is a typo that could be dropped: A-2 outnumbers A2 about three to one, C-1 outnumbers
# C1 about six to one. Ninety-nine distinct tokens collapse to seventy-four under the rule below.
def canonical_series(token: str) -> str:
    """One spelling per series, because the filings carry two and a key is a string.

    Filers write the same tranche as "SERIES A-2" and "SERIES A2". Captured as written those
    are two keys, so §2.3 scores two houses holding one series as holding two — the same
    defect the widened pattern above exists to remove, one layer down.

    The hyphenated form is canonical because §2 and the tables print these labels.

    The letters and the digits are separated by matching them, not by slicing at position one.
    Slicing was right while a series was one letter and turned "BB-1" into "B-B-1" the moment
    the pattern above learned to read a doubled letter — a normaliser that corrupts exactly
    the tokens it was just taught to see.
    """
    m = re.fullmatch(r"([A-Z]+)-?(\d+)?", token)
    if not m:
        return token
    letters, digits = m.group(1), m.group(2)
    return f"{letters}-{digits}" if digits else letters


def extract_series(text: pd.Series) -> pd.Series:
    """The one series a title names, canonicalised, or NA. One regex, one extraction rule.

    `SERIES_RE` carries three alternatives and therefore three capture groups, which is why
    callers cannot use `str.extract(..., expand=False)` on it and why two of them used to keep
    their own single-group copies instead. They call this instead.
    """
    def one(t: str):
        m = SERIES_RE.search(t)
        if not m:
            return None
        return canonical_series(next(v for v in m.groups() if v))
    return text.astype(str).str.upper().map(one)


def series_letters(d: pd.DataFrame) -> pd.Series:
    """Which share class or preferred series each filing says it is holding, where it says.

    Filers are not required to name the security beyond the issuer, and most of the time
    they do anyway: about one row in four carries a series or class letter in its title.
    """
    txt = (d.ISSUER_TITLE.astype(str).str.upper() + " | " + d.ISSUER_NAME.astype(str).str.upper())
    return pd.Series([frozenset(canonical_series(next(v for v in m.groups() if v))
                                for m in SERIES_RE.finditer(t))
                      for t in txt], index=d.index)


def same_security(d: pd.DataFrame, c: pd.DataFrame) -> dict:
    """The other half of the identification problem, and the bound it puts on the headline.

    Excluding claim instruments removes the securities that are plainly not the company's
    stock. It cannot remove the case where two houses hold two different rounds of preferred
    and the filings say so, because an issuer identifier cannot tell those apart either.

    The bound restricts to cells whose filings never name two different letters. It is a
    bound and not a correction, because a letter is weak evidence of a price difference:
    funds routinely carry every series of one company at a single number, so requiring one
    letter throws away real agreement along with the artifact, and it discards the most
    widely held private companies entirely, since those are the ones filers describe.
    """
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    x = comparable(d)
    x = x[[k in keys for k in zip(x.company, x.dt)]].copy()
    x["ser"] = series_letters(x)
    n_let = (x.groupby(["company", "dt"]).ser
              .agg(lambda s: len(set().union(*s)) if len(s) else 0).rename("n_letters"))
    g = c[c.guarded].merge(n_let.reset_index(), on=["company", "dt"])
    one = g[g.n_letters < 2]
    # The counter-example is named rather than asserted: the most widely held private company
    # in the data is held almost only on letter-mixed cells, and its houses file one price.
    sx = g[(g.company == "NM:SPACEX") & (g.n_letters >= 2)]
    return {
        "spacex_cells": len(sx),
        "spacex_median": float(sx.spread_pct.median()) if len(sx) else float("nan"),
        "cells": len(one), "companies": int(one.company.nunique()),
        "median": float(one.spread_pct.median()),
        "share_above_24": float((one.spread_pct > 24).mean() * 100),
        "nav_busd": float(one.nav.sum() / 1e9),
        "dropped_cells": len(g) - len(one),
        "mixed_median": float(g[g.n_letters >= 2].spread_pct.median()),
    }


def _named_rows(d: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    """Guarded-cell rows that name exactly one series letter, with that letter."""
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    x = comparable(d)
    x = x[[k in keys for k in zip(x.company, x.dt)]].copy()
    x["ser"] = series_letters(x)
    x = x[x.ser.map(len) == 1].copy()
    x["letter"] = x.ser.map(lambda s: next(iter(s)))
    return x


def series_composition(d: pd.DataFrame, c: pd.DataFrame) -> dict:
    """What `same_security`'s bound is computed on, which is not what it says.

    `same_security` restricts to cells whose filings never name two DIFFERENT letters and
    reports the median spread there as a floor. The restriction is satisfied two ways, and
    only one of them fixes the security: a cell can pass because every filer named the same
    series, or because nobody named anything. The second is the common case. The median
    share of rows carrying a letter inside that subset is zero, so two thirds of the "bound"
    is computed on cells whose security is unknown rather than shared, and those cells are
    WIDER than the panel, not narrower.

    Split three ways so the sentence the paper can defend is visible in the numbers:
    unnamed, partially named, and fully named. The third is the only one that holds the
    security fixed, and it is the population-scale version of what §2.2's N-CSR harvest
    finds on hand-parsed lots.
    """
    x = _named_rows(d, c)
    x["named"] = True
    all_rows = comparable(d)
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    all_rows = all_rows[[k in keys for k in zip(all_rows.company, all_rows.dt)]].copy()
    all_rows["ser"] = series_letters(all_rows)
    agg = all_rows.groupby(["company", "dt"]).agg(
        n_letters=("ser", lambda s: len(set().union(*s)) if len(s) else 0),
        rows=("ser", "size"),
        named_rows=("ser", lambda s: int((s.map(len) > 0).sum())),
    ).reset_index()
    t = c[c.guarded].merge(agg, on=["company", "dt"])
    t["named_share"] = t.named_rows / t.rows
    one = t[t.n_letters < 2]

    def blk(sub):
        return {"cells": len(sub), "companies": int(sub.company.nunique()),
                "median": float(sub.spread_pct.median()),
                "above_24": float((sub.spread_pct > 24).mean() * 100)}

    return {
        "bound": blk(one),
        "unnamed": blk(one[one.named_rows == 0]),
        "partial": blk(one[(one.n_letters == 1) & (one.named_share < 1)]),
        "fully_named": blk(one[(one.n_letters == 1) & (one.named_share == 1)]),
        "mixed": blk(t[t.n_letters >= 2]),
        "median_named_share_in_bound": float(one.named_share.median()),
    }


def same_series_spread(d: pd.DataFrame, c: pd.DataFrame) -> dict:
    """Between-house spread with the security held fixed by the filers' own series name.

    The decomposition the paper owed a reader and could not previously give: of the headline
    between-house spread, how much is two houses disagreeing about one security and how much
    is two houses holding two securities of one company? An issuer identifier cannot separate
    those. The rows that name their series can, wherever two houses name the SAME one.

    Unit is (company, date, series) with two or more houses, house medians compared, so a
    complex filing thirty funds votes once. The 4x class guard is re-applied inside the
    series group rather than inherited from the cell: it removes two groups, one of them the
    Magic Leap price outlier §3.2 already documents.

    Reported against the same cells scored the paper's way, because the comparison is only
    honest if the denominator is held fixed. It is also a selected subset and the selection
    runs one way: cells carrying a shared named series are calmer than the panel before any
    series is fixed, so `pooled_median` is printed beside `panel_median` rather than left for
    a reader to discover.
    """
    x = _named_rows(d, c)
    hm = x.groupby(["company", "dt", "letter", "house"]).pps.median().reset_index()
    per = hm.groupby(["company", "dt", "letter"]).agg(
        houses=("house", "nunique"), lo=("pps", "min"), hi=("pps", "max")).reset_index()
    per = per[per.houses >= 2]
    # `<=`, exactly as `cells()` applies it at line 317. Written `<` first, which is a
    # different filter on a boundary case and the kind of near-miss this repo has paid for.
    guarded = per[per.hi / per.lo <= CLASS_GUARD].copy()
    guarded["spread_pct"] = (guarded.hi / guarded.lo - 1) * 100
    ck = set(zip(guarded.company, guarded.dt))
    g = c[c.guarded]
    same = g[[k in ck for k in zip(g.company, g.dt)]]
    wide = guarded[guarded.spread_pct > 24]
    top5 = wide.company.value_counts().head(5)
    return {
        "groups": len(guarded), "companies": int(guarded.company.nunique()),
        "cells": int(guarded.groupby(["company", "dt"]).ngroups),
        "dropped_by_guard": len(per) - len(guarded),
        "median": float(guarded.spread_pct.median()),
        "p75": float(guarded.spread_pct.quantile(0.75)),
        "p90": float(guarded.spread_pct.quantile(0.90)),
        "above_24": float((guarded.spread_pct > 24).mean() * 100),
        "tail_groups": len(wide), "tail_companies": int(wide.company.nunique()),
        "tail_top5_share": float(top5.sum() / len(wide) * 100),
        # the same cells, series ignored — the paper's own statistic on this denominator
        "pooled_median": float(same.spread_pct.median()),
        "pooled_above_24": float((same.spread_pct > 24).mean() * 100),
        "panel_median": float(g.spread_pct.median()),
    }


MAX_GAP_DAYS = 100          # `REMARK_TOL` is defined once, at the top of this module.
# It was defined a second time here, with the same value, so §6.2 read one copy and
# `staleness` read the other. Identical values make that harmless and invisible, which
# is the problem: the next person to tune one of them would have moved half the paper.


def staleness(d: pd.DataFrame, c: pd.DataFrame) -> dict:
    """Do two houses that have both stopped moving still disagree?

    Section 4.8 put that question and said the nine-name panel could not answer it. This is
    the answer on the population. A house's mark counts as having moved when its median
    across its own funds changes by more than the tolerance against its previous observation
    of the same company, provided that observation is recent enough to be a comparison at
    all — filings arrive quarterly for most funds and monthly for some, so a gap longer than
    a quarter is a hole in the record rather than a decision to stand pat.

    A cell is judgeable when every house in it has such a previous observation. QUIET means
    no house moved; FRESH means all of them did. Quiet is the strict side of the two: a
    house whose median shifts because its own fund set changed is counted as having moved,
    which can only take cells out of the quiet set.
    """
    x = comparable(d)
    h = (x.groupby(["company", "house", "dt"], as_index=False)
           .agg(pps=("pps", "median"), n_funds=("fund", "nunique"))
           .sort_values(["company", "house", "dt"]))
    prev = h.groupby(["company", "house"])
    h["prev_pps"] = prev.pps.shift(1)
    h["gap"] = (h.dt - prev.dt.shift(1)).dt.days
    h["judge"] = h.gap.le(MAX_GAP_DAYS) & h.prev_pps.notna()
    h["moved"] = h.judge & ((h.pps / h.prev_pps - 1).abs() > REMARK_TOL)

    g = c[c.guarded]
    keys = set(zip(g.company, g.dt))
    h = h[[k in keys for k in zip(h.company, h.dt)]]
    per = (h.groupby(["company", "dt"])
             .agg(nh=("house", "nunique"), njudge=("judge", "sum"), nmoved=("moved", "sum"))
             .reset_index())
    cell = g.merge(per, on=["company", "dt"])
    cell = cell[cell.njudge == cell.nh]
    quiet, fresh = cell[cell.nmoved == 0], cell[cell.nmoved == cell.nh]

    # How long a parked house has been parked, counted back from each wide quiet cell. A
    # single unchanged report could be a filing that crossed a repricing; a run of them is a
    # position held at one number across quarters.
    runs = []
    for co, dt in quiet[quiet.spread_pct > 24][["company", "dt"]].to_numpy():
        for house, ss in h[(h.company == co) & (h.dt <= dt)].groupby("house"):
            ss = ss.sort_values("dt")
            if ss.dt.iloc[-1] != dt:
                continue
            k = 0
            for i in range(len(ss) - 1, 0, -1):
                same = abs(ss.pps.iloc[i] / ss.pps.iloc[i - 1] - 1) <= REMARK_TOL
                near = (ss.dt.iloc[i] - ss.dt.iloc[i - 1]).days <= MAX_GAP_DAYS
                if same and near:
                    k += 1
                else:
                    break
            runs.append(k)

    pairs = []
    for _, s in cell.groupby("company"):
        f, q = s[s.nmoved == s.nh], s[s.nmoved == 0]
        if len(f) and len(q):
            pairs.append((f.spread_pct.median(), q.spread_pct.median()))
    a = np.array(pairs)
    # Ties are decided by `same_number`, never by ==. Zeroing them here rather than filtering
    # keeps the signed-rank test and the sign test on one definition of a tie; scipy drops
    # exact zeros itself, so handing it the cleaned differences makes that agreement explicit.
    dif = np.where(same_number(a[:, 0], a[:, 1]), 0.0, a[:, 0] - a[:, 1])
    nz = dif[dif != 0]
    return {
        "judgeable": len(cell), "quiet": len(quiet), "fresh": len(fresh),
        "quiet_companies": int(quiet.company.nunique()),
        "quiet_median": float(quiet.spread_pct.median()),
        "quiet_nonzero_pct": float((quiet.spread_pct > IDENTICAL).mean() * 100),
        "quiet_above_24_pct": float((quiet.spread_pct > 24).mean() * 100),
        "quiet_above_24_n": int((quiet.spread_pct > 24).sum()),
        "quiet_above_24_nav_busd": float(quiet[quiet.spread_pct > 24].nav.sum() / 1e9),
        "fresh_median": float(fresh.spread_pct.median()),
        "parked_reports_median": float(np.median(runs)) if runs else float("nan"),
        "parked_four_or_more_pct": float(np.mean(np.array(runs) >= 4) * 100) if runs else float("nan"),
        "mwu_fresh_wider_p": float(mannwhitneyu(fresh.spread_pct, quiet.spread_pct,
                                                alternative="greater").pvalue),
        "paired_companies": len(a),
        "paired_fresh_wider": int((dif > 0).sum()),
        "paired_untied": len(nz),
        "paired_fresh_wider_pct": float((dif > 0).sum() / len(nz) * 100),
        "wilcoxon_p": float(wilcoxon(dif, alternative="greater").pvalue),
        "sign_p": float(binomtest(int((nz > 0).sum()), len(nz)).pvalue),
        # The narrowest gap between a tie and a real difference. The manuscript's integer
        # count is only meaningful while this stays far above float noise.
        "narrowest_untied_gap": float(np.abs(nz).min()),
    }


def main() -> None:
    d, c = panel()
    print(f"marks {len(d):,} · quarters {d.src_quarter.nunique()} · "
          f"issuer strings {d.ISSUER_NAME.nunique():,} -> companies {d.company.nunique():,}")
    dom = d.INVESTMENT_COUNTRY.value_counts()
    print(f"  US {dom.get('US', 0):,} · non-US {len(d) - dom.get('US', 0):,} "
          f"· feeder rows held out {int(d.is_wrapper.sum()):,}")

    c.to_csv(CELLS, index=False)
    k = concentration(c)
    g_all = c[c.guarded]
    print(f"\ncells {k['cells']:,} across {k['companies']:,} companies · "
          f"median spread {k['median']:.3f}% · p75 {k['p75']:.1f}% · p90 {k['p90']:.1f}%")
    print(f"  identical to the last digit {k['identical_pct']:.1f}% · "
          f"within a basis point {k['within_1bp_pct']:.1f}%")
    pct24 = float((g_all.spread_pct < 24).mean() * 100)
    print(f"  above 24%: {k['share_above_24']:.1f}% of cells "
          f"(the ten-name median of 24% sits at the population's "
          f"{pct24:.0f}{'th' if 11 <= pct24 % 100 <= 13 else {1:'st',2:'nd',3:'rd'}.get(int(pct24) % 10, 'th')} percentile)")
    print(f"  booked NAV ${k['nav_busd']:,.1f}B, of which ${k['nav_disagreeing_busd']:,.1f}B "
          f"({k['nav_disagreeing_share']:.1f}%) sits in cells disagreeing by over 24%")

    p = persistence(c)
    if p:
        print(f"\npersistence on {p['companies']:,} companies seen on 4+ report dates")
        print(f"  between-company share of spread variance {p['between_share']:.1f}% "
              f"vs relabelling null {p['null_median']:.1f}% (95th {p['null_p95']:.1f}%)")
        print(f"  own lag-1 rho {p['rho_all']:.3f} (p={p['p_all']:.2g}, n={p['n_all']:,})")
        print(f"  restricted to pairs where the top mark moved: rho {p['rho_moved']:.3f} "
              f"(p={p['p_moved']:.2g}, n={p['n_moved']:,})")
        print(f"  companies quiet {p['n_quiet']} · loud {p['n_loud']} · "
              f"median NAV loud/quiet {p['nav_ratio']:.2f}x, two-sided MWU p={p['nav_mwu_p']:.3g}")

    s = same_security(d, c)
    print(f"\nrestricting to cells whose filings never name two series or classes: "
          f"{s['cells']:,} cells, {s['companies']:,} companies")
    print(f"  median spread {s['median']:.2f}% (against {k['median']:.2f}% on all cells), "
          f"{s['share_above_24']:.1f}% above 24%, NAV ${s['nav_busd']:,.1f}B")
    print(f"  the {s['dropped_cells']:,} cells naming two or more sit at a median of "
          f"{s['mixed_median']:.2f}%")

    st = staleness(d, c)
    print(f"\ndoes a pair of houses that both stood pat still disagree? "
          f"({st['judgeable']:,} cells carry the evidence to say)")
    print(f"  nobody moved: {st['quiet']:,} cells over {st['quiet_companies']} companies, "
          f"median {st['quiet_median']:.2f}%, {st['quiet_nonzero_pct']:.1f}% not unanimous")
    print(f"  of those, {st['quiet_above_24_pct']:.1f}% ({st['quiet_above_24_n']}) exceed 24%, "
          f"holding ${st['quiet_above_24_nav_busd']:.1f}B")
    print(f"  everyone moved: {st['fresh']:,} cells, median {st['fresh_median']:.2f}% — "
          f"WIDER, not narrower (MWU p={st['mwu_fresh_wider_p']:.2g})")
    print(f"  within company ({st['paired_companies']} have both kinds): fresh wider in "
          f"{st['paired_fresh_wider']} of {st['paired_untied']} untied, "
          f"Wilcoxon p={st['wilcoxon_p']:.3g}, sign test p={st['sign_p']:.2f}")

    hz = size_effect_by_horizon(c)
    print("\nsize effect as the panel accumulates (the finding that dissolved)")
    print(f"  {'dates':>6} {'companies':>10} {'loud':>5} {'quiet':>6} {'NAV ratio':>10} {'p':>10}")
    for _, r in hz.iterrows():
        print(f"  {int(r.dates):>6} {int(r.companies):>10,} {int(r.loud):>5} {int(r.quiet):>6} "
              f"{r.nav_ratio:>9.2f}x {r.p:>10.3g}")

    h = house_policy(d, c)
    print(f"\nhouse policy: {h['identical_pct']:.1f}% of {h['family_cells']:,} multi-fund house "
          f"cells file one identical mark · between-family variance share median "
          f"{h['eta2_median']:.3f} (n={h['eta2_cells']:,})")
    print(f"\nwrote {CELLS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
