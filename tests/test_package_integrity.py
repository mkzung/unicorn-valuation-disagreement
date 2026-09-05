"""The replication package must be self-contained.

Twice this repository shipped a file pointing at a document it did not contain: four files
cited a private pre-publication fact check, and a methods note cited a scratch script from
the untracked working directory. Each looked fine locally, because the file was right there
on disk. The defect exists only for a reader who clones the repository, which is the only
reader a replication package is for, so the check runs against `git ls-files`.

This file cannot name the offending paths, even to explain itself. It is shipped, so it is
scanned, and prose describing a dangling path is indistinguishable from the dangling path —
which is how the first version of this module failed: it passed while untracked, and started
flagging its own docstring the moment it was committed. Concrete examples of what these
tests catch live in the commit that added them.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Regenerated on demand by src/build_pdf.py, so deliberately not shipped.
BUILD_INTERMEDIATES = {"paper/_build.md", "paper/_header.tex"}
# A stand-in inside a docstring, not a path anyone is meant to open.
ILLUSTRATIVE = {"figures/x.png"}
# Figures of the three legs that left this paper — the Forge secondary index, the prediction
# markets and the valuation cycle. The scripts that draw them are still here because they are
# the seed of the second paper and because two of them are imported by the robustness suite,
# but the charts themselves were deleted: a reader who has just read §3.4 saying those signals
# are not used should not find a megabyte of them in `figures/`. They are produced only when
# someone runs one of those scripts by hand, and
# `test_the_figures_directory_holds_exactly_what_the_paper_cites` fails if one is ever
# committed again, so the pair of guards is what keeps this list from becoming an excuse.
CUT_LEG_FIGURES = {
    "figures/coverage_matrix.png", "figures/forge_vs_fundmarks.png",
    "figures/fund_marks_timeseries.png", "figures/gap_chart.png",
    "figures/headline_vs_forge.png", "figures/prediction_markets.png",
}

PATH_TOKEN = re.compile(
    r"\b(?:src|data|notes|figures|paper|tests)/[A-Za-z0-9_.-]+\.(?:py|csv|md|png|gz|bib|pdf|cff)\b")


def shipped_files() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return set(out.stdout.split())


@pytest.fixture(scope="module")
def shipped():
    files = shipped_files()
    assert len(files) > 50, "git ls-files returned almost nothing; the check would pass vacuously"
    return files


def test_no_shipped_file_points_outside_the_package(shipped):
    """Every in-repository path a shipped file names must itself be shipped."""
    dangling: dict[str, set[str]] = {}
    scanned = 0
    for rel in sorted(shipped):
        if rel.endswith((".png", ".pdf", ".gz")):
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        scanned += 1
        for tok in PATH_TOKEN.findall(text):
            if (tok in shipped or tok in BUILD_INTERMEDIATES or tok in ILLUSTRATIVE
                    or tok in CUT_LEG_FIGURES):
                continue
            dangling.setdefault(tok, set()).add(rel)

    # Print the denominator: a scan over nothing is not evidence of anything.
    assert scanned > 30, f"only {scanned} shipped text files scanned; the check proves nothing"
    assert not dangling, "shipped files point at paths the package does not contain: " + "; ".join(
        f"{tok} <- {sorted(who)}" for tok, who in sorted(dangling.items()))


def test_the_private_working_directory_is_never_referenced(shipped):
    """The untracked working directory holds the worklog, the fact check and reviewer notes.
    It is not published, so a shipped file citing it sends the reader nowhere. The directory
    name is built rather than written out, for the reason the module docstring gives."""
    private_dir = "_" + "work/"
    offenders = []
    for rel in sorted(shipped):
        if rel == ".gitignore" or rel.endswith((".png", ".pdf", ".gz")):
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if private_dir in text:
            offenders.append(rel)
    assert not offenders, f"these shipped files cite the private working directory: {offenders}"


def test_notes_holds_only_what_ships(shipped):
    """notes/ used to mix the shipped methods notes with private working records, separated
    only by seven lines in .gitignore. Nothing about the folder said which a file was, and
    the private ones outweighed the public ones. They live in the working directory now."""
    on_disk = {f"notes/{p.name}" for p in (ROOT / "notes").iterdir() if p.is_file()}
    unshipped = on_disk - shipped
    assert not unshipped, (
        f"notes/ again holds files that do not ship: {sorted(unshipped)} — put working "
        "records in the untracked working directory instead")


def test_cross_references_out_of_the_paper_resolve(shipped):
    """The README and the methods notes cite the manuscript by section number. Inserting
    section 5 pushed Limitations to 6 and Conclusion to 7, and the README line sending
    readers to the caveats quietly started pointing at the population panel instead — still
    a real section, so a check for existence alone passes it. Existence is what this test
    can prove; whether the target is the right one has to be a human reading the sentence.
    """
    body = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8").split("## References")[0]
    tops = set(re.findall(r"^## (\d+)\.", body, re.M))
    # Subsections were bold run-ins ("**5.5 Between houses ...**") until the manuscript was
    # rebuilt around headings; they are `### 5.1 ...` now. Both forms are scraped, because a
    # scrape that silently found nothing would let every stale cross-reference through — which
    # is exactly what this test exists to catch, and it is one line away from not doing it.
    subs = (set(re.findall(r"^\*\*(\d+\.\d+) ", body, re.M))
            | set(re.findall(r"^### (\d+\.\d+) ", body, re.M)))
    assert len(tops) >= 5 and len(subs) >= 10, "section scrape found too little to check against"

    bad = {}
    for rel in sorted(shipped):
        if not rel.endswith(".md") or rel.startswith("paper/"):
            continue
        text = (ROOT / rel).read_text(encoding="utf-8")
        for ref in set(re.findall(r"§(\d+(?:\.\d+)?)", text)):
            known = subs if "." in ref else tops
            if ref not in known:
                bad.setdefault(rel, set()).add(f"§{ref}")
    assert not bad, f"shipped documents cite sections the paper does not have: {bad}"


def test_every_shipped_dataset_is_in_the_data_dictionary(shipped):
    """Appendix A tells a reader the dictionary documents every column. It has to be true.

    Six of the thirty-five files in `data/` had no entry at all, and two of them are not
    minor: `nav_wedge.csv` is §11's whole panel and `round_event_study_stats.csv` is the file
    §8's prose is pinned against. A reader who takes Appendix A at its word and goes looking
    for the columns of the section he is checking finds nothing, and the sentence that sent
    him there is the paper's own.

    Checked against `git ls-files`, so a file that exists only on the author's disk cannot
    satisfy it and a file that ships cannot escape it.
    """
    doc = (ROOT / "notes" / "data_dictionary.md").read_text(encoding="utf-8")
    missing = []
    for rel in sorted(f for f in shipped if f.startswith("data/")):
        stem = Path(rel).name.split(".")[0]
        if f"`{rel}`" not in doc and f"`data/{stem}" not in doc:
            missing.append(rel)
    assert not missing, (
        "shipped dataset(s) with no entry in notes/data_dictionary.md, which Appendix A says "
        "documents every column:\n  " + "\n  ".join(missing))
    # A dictionary that documented nothing would also pass a check for "no missing entries".
    assert doc.count("\n## `data/") >= 30, "the dictionary scrape found almost no entries"


# Modules that belong to the second paper rather than to this one. They ship because two of
# them are imported by the robustness suite and all of them are that paper's seed, and they
# are named here rather than inferred, so adding one is a decision somebody made in writing.
PAPER_TWO = {"analyze", "coverage_matrix", "forge_index", "fund_marks_timeseries",
             "panel_table", "prediction_markets"}


def test_every_module_ships_for_a_reason(shipped):
    """A module nothing imports, tests or runs is either dead or an unguarded claim.

    `src/panel_table.py` was the case: it renders the §7.2 cross-section as a table, §7.2 left
    for the second paper, and its own test file was deleted with the section. What remained was
    a module whose docstring says `paper/draft.md` is pinned to its output and a `--check` mode
    that would exit non-zero — neither of which anything ran. Forty modules and one of them was
    a promise nobody kept, which is not visible in a coverage report, because a module at 34%
    and a module nothing calls at all look the same from a percentage.

    Three ways to be alive: imported by another module here, named by a test, or run as a stage
    of `reproduce.py`. Anything else has to be on `PAPER_TWO` in writing.
    """
    src = {Path(f).stem: f for f in shipped if f.startswith("src/") and f.endswith(".py")}
    assert len(src) > 30, f"only {len(src)} modules found; the scan is not reading src/"
    bodies = {s: (ROOT / f).read_text(encoding="utf-8") for s, f in src.items()}
    # Every test file EXCEPT this one. This file names each exempt module twice, in the list
    # and in the docstring explaining it, so counting itself as evidence would make the
    # exemption its own justification: taking `panel_table` off `PAPER_TWO` left the check
    # green, because the line that removed the exemption was itself the mention.
    me = Path(__file__).name
    tests_text = " ".join((ROOT / f).read_text(encoding="utf-8")
                          for f in shipped
                          if f.startswith("tests/") and f.endswith(".py") and not f.endswith(me))
    stages = bodies["reproduce"]

    orphans = sorted(
        s for s in src
        if s not in {"reproduce"} | PAPER_TWO
        and s not in tests_text
        and f'"src/{s}.py"' not in stages
        and not any(s in b for m, b in bodies.items() if m != s))
    assert not orphans, (
        "module(s) in src/ that nothing imports, tests or runs, and that are not declared "
        "second-paper seed:\n  " + "\n  ".join(orphans))

    # The other direction: an exemption for a module that is in fact exercised is an excuse,
    # and an exemption for a module that no longer exists is rot.
    assert set(src) >= PAPER_TWO, (
        f"PAPER_TWO names module(s) that are not shipped: {sorted(PAPER_TWO - set(src))}")


def test_a_second_paper_module_makes_no_promise_about_this_one(shipped):
    """The reason `panel_table` was worth finding rather than just listing.

    Its docstring said the manuscript is pinned to its output "by the second paper's own
    suite", in a repository that is the first paper. A shipped file may not claim a guard that
    does not run here: that is the same failure as a slack budget, one layer up.
    """
    claims = re.compile(r"paper/draft\.md is pinned|the manuscript is pinned|cannot silently "
                        r"drift", re.I)
    bad = []
    for s in sorted(PAPER_TWO):
        f = ROOT / "src" / f"{s}.py"
        if f.exists() and claims.search(f.read_text(encoding="utf-8")):
            bad.append(s)
    assert not bad, ("second-paper module(s) claiming this package enforces something about "
                     f"them: {bad}")
