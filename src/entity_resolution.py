"""Resolve N-PORT issuer strings to companies.

At thirty hand-picked names a human reads the issuer strings and decides. At population
scale that is not available, and the decision has to be a rule. The two failure modes are
not symmetric: splitting one company across several labels costs coverage, while fusing
two companies into one label invents a price spread that no fund ever filed. The rule is
therefore built to fail closed — identifiers first, conservative text second, and an
explicit alias list for the few cases text cannot decide, never a similarity score.

`tests/test_entity_resolution.py` holds the resolver to the companies hand-labelled in
`data/fund_marks.csv`: it must reproduce every one of those groupings, splitting none and
fusing none. The first version of this module failed that test by fusing three unrelated
companies through the placeholder CUSIP 999999999.

Run:  python3 src/entity_resolution.py        # validate against the hand-labelled set
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Aliases text cannot resolve. Each is a judgement and is reported in the manuscript.
#   DOUYIN - ByteDance's operating name; the two strings share no characters.
#   CANVAS - a filer's misspelling of Canva. One letter apart, which is exactly the
#            distance at which a fuzzy matcher starts fusing genuinely different firms.
ALIASES = {
    # operating name with no textual overlap
    "DOUYIN": "BYTEDANCE",
    # one-letter filer misspelling; a fuzzy matcher fusing at this distance would also
    # fuse genuinely different firms, so it is declared instead of inferred
    "CANVAS": "CANVA",
    # longer legal names for the same issuer. Each was read off the filings rather than
    # generalised: a containment rule that produces these also produces chains that fuse
    # unrelated companies once the population is large.
    "ANDURIL INDUSTRIES": "ANDURIL",
    "CANVA AUSTRALIA": "CANVA",
    "SPACE EXPLORATION": "SPACEX",
    "SPACE EXPLORATION TECH": "SPACEX",
    "SPACE EXPLORATION TECHNOLOGICS": "SPACEX",
    "SPACE EXPLORATION TECHNOLOGIES": "SPACEX",
    "STRIPE GLOBAL": "STRIPE",
    "RAMP BUSINESS": "RAMP",
    "PLAID CA": "PLAID",
    # the non-profit parent and the profit-participation vehicle are separate legal
    # entities carrying the same underlying economics; treating them as one company is a
    # judgement, so it is declared here rather than inferred from the shared word "OPENAI"
    "OPENAI FOUNDATION": "OPENAI",
    "OPENAI GLOBAL PROFIT PARTICIPATION": "OPENAI",
}

SUFFIX = re.compile(
    r"\b(inc|incorporated|corp|corporation|co|llc|l\.l\.c|lp|l\.p|plc|ltd|limited|pbc|"
    r"holdings?|holding|group|technologies|technology|labs?|systems?|the|company|pty|pcb|pte|bv|gmbh)\b",
    re.I)
CLASS_TEXT = re.compile(
    r"\b(SER(IES)?|CLASS|CL|PFD|PREF(ERRED)?|CVT|CONV(ERTIBLE)?|COMMON|COM|ORD(INARY)?|"
    r"PP|PRIVATE PLACEMENT|WARRANT|WTS?|UNITS?|STOCK|SHARES?)\b", re.I)
# Spelled-out forms are unambiguous anywhere in the name. Two-letter forms are not -
# AS, AB, SA, NV and AG are ordinary words and initials - so they are stripped only where
# a legal form actually sits, at the very end.
LEGAL_FORM = re.compile(
    r"\b(PUBLIC JOINT[- ]STOCK (?:COMPANY|SOCIETY)|JOINT[- ]STOCK (?:COMPANY|SOCIETY)|"
    r"PJSC|PJSCO|OJSC|AKTIENGESELLSCHAFT)\b", re.I)
LEGAL_FORM_TAIL = re.compile(r"(?:[ ,]+(?:AG|NV|SA|AB|AS|PAO|OAO|PTE|BV|GMBH|OY|OYJ|SPA|SRL))+\s*$",
                             re.I)
# Names that identify nothing. A degenerate name must never become a shared cluster seed:
# every row carrying it would be joined to every other, and identifiers then chain real
# companies through that hub. This is how 26,933 rows with a missing issuer name pulled
# Databricks, Canva and Waymo into one cluster.
DEGENERATE = {"", "NAN", "NONE", "NA", "N A", "PUBLIC JOINT", "PUBLIC", "PRIVATE",
              "COMPANY", "FUND", "TRUST", "HOLDINGS", "CLASS", "SERIES", "COMMON"}

VEHICLE = re.compile(r"\b(LLC|L\.L\.C|LP|L\.P|FUND|PARTNERS|CAPITAL|TRUST|SPV|VENTURES?)\b", re.I)
# The trailing \b is what stops this matching inside an ordinary name. Without it "holdings in" matches inside
# "HOLDINGS INC",
# so "FANATICS HOLDINGS INC CLASS A" was read as a feeder holding a company called "C" —
# and Stripe, whose name also contains "Holdings Inc", was fused into the same company.
LOOKTHROUGH = re.compile(
    r"\b(?:invested in|economic exposure to|exposure to|holdings? in)\b\s*(.+)", re.I)
# Bracket contents that are never a portfolio company: places of incorporation,
# currencies, former-name markers, and generic descriptors.
NOT_A_COMPANY = re.compile(
    r"^\s*(?:AKA|A/K/A|DBA|D/B/A|FKA|F/K/A|FORMERLY|NEE)\b|"
    r"\b(CAYMAN|BERMUDA|JERSEY|GUERNSEY|LUXEMBOURG|IRELAND|SINGAPORE|DELAWARE|NETHERLANDS|"
    r"MAURITIUS|BVI|BRITISH VIRGIN ISLANDS|HONG KONG|ONTARIO|CANADA|AUSTRALIA|UNITED KINGDOM|"
    r"USD|EUR|GBP|JPY|CHF|SEK|NOK|DKK|AUD|CAD|EEA|PROPRIETARY|MASTER|FEEDER|ONSHORE|OFFSHORE|"
    r"PARALLEL|BLOCKER|AIV|SPV|CO INVEST|CO-INVEST)\b", re.I)



_CUSIP_VALUE = {**{str(d): d for d in range(10)},
                **{chr(ord("A") + i): i + 10 for i in range(26)},
                "*": 36, "@": 37, "#": 38}


def cusip_check_digit_ok(s: str) -> bool:
    """Standard CUSIP check digit (CUSIP Global Services): double every second character
    value, sum the digits of the results, and the last character closes the sum to a
    multiple of ten."""
    total = 0
    for i, ch in enumerate(s[:8]):
        v = _CUSIP_VALUE.get(ch)
        if v is None:
            return False
        if i % 2:
            v *= 2
        total += v // 10 + v % 10
    return (10 - total % 10) % 10 == _CUSIP_VALUE.get(s[8], -1)


def clean_cusip(v) -> str:
    """A CUSIP only if it really is one.

    Shape is not enough. Private issuers are filed as 000000000 or 999999999, and filers
    also use internal codes that are nine characters of mixed letters and digits — TC
    codes in this data — which look like CUSIPs and are reused across companies. Joining
    on one of those chains unrelated issuers into a single cluster: it is what put Socure,
    Jetti, Epirus and Parabilis Medicines together. The check digit settles it, because a
    real CUSIP closes and an internal code almost never does.
    """
    s = str(v).strip().upper()
    if s in {"", "NAN", "NONE"} or s.startswith("N/A") or len(s) != 9:
        return ""
    if len(set(s)) == 1:
        return ""
    return s if cusip_check_digit_ok(s) else ""


def clean_lei(v) -> str:
    s = str(v).strip().upper()
    return "" if s in {"", "NAN", "NONE"} or s.startswith("N/A") or len(s) != 20 else s


def _is_acronym_of(short: str, long: str) -> bool:
    """"(MPL)" beside "Mexico Pacific Limited" is the same name abbreviated, not a
    different company held through a vehicle."""
    letters = re.sub(r"[^A-Z]", "", short.upper())
    initials = "".join(w[0] for w in re.findall(r"[A-Za-z]+", long))[:12].upper()
    return bool(letters) and len(letters) <= 5 and letters in initials


def unwrap(name: str) -> tuple[str, bool]:
    """Return (text_to_identify_on, is_wrapper).

    A feeder vehicle holds one company and says so, usually as "invested in X" or
    "economic exposure to X". That wording is the only reliable signal and it is not
    always inside brackets, so it is searched across the whole name.

    Brackets on their own mean very little. They carry jurisdictions ("(Cayman)"),
    currencies ("(EUR)"), former names ("(AKA: ...)"), share classes ("(Class A Common
    Stock)") and plain abbreviations ("MEXICO PACIFIC LIMITED LLC (MPL)"). Reading any of
    those as the underlying company is what fused nine unrelated Cayman partnerships into
    a single issuer called CAYMAN, so a bracket is only read as a look-through when its
    content is none of those things and the outer name is a vehicle.
    """
    m = LOOKTHROUGH.search(name)
    if m:
        return re.sub(r"[()]", " ", m.group(1)), True

    parens = re.findall(r"\(([^)]*)\)", name)
    outer = re.sub(r"\([^)]*\)", " ", name)
    if parens and VEHICLE.search(outer):
        for p in reversed(parens):
            t = p.strip()
            if len(t) <= 2 or CLASS_TEXT.search(t) or NOT_A_COMPANY.search(t):
                continue
            if _is_acronym_of(t, outer):
                continue
            return t, True
    return outer, False


def norm_name(s: str, lookthrough: bool = False) -> str:
    """`lookthrough` marks text taken from inside a feeder's brackets. There the tail is a
    description of the security rather than part of the company's name, so trailing lot
    and class numbers are noise. In a directly filed issuer name they are not: stripping
    them merges 256 separately incorporated Masterworks vehicles into one company."""
    t = LEGAL_FORM_TAIL.sub(" ", LEGAL_FORM.sub(" ", str(s).upper()))
    parts = CLASS_TEXT.split(t)
    if parts and parts[0].strip():
        t = parts[0]
    t = SUFFIX.sub(" ", t)
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if lookthrough:
        t = re.sub(r"(?: \d+)+$", "", t).strip()
    return ALIASES.get(t, t)


class _Union:
    def __init__(self):
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def join(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def modal(s: pd.Series):
    """The commonest value, ties broken by sort order rather than by row order.

    `value_counts().idxmax()` returns whichever tied value pandas met first, and 290 of the
    19,056 clusters here have a tied top name, so the label a cluster displays was a
    function of how the file happened to be ordered. Nothing numeric hangs on it — the key
    is the cluster root, which is the whole point of the comment in `resolve` — but a label
    that moves when pandas changes its grouping order is a diff nobody can explain, and the
    same idiom is used in `company_class` and `reconcile_versions` where a table row does
    carry the name. One rule, sorted, in one place.
    """
    vc = s.value_counts()
    top = vc.max()
    return sorted(str(v) for v in vc[vc == top].index)[0]


def resolve(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (company_key, display_label, is_wrapper) for every row.

    `company_key` is the identity to group on. `display_label` is for reading and may
    repeat across different companies, so it must never be used as a grouping key."""
    if not df.index.is_unique:
        raise ValueError(
            "resolve() needs a unique index: every lookup below is by label, and a repeated "
            "label returns a Series rather than a value. Pass df.reset_index(drop=True).")
    names, wrapped = {}, {}
    for i, raw in df["ISSUER_NAME"].items():
        txt, w = unwrap(str(raw))
        names[i], wrapped[i] = norm_name(txt, lookthrough=w), w
    nm = pd.Series(names)

    blank = pd.Series("", index=df.index)
    lei = (df["ISSUER_LEI"] if "ISSUER_LEI" in df else blank).map(clean_lei)
    cus = (df["ISSUER_CUSIP"] if "ISSUER_CUSIP" in df else blank).map(clean_cusip)

    u = _Union()
    for i in df.index:
        seed = f"NM:{nm[i]}" if nm[i] not in DEGENERATE else f"ROW:{i}"
        u.find(seed)
        if lei[i]:
            u.join(seed, f"LEI:{lei[i]}")
        if cus[i]:
            u.join(seed, f"CUS:{cus[i]}")

    # No automatic containment rule. "ANDURIL absorbs ANDURIL INDUSTRIES" reads as a safe
    # generalisation of the alias list, and on a few hundred rows it is. On the full
    # population it is not: containment is transitive through the union, so short names
    # chain into long ones and the chains meet. The first attempt at population scale
    # built a single cluster of 448 unrelated issuer strings labelled "SB", and merged
    # Gusto with Canva. Splitting a company across labels costs coverage; fusing two
    # companies invents a price spread. Only identifiers, exact names and declared
    # aliases join anything here.
    root = pd.Series({i: u.find(f"NM:{nm[i]}" if nm[i] not in DEGENERATE else f"ROW:{i}")
                      for i in df.index})
    # The key is the cluster root and nothing else. A readable label is the most common
    # normalised name in the cluster, and labels are NOT unique: several clusters can be
    # dominated by the same string, most often an empty issuer name. Grouping on the label
    # therefore pools unrelated companies — it put Gusto and Canva in one row and returned
    # a cross-family spread of eighteen million percent. Group on the key, display the
    # label.
    display = (pd.DataFrame({"root": root, "nm": nm})
                 .groupby("root").nm.agg(modal))
    return root, root.map(display), pd.Series(wrapped)


def hand_labelled() -> pd.DataFrame:
    """The first version's fund-mark file, with its human `company` column, resolved."""
    p = pd.read_csv(ROOT / "data" / "fund_marks.csv", dtype=str)
    p = p.rename(columns={"issuer_name": "ISSUER_NAME", "cusip": "ISSUER_CUSIP"})
    p["ISSUER_LEI"] = ""
    # Five of the 409 hand-labelled marks carry no issuer name at all. They cannot test a
    # name-based rule, so they are held out — but silently dropping rows from a validation
    # set is how a validation set stops validating, so the count is reported.
    named = p.dropna(subset=["ISSUER_NAME"]).reset_index(drop=True)
    named.attrs["dropped_unnamed"] = len(p) - len(named)
    named["resolved"], named["label"], named["wrapper"] = resolve(named)
    return named


def disagreements(p: pd.DataFrame) -> tuple[list, list]:
    split = [(co, sorted(g.resolved.unique())) for co, g in p.groupby("company")
             if g.resolved.nunique() > 1]
    fused = [(r, sorted(g.company.unique())) for r, g in p.groupby("resolved")
             if g.company.nunique() > 1]
    return split, fused


if __name__ == "__main__":
    p = hand_labelled()
    split, fused = disagreements(p)
    print(f"hand-labelled rows {len(p)} · companies {p.company.nunique()} · "
          f"issuer strings {p.ISSUER_NAME.nunique()} · wrappers {int(p.wrapper.sum())}")
    print(f"  held together {p.company.nunique() - len(split)}/{p.company.nunique()} · "
          f"split {len(split)} · fused {len(fused)}")
    for co, rs in split:
        print(f"    SPLIT {co} -> {rs}")
    for r, cs in fused:
        print(f"    FUSED {r} <- {cs}")
