"""The harvest decides which rows can ever become a mark, so its filter decides the sample.

These tests run without touching the network: the filter and the price arithmetic are
pure functions over a frame shaped like the SEC data set.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import nport_bulk as nb


def _rows():
    """One keeper plus one of every reason to reject."""
    return pd.DataFrame([
        # keeper: private equity holding, share-denominated
        dict(tag="keep", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="Y", ASSET_CAT="EC",
             UNIT="NS", BALANCE="1000", CURRENCY_VALUE="50000"),
        # keeper: preferred equity is also equity
        dict(tag="keep_pref", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="Y", ASSET_CAT="EP",
             UNIT="NS", BALANCE="200", CURRENCY_VALUE="1000"),
        # observable inputs: a Level-1 quote is not a private mark
        dict(tag="level1", FAIR_VALUE_LEVEL="1", IS_RESTRICTED_SECURITY="Y", ASSET_CAT="EC",
             UNIT="NS", BALANCE="1000", CURRENCY_VALUE="50000"),
        # unrestricted: a public security carried at Level 3 for some other reason
        dict(tag="unrestricted", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="N", ASSET_CAT="EC",
             UNIT="NS", BALANCE="1000", CURRENCY_VALUE="50000"),
        # debt, not equity
        dict(tag="debt", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="Y", ASSET_CAT="DBT",
             UNIT="NS", BALANCE="1000", CURRENCY_VALUE="50000"),
        # principal amount: dividing it by anything does not give a price per share
        dict(tag="principal", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="Y", ASSET_CAT="EC",
             UNIT="PA", BALANCE="1000", CURRENCY_VALUE="50000"),
    ])


def test_filter_keeps_share_denominated_level3_equity():
    kept = set(nb.select_private(_rows()).tag)
    assert kept == {"keep", "keep_pref", "unrestricted"}, kept


def test_filter_is_not_vacuous():
    """A filter that rejected everything, or kept everything, would pass a weaker test."""
    assert len(nb.select_private(_rows())) == 3
    assert len(_rows()) == 6


def test_the_restricted_flag_does_not_filter():
    """Filers disagree about the flag for the same security. On 2026-04-30 Fidelity
    reported Revolut as restricted and ARK reported the identical holding as unrestricted,
    so filtering on it drops houses rather than securities — and it dropped the one house
    that disagreed, turning a 35% cross-family spread into zero."""
    revolut = pd.DataFrame([
        dict(tag="fidelity", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="Y", ASSET_CAT="EC",
             UNIT="NS", BALANCE="100", CURRENCY_VALUE="149597"),
        dict(tag="ark", FAIR_VALUE_LEVEL="3", IS_RESTRICTED_SECURITY="N", ASSET_CAT="EC",
             UNIT="NS", BALANCE="100", CURRENCY_VALUE="111031"),
    ])
    kept = nb.select_private(revolut)
    assert set(kept.tag) == {"fidelity", "ark"}, "the flag is still acting as a filter"

    priced = nb.price_per_share(kept)
    spread = priced.pps.max() / priced.pps.min() - 1
    assert spread > 0.3, "both houses must be present for the disagreement to be visible"


def test_price_per_share_is_value_over_shares_and_drops_unusable_rows():
    df = pd.DataFrame([
        dict(BALANCE="1000", CURRENCY_VALUE="50000"),      # 50.00
        dict(BALANCE="0", CURRENCY_VALUE="50000"),         # no shares -> undefined
        dict(BALANCE="1000", CURRENCY_VALUE="0"),          # no value -> not a mark
        dict(BALANCE="oops", CURRENCY_VALUE="50000"),      # unparseable
    ])
    out = nb.price_per_share(df)
    assert len(out) == 1
    assert abs(out.pps.iloc[0] - 50.0) < 1e-9


def test_appended_gzip_members_read_back_as_one_frame(tmp_path):
    """The harvest appends one gzip member per quarter. Nothing guarantees a reader
    stitches those members together, and a silent truncation would quietly drop every
    quarter after the first."""
    p = tmp_path / "chunked.csv.gz"
    a = pd.DataFrame({"src_quarter": ["2019q4"] * 3, "v": [1, 2, 3]})
    b = pd.DataFrame({"src_quarter": ["2020q1"] * 2, "v": [4, 5]})
    a.to_csv(p, index=False, compression="gzip")
    b.to_csv(p, mode="a", header=False, index=False, compression="gzip")

    back = pd.read_csv(p)
    assert len(back) == 5, f"reader saw {len(back)} rows, not 5 - members were dropped"
    assert set(back.src_quarter) == {"2019q4", "2020q1"}
    assert list(back.v) == [1, 2, 3, 4, 5]
