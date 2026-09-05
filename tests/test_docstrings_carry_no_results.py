"""Results live in the registry. Docstrings explain method.

The number registry pins every headline figure against `paper/draft.md`, `README.md` and
the data dictionary, and reads nothing else. So when the population panel was regrouped from
registrants to fund houses, five figures inside `src/*.py` docstrings kept the old answers —
two registrant counts, a median the rebuild had superseded, a share off by a factor of two
and a half, and a row count from before the data grew — while the whole suite stayed green.
Nobody had lied; nobody had looked either.

Two ways out. Extend the registry to parse docstrings and match every token against a
computed value, which needs an ever-growing allowlist for design constants and breaks on
every rephrase. Or state the rule: **a docstring in an analysis module does not quote a
result**. It says what the function computes and why the choice was made, and the answer
lives in one place. That is the rule, and this is the test.

Design constants are not results. `4x`, `1e-12`, `>=5 funds`, `>=2 complexes`, `200 draws`,
a seed, a section number, a year: these define the method rather than report its output, so
they stay. What cannot stay is a percentage, a dollar figure, or a thousands-separated count
that answers "and what came out?".
"""
from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Modules whose docstrings describe the population analysis. These are the ones that went
# stale; the older harvesters quote counts of their own inputs, which is a different thing.
GOVERNED = ["population.py", "fund_complex.py", "population_figure.py", "reconcile_versions.py"]

# A result answers "what came out": a percentage, a dollar amount, a magnitude with a
# thousands separator, or a correlation to three decimals.
RESULT_TOKEN = re.compile(
    r"""(?<![\w.])(?:
          \$\s?\d+(?:\.\d+)?\s?[BMK]?      # $517.3B
        | \d{1,3}(?:,\d{3})+               # 4,606
        | \d+(?:\.\d+)?\s?%                # 12.5%
        | 0\.\d{3}(?![\d\w])               # 0.735
        # A bare integer is ambiguous on its own, so it counts only when it carries the unit
        # that makes it an answer. Two digits or more, which leaves "5 funds" and "2
        # complexes" -- the bar itself -- alone.
        | \d{2,}\s+(?:registrant|CIK|cell|company|companies|row|mark|fund|house|complex)
    )""",
    re.X | re.I)

# Method constants, written the way the modules write them. Each defines the procedure.
ALLOWED = {
    "4x", "10:1", "0.5%", "1e-9", "1e-12", "1e-25",
    "4.3", "4.4", "4.8", "5.1",                   # section references
}


def docstrings(path: Path):
    """(qualified name, text) for the module docstring and every def/class docstring."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            text = ast.get_docstring(node)
            if text:
                yield getattr(node, "name", "<module>"), text


def test_analysis_docstrings_quote_no_results():
    offenders, scanned = [], 0
    for name in GOVERNED:
        path = ROOT / "src" / name
        assert path.exists(), f"{name} is missing; this test would pass over nothing"
        for where, text in docstrings(path):
            scanned += 1
            for tok in RESULT_TOKEN.findall(text):
                if tok.strip() in ALLOWED:
                    continue
                offenders.append(f"{name}:{where} quotes {tok.strip()!r}")

    # Print the denominator. A scan that found no docstrings would pass and prove nothing.
    assert scanned >= 15, f"only {scanned} docstrings scanned across {GOVERNED}"
    assert not offenders, (
        "results belong in src/paper_numbers.py, not in a docstring no guard reads:\n  "
        + "\n  ".join(offenders))


def test_the_pattern_would_actually_catch_a_stale_result():
    """The test above is worth nothing unless it fires. These are the five real figures that
    went stale, in the form they appeared, plus two constants that must survive."""
    for bad in ["Fidelity files under 30 registrant CIKs", "the median spread is 0.02%",
                "feeders hold 0.016% of value", "an entity-resolution pass over 146,000 rows",
                "$1.3B of the $518B total", "lag-1 rho 0.750"]:
        found = [t for t in RESULT_TOKEN.findall(bad) if t.strip() not in ALLOWED]
        assert found, f"the pattern misses a known-stale result: {bad!r}"
    for good in ["cells guarded at 4x for the share-class artifact",
                 "at least 5 funds across 2 complexes", "200 draws, seed 20260624",
                 "squared-log variance below 1e-12 is noise"]:
        assert not [t for t in RESULT_TOKEN.findall(good) if t.strip() not in ALLOWED], (
            f"the pattern would flag a method constant: {good!r}")
