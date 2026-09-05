"""What the disagreement does to net asset value, and whether it is forecastable.

The paper measures how far apart houses mark the same private share. That is an accounting
fact until someone says what it costs, and the cost lands in one place: a mutual fund's net
asset value is the price at which its investors buy and sell. If two houses carry one company
at prices 12% apart, two sets of investors are credited with different value for the same
asset on the same day, and one of them transacts at a number the other's filing contradicts.
Zitzewitz (2003) showed a *stale* NAV is exploitable; this is the same question with a
different cause, and it has not been asked of private marks because nobody has had the
population to ask it on.

Two quantities, and neither needs a byte of new data — `NET_ASSETS` is on every row of the
panel already.

THE WEDGE
For every fund holding a company inside a comparable cell, reprice its position at the
cross-house consensus and ask how many basis points of THAT FUND'S OWN net assets move. That
is the size of the disagreement seen from the only position in which it is a cost rather than
a curiosity: the person who owns the fund.

The consensus is the median of house medians, so a complex filing thirty series cannot vote
thirty times, and a fund at the consensus contributes zero by construction.

THREE FILTERS, AND WHY A NAV STATISTIC NEEDS ALL THREE WHERE A SPREAD NEEDED NONE
Section 5's median absorbs a handful of contaminated cells. This measure cannot, because its
entire content is in the tail — and each filter below was added because the tail said so.

1. ONE PRICE PER FUND PER COMPANY. The first run's largest wedge was JPMorgan on Claire's
   Stores: $881 a share against a $12.50 consensus. JPMorgan files *two lines* for Claire's
   in each fund, one at $10.00 and one at $1,765.66. Two prices under one issuer key are two
   instruments, and the value-weighted blend of them is not a price at all. A fund whose own
   lines disagree by more than `LINE_TOL` is dropped: its book says the issuer key covers more
   than one security, which is section 3.2's problem arriving where it does real damage.

2. ONE SERIES. The next run's ten largest were all SpaceX — Baron at $1,294 against a $527
   consensus, 2,227 basis points of one fund's net assets. That is the multi-class structure
   section 4.3 excludes SpaceX for, and the 4x guard passes it at a ratio of 2.5. The wedge
   therefore runs on section 3.3's like-for-like restriction: cells whose filings never name
   two different letters.

3. VENTURE-BACKED. The filing system carries buyout stubs, reorganisation equity and delisted
   microcaps at Level 3, and section 5.2 separates them because only the venture-backed names
   are what this paper is about. The mixed-panel figure is reported beside the headline.

Everything is recomputed at the position unit — including the cell membership and the class
guard — because mixing units is what produced the Claire's row: section 5's cells are built on
row-level prices and a wedge is a property of the position.

WHY THE FORECASTABILITY TEST IS LAGGED
A wedge matters more if it is predictable: an investor who knows which way a fund's private
mark will move knows something about tomorrow's NAV today.

The obvious test — does a house's deviation at t predict its own change from t to t+1 — is
mechanically negative and therefore worthless. Write a house's mark as p = v + e. The house
with the largest e_t is selected partly on noise, and its next change carries -e_t inside it.
Regression to the mean produces the "result" whether or not anything reverts.

`reversion` selects on the deviation at t-1 and measures the change from t to t+1, so the
selection noise is independent of the measured change. The biased version is computed too and
printed beside it, because it is what a reader would have run.

Run:  python3 src/nav_wedge.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop

OUT = ROOT / "data" / "nav_wedge.csv"
STATS = ROOT / "data" / "nav_wedge_stats.csv"

# A fund's own lines for one company must agree to this before its position is a price. Half a
# percent, the same tolerance section 6.2 uses to decide whether a mark moved.
LINE_TOL = 0.005
# Nothing in this module may ask whether two floats are equal. A deviation of 1e-17 is a
# consensus house, not a house with a side, and a change of 1e-17 is a mark that did not move.
# The first version used `== 0` and `np.sign`, and a round-trip through the committed CSV moved
# the cell count from 498 to 481 — the same panel, a different answer, which is the failure the
# replication note says this repository does not have.
ZERO = 1e-9
# A fund-date is "materially exposed" at this many basis points of its own net assets. Ten is a
# label on a curve `exposure_ladder` prints in full, not a threshold the result rests on.
MATERIAL_BPS = 10.0


def _numeric(x: pd.DataFrame) -> pd.DataFrame:
    """Coerce every column this module does arithmetic on, and prove it.

    `balance` and `NET_ASSETS` arrive as object columns. Summing an object column concatenates
    the strings instead of adding them, which is a silent wrong answer rather than an error.
    """
    x = x.copy()
    for col in ("balance", "val_usd", "pps", "NET_ASSETS"):
        x[col] = pd.to_numeric(x[col], errors="coerce")
    x = x.rename(columns={"NET_ASSETS": "net_assets"})
    x = x[(x.net_assets > 0) & (x.balance > 0) & (x.val_usd > 0)]
    assert all(pd.api.types.is_numeric_dtype(x[c])
               for c in ("balance", "val_usd", "pps", "net_assets")), "non-numeric survived"
    return x


def fund_positions(d: pd.DataFrame) -> pd.DataFrame:
    """One row per fund, company and date — with the funds whose own lines disagree removed."""
    x = _numeric(pop.comparable(d))
    # The key is the fund, not the fund plus two columns the fund determines. `SERIES_ID` is
    # empty for 52,774 of the comparable rows — closed-end and interval funds do not file a
    # series identifier, which `population.fund_key` documents and works around — and pandas
    # drops null keys by default, so a fifth of the panel disappeared here, silently, BEFORE
    # the five-fund bar and the two-house bar could see it. `REGISTRANT_NAME` is worse than
    # redundant: 324 funds file under more than one spelling of their registrant, so keying on
    # it splits one fund into several rows. Both are carried as attributes instead.
    f = (x.groupby(["company", "dt", "fund", "house"])
          .agg(lines=("pps", "size"), lo_line=("pps", "min"), hi_line=("pps", "max"),
               balance=("balance", "sum"), val_usd=("val_usd", "sum"),
               net_assets=("net_assets", "max"),
               SERIES_ID=("SERIES_ID", "first"),
               REGISTRANT_NAME=("REGISTRANT_NAME", "first")).reset_index())
    f["own_pps"] = f.val_usd / f.balance
    f["one_price"] = f.hi_line / f.lo_line <= 1 + LINE_TOL
    return f


def one_series_cells(d: pd.DataFrame, keys: set) -> set:
    """Of the given cells, those whose filings never name two different series letters."""
    x = pop.comparable(d)
    x = x[[k in keys for k in zip(x.company, x.dt)]].copy()
    x["ser"] = pop.series_letters(x)
    n = (x.groupby(["company", "dt"]).ser
          .agg(lambda s: len(set().union(*s)) if len(s) else 0))
    return set(n[n < 2].index)


def _band(p: pd.DataFrame) -> pd.Series:
    """How far a position's own price is from its cell's consensus, as a ratio either way."""
    return pd.concat([p.own_pps / p.consensus_pps, p.consensus_pps / p.own_pps],
                     axis=1).max(axis=1)


def class_guard_cost(d: pd.DataFrame | None = None) -> dict:
    """What the position-level class guard removes, so §11.1's example is recomputed.

    The guard is applied inside `positions`, so by the time anything downstream sees the panel
    these rows are gone. This rebuilds the panel one step short of the guard and reports the
    worst row it removes. Every figure §11.1 prints about First Trust and Epic Games comes from
    here rather than from a note, which is the whole point: the example that justifies a filter
    has to be recomputed with the filter.
    """
    p = positions(d, _skip_class_guard=True)
    band = _band(p)
    bad = p[band > pop.CLASS_GUARD]
    if bad.empty:
        return {"removed_positions": 0}
    w = bad.reindex((bad.val_usd - bad.balance * bad.consensus_pps).abs()
                    .sort_values(ascending=False).index).iloc[0]
    return {
        "removed_positions": len(bad),
        "worst_shares": float(w.balance), "worst_pps": float(w.own_pps),
        "worst_consensus_pps": float(w.consensus_pps),
        "worst_net_assets_musd": float(w.net_assets / 1e6),
        "worst_wedge_bps": float((w.val_usd - w.balance * w.consensus_pps) / w.net_assets * 1e4),
    }


def positions(d: pd.DataFrame | None = None, one_series: bool = True,
              venture_only: bool = True, _skip_class_guard: bool = False) -> pd.DataFrame:
    """Fund positions inside comparable cells, with the NAV wedge each one carries.

    Cell membership, the class guard and the consensus are all rebuilt here at the POSITION
    unit rather than taken from `population.cells`, which builds them on filing lines. The two
    units disagree exactly where a fund files one company twice, and that is the case this
    measure is most sensitive to.
    """
    d = pop.panel()[0] if d is None else d
    f = fund_positions(d)
    f = f[f.one_price]

    house = (f.groupby(["company", "dt", "house"]).own_pps.median()
              .rename("house_pps").reset_index())
    cell = (house.groupby(["company", "dt"])
                 .agg(n_houses=("house", "nunique"), lo=("house_pps", "min"),
                      hi=("house_pps", "max")).reset_index())
    breadth = (f.groupby(["company", "dt"]).fund.nunique().rename("n_funds").reset_index())
    cell = cell.merge(breadth, on=["company", "dt"])
    cell = cell[(cell.n_funds >= pop.MIN_FUNDS) & (cell.n_houses >= pop.MIN_FAMS)
                & (cell.hi / cell.lo <= pop.CLASS_GUARD)].copy()
    cell["spread_pct"] = (cell.hi / cell.lo - 1) * 100
    cell["consensus_pps"] = (house.merge(cell[["company", "dt"]], on=["company", "dt"])
                                  .groupby(["company", "dt"]).house_pps.median()
                                  .reindex(pd.MultiIndex.from_frame(cell[["company", "dt"]]))
                                  .to_numpy())

    keys = set(zip(cell.company, cell.dt))
    if one_series:
        keep = one_series_cells(d, keys)
        cell = cell[[k in keep for k in zip(cell.company, cell.dt)]]
    if venture_only:
        # The panel's own `label` column is the resolver's provenance tag, not the venture
        # classification — reading it as one silently returned an empty frame, which is the
        # good failure mode. The classification lives where section 5.2 puts it.
        cls = pd.read_csv(ROOT / "data" / "company_classification.csv")
        keep_co = set(cls[cls.label == "venture"].company)
        cell = cell[cell.company.isin(keep_co)]

    p = (f.merge(cell[["company", "dt", "n_houses", "n_funds", "spread_pct", "consensus_pps"]],
                 on=["company", "dt"], how="inner")
          .merge(house, on=["company", "dt", "house"], how="left"))
    # The class guard again, at the POSITION unit. It runs above on house medians, so a single
    # fund can carry a unit-convention price inside a cell whose houses look fine: First Trust
    # files 2,145,462 Epic Games "shares" at $1.00 against a $637 consensus and 1,873 shares at
    # $555.65 six months later, which is dollars of exposure written into a share count. At the
    # house level its median is pulled back inside the 4x band by its other funds; at the
    # position level the row survives and repricing it moves $1.4bn of a $32m fund — a wedge of
    # 421,062 basis points. This is the same artifact `one_price` removes across a fund's own
    # lines, expressed across funds of one house instead, and it is removed by the same rule.
    if not _skip_class_guard:
        p = p[_band(p) <= pop.CLASS_GUARD].copy()
    p["repriced_usd"] = p.balance * p.consensus_pps
    p["wedge_usd"] = p.val_usd - p.repriced_usd
    p["wedge_bps"] = p.wedge_usd / p.net_assets * 1e4
    p["own_vs_consensus_pct"] = (p.own_pps / p.consensus_pps - 1) * 100
    p["position_pct_of_nav"] = p.val_usd / p.net_assets * 100
    return p.sort_values(["company", "dt", "fund"]).reset_index(drop=True)


def fund_dates(p: pd.DataFrame | None = None) -> pd.DataFrame:
    """Per fund and report date, the net wedge across all its exposed private positions."""
    p = positions() if p is None else p
    if p.empty:
        return p
    return (p.groupby(["fund", "house", "dt"])
             .agg(positions=("company", "nunique"), net_assets=("net_assets", "max"),
                  booked_usd=("val_usd", "sum"), wedge_usd=("wedge_usd", "sum"),
                  SERIES_ID=("SERIES_ID", "first"),
                  REGISTRANT_NAME=("REGISTRANT_NAME", "first"))
             .reset_index()
             .assign(wedge_bps=lambda t: t.wedge_usd / t.net_assets * 1e4,
                     private_pct_of_nav=lambda t: t.booked_usd / t.net_assets * 100)
             .sort_values("wedge_bps"))


def _no_series(fd: pd.DataFrame) -> pd.Series:
    """Fund-dates filed by a vehicle with no series identifier, aligned to `fd`'s index."""
    s = fd.SERIES_ID
    return s.isna() | (s.astype(str).str.strip().isin({"", "None", "nan"}))


def wedge_summary(p: pd.DataFrame | None = None) -> dict:
    """The size of the NAV wedge, per position and per fund-date."""
    p = positions() if p is None else p
    fd = fund_dates(p)
    a = fd.wedge_bps.abs()
    return {
        "positions": len(p), "funds": int(p.fund.nunique()),
        "companies": int(p.company.nunique()), "houses": int(p.house.nunique()),
        "cells": int(p.groupby(["company", "dt"]).ngroups),
        "fund_dates": len(fd), "distinct_funds": int(fd.fund.nunique()),
        "median_abs_bps": float(a.median()), "p75_abs_bps": float(a.quantile(0.75)),
        "p90_abs_bps": float(a.quantile(0.90)), "p99_abs_bps": float(a.quantile(0.99)),
        "max_abs_bps": float(a.max()),
        "share_over_material_pct": float((a > MATERIAL_BPS).mean() * 100),
        "n_over_material": int((a > MATERIAL_BPS).sum()),
        "n_over_25bps": int((a > 25).sum()), "n_over_100bps": int((a > 100).sum()),
        "funds_over_material": int(fd[a > MATERIAL_BPS].fund.nunique()),
        "funds_over_100bps": int(fd[a > 100].fund.nunique()),
        # The vehicles that file no series identifier: interval funds, closed-end funds and
        # the tender-offer funds. An earlier version of this module made SERIES_ID a groupby
        # key, and pandas drops null keys by default, so every one of these disappeared before
        # the five-fund bar was applied. They are 7.7% of the fund-dates and three-quarters of
        # the fund-dates above a hundred basis points: the drop was not a random 20%, it was
        # the funds the SEC lets hold illiquid assets in size.
        "no_series_fund_dates": int(_no_series(fd).sum()),
        "no_series_fund_dates_pct": float(_no_series(fd).mean() * 100),
        "no_series_over_100bps": int((a[_no_series(fd)] > 100).sum()),
        "no_series_median_abs_bps": float(a[_no_series(fd)].median()),
        "gross_wedge_busd": float(p.wedge_usd.abs().sum() / 1e9),
        "net_wedge_busd": float(p.wedge_usd.sum() / 1e9),
        "booked_busd": float(p.val_usd.sum() / 1e9),
        "median_private_pct_of_nav": float(fd.private_pct_of_nav.median()),
        "max_private_pct_of_nav": float(fd.private_pct_of_nav.max()),
        # Why the median is small. The first draft of the section said "a large disagreement
        # about a small book", and its own arithmetic disagreed by a factor of twelve: 12% of a
        # 0.21% book is 2.5 bps, not 0.21. The real reason is the mass at zero — most funds sit
        # AT the consensus, so most positions carry no wedge at all.
        "at_consensus_pct": float((p.own_vs_consensus_pct.abs() < 0.01).mean() * 100),
        "zero_wedge_fund_dates_pct": float((fd.wedge_bps.abs() <= 1e-9).mean() * 100),
        "median_wedge_of_own_book_pct": float(
            (p.wedge_usd.abs() / p.val_usd * 100).median()),
        "median_cell_spread_pct": float(p.drop_duplicates(["company", "dt"]).spread_pct.median()),
    }


def exposure_ladder(p: pd.DataFrame | None = None,
                    cuts=(1, 5, 10, 25, 50, 100)) -> pd.DataFrame:
    """The whole curve, so `MATERIAL_BPS` is a label on it rather than a load-bearing choice."""
    fd = fund_dates(positions() if p is None else p)
    a = fd.wedge_bps.abs()
    return pd.DataFrame([{"bps_over": k, "fund_dates": int((a > k).sum()),
                          "share_pct": float((a > k).mean() * 100),
                          "distinct_funds": int(fd[a > k].fund.nunique())} for k in cuts])


def worst(p: pd.DataFrame | None = None, n: int = 8) -> pd.DataFrame:
    """The largest single-position wedges, named, so the tail can be read rather than trusted."""
    p = positions() if p is None else p
    q = p.reindex(p.wedge_bps.abs().sort_values(ascending=False).index).head(n)
    return q[["company", "dt", "house", "REGISTRANT_NAME", "own_pps", "consensus_pps",
              "own_vs_consensus_pct", "position_pct_of_nav", "wedge_bps"]].round(2)


def filter_cost(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """What each of the three filters removes, so none of them is taken on trust."""
    d = pop.panel()[0] if d is None else d
    rows = []
    for name, kw in [("all comparable cells", dict(one_series=False, venture_only=False)),
                     ("+ one series only", dict(one_series=True, venture_only=False)),
                     ("+ venture-backed only", dict(one_series=True, venture_only=True))]:
        p = positions(d, **kw)
        fd = fund_dates(p)
        a = fd.wedge_bps.abs()
        rows.append({"selection": name, "positions": len(p), "fund_dates": len(fd),
                     "median_abs_bps": round(float(a.median()), 2),
                     "p99_abs_bps": round(float(a.quantile(0.99)), 1),
                     "max_abs_bps": round(float(a.max()), 1),
                     "over_10bps": int((a > MATERIAL_BPS).sum())})
    return pd.DataFrame(rows)


def _dev_panel(p: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per company, date and house: its deviation from consensus, and its next move."""
    p = positions() if p is None else p
    h = (p.groupby(["company", "dt", "house"])
          .agg(house_pps=("house_pps", "max"), consensus_pps=("consensus_pps", "max"))
          .reset_index())
    h["dev"] = np.log(h.house_pps / h.consensus_pps)
    h = h.sort_values(["company", "house", "dt"])
    g = h.groupby(["company", "house"])
    h["dt_next"], h["dt_lag"] = g.dt.shift(-1), g.dt.shift(1)
    h["chg_next"] = np.log(g.house_pps.shift(-1) / h.house_pps)
    h["dev_lag"] = g.dev.shift(1)
    h["dev_next"] = g.dev.shift(-1)
    # A gap longer than a quarter is a hole in the record, not a decision — section 6.2's rule.
    h["step_ok"] = (h.dt_next - h.dt).dt.days.le(100)
    h["lag_ok"] = (h.dt - h.dt_lag).dt.days.le(100)
    return h


def reversion(p: pd.DataFrame | None = None, lagged: bool = True,
              require_move: bool = True) -> dict:
    """Does the house above consensus mark down, relative to the house below it?

    Within a cell, take the house with the highest deviation and the one with the lowest, and
    compare what each did to its OWN mark over the next reporting step. Paired inside the cell,
    so whatever happened to the company between the two dates is common to both.

    `lagged` selects on the deviation at the PREVIOUS date, so the selection noise cannot enter
    the measured change with a minus sign. `require_move` keeps only steps in which at least
    one of the two houses actually re-marked: most house-months carry no change at all, and a
    test dominated by zeros measures reporting frequency rather than valuation.
    """
    h = _dev_panel(p)
    key = "dev_lag" if lagged else "dev"
    ok = h.step_ok & h[key].notna() & h.chg_next.notna()
    if lagged:
        ok &= h.lag_ok
    h = h[ok]
    rows = []
    for (co, dt), g in h.groupby(["company", "dt"]):
        # A cell in which every house sits at the consensus has no house above it and no
        # house below it, and `idxmax` on tied values picks one arbitrarily. That is not a
        # theoretical worry here: 56% of positions ARE at the consensus, and without this skip
        # a round-trip of the same panel through the committed CSV — which loses 2e-13 of
        # precision — moves the count from 529 to 527, purely by flipping those ties. Cells
        # whose houses are not distinguishable are skipped.
        # `test_the_tie_guard_is_what_makes_the_two_paths_agree` pins both numbers.
        if g[key].max() - g[key].min() <= ZERO:
            continue
        # The skip above only catches a cell where EVERY house ties. Where the top is shared
        # and the bottom is not, `idxmax` separated the sharers by bit-equality — the one
        # comparison ZERO exists to forbid. 40 of the 421 cells reported here have two or more
        # houses at the top within ZERO and 16 of those are not bit-identical, so multiplying
        # every price by 1 +/- 1e-15, the size of a disagreement between two libms, moved the
        # old design from 226 of 415 to 223 of 412 and its one-sided sign p from 0.039 to
        # 0.052, across the threshold the section quoted. Choosing adversarially spans 0.005
        # to 0.19.
        #
        # A shared top is a SET, so "what the high house did next" is what houses in that
        # position did on average; unique extremes are unaffected. Dropping the ambiguous
        # cells gives p=0.036 and was rejected: ties are commoner where houses agree, so
        # dropping selects on the herding regime section 4.3 names.
        top = g.chg_next[g[key] >= g[key].max() - ZERO]
        bot = g.chg_next[g[key] <= g[key].min() + ZERO]
        # `require_move` asks whether anybody re-marked, so it reads the houses and not their
        # average: two tied houses that moved +x and -x average to zero and both re-marked.
        # The two forms drop the same 64 cells on this panel, which is the only reason the
        # averaged version was not also a change in the answer.
        if require_move and (top.abs() <= ZERO).all() and (bot.abs() <= ZERO).all():
            continue
        hi, lo = top.mean(), bot.mean()
        rows.append({"company": co, "dt": dt, "hi_chg": hi, "lo_chg": lo,
                     "diff": hi - lo})
    if len(rows) < 10:
        return {"cells": len(rows), "underpowered": True, "lagged": lagged}
    t = pd.DataFrame(rows)
    diff = t["diff"].to_numpy()
    neg, untied = int((diff < -ZERO).sum()), int((np.abs(diff) > ZERO).sum())
    return {
        "lagged": lagged, "require_move": require_move, "cells": len(t),
        "companies": int(t.company.nunique()),
        "median_diff_pct": float(np.median(diff) * 100),
        "hi_median_chg_pct": float(t.hi_chg.median() * 100),
        "lo_median_chg_pct": float(t.lo_chg.median() * 100),
        "negative": neg, "untied": untied,
        # `neg` counts the cells where the high house moved LESS, which is the hypothesis,
        # so the alternative is that negatives are MORE frequent than half. Written as
        # `less` first, this returned 0.99 and read as a clean null while the data said the
        # opposite — a p-value pointed backwards is worse than no p-value.
        "p_sign": float(binomtest(neg, untied, 0.5, alternative="greater").pvalue)
        if untied else float("nan"),
        "neg_share_pct": float(neg / untied * 100) if untied else float("nan"),
        "p_sign_two_sided": float(binomtest(neg, untied, 0.5).pvalue) if untied else float("nan"),
        "p_signed_rank": float(wilcoxon(diff, alternative="less").pvalue)
        if (np.abs(diff) > ZERO).any() else float("nan"),
    }


def persistence(p: pd.DataFrame | None = None) -> dict:
    """How much of a deviation is still there one reporting step later.

    A slope of the next deviation on this one. Measurement error in the regressor attenuates
    the slope toward zero, so whatever this returns is a FLOOR on how persistent deviations
    are, which is the direction that costs the argument rather than helping it.

    A HOUSE AT THE CONSENSUS HAS NO SIDE, AND THE FIRST VERSION COUNTED IT AS AGREEING WITH
    ITSELF. In a cell with an odd number of houses one of them IS the median, so its deviation
    is exactly zero by construction, and `np.sign(0) == np.sign(0)` scored those as "on the
    same side one step later". They are 62% of this sample. The share is now computed on the
    house-dates that have a side; the slope is reported both ways, because a consensus house
    is informative about a slope and meaningless in a share.
    """
    h = _dev_panel(p)
    h = h[h.step_ok & h.dev.notna() & h.dev_next.notna()]
    if len(h) < 50:
        return {"n": len(h), "underpowered": True}
    b = float(np.polyfit(h.dev.to_numpy(), h.dev_next.to_numpy(), 1)[0])
    sided = h[(h.dev.abs() > ZERO) & (h.dev_next.abs() > ZERO)]
    b_sided = float(np.polyfit(sided.dev.to_numpy(), sided.dev_next.to_numpy(), 1)[0])
    same = float((np.sign(sided.dev_next) == np.sign(sided.dev)).mean() * 100)
    return {"n": len(h), "companies": int(h.company.nunique()),
            "slope": b, "survives_pct": b * 100, "n_sided": len(sided),
            "slope_sided": b_sided, "same_side_pct": same,
            "at_consensus_pct": float((h.dev.abs() <= ZERO).mean() * 100)}


def design_key() -> str:
    """A content hash of everything these numbers are a function of.

    Same contract as `round_event_study.design_key`: the guard pins prose against a committed
    statistics file, and a committed artifact the guard trusts is a staleness hole unless
    something fails when its inputs move. Content, not mtime, because a clone does not
    preserve mtime.
    """
    h = hashlib.sha256()
    for f in (pop.MARKS, ROOT / "data" / "company_classification.csv"):
        with f.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    h.update(repr((LINE_TOL, MATERIAL_BPS, pop.MIN_FUNDS, pop.MIN_FAMS,
                   pop.CLASS_GUARD)).encode())
    return h.hexdigest()[:16]


def stats(p: pd.DataFrame | None = None) -> pd.DataFrame:
    """Every scalar the manuscript quotes from this module, in one long table."""
    p = positions() if p is None else p
    rows = list(wedge_summary(p).items())
    for _, r in exposure_ladder(p).iterrows():
        rows += [(f"over{int(r.bps_over)}_fund_dates", r.fund_dates),
                 (f"over{int(r.bps_over)}_share_pct", r.share_pct),
                 (f"over{int(r.bps_over)}_funds", r.distinct_funds)]
    fc = filter_cost()
    for i, r in fc.iterrows():
        rows += [(f"filter{i}_positions", r.positions), (f"filter{i}_fund_dates", r.fund_dates),
                 (f"filter{i}_median_abs_bps", r.median_abs_bps),
                 (f"filter{i}_max_abs_bps", r.max_abs_bps),
                 (f"filter{i}_over_10bps", r.over_10bps)]
    for lag in (True, False):
        rv = reversion(p, lagged=lag)
        k = "rev_lagged" if lag else "rev_same"
        for f in ("cells", "companies", "negative", "untied", "neg_share_pct", "p_sign",
                  "p_sign_two_sided", "p_signed_rank"):
            rows.append((f"{k}_{f}", rv.get(f, float("nan"))))
    for f, v in persistence(p).items():
        if isinstance(v, (int, float)):
            rows.append((f"persistence_{f}", v))
    rows += [(f"class_guard_{k}", v) for k, v in class_guard_cost().items()]
    out = pd.DataFrame(rows, columns=["statistic", "value"])
    out["value"] = out.value.astype(float)
    out.insert(0, "design_key", design_key())
    return out


def load_stats() -> pd.Series:
    """The committed statistics as a name -> value mapping, for the manuscript guard."""
    return pd.read_csv(STATS).set_index("statistic").value


def main() -> None:
    d, _ = pop.panel()
    p = positions(d)
    p.to_csv(OUT, index=False)
    s = wedge_summary(p)
    print("THE WEDGE — repricing a fund's private marks at the cross-house consensus, in basis "
          "points of that fund's own net assets")
    print(f"  {s['positions']:,} fund-positions · {s['funds']:,} funds · {s['cells']:,} cells · "
          f"{s['companies']} companies · {s['houses']} houses · {s['fund_dates']:,} fund-dates")
    print(f"  booked ${s['booked_busd']:.1f}B; gross wedge ${s['gross_wedge_busd']:.1f}B, "
          f"net ${s['net_wedge_busd']:+.1f}B")
    print(f"  private book as a share of net assets: median {s['median_private_pct_of_nav']:.2f}%, "
          f"max {s['max_private_pct_of_nav']:.1f}%")
    print(f"  |wedge| bps: median {s['median_abs_bps']:.2f}, p75 {s['p75_abs_bps']:.2f}, "
          f"p90 {s['p90_abs_bps']:.1f}, p99 {s['p99_abs_bps']:.1f}, max {s['max_abs_bps']:.0f}")
    print(f"  over {MATERIAL_BPS:.0f} bps: {s['n_over_material']:,} fund-dates "
          f"({s['share_over_material_pct']:.1f}%) on {s['funds_over_material']} distinct funds; "
          f"over 25 bps {s['n_over_25bps']}; over 100 bps {s['n_over_100bps']}")
    print("\nthe whole curve")
    print(exposure_ladder(p).round(2).to_string(index=False))
    print("\nwhat each filter costs, and what it removes from the tail")
    print(filter_cost(d).to_string(index=False))
    print("\nthe largest single-position wedges")
    print(worst(p).to_string(index=False))

    print("\n\nIS IT FORECASTABLE? the house above consensus against the house below it, over "
          "the next reporting step")
    for lag in (True, False):
        r = reversion(p, lagged=lag)
        name = ("selected on the PREVIOUS date (unbiased)" if lag
                else "selected on the SAME date (mechanically negative)")
        if r.get("underpowered"):
            print(f"  {name}: only {r['cells']} cells, underpowered")
            continue
        print(f"  {name}: {r['cells']} cells on {r['companies']} companies")
        print(f"    high house {r['hi_median_chg_pct']:+.2f}%, low house "
              f"{r['lo_median_chg_pct']:+.2f}%, difference {r['median_diff_pct']:+.2f} points; "
              f"high moves less in {r['negative']} of {r['untied']} untied, "
              f"sign p={r['p_sign']:.4f}, signed-rank p={r['p_signed_rank']:.4f}")
    pe = persistence(p)
    if not pe.get("underpowered"):
        print(f"\n  persistence: {pe['survives_pct']:.0f}% of a deviation survives one "
              f"reporting step, {pe['slope_sided']*100:.0f}% among the houses that have a side "
              f"(a floor either way — errors in the regressor attenuate it). "
              f"{pe['same_side_pct']:.0f}% of the {pe['n_sided']:,} sided deviations are on the "
              f"same side one step later; {pe['at_consensus_pct']:.0f}% of house-dates sit AT "
              f"the consensus and have no side at all (n={pe['n']:,}, "
              f"{pe['companies']} companies)")
    st = stats(p)
    st.to_csv(STATS, index=False)
    print(f"\n  wrote {OUT.relative_to(ROOT)} and {STATS.relative_to(ROOT)} "
          f"({len(st)} statistics, design key {st.design_key.iat[0]})")


if __name__ == "__main__":
    main()
