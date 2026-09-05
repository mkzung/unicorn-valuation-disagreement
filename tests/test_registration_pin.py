"""The registration claims the analysis code has not moved since a named commit. Check it.

`notes/registration.md` §8 names a commit and says re-running the pipeline on extended data
"executes them unchanged". That is a statement about this repository, and it was false for a
while: the pin sat at a commit from before two of the four files were rewritten, and nothing
in the build noticed. A registration whose own provenance claim is stale is worth less than
no registration, because it invites a reader to check one cheap thing and find it wrong.

So the pin is verified rather than asserted. If a file listed in §8 differs between the
pinned commit and the working tree, this fails and the pin has to be moved deliberately.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "notes" / "registration.md"

# The files §8 names. Kept here rather than parsed out of the prose, so that dropping a file
# from the sentence cannot silently drop it from the check.
PINNED_FILES = [
    "src/robustness.py",
    "src/validation.py",
    "src/population.py",
    "src/sector_specification_curve.py",
]


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(("git", *args), cwd=ROOT, capture_output=True, text=True, check=False)


def _pinned_commit() -> str:
    text = REGISTRATION.read_text(encoding="utf-8")
    head = text.split("## 8. Analysis code", 1)[-1]
    m = re.search(r"`([0-9a-f]{7,40})`", head)
    assert m, "section 8 of the registration names no commit"
    return m.group(1)


@pytest.fixture(scope="module")
def repo() -> bool:
    if _git("rev-parse", "--git-dir").returncode != 0:
        pytest.skip("not a git checkout")
    return True


def test_section_8_names_every_file_it_pins(repo):
    """The prose and the checked list have to agree, or the check covers less than it says."""
    text = REGISTRATION.read_text(encoding="utf-8")
    section = text.split("## 8. Analysis code", 1)[-1]
    missing = [f for f in PINNED_FILES if f"`{f}`" not in section]
    assert not missing, f"section 8 does not name {missing}, but this test checks them"


def test_the_pinned_commit_exists(repo):
    sha = _pinned_commit()
    assert _git("cat-file", "-e", f"{sha}^{{commit}}").returncode == 0, (
        f"the registration pins {sha}, which is not a commit in this repository")


def test_no_analysis_file_has_moved_since_the_pin(repo):
    """The claim is 'executes them unchanged'. This is that claim, as a diff."""
    sha = _pinned_commit()
    changed = []
    for f in PINNED_FILES:
        if _git("diff", "--quiet", sha, "--", f).returncode != 0:
            changed.append(f)
    assert not changed, (
        f"the registration pins {sha} and claims these run unchanged, but they differ: "
        f"{changed}. Move the pin in notes/registration.md section 8, or do not make the claim.")


def test_the_diff_check_would_actually_fire(repo):
    """A comparison against HEAD passes trivially whatever the pin says. Prove the mechanism
    detects a real difference by pointing it at a commit where one of these files is known to
    differ — the parent of the commit that last touched population.py."""
    log = _git("log", "-1", "--format=%H", "--", "src/population.py").stdout.strip()
    assert log, "no history for src/population.py"
    parent = _git("rev-parse", f"{log}^").stdout.strip()
    if not parent:
        pytest.skip("population.py was added in the root commit")
    assert _git("diff", "--quiet", parent, "--", "src/population.py").returncode != 0, (
        "the diff check cannot tell two versions of population.py apart")


DRAFT = ROOT / "paper" / "draft.md"
SPELLED = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
           8: "eight", 9: "nine", 10: "ten"}


def _registered_predictions() -> list[str]:
    return re.findall(r"^\*\*(P\d+) — ", REGISTRATION.read_text(encoding="utf-8"), re.M)


def test_the_prediction_scrape_finds_the_registration_s_own_list():
    """Vacuous against a reworded heading, which is how this check would die unnoticed."""
    p = _registered_predictions()
    assert len(p) >= 4, f"scraped only {p} from the registration; the heading format moved"
    assert p == [f"P{i}" for i in range(1, len(p) + 1)], f"predictions are not consecutive: {p}"


def test_the_paper_counts_the_registration_s_predictions_correctly():
    """The manuscript says how many predictions the drafted registration makes. It was wrong.

    P5 was added to `notes/registration.md` and two sentences went on saying four — one in
    §10.1 and one inside a lifted appendix block. No guard in this repository could see it.
    The registry pins figures computed from the panel, and this number is a property of a file
    that is not the paper and is not data; it had nowhere to be checked.

    A count of something outside the manuscript belongs to whatever owns that something, so it
    is read from the registration here and required of the prose rather than the other way
    round. The paper's OWN P1–P4 list in the appendix is a different list and is not counted:
    it drops the registration's secondary-leg prediction, which left with §3.4.
    """
    n = len(_registered_predictions())
    draft = DRAFT.read_text(encoding="utf-8")
    stated = re.findall(r"registration(?:'s)?[^.]{0,40}?\b(\w+) predictions"
                        r"|\b(\w+) predictions the drafted registration", draft)
    said = {a or b for a, b in stated}
    assert said, ("the manuscript no longer states how many predictions the registration "
                  "makes; if that sentence was cut, cut this guard with it")
    assert said == {SPELLED[n]}, (
        f"the registration carries {n} predictions ({SPELLED[n]}) and the manuscript says "
        f"{sorted(said)}. Update the prose, or the registration, but not neither.")
