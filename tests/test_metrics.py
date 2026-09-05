import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _panel():
    return pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")


def test_gap_sign():
    df = _panel()
    gap = df.forge_val_busd / df.headline_val_busd - 1
    assert gap.loc["Anduril"] > 0      # secondary above last round
    assert gap.loc["Kraken"] < 0       # secondary below last round
    assert abs(gap.loc["Anthropic"]) < 0.02  # secondary ~= recent round


def test_overshoot_direction():
    v = pd.read_csv(ROOT / "data" / "ipo_validation.csv").set_index("company")
    ov = v.last_private_val_busd / v.ipo_val_busd - 1
    assert ov.loc["Instacart"] > 1.0      # >100% overshoot (down-round)
    assert ov.loc["SpaceX-xAI"] < 0       # undershoot (up-case)


def test_ipo_least_wrong_is_fund_mark():
    """The DIFFERENTIATOR (sec. 4.3): for the fund-held exits, the last pre-IPO N-PORT fund
    mark was the least-wrong signal vs the stale headline. v0.13 doubles the fund-held sample
    from 2 to 4 with two 2025 listings: Chime (down-round, mark -1% vs headline +116%) and
    Figma (a FLOOR case where the maximally-stale 2021 headline UNDERshot, -48%, and the mark
    -28% was still less wrong). Klarna's interim down round overcorrected below the IPO yet
    still beat the headline."""
    import validation as val
    v = val.add_errors(val.load()).set_index("company")
    for co in ["Instacart", "Reddit", "Chime"]:                     # down-round listings the mark ~nailed
        assert v.loc[co, "preipo_signal_type"] == "fund_mark"
        assert abs(v.loc[co, "signal_err_pct"]) < 15                 # fund mark within ~15% of the IPO
        assert abs(v.loc[co, "overshoot_pct"]) > 50                  # headline far off (+294%/+56%/+116%)
        assert abs(v.loc[co, "signal_err_pct"]) < abs(v.loc[co, "overshoot_pct"]) / 3
        assert v.loc[co, "least_wrong"] == "fund mark"
    # Figma: a FLOOR case (headline UNDERshot the IPO) -- the fund mark is still the less-wrong signal
    assert v.loc["Figma", "preipo_signal_type"] == "fund_mark"
    assert v.loc["Figma", "overshoot_pct"] < 0                       # 2021 headline below the realized IPO
    assert abs(v.loc["Figma", "signal_err_pct"]) < abs(v.loc["Figma", "overshoot_pct"])
    assert v.loc["Figma", "least_wrong"] == "fund mark"
    # across the seven fund-held exits (v0.15) the fund mark's median |error| is far smaller
    fm = v[v.preipo_signal_type == "fund_mark"]
    assert len(fm) == 7
    assert fm["signal_err_pct"].abs().median() < 15                 # ~11%
    assert fm["overshoot_pct"].abs().median() > 30                  # ~48%
    # fund mark is least-wrong in 5 of 7; the two exceptions are recent fairly-priced rounds
    assert (fm["least_wrong"] == "fund mark").sum() == 5
    # Klarna: 2022 down round overcorrected (< -40%) but is still less wrong than the +205% headline
    assert v.loc["Klarna", "signal_err_pct"] < -40
    assert abs(v.loc["Klarna", "signal_err_pct"]) < abs(v.loc["Klarna", "overshoot_pct"])
    # the flat/up recent-vintage exits without a mutual-fund mark have no comparable interim signal
    assert v.loc["CoreWeave", "least_wrong"] == "(no interim signal)"


def test_both_headline_medians_are_a_named_single_exit():
    """On seven exits the median IS an observation, and §7.1 now says whose.

    The paper prints "median |error| 11% against 48%" beside Figma's own -48% two sentences
    earlier, as though they were two facts. They are one: with n=7 the fourth-ranked error is
    the median, and it is Figma's. The mark's 11% is ServiceTitan's. Stated in §7.1 because a
    referee who computes the median finds it landing exactly on a named case and is entitled
    to know whether that is construction or arithmetic.

    Pinned here so the identity cannot silently break: if an eighth exit is added, the median
    stops being one row and §7.1's sentence has to be rewritten rather than left standing.
    """
    import validation as val
    v = val.add_errors(val.load())
    fm = v[v.preipo_signal_type == "fund_mark"]
    assert len(fm) == 7, "n changed; §7.1's 'median of seven is one observation' no longer holds"
    hi = fm.set_index("company").overshoot_pct.abs()
    lo = fm.set_index("company").signal_err_pct.abs()
    assert hi.idxmin() != hi.idxmax()          # the ranking is not degenerate
    # Identity by rank, not by float comparison: for odd n the median is the middle element,
    # so the claim is "Figma is 4th of 7", which is exact and does not depend on how pandas
    # computes a median. Asserting `median() == hi["Figma"]` would be the float equality that
    # has already cost this repository three bugs.
    assert hi.rank().loc["Figma"] == 4, "the headline median is no longer Figma's own error"
    assert lo.rank().loc["ServiceTitan"] == 4, "the mark median is no longer ServiceTitan's"
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    body = draft.split("## 7. Which mark was right")[1].split("## 8.")[0]
    assert "is Figma's own" in body and "ServiceTitan's" in body, \
        "§7.1 no longer names the two exits its medians are"


def test_ipo_validation_provenance_and_bridge():
    """Every exit fact is sourced; fund-mark rows are SEC-anchored, and the stored implied
    valuation matches the IPO per-share bridge (implied = IPO_val * mark_pps / IPO_pps)."""
    import numpy as np
    import validation as val
    raw = val.load()
    for c in ["company", "last_private_val_busd", "ipo_val_busd", "direction",
              "preipo_signal_type", "source"]:
        assert c in raw.columns
    assert raw["source"].notna().all()
    assert raw["preipo_signal_type"].isin(["fund_mark", "down_round", "na"]).all()
    fm = raw[raw.preipo_signal_type == "fund_mark"]
    assert len(fm) >= 2
    assert fm["preipo_signal_source"].str.contains("N-PORT").all()          # SEC-anchored
    assert fm[["preipo_signal_pps", "ipo_pps"]].notna().all().all()
    bridge = fm["ipo_val_busd"] * fm["preipo_signal_pps"] / fm["ipo_pps"]
    assert np.allclose(bridge.values, fm["preipo_signal_busd"].astype(float).values, atol=0.1)


def test_v013_new_ipo_exits_chime_figma():
    """v0.13 doubles the fund-held IPO-exit sample from 2 to 4 with two 2025 listings. Pin the
    additions (each >=2-sourced, SEC-anchored marks) so a silent CSV edit is flagged, and confirm
    the last fund mark beats the headline in all four fund-held exits."""
    import validation as val
    raw = val.load().set_index("company")
    # Chime: 2021 $25B Series G -> 2025 $27/sh ~$11.6B IPO; 4 Alger funds marked $26.77 pre-IPO
    for col, want in {"last_private_val_busd": 25, "ipo_val_busd": 11.6, "ipo_pps": 27,
                      "preipo_signal_pps": 26.77}.items():
        assert abs(raw.loc["Chime", col] - want) < 1e-9, ("Chime", col)
    assert raw.loc["Chime", "direction"] == "down"
    assert "Alger" in raw.loc["Chime", "preipo_signal_source"]
    # Figma: a FLOOR case -- 2021 $10B Series E (last PRIMARY round) -> 2025 $33/sh $19.3B IPO
    for col, want in {"last_private_val_busd": 10, "ipo_val_busd": 19.3, "ipo_pps": 33,
                      "preipo_signal_pps": 23.73}.items():
        assert abs(raw.loc["Figma", col] - want) < 1e-9, ("Figma", col)
    assert raw.loc["Figma", "direction"] == "up"               # headline below the realized IPO
    assert "Fidelity" in raw.loc["Figma", "preipo_signal_source"]
    # the fund-held exit set is now 7 (v0.15); the fund mark is least-wrong in 5, Chime+Figma among them
    v = val.add_errors(val.load()).set_index("company")
    assert v.loc["Chime", "least_wrong"] == "fund mark"
    assert v.loc["Figma", "least_wrong"] == "fund mark"
    fm = v[v.preipo_signal_type == "fund_mark"]
    assert len(fm) == 7
    assert (fm["least_wrong"] == "fund mark").sum() == 5


def test_v015_new_ipo_exits_servicetitan_circle_klaviyo():
    """v0.15 expands the IPO-exit differentiator from 4 to 7 fund-held exits with the three
    broadly-fund-held 2023-25 listings not previously in the panel -- ServiceTitan, Circle,
    Klaviyo -- screened together so the additions cannot be cherry-picked. Each new fact is
    >=2-sourced with SEC-anchored marks; the honest result is 5-of-7 with TWO counter-examples
    (Klaviyo, Circle) where a recent fairly-priced headline beat the fund mark -- which sharpens
    the staleness mechanism (the fund mark's edge is the absence of staleness, not foresight)."""
    import validation as val
    raw = val.load().set_index("company")
    for col, want in {"last_private_val_busd": 7.6, "ipo_val_busd": 6.3, "ipo_pps": 71,
                      "preipo_signal_pps": 78.85}.items():
        assert abs(raw.loc["ServiceTitan", col] - want) < 1e-9, ("ServiceTitan", col)
    for col, want in {"last_private_val_busd": 9.5, "ipo_val_busd": 9.2, "ipo_pps": 30,
                      "preipo_signal_pps": 34.38}.items():
        assert abs(raw.loc["Klaviyo", col] - want) < 1e-9, ("Klaviyo", col)
    for col, want in {"last_private_val_busd": 7.65, "ipo_val_busd": 6.9, "ipo_pps": 31,
                      "preipo_signal_pps": 23.33}.items():
        assert abs(raw.loc["Circle", col] - want) < 1e-9, ("Circle", col)
    # SEC-anchored marks naming the disclosing family
    assert "T. Rowe Price" in raw.loc["ServiceTitan", "preipo_signal_source"]
    assert "ClearBridge" in raw.loc["Klaviyo", "preipo_signal_source"]
    assert "Fidelity" in raw.loc["Circle", "preipo_signal_source"]
    # the honest result: fund mark least-wrong in 5 of 7, Klaviyo & Circle the counter-examples
    v = val.add_errors(val.load()).set_index("company")
    assert v.loc["ServiceTitan", "least_wrong"] == "fund mark"      # +11% vs +21%
    assert v.loc["Klaviyo", "least_wrong"] == "headline"            # +3% headline beats +15% mark
    assert v.loc["Circle", "least_wrong"] == "headline"            # +11% headline beats Fidelity's -25%
    fm = v[v.preipo_signal_type == "fund_mark"]
    assert len(fm) == 7
    assert (fm["least_wrong"] == "fund mark").sum() == 5
    assert fm["signal_err_pct"].abs().median() < 15                # ~11%
    assert fm["overshoot_pct"].abs().median() > 30                 # ~48%


def test_ipo_valuations_use_consistent_offer_price_basis():
    """Source check of 2026-06-27: every realized-IPO valuation is on a
    consistent OFFER-PRICE fully-diluted basis, each cross-checked vs >=2 public sources. Klarna was
    corrected from a first-day-close figure ($17.5B) to the offer-price ~$15.1B that matches the
    other exits (CNBC '$15B' + FinTech Weekly '$15.1B'), making the down-round headline overshoot
    median +205% (was +163%); the differentiator (Instacart/Reddit fund-mark) is unaffected."""
    import validation as val
    v = val.add_errors(val.load()).set_index("company")
    verified = {"Instacart": 9.9, "Reddit": 6.4, "Klarna": 15.1, "CoreWeave": 23.0,
                "SpaceX-xAI": 1750.0, "Chime": 11.6, "Figma": 19.3}   # offer-price vals, >=2 sources each
    for co, iv in verified.items():
        assert abs(v.loc[co, "ipo_val_busd"] - iv) < 1e-9, co
    peak = v[v.vintage == "2021-peak"]                      # the four 2021-bubble-vintage stale headlines
    assert len(peak) == 4                                   # Instacart/Klarna/Reddit/Chime
    assert abs(peak["overshoot_pct"].median() - 160) < 1.5  # +160% (the claim is scoped to the 2021-peak cohort)
    assert -60 < v.loc["Klarna", "signal_err_pct"] < -50    # still overcorrected below the IPO (~ -56%)


def test_verified_headline_rounds():
    """Source check of 2026-06-27: load-bearing headline rounds, each
    cross-checked vs >=2 independent public sources, pinned so a silent CSV edit is flagged."""
    df = pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")
    verified = {"Anthropic": 965, "OpenAI": 852, "Databricks": 134, "Anduril": 61,
                "Kraken": 20, "Ramp": 44, "Mercury": 5.2, "Perplexity": 20, "Epic Games": 31.5}
    for co, hv in verified.items():
        assert abs(df.loc[co, "headline_val_busd"] - hv) < 1e-9, co


def test_required_columns_and_provenance():
    df = pd.read_csv(ROOT / "data" / "valuation_panel.csv")
    for c in ["company", "headline_val_busd", "forge_val_busd", "headline_source", "quality_flag"]:
        assert c in df.columns
    assert df["headline_source"].notna().all()   # every fact carries a source
    assert df["forge_val_busd"].gt(0).all()


def test_fund_marks_provenance():
    """Every N-PORT mark is a sourced public fact: filing locator + positive fair value."""
    df = pd.read_csv(ROOT / "data" / "fund_marks.csv")
    for c in ["company", "fund", "accession", "report_date", "val_usd", "fair_val_level"]:
        assert c in df.columns
    assert df["accession"].notna().all()                 # every mark locates its SEC filing
    assert pd.to_numeric(df["val_usd"], errors="coerce").gt(0).all()
    assert (df["fair_val_level"] == 3).all()             # all are Level-3 private marks


def test_cross_fund_dispersion_pattern():
    """Funds disagree on some names (Anthropic) and herd on others (OpenAI)."""
    import fund_marks as fm
    tab = fm.fund_price_table(fm.load())

    def spread_at_modal(co):
        s = tab[tab.company == co]
        md = s.report_date.mode().iloc[0]
        v = s[s.report_date == md].pps
        return v.max() / v.min()

    assert spread_at_modal("Anthropic") > 1.3          # 14 funds, ~39% spread
    assert spread_at_modal("OpenAI") < 1.01            # 13 funds herd to one price
    assert spread_at_modal("Anthropic") > spread_at_modal("Stripe")
    # marks cluster within a fund family (all Alger Anthropic marks equal to the cent)
    alg = tab[(tab.company == "Anthropic") & (tab.family == "Alger")].pps
    assert alg.round(2).nunique() == 1                  # all $259.14


def test_expanded_sample_new_names_and_bytedance_excluded():
    """The v0.8 expansion adds broadly-held, still-private names (Plaid, Revolut, Gusto) and
    EXCLUDES ByteDance, whose holders split across legal entities (Douyin Co Ltd vs ByteDance
    Ltd) and share classes (common vs convertible preferred) so per-share is not comparable."""
    import fund_marks as fm
    # ByteDance is on the documented cross-class/entity exclusion list, with marks in the raw file
    assert "ByteDance" in fm.CROSS_CLASS_EXCLUDE
    raw = pd.read_csv(ROOT / "data" / "fund_marks.csv")
    assert (raw.company == "ByteDance").sum() >= 10          # harvested, then excluded (not hidden)

    disp = pd.read_csv(ROOT / "data" / "fund_marks_dispersion.csv").set_index("company")
    assert "ByteDance" not in disp.index                     # excluded from the per-share result
    for nm in ["Plaid", "Revolut", "Gusto"]:                 # new names present...
        assert nm in disp.index
        assert disp.loc[nm, "n_families"] >= 2               # ...with cross-family coverage
    # the expansion lifts the typical cross-fund disagreement (was 13% on 8 names -> ~24% on 10)
    big = disp[disp.n_funds >= 5]
    assert len(big) >= 10
    assert 20 < ((big["maxmin"].median()) - 1) * 100 < 28


# ---- N-PORT time-series leg (markup/markdown trajectory) -----------------------------

def test_timeseries_provenance():
    """Every time-series mark is a sourced public fact: SEC filing locator + positive price."""
    df = pd.read_csv(ROOT / "data" / "fund_marks_timeseries.csv")
    for c in ["company", "fund", "accession", "report_date", "pps", "tot_val_usd"]:
        assert c in df.columns
    assert df["accession"].notna().all()
    assert pd.to_numeric(df["pps"], errors="coerce").gt(0).all()
    assert df["report_date"].str.match(r"\d{4}-\d{2}-\d{2}").all()
    # deep tracers really span the cycle (Databricks back to 2019, SpaceX/Stripe multi-year)
    db = df[df.company == "Databricks"]
    assert db["report_date"].min() < "2020-06-30"
    assert db["fund"].nunique() >= 3


def test_split_adjust_removes_tenfold_break():
    """A ~10:1 share-count restatement is removed; a real ~2x valuation move is preserved."""
    import fund_marks_timeseries as ts
    import pandas as pd
    s = pd.Series([100.0, 110.0, 10.5, 11.0],                       # 10x split between idx 1,2
                  index=["2021Q1", "2021Q2", "2021Q3", "2021Q4"])
    adj = ts.split_adjust(s)
    assert max(adj) / min(adj) < 1.3                               # continuity restored
    real = pd.Series([100.0, 200.0], index=["a", "b"])             # genuine 2x markup, untouched
    assert abs(ts.split_adjust(real).iloc[1] / ts.split_adjust(real).iloc[0] - 2.0) < 1e-9


def test_timeseries_cycle_and_comovement():
    """The headline within-fund cycle (deep drawdown + recovery) and cross-fund co-movement."""
    import fund_marks_timeseries as ts
    df = ts.load()
    tidy = pd.concat([ts.clean_company(co, g) for co, g in df.groupby("company")
                      if co not in ts.EXCLUDE_PERSHARE], ignore_index=True)

    def med(co):
        return (tidy[tidy.company == co].groupby("quarter")["pps"].median().sort_index())

    db = ts.cycle_metrics(med("Databricks"))
    assert db["drawdown_pct"] < -50            # 2022-23 reset: marked down >50%
    assert db["recovery_pct"] > 100            # and substantially re-marked up by 2026
    assert db["peak_q"] < db["trough_q"]       # peak precedes trough

    st = ts.cycle_metrics(med("Stripe"))
    assert st["drawdown_pct"] < -40 and st["recovery_pct"] > 100  # new-high recovery still shows reset

    cm = ts.comovement(tidy).set_index("company")
    assert cm.loc["Databricks", "level_rho"] > 0.9   # co-held funds re-mark in step over time

    # v0.12: the "re-mark in the same direction" result no longer rests on Databricks alone.
    # Stripe's three funds span three DIFFERENT families (Fidelity, Franklin, American Funds)
    # yet co-move at rho>0.85 in levels -> direction-agreement ACROSS houses, not within one.
    assert cm.loc["Stripe", "level_rho"] > 0.85
    stripe_funds = set(tidy[tidy.company == "Stripe"].fund.unique())
    assert len(stripe_funds) >= 3
    assert len({f.split()[0] for f in stripe_funds}) >= 3        # Fidelity / Franklin / New(Economy)
    # broad-cycle agreement holds for EVERY co-held name (level rho positive)...
    assert (cm["level_rho"] > 0).all()
    # ...but tick-by-tick lockstep only for the deepest-overlap names (Databricks, Stripe),
    # not the loose-overlap ones (Discord's two funds entered three years apart).
    assert cm.loc["Stripe", "change_rho"] > 0.5
    assert cm.loc["Discord", "change_rho"] < 0.5


# ---- Forge FPMI secondary-index corroboration (section 4.6) --------------------------

def test_forge_index_provenance_and_consistency():
    """Every FPMI anchor is attributed to Forge and the path is internally consistent."""
    df = pd.read_csv(ROOT / "data" / "forge_index.csv")
    for c in ["date", "fpmi_level", "basis", "source", "accessed"]:
        assert c in df.columns
    assert df["source"].str.contains("Forge", case=False).all()      # attributed
    assert pd.to_numeric(df["fpmi_level"], errors="coerce").gt(0).all()
    lvl = dict(zip(df.date, df.fpmi_level))
    # the 1Y-ago anchor (1Y return back-out) must equal the stated 52-week low ~317.11
    assert abs(lvl["2025-06-24"] - 317.11) < 1.0


def test_forge_fundmark_same_cycle():
    """Two independent public signals trace the same cycle: deep drawdown into a
    mid-2023 trough, then a strong recovery by 2026."""
    import forge_index as fi
    f = fi.load_fpmi()
    fc = fi.cycle_from_path(pd.Series(f.fpmi_level.values, index=f.date))
    fmi, _, _ = fi.fund_mark_index()
    mc = fi.cycle_from_path(fmi)
    assert fc["drawdown_pct"] < -40 and mc["drawdown_pct"] < -40   # both deep drawdowns
    assert fc["recovery_pct"] > 100 and mc["recovery_pct"] > 100   # both strong recoveries
    assert fc["trough_lbl"].year == 2023 and mc["trough_lbl"].startswith("2023")  # troughs coincide


# ---- Prediction-market leg (section 4.7) --------------------------------------------

def test_prediction_markets_provenance():
    """Every prediction-market reading is a dated, attributed public fact."""
    df = pd.read_csv(ROOT / "data" / "prediction_markets.csv")
    for c in ["company", "platform", "contract", "metric_type", "as_of", "source"]:
        assert c in df.columns
    assert df["platform"].isin(["Polymarket", "Kalshi"]).all()
    assert df["source"].notna().all()                       # every reading is attributed
    assert df["as_of"].str.match(r"\d{4}-\d{2}-\d{2}").all()  # and dated
    prob = pd.to_numeric(df["implied_prob_pct"], errors="coerce").dropna()
    assert prob.between(0, 100).all()
    assert {"Polymarket", "Kalshi"} <= set(df["platform"])   # both venues present


def test_prediction_markets_cross_platform_disagreement():
    """The forward signal disagrees across venues: Kalshi 'announce' >> Polymarket
    'complete' on OpenAI's 2026 IPO (launch week), a ~59-pt gap; and the listing-
    order market flips across venues by tens of points."""
    import prediction_markets as pmkt
    assert pmkt.launchweek_openai_gap() >= 50               # 88 - 29 = 59
    assert abs(pmkt.order_gap()) >= 40                      # Poly 74 vs Kalshi-implied 15


def test_prediction_markets_forward_above_round():
    """The forward market prices Anthropic's debut ABOVE its last private round."""
    import prediction_markets as pmkt
    caps, probs = pmkt.exceedance_curve("Anthropic")
    headline = float(pmkt.PANEL.loc["Anthropic", "headline_val_busd"])
    med = pmkt.implied_median_cap(caps, probs)
    assert med > headline                                   # implied median > last round
    assert med / headline > 1.5                             # ~1.9x
    assert pmkt.interp_prob(caps, probs, headline) > 60     # ~81% to debut at/above round


# ---- Robustness suite (section 4.8) -------------------------------------------------

def test_robustness_cross_section_stability():
    """(n=17): the clean cross-section median hugs zero, survives leave-one-out,
    and is insignificant on every test (median −4.6%, Wilcoxon p=0.281)."""
    import robustness as rb
    from scipy.stats import wilcoxon
    clean = rb.cross_section_gaps(True)
    assert len(clean) == 17                                      # expanded clean subset
    assert abs(float(clean.median())) < 8.0                      # small insignificant discount (~ -4.6%)
    loo = rb.leave_one_out_medians(clean)
    assert min(loo.values()) >= -8 and max(loo.values()) <= 0    # LOO median (-6.7..-2.3)
    assert wilcoxon(clean.values).pvalue > 0.10                  # not significant (p=0.281)


def test_expanded_cross_section_v010():
    """expansion of the secondary cross-section: 28-name panel / 17 clean, each new
    headline round >=2-sourced (pinned so a silent CSV edit is flagged), and the full panel
    spans fallen 2021-22 unicorns (deep discounts) to one stale round bid far up."""
    df = pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")
    assert len(df) == 28
    assert (df.quality_flag == "clean").sum() == 17
    verified_new = {"Glean": 7.2, "PsiQuantum": 7.0, "Gecko Robotics": 1.25,
                    "Redwood Materials": 6.0, "Chainalysis": 8.6, "Flexport": 8.0,
                    "Consensys": 7.0, "Rippling": 16.8,
                    "Zipline": 7.6, "Upgrade": 7.3, "Harness": 5.5, "SambaNova": 2.2}  # >=2 public sources each
    for co, hv in verified_new.items():
        assert abs(df.loc[co, "headline_val_busd"] - hv) < 1e-9, co
    gap = df.forge_val_busd / df.headline_val_busd - 1
    assert gap.loc["Flexport"] < -0.8           # fallen 2021-22 unicorn: deep discount to peak headline
    assert gap.loc["SandboxAQ"] > 0.8           # stale round bid far up by the secondary
    for co in ["Glean", "PsiQuantum", "Gecko Robotics", "Redwood Materials"]:
        assert df.loc[co, "quality_flag"] == "clean"             # clean recent-round growers
        assert gap.loc[co] < 0                                   # all sit at/below their recent round


def test_robustness_dispersion_invariant_to_band():
    """The cross-fund median spread doesn't move with the unit-outlier band K (no marginal marks)."""
    import robustness as rb
    meds = [rb.dispersion_median(K, 5)[0] for K in (2.0, 3.0, 4.0, 5.0)]
    assert max(meds) - min(meds) < 1e-6                          # identical across the band
    assert 20 < meds[0] < 28                                     # ~24% (expanded 10-name sample)


def test_robustness_family_is_the_disagreement():
    """Cross-fund disagreement is a deterministic family effect: between-family variance ~100%,
    within-family spread ~0 (funds in a house file the identical mark), and it survives
    collapsing each family to one mark."""
    import robustness as rb
    vd = rb.family_variance_decomp().set_index("company")
    assert vd.loc["Anthropic", "eta2_between_family"] > 0.95
    assert vd.loc["Databricks", "eta2_between_family"] > 0.99
    wf = rb.within_family_spreads()
    assert (wf.within_spread_pct < 0.5).mean() > 0.8            # >80% of family-cells bit-identical
    fc = rb.family_collapsed_dispersion().set_index("company")
    assert fc.loc["Anthropic", "family_spread_pct"] > 30        # not a fund-count artifact


def test_robustness_cycle_invariant_but_knob_live():
    """The -58%/+200% cycle is flat across the plausible band, identical for mean vs median path,
    but the parameter is provably live (an implausibly tight band moves it)."""
    import robustness as rb
    base = rb.deep_cycle_medians(4.0, "median")
    assert base["median_drawdown_pct"] < -50 and base["median_recovery_pct"] > 150
    for K in (3.0, 6.0):
        r = rb.deep_cycle_medians(K, "median")
        assert abs(r["median_drawdown_pct"] - base["median_drawdown_pct"]) < 1
        assert abs(r["median_recovery_pct"] - base["median_recovery_pct"]) < 1
    rmean = rb.deep_cycle_medians(4.0, "mean")
    assert abs(rmean["median_drawdown_pct"] - base["median_drawdown_pct"]) < 1
    tight = rb.deep_cycle_medians(2.0, "median")               # K<=2 clips real writedowns
    assert tight["median_recovery_pct"] < base["median_recovery_pct"] - 50


def test_robustness_sector_signsplit():
    """v0.11 (sec. 4.2 / 4.8): the ceiling-or-floor sign-split is given an INFERENTIAL test.
    The assumption-free omnibus across the (mostly singleton) sectors is NULL, but a contrast
    PRE-SPECIFIED from the demand thesis — demand-favored {AI, Data/AI, Defense} vs the rest —
    is significant on the clean subset, a large effect, and robust to leave-one-out (so the
    +69% Anduril does not drive it)."""
    import robustness as rb
    assert frozenset({"AI", "Data/AI", "Defense"}) == rb.FAVORED_SECTORS   # fixed a priori
    c = rb.sector_contrast(clean_only=True)
    assert c["kruskal_p"] > 0.10                 # omnibus cannot reject equality (singletons)
    assert c["median_fav"] > c["median_rest"]    # favored sits above the rest (+4.0% vs −15.0%)
    assert c["mwu_p_one"] < 0.05                 # one-sided Mann-Whitney ~0.023
    assert c["mwu_p_two"] < 0.05                 # two-sided ~0.045 (still under .05 on the clean cut)
    assert c["perm_p_one"] < 0.05                # 20k label-shuffle permutation ~0.017
    assert c["rank_biserial"] > 0.5             # large effect (+0.69)
    loo = rb.sector_loo_one_sided(clean_only=True)
    assert max(loo.values()) < 0.05             # every leave-one-out drop stays significant
    assert rb.sector_contrast(clean_only=False)["mwu_p_one"] < 0.05   # full panel also one-sided sig.


def test_robustness_sector_confound():
    """v0.14 (sec. 4.2 / 4.8): the demand-favored sign-split is not a round-SIZE or round-RECENCY
    artifact. On the clean subset the two groups are BALANCED on recency (favored names are not
    systematically fresher) though favored names ARE larger; controlling for BOTH in a multiple
    regression gap ~ favored + recency + log(size), the demand-favored coefficient stays positive and
    significant under a Freedman-Lane permutation (raw and rank gap). On the full panel it washes out,
    matching the already-marginal full-panel univariate contrast."""
    import robustness as rb
    # date parser handles the coarse forms the panel uses
    assert rb.parse_round_date("2026-03") == pd.Timestamp(2026, 3, 15)
    assert rb.parse_round_date("2025-Q4").month == 11
    assert rb.parse_round_date("2026") == pd.Timestamp(2026, 7, 1)
    # Shield AI's year-only date was precisioned to the verified Mar-2026 (no future-dated round)
    panel = pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")
    assert panel.loc["Shield AI", "headline_date"] == "2026-03"
    assert (rb.FORGE_ASOF - rb.parse_round_date(panel.loc["Shield AI", "headline_date"])).days > 0

    c = rb.sector_confound(clean_only=True)
    assert c["rec_p"] > 0.05            # recency BALANCED across favored vs rest (~0.77)
    assert c["size_p"] < 0.05           # but favored names are larger (~0.03) -> the real confound
    assert c["b_raw"] > 0               # favored sit above, adjusting for size+recency (+36.7 pts)
    assert c["p_raw"] < 0.05            # and significantly so under Freedman-Lane (~0.008)
    assert c["p_rank"] < 0.05           # robust to the fat tails via the rank-gap regression (~0.003)
    f = rb.sector_confound(clean_only=False)
    assert f["p_raw"] > 0.05            # full panel washes out (~0.31), as the univariate full also does
    # released CSV carries the new multivariate checks
    summ = pd.read_csv(ROOT / "data" / "robustness_summary.csv")
    assert {"mv_favored_fl_p_raw_clean", "mv_recency_mwu_p_clean", "mv_size_mwu_p_clean"} \
        <= set(summ["check"])


def test_robustness_summary_csv():
    """The released robustness CSV carries all four legs."""
    df = pd.read_csv(ROOT / "data" / "robustness_summary.csv")
    assert {"section", "check", "value"} <= set(df.columns)
    assert {"4.1", "4.2", "4.4", "4.5"} <= set(df["section"].astype(str))


# ---- Cross-signal synthesis (section 4.9) -------------------------------------------

def test_cross_signal_coverage_and_overlap():
    """v0.17 (sec. 4.9): the two CROSS-SECTIONAL signals cover largely different companies.
    The secondary panel (28) and the >=5-fund cross-fund marks (10) overlap on exactly six
    names; several broadly-held fund-mark names (Discord, Revolut, Gusto, Canva) are NOT in the
    secondary panel, and most secondary names are not fund-covered -- so the signals are
    complementary, which is the case for the four-way triangulation."""
    import cross_signal as cs
    cov = cs.coverage()
    assert cov["n_secondary"] == 28
    assert cov["n_fund5"] == 10
    assert cov["overlap_xsec"] == ["Anduril", "Anthropic", "Databricks",
                                   "Epic Games", "OpenAI", "Stripe"]
    # broadly fund-held names the secondary panel does not reach
    assert {"Discord", "Revolut", "Gusto", "Canva"} <= set(cov["fund_only"])
    # the three names seen by all of §7.2 / §4.3 / Appendix C.1
    assert set(cov["all_three"]) == {"Databricks", "Epic Games", "Stripe"}


def test_cross_signal_agreement_directional_not_significant():
    """v0.17 (sec. 4.9): on the six overlapping names the secondary gap and the cross-fund spread
    move TOGETHER as the shared staleness/demand mechanism predicts -- a name funds herd on is a
    name the secondary bids at/above its round -- but the overlap is far too small to be significant.
    Reported honestly as directional corroboration, not proof."""
    import cross_signal as cs
    m = cs.merged_overlap()
    assert len(m) == 6
    rho, p, n = cs.spearman_exact(m.gap_pct.values, m.spread_pct.values)
    assert n == 6
    assert -0.6 < rho < -0.25                     # negative (more premium <-> more consensus), ~ -0.43
    assert p > 0.10                               # exact permutation p ~ 0.42 -> NOT significant
    # the negative sign is not an artifact of the two flagged-headline rows (Stripe, Epic Games)
    mc = m[m.quality_flag == "clean"]
    assert cs.spearman_exact(mc.gap_pct.values, mc.spread_pct.values)[0] < 0
    # regime view (distribution-free): every herded name trades at/above its last round;
    # the only below-round overlap name is a stale-headline name funds also disagree on
    herd = m[m.fund_consensus == "herd"]
    assert set(herd.index) == {"OpenAI", "Stripe", "Anduril"}
    assert (herd.secondary_sign == "at/above").all()        # 3/3
    below = m[m.secondary_sign == "below"]
    assert list(below.index) == ["Epic Games"]
    assert below.loc["Epic Games", "fund_consensus"] == "disagree"
    assert below.loc["Epic Games", "quality_flag"] == "stale_headline"


def test_cross_signal_csv_provenance():
    """The released Appendix C.4 table carries both signals' metrics + the regime labels per company."""
    df = pd.read_csv(ROOT / "data" / "cross_signal_consistency.csv")
    for c in ["company", "n_funds", "spread_pct", "gap_pct", "quality_flag",
              "fund_consensus", "secondary_sign"]:
        assert c in df.columns
    assert len(df) == 6
    assert set(df["fund_consensus"]) <= {"herd", "disagree"}
    assert set(df["secondary_sign"]) <= {"at/above", "below"}


# ---- Forge secondary-leg independent corroboration (section 4.8) --------------------

def test_forge_corroboration_independent_signals():
    """v0.18 (sec. 4.8): the Forge per-company secondary estimates the lead result rests on are
    cross-checked against an INDEPENDENT public market signal (a second secondary venue, an employee
    tender, or a confirming new round) for 11 names, corroborated within a median of ~7%. The
    provenance guard in load() requires each forge value to equal the panel's; honest divergences
    (Forge runs conservative on Epic Games/PsiQuantum/Perplexity) are reported, not hidden."""
    import forge_corroboration as fcor
    df = fcor.enrich(fcor.load())               # load() raises if forge_val drifts from the panel
    s = fcor.summary(df)
    assert s["n_cross_checked"] == 11
    assert s["n_numeric"] == 10                 # Kraken is directional-only (no single clean figure)
    assert 5 < s["median_abs_diff_pct"] < 9     # ~7%
    assert s["mean_abs_diff_pct"] < 10          # ~7.6%
    assert s["n_within_band"] == 9              # 9/10 within +/-15%
    assert s["n_secondary"] == 6 and s["n_secondary_dir_agree"] == 6   # direction agrees 6/6
    # the strongest corroboration is a hard market fact: Databricks' new round ~ the Forge estimate
    assert abs(df.loc["Databricks", "diff_pct"]) < 2
    # honest divergences: Forge runs conservative (below other secondary venues) on exactly these
    assert set(s["forge_conservative"]) == {"Epic Games", "Perplexity", "PsiQuantum"}
    # every numeric row carries an attributed, dated independent source
    num = df[df.indep_implied_val_busd.notna()]
    assert num["indep_source"].notna().all() and num["indep_date"].notna().all()


def test_forge_corroboration_summary_csv():
    """The released Appendix D corroboration table carries both values + the per-name diff and direction."""
    df = pd.read_csv(ROOT / "data" / "forge_corroboration_summary.csv")
    for c in ["company", "forge_val_busd", "indep_implied_val_busd", "indep_type",
              "diff_pct", "direction_agree", "indep_source"]:
        assert c in df.columns
    assert len(df) == 11
    assert set(df["indep_type"]) <= {"secondary_venue", "tender", "primary_round", "secondary_press"}


def test_no_named_house_is_pooled_into_the_catch_all():
    """The ten-name panel and the population panel must not run on two different house maps.

    `fund_marks.FAMILIES` is keyed on FUND names and `fund_complex.RULES` on REGISTRANT names,
    so the two cannot be merged into one table — the fund map would lose Fidelity's series
    names and the registrant map would lose "Destiny Tech100 Inc.". What they must not do is
    disagree about whether a holder is a house at all.

    They did. Seven managers the population panel names — First Trust, Voya, AllianceBernstein,
    Lincoln, Grandeur Peak, MFS and the Private Shares Fund — fell into `fund_marks`' "Other"
    bucket, and the cross-fund spread then treated that bucket as ONE house. Pooling distinct
    managers into a single unit is this paper's headline defect running in the other direction,
    and it understated the ten-name house-level median: 23.7%, not 12.6%. It surfaced as four
    identical grey dots on one row of the dispersion figure.

    The rule below is the narrow one that has no judgement in it: a fund whose own name the
    production map can resolve to a house must not be labelled "Other" here.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import fund_complex as fx
    import fund_marks as fm

    m = fm.load()
    pooled = []
    for name in sorted(set(m[m.family == "Other"].fund)):
        house = fx.complex_of(name)
        if house.strip().upper() != str(name).strip().upper():
            pooled.append(f"{name!r} -> fund_complex says {house!r}, fund_marks says 'Other'")
    assert not pooled, (
        "holder(s) the population panel names and the ten-name panel pools:\n  "
        + "\n  ".join(pooled))
    # Print the denominator: if `family` ever returned a name for everything, the check above
    # would pass while saying nothing, and the catch-all is meant to stay small, not vanish.
    other = int((m.family == "Other").sum())
    assert 0 < other <= 12, f"{other} marks in the catch-all; read them before moving this bound"
