"""One source line, one home.

The assembler builds `paper/draft.md` by lifting numbered line ranges out of the audited
source draft into the part files that make up the manuscript. Nothing stopped two parts naming
the same range, and for one line nothing did: source 359 was lifted into both §5.2 and
Appendix C.2, so the body ran the cluster-labelling arithmetic at length and then summarised
the same arithmetic in the very next paragraph, while the appendix carried the long version
word for word.

Every guard in the repository stayed green. Each number in the duplicated paragraph was
correct and registered; `reproduce.py` reported no drift; and the near-duplicate scan in
`test_one_quantity_one_number.py` could not see it either, because that scan looks for one
quantity stated two WAYS and this was one quantity stated one way, twice.

The assembler now refuses to build in that state. This is the test that the refusal works,
which the guard did not have when it was written — eleven other guards in this suite carry a
firing test and this was the twelfth without one.

The build inputs are gitignored: they are the author's working copy of nineteen rounds of
audited prose, not part of the replication package. So this skips in a clean clone and says
so, the way `test_registration_pin.py` skips without a repository.

The directory holding them is named by construction rather than written out, which is the
convention `test_package_integrity.py` uses on itself and enforces on everything shipped: a
published file must not print a path the package does not contain, because that sends a reader
nowhere. This file is shipped; the directory is not.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / ("_" + "work")
ASSEMBLE = BUILD_DIR / "assemble.py"


@pytest.fixture(scope="module")
def asm():
    if not ASSEMBLE.exists():
        pytest.skip("the manuscript build inputs are not in this tree")
    sys.path.insert(0, str(BUILD_DIR))
    import assemble
    return assemble


def _part(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_the_real_manuscript_lifts_every_line_once(asm):
    """The state the shipped paper is in, asserted rather than assumed."""
    twice = {n: w for n, w in asm.lift_owners(asm.PARTS).items() if len(w) > 1}
    assert not twice, f"source line(s) lifted into more than one section: {twice}"
    total = asm.lift_owners(asm.PARTS)
    assert len(total) > 100, (
        f"only {len(total)} source lines are lifted at all; the marker format has moved and "
        f"this guard has stopped reading anything")


def test_the_lift_guard_fires_on_the_duplicate_it_exists_for(asm, tmp_path):
    """Source 359 in two parts, which is the defect in the shape it really had."""
    a = _part(tmp_path, "05_howfar.md", "### 5.2\n\n@@DRAFT 357-357\n\n@@DRAFT 359-359\n")
    b = _part(tmp_path, "12_appendix.md", "### C.2\n\n@@DRAFT 359-359\n\n@@DRAFT 361-361\n")
    owners = asm.lift_owners([a, b])
    assert sorted(owners) == [357, 359, 361], f"the marker scan read {sorted(owners)}"
    assert owners[359] == ["05_howfar.md:5", "12_appendix.md:3"], (
        f"the duplicate is not reported with both homes: {owners[359]}")
    assert owners[357] == ["05_howfar.md:3"] and owners[361] == ["12_appendix.md:5"]


def test_a_range_counts_every_line_inside_it(asm, tmp_path):
    """`@@DRAFT 109-122` claims fourteen lines, not one, and an overlap inside a range is the
    version of this defect nobody would notice by reading the markers."""
    a = _part(tmp_path, "one.md", "@@DRAFT 109-122\n")
    b = _part(tmp_path, "two.md", "@@DRAFT 115-115\n")
    owners = asm.lift_owners([a, b])
    assert len(owners) == 14, f"a 14-line range claimed {len(owners)} lines"
    assert len(owners[115]) == 2, "an overlap inside a range went unreported"
    assert len(owners[109]) == 1 and len(owners[122]) == 1


def test_the_keep_title_marker_is_still_a_lift(asm, tmp_path):
    """`@@DRAFT 305-305 keep-title` is the same claim on the same line with a flag after it.
    A scan keyed on the bare form would let every titled lift collide silently."""
    a = _part(tmp_path, "one.md", "@@DRAFT 305-305 keep-title\n")
    b = _part(tmp_path, "two.md", "@@DRAFT 305-305\n")
    owners = asm.lift_owners([a, b])
    assert len(owners.get(305, [])) == 2, (
        "a keep-title lift is not counted as an owner, so it can duplicate any other lift "
        "without the build noticing")


def test_prose_that_merely_mentions_a_marker_is_not_a_lift(asm, tmp_path):
    """The appendix discusses `@@DRAFT` ranges in prose. A scan that matched those would report
    duplicates that do not exist, and the first version of this check was a `in` test."""
    a = _part(tmp_path, "one.md", "The block lifted at @@DRAFT 359-359 is discussed here.\n"
                                  "See also @@DRAFT 400-400 in passing.\n")
    assert asm.lift_owners([a]) == {}, "an inline mention was counted as a lift"
