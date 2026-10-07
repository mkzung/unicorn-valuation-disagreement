"""The resolver is the one component that can create a result out of nothing.

Merging two securities that belong to different companies invents a cross-family price
spread nobody filed, and at population scale nobody reads the issuer strings to catch it.
These tests hold the rule to the companies a human labelled by hand in the first version's
data/fund_marks.csv, and to the specific traps that broke the first implementation.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import entity_resolution as er


@pytest.fixture(scope="module")
def labelled():
    return er.hand_labelled()


def test_ground_truth_has_something_to_prove(labelled):
    """A test that silently reads nothing proves nothing: the hand-labelled set must
    actually contain several companies and many more raw strings than companies."""
    assert len(labelled) > 300
    assert labelled.company.nunique() >= 15
    assert labelled.ISSUER_NAME.nunique() > 3 * labelled.company.nunique()


def test_no_two_companies_are_fused(labelled):
    """The asymmetric failure: fusion manufactures a spread. Zero tolerance."""
    _, fused = er.disagreements(labelled)
    assert not fused, f"resolver fused distinct companies: {fused}"


def test_no_company_is_split(labelled):
    split, _ = er.disagreements(labelled)
    assert not split, f"resolver split a company across labels: {split}"


def test_placeholder_cusips_never_join_anything():
    """000000000 and 999999999 are filler. Joining on either merges every company that
    used the same filler - which is exactly how Discord, Epic Games and Ramp became one."""
    for junk in ["000000000", "999999999", "N/A", "", "nan"]:
        assert er.clean_cusip(junk) == "", junk
    assert er.clean_cusip("38259P508") == "38259P508"

    df = pd.DataFrame({
        "ISSUER_NAME": ["Discord Inc", "Epic Games Inc", "Ramp Business Corp"],
        "ISSUER_CUSIP": ["999999999", "999999999", "999999999"],
        "ISSUER_LEI": ["", "", ""],
    })
    labels, _, _ = er.resolve(df)
    assert labels.nunique() == 3, f"placeholder CUSIP fused companies: {list(labels)}"


def test_feeder_vehicles_resolve_to_the_underlying_and_are_flagged():
    """A feeder names its company inside brackets. Stripping brackets throws away the only
    identifying text; keeping the vehicle name splits the company. Both are wrong."""
    df = pd.DataFrame({
        "ISSUER_NAME": [
            "OpenAI Group PBC",
            "Studio Type One Soul II LLC (OpenAI)",
            "DXYZ OAI I LLC (economic exposure to OpenAI Global LLC, Profit Participation Units)",
            "Goanna Capital 26E LLC (invested in OpenAI Group PBC Series C Preferred Stock)",
        ],
        "ISSUER_CUSIP": [""] * 4,
        "ISSUER_LEI": [""] * 4,
    })
    labels, _, wrapper = er.resolve(df)
    assert labels.nunique() == 1, f"feeders did not resolve to one company: {list(labels)}"
    assert list(wrapper) == [False, True, True, True]


def test_share_class_parenthetical_is_not_a_feeder():
    """"(Class A Common Stock)" describes the security, not a wrapper around another firm."""
    df = pd.DataFrame({
        "ISSUER_NAME": ["Ramp Business Corporation (Class A Common Stock)",
                        "Ramp Business Corporation (Series E-3 Preferred Stock)"],
        "ISSUER_CUSIP": ["", ""], "ISSUER_LEI": ["", ""],
    })
    labels, _, wrapper = er.resolve(df)
    assert labels.nunique() == 1
    assert not wrapper.any()


def test_longer_legal_names_merge_only_when_declared():
    """There is no containment rule. "ANDURIL INDUSTRIES" joins "ANDURIL" because the
    alias list says so, and nothing generalises from that: RAMP must not reach RAMPART,
    and an undeclared longer name stays separate rather than being absorbed on a hunch."""
    df = pd.DataFrame({
        "ISSUER_NAME": ["Anduril Inc", "Anduril Industries Inc", "Ramp Inc", "Rampart Inc",
                        "Acme Inc", "Acme Robotics Inc"],
        "ISSUER_CUSIP": [""] * 6, "ISSUER_LEI": [""] * 6,
    })
    keys, _, _ = er.resolve(df)
    assert keys.iloc[0] == keys.iloc[1], "declared alias did not merge"
    assert keys.iloc[2] != keys.iloc[3], "RAMP absorbed RAMPART"
    assert keys.iloc[4] != keys.iloc[5], "an undeclared longer name was absorbed"


def test_labels_repeat_but_keys_do_not():
    """Two companies whose issuer names are both missing share a display label. Grouping
    on that label pooled Gusto with Canva and produced a spread of eighteen million
    percent, so the key must separate them even when the label cannot."""
    df = pd.DataFrame({
        "ISSUER_NAME": [None, None, "Gusto Inc", "Canva Inc"],
        "ISSUER_CUSIP": [""] * 4, "ISSUER_LEI": [""] * 4,
    })
    keys, labels, _ = er.resolve(df)
    assert keys.nunique() == 4, f"keys collapsed: {list(keys)}"
    assert labels.iloc[0] == labels.iloc[1], "the two nameless rows should share a label"


def test_ordinary_names_are_not_read_as_feeders():
    """"Holdings Inc" contains the letters "holdings in". Matching the look-through phrase
    without a closing word boundary turned "FANATICS HOLDINGS INC CLASS A" into a feeder
    holding a company called "C", and fused Stripe into it through the same route."""
    df = pd.DataFrame({
        "ISSUER_NAME": ["FANATICS HOLDINGS INC CLASS A",
                        "Stripe Global Holdings Inc. (Class B Common Stock)",
                        "Disco Topco Holdings (Cayman) LP Series E",
                        "MEXICO PACIFIC LIMITED LLC (MPL) SERIES A"],
        "ISSUER_CUSIP": [""] * 4, "ISSUER_LEI": [""] * 4,
    })
    keys, labels, wrapper = er.resolve(df)
    assert not wrapper.any(), f"ordinary names flagged as feeders: {list(labels[wrapper])}"
    assert keys.nunique() == 4, f"names fused: {list(labels)}"
    assert set(labels) == {"FANATICS", "STRIPE", "DISCO TOPCO", "MEXICO PACIFIC"}, list(labels)


def test_aliases_are_declared_not_inferred():
    """Anything text cannot decide is an explicit, published judgement."""
    assert er.ALIASES["DOUYIN"] == "BYTEDANCE"
    df = pd.DataFrame({"ISSUER_NAME": ["ByteDance Ltd", "DOUYIN CO LTD"],
                       "ISSUER_CUSIP": ["", ""], "ISSUER_LEI": ["", ""]})
    labels, _, _ = er.resolve(df)
    assert labels.nunique() == 1


def test_a_cluster_label_does_not_depend_on_the_order_of_the_file():
    """Two names tied for commonest must give the same label whichever came first.

    `value_counts().idxmax()` returned whichever tied value pandas met first, and 290 of the
    19,056 clusters in the population panel have a tied top name, so the label was a
    function of file order. Nothing numeric hangs on the label — the key is the cluster
    root — but `company_class` and `reconcile_versions` use the same helper where a table
    row and a lookup do carry the name.
    """
    s = pd.Series(["BRAVO", "BRAVO", "ALPHA", "ALPHA", "CHARLIE"])
    assert er.modal(s) == "ALPHA"
    assert er.modal(s[::-1]) == "ALPHA", "the label moved when the rows were reversed"
    assert er.modal(pd.Series(["ZULU", "ZULU", "ZULU", "ALPHA"])) == "ZULU", \
        "a clear winner must still win; this is a tie-break, not an alphabetical sort"


def test_the_label_tie_break_is_reachable_in_the_real_panel():
    """A tie-break nothing ties on is a guard with no subject.

    Counted once, on the committed population marks: if this ever reads zero the helper can
    be replaced by `idxmax` again and nobody would be any the wiser.
    """
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[1] / "data" / "nport_population_marks.csv.gz"
    if not src.exists():
        pytest.skip("no committed population marks in this tree")
    d = pd.read_csv(src, usecols=["ISSUER_NAME", "ISSUER_CUSIP", "ISSUER_LEI"])
    root, _label, _w = er.resolve(d)
    df = pd.DataFrame({"root": root.values, "nm": d.ISSUER_NAME.astype(str).values})
    tied = 0
    for _, s in df.groupby("root").nm:
        vc = s.value_counts()
        tied += len(vc) > 1 and int((vc == vc.iloc[0]).sum()) > 1
    assert tied > 100, f"only {tied} clusters have a tied top name; the tie-break is idle"
