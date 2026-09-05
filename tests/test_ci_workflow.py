"""The workflow is a gate nobody local ever runs, which is how it went red and stayed red.

`.github/workflows/verify.yml` is the only place the suite has ever been run on an
environment other than the author's, and a referee found that it had never run publicly on
the reframed paper at all. The reason it would have failed, had it run, was a step checking a
table the manuscript stopped printing when the secondary-market leg was cut: the step exits 1
on every commit since, and nothing local executes the workflow, so nothing said so.

That is the general shape of the problem — a CI file drifts away from the repository it
guards and there is no local signal — so what is asserted here is that every command the
workflow runs still refers to something this package has. Whether the command PASSES is not
checkable here without running it, and two of them take minutes; what is checkable is that
the script exists, that it is not one of the second paper's, and that the steps a reader is
told about are the steps that run.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "verify.yml"

# From `tests/test_package_integrity.py`. A workflow step may not invoke one of these: they
# ship as the second paper's seed and are not held to this paper's state, so a gate pointed
# at one of them is a gate that fails for a reason the paper does not care about.
PAPER_TWO = {"analyze", "coverage_matrix", "forge_index", "fund_marks_timeseries",
             "panel_table", "prediction_markets"}


def _runs() -> str:
    return WF.read_text(encoding="utf-8")


def test_the_workflow_exists_and_is_read():
    text = _runs()
    assert len(text) > 500, "the workflow is too short to be the one this checks"
    assert "python3 -m pytest" in text, "the workflow no longer runs the suite"


def test_every_script_the_workflow_runs_is_in_the_package():
    """A step naming a script the repository does not contain fails on the runner and
    nowhere else."""
    text = _runs()
    called = set(re.findall(r"python3? (src/\w+\.py)", text))
    assert called, "no `python src/...` step found; the scrape has stopped reading the file"
    missing = sorted(s for s in called if not (ROOT / s).exists())
    assert not missing, f"the workflow runs script(s) this package does not ship: {missing}"


def test_no_workflow_step_gates_on_a_second_paper_module():
    """The failure this file was written for. `src/panel_table.py --check` compares its own
    rendering against a table in `paper/draft.md`; that table left with the secondary leg, so
    the step exited 1 on every commit after the cut while the workflow sat unrun.
    """
    text = _runs()
    called = {Path(s).stem for s in re.findall(r"python3? (src/\w+\.py)", text)}
    offenders = sorted(called & PAPER_TWO)
    assert not offenders, (
        "workflow step(s) gate on a module belonging to the second paper, which this "
        f"paper's state cannot keep green: {offenders}")


def test_the_workflow_runs_the_lint_gate_the_config_promises():
    """`pyproject.toml` states a ruleset so that "the code is clean" is checkable. A stated
    ruleset nothing runs is the same as no ruleset."""
    assert (ROOT / "pyproject.toml").exists(), "the lint configuration is gone"
    assert "ruff check" in _runs(), (
        "pyproject.toml states a ruff ruleset and no workflow step runs it")


def test_the_workflow_installs_what_the_pdf_checks_need_to_run_at_all():
    """A skipped check reports the same green as a passing one, and says nothing.

    Measured: with `pdftotext` and `pdffonts` off the PATH, nine of the eleven checks in
    `tests/test_pdf_artifact.py` skip and two run. The runner had no poppler, so the suite
    had been reporting green on a file that was doing almost nothing — including the guard
    that a URL is not broken across a line, which exists because a shipped page had one.
    The PDF is committed, so the checks need poppler and nothing else.
    """
    pdf_tests = (ROOT / "tests" / "test_pdf_artifact.py").read_text(encoding="utf-8")
    needs = {t for t in ("pdftotext", "pdffonts") if t in pdf_tests}
    assert needs, "test_pdf_artifact.py no longer shells out; this guard has lost its subject"
    assert "poppler-utils" in _runs(), (
        f"the PDF checks shell out to {sorted(needs)} and no workflow step installs poppler, "
        "so they all skip on the runner and the suite is green for the wrong reason")
