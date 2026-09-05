"""No analytical decision may be defined twice.

`population.SERIES_RE`, `round_dates.SERIES` and `ncsr_acquisitions.SERIES` were three answers
to one question — what names a series — and two of them were wrong. One stopped at [A-K], so
Databricks Series L was invisible to §2.3; one dropped the numeric suffix, so two houses
holding C-1 and C-3 of a company were scored as holding the same named series, which is the
composition the decomposition exists to remove. 417 pinned numbers were all green throughout,
because all 417 were computed by the same wrong copy. A registry compares a value against the
code; it cannot see the code answering one question three ways.

So the class gets a guard rather than the incident, and it takes two guards because the first
one written here was not enough. `test_no_analytical_constant_is_defined_twice_differently`
matches on the NAME: any constant two modules both define must be the same object or compare
equal. That closes the case where one decision is retyped under one name — and it went green
the moment the second copy was renamed. For four commits `population` carried `SERIES_RE` and
`SERIES_TITLE_RE` side by side, two patterns answering the one question differently on 4,502
panel rows, and this file was green throughout. A name guard cannot see a rename.

`test_no_two_patterns_answer_one_question_differently` matches on BEHAVIOUR instead: two
compiled patterns that agree on most of a corpus but not all of it are one decision that has
drifted, whatever they are called. The threshold below is read off the historical pair, not
chosen.

Path constants are exempt: every module having its own output path is the point of having one.
"""
from __future__ import annotations

import importlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Names that are per-module by design: where a module reads from, writes to, or fetches with.
PATHY = {"ROOT", "OUT", "STATS", "PANEL", "DRAFT", "REPO", "CTX", "ARCH", "CACHE", "OUTDIR",
         "COLS", "SLEEP", "UA", "HEADERS", "BASE", "URL", "FORMS", "TARGETS", "VEHICLE"}
DEFN = re.compile(r"^([A-Z][A-Z0-9_]{2,})\s*=", re.M)

# Modules that touch the network at import. Each was tried before being listed, and
# `ncsr_acquisitions` imports clean and is deliberately NOT here: it is one of the two modules
# the defect this guard exists for lived in, and a guard that exempts the scene of the crime
# is theatre.
SKIP = {"nport_fetch", "nport_bulk", "form_d", "verify_marks", "verify_placebo_sec",
        "family_forecast", "listing_dates"}


def _shared() -> dict[str, dict[str, object]]:
    where: dict[str, dict[str, object]] = defaultdict(dict)
    for f in sorted((ROOT / "src").glob("*.py")):
        if f.stem in SKIP:
            continue
        names = set(DEFN.findall(f.read_text(encoding="utf-8"))) - PATHY
        if not names:
            continue
        try:
            mod = importlib.import_module(f.stem)
        except Exception:
            continue
        for n in names:
            if hasattr(mod, n):
                where[n][f.stem] = getattr(mod, n)
    return {n: v for n, v in where.items() if len(v) > 1}


def test_the_scan_sees_the_constants():
    """A scan that imports nothing would report no duplicates and prove nothing."""
    seen = 0
    for f in sorted((ROOT / "src").glob("*.py")):
        seen += len(set(DEFN.findall(f.read_text(encoding="utf-8"))) - PATHY)
    assert seen > 80, f"only {seen} analytical constants found across src/"


def test_no_analytical_constant_is_defined_twice_differently():
    bad = []
    for name, bymod in sorted(_shared().items()):
        vals = {}
        for mod, val in bymod.items():
            key = val.pattern if hasattr(val, "pattern") else repr(sorted(val)) \
                if isinstance(val, (set, frozenset)) else repr(val)
            vals.setdefault(key, []).append(mod)
        if len(vals) > 1:
            detail = "; ".join(f"{','.join(sorted(m))}={k[:60]}" for k, m in vals.items())
            bad.append(f"{name}: {detail}")
    assert not bad, ("one decision, two definitions — import it instead of retyping it:\n  "
                     + "\n  ".join(bad))


def test_no_module_does_work_at_import():
    """Importing a module must not fetch, write or print. Three of them did.

    `family_forecast` ran a live EDGAR harvest on import and overwrote
    `data/ipo_premarks_byfund.csv`, an input §7 quotes — and the fresh harvest disagreed with
    the committed one, so an accidental import moved a number the paper prints. `verify_marks`
    re-fetched every cited accession and then called `SystemExit`. `analyze` wrote two figures
    into `figures/`, both belonging to a cut leg and both deliberately deleted, so importing it
    put back a file another test exists to keep out.

    All three were found by importing every module in `src/` to enumerate its constants, which
    is a thing tools do: an IDE indexing the package, a doc generator, a coverage run. A module
    with a `main()` behind a guard is safe to import; a module whose body is its program is not.
    """
    offenders = []
    for f in sorted((ROOT / "src").glob("*.py")):
        text = f.read_text(encoding="utf-8")
        if "__main__" in text:
            continue
        # Module-level statements that are neither imports, definitions, constants nor docstring.
        for line in text.split("\n"):
            if not line or line[0] in " \t#)]}\"'":
                continue
            if re.match(r"(?:from|import|def|class|@|if TYPE_CHECKING)\b", line):
                continue
            if re.match(r"[A-Za-z_][A-Za-z0-9_]*\s*(?::[^=]+)?=", line):
                continue
            offenders.append(f"{f.name}: {line[:60]}")
            break
    assert not offenders, (
        "module(s) that run their program at import — put the body in main() behind "
        "`if __name__ == \"__main__\":`\n  " + "\n  ".join(offenders))


# ---------------------------------------------------------------------------------------
# The behavioural half. Two patterns under two names, answering one question two ways.
# ---------------------------------------------------------------------------------------

# The two patterns the correction replaced, kept as literals because neither is in the tree
# any more and a guard calibrated on a defect it can no longer see is calibrated on nothing.
HISTORIC = {
    "the [A-K] copy §2.3 read": re.compile(
        r"\bSER(?:IES)?\.?\s+([A-K])\b|\bCLASS\s+([A-K])\b|\b([A-K])[- ]?(?:SHARES?|SHS)\b"),
    "the copy `round_dates` read": re.compile(
        r"\b(?:SER|SERIES|CLASS|CL)\.?\s*([A-Z](?:-?\d{1,2})?)\b", re.I),
}

# Read off the measurement, not chosen. The three live pairs that are one decision score
# exactly 1.000; the three historical pairs that are one decision drifted score 0.79, 0.81 and
# 0.98; every pair of genuinely different patterns scores at most 0.08. The whole distribution
# sits at the two ends and the band between is empty, so the threshold sits in the middle of
# the empty band.
AGREEMENT_FLOOR = 0.50
MIN_EVIDENCE = 200          # a pair that has never both matched proves nothing either way
CORPUS_ROWS = 20000


def _corpus() -> list[str]:
    import pandas as pd
    f = ROOT / "data" / "nport_population_marks.csv.gz"
    d = pd.read_csv(f, usecols=["ISSUER_TITLE"], nrows=CORPUS_ROWS, low_memory=False)
    return d.ISSUER_TITLE.astype(str).str.upper().tolist()


def _value(rx: re.Pattern, t: str):
    """What the pattern says about this row: its first non-empty group, or the whole match."""
    m = rx.search(t)
    if not m:
        return None
    return next((v for v in m.groups() if v), m.group(0)) if m.groups() else m.group(0)


def _patterns() -> dict[str, re.Pattern]:
    found = {}
    for f in sorted((ROOT / "src").glob("*.py")):
        if f.stem in SKIP:
            continue
        names = set(DEFN.findall(f.read_text(encoding="utf-8")))
        if not names:
            continue
        try:
            mod = importlib.import_module(f.stem)
        except Exception:
            continue
        for n in names:
            v = getattr(mod, n, None)
            if isinstance(v, re.Pattern):
                found[f"{f.stem}.{n}"] = v
    return found


def _agreements(pats: dict[str, re.Pattern], texts: list[str]) -> dict[tuple, tuple]:
    """Share of the rows either pattern matches on which both match and return one answer.

    Values are computed once per pattern rather than once per pair: eighteen patterns make a
    hundred and fifty pairs, and the naive loop reads the corpus a hundred and fifty times.
    """
    vals = {k: [_value(rx, t) for t in texts] for k, rx in pats.items()}
    out = {}
    keys = sorted(vals)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            same = union = 0
            for x, y in zip(vals[a], vals[b]):
                if x is None and y is None:
                    continue
                union += 1
                same += x is not None and x == y
            if union >= MIN_EVIDENCE:
                out[(a, b)] = (same / union, union)
    return out


def test_the_pair_scan_sees_the_patterns():
    """A scan that found one pattern would report no drift and prove nothing."""
    pats = _patterns()
    assert len(pats) >= 10, f"only {len(pats)} module-level patterns found across src/"
    assert any(k.endswith(".SERIES_RE") for k in pats), "the series pattern is not in the scan"


def test_no_two_patterns_answer_one_question_differently():
    """Agreement of 1.0 is one decision; 0.08 is two questions; 0.79 is one decision drifted."""
    scored = _agreements(_patterns(), _corpus())
    bad = [f"{a} vs {b}: agree on {r:.1%} of {u} rows"
           for (a, b), (r, u) in sorted(scored.items()) if AGREEMENT_FLOOR < r < 1.0]
    assert not bad, (
        "two patterns answering one question two ways — the name guard cannot see this "
        "because they are named differently:\n  " + "\n  ".join(bad))


def test_the_pair_guard_fires_on_the_defect_it_exists_for():
    """The reason to trust the guard above: it is shown failing on the real pair.

    Both historical patterns are scored against whichever pattern the tree now uses for the
    series. A guard that has only ever been seen passing has not been reviewed.
    """
    import population as pop
    scored = _agreements({"now": pop.SERIES_RE, **HISTORIC}, _corpus())
    caught = {k: v for k, v in scored.items()
              if "now" in k and AGREEMENT_FLOOR < v[0] < 1.0}
    assert len(caught) == 2, (
        "the historical divergence no longer scores as drift against the current pattern, so "
        f"the threshold has stopped meaning what it was measured to mean: {scored}")
