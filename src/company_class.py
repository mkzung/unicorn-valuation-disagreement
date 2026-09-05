"""What kind of company is on the other side of the mark?

Section 5 takes every Level-3 equity position registered funds report and calls the result
the population. That is an honest description of the filings and a poor description of
*unicorns*, which is what the paper is about. The filings contain AT&T Mobility II's
structured preferred, AmSurg and Southeastern Grocers out of buyout portfolios, Neiman
Marcus and Intelsat after their reorganisations, and Taiwan Semiconductor — listed on the
TWSE — carried at Level 3 for one month. None of those is a venture-backed private company,
and together they hold enough of the booked value to move a dollar figure the abstract
quotes. The paper already makes exactly this argument for Russian issuers, which sit at
Level 3 by sanction rather than by being venture backed; it simply never applied the
argument anywhere else.

So each cluster gets a label, and the label's *basis* is reported alongside it:

  verified       read off the filings and public record, one line of reasoning per cluster,
                 listed in VERIFIED below. Every cluster holding more than $500M is here.
  rule           assigned by the ordered rule in `classify`, which fires only where the
                 filings are unambiguous and abstains everywhere else.
  unclassified   the filings do not say and the position is too small to be worth a claim.

Nothing is silently assigned. Table 11 reports a total for each label, and the manuscript
quotes the venture-only figure, because that is the population it claims to describe.

Why there is no single threshold. The strongest signal in the data is the filer's own
security title: a private placement is written as one ("SER H PC PP", "PRIVATE PLACEMENT"),
and among clusters whose kind is known, that token separates venture from non-venture at an
AUC of 0.96. It is not a boundary. Its distribution over the 656 clusters runs continuously
from a seventh of a percent upward, with the only real discontinuity between clusters where
no filer ever wrote it and clusters where one did. A threshold placed on that slope would be
invented precision of exactly the kind this paper refuses elsewhere, so the rule uses the
signal only at its ends and the middle is verified by hand or left alone.

`main` prints how often the rule agrees with the verified labels where both exist. That
number is the honest measure of what the tail's labels are worth.

Run:  python3 src/company_class.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop

OUT = ROOT / "data" / "company_classification.csv"

VENTURE, NONVENTURE, LISTED, UNKNOWN = "venture", "private_nonventure", "listed", "unclassified"

# Every cluster holding more than $500M of booked value, plus any smaller one the rule would
# get wrong. The key is the resolver's cluster id; the canonical issuer string is written to
# the CSV beside it, because a reader searching for "Taiwan Semiconductor" will not otherwise
# find `NM:TAIWAN SEMICONDUCTOR M...`, and a reviewer looking for Neiman Marcus will not guess
# `ROW:307758`.
VERIFIED: dict[str, tuple[str, str]] = {
    # -- venture-backed private operating companies ------------------------------------
    "NM:SPACEX": (VENTURE, "venture-backed; private throughout the window"),
    "NM:PROJECT DEBUSSY": (VENTURE, "Databricks, filed under a deal code name"),
    "NM:BYTEDANCE": (VENTURE, "venture-backed; private throughout"),
    "NM:EPIC GAMES": (VENTURE, "venture and strategic rounds; private"),
    "NM:FANATICS": (VENTURE, "growth-equity rounds; private"),
    "NM:WAYMO": (VENTURE, "external rounds alongside Alphabet; private"),
    "NM:STRIPE": (VENTURE, "venture-backed; private"),
    "NM:RIVIAN AUTOMOTIVE": (VENTURE, "pre-IPO venture rounds; cells end at the Nov-2021 listing"),
    "NM:RIVIAN AUTO": (VENTURE, "same issuer, Series E preferred, separate cluster"),
    "ROW:276028": (VENTURE, "Canva; venture-backed"),
    "NM:ANTHROPIC": (VENTURE, "venture-backed"),
    "NM:ANT INTERNATIONAL": (VENTURE, "Ant Group international arm; private"),
    "NM:ANT": (VENTURE, "Ant Group; private after the 2020 listing was pulled"),
    "ROW:275786": (VENTURE, "Gusto, filed as ZenPayroll"),
    "NM:OPENAI": (VENTURE, "private; capped-profit and later PBC structure"),
    "NM:X AI": (VENTURE, "xAI; private"),
    "NM:XAI": (VENTURE, "xAI, separate cluster from the same issuer"),
    "NM:PSIQUANTUM": (VENTURE, "venture-backed"),
    "ROW:276322": (VENTURE, "Redwood Materials; venture-backed"),
    "NM:NATIONAL RESILIENCE": (VENTURE, "venture-backed biomanufacturing"),
    "NM:TANIUM": (VENTURE, "venture-backed"),
    "NM:FARMERS BUS NETWORK BRYRHM7J9": (VENTURE, "Farmers Business Network; venture-backed"),
    "NM:PINE PRIVATE IND": (VENTURE, "Pine Labs; venture-backed"),
    "NM:CHECKR": (VENTURE, "venture-backed"),
    "ROW:275739": (VENTURE, "Nuro; venture-backed"),
    "NM:RELATIVITY SPACE": (VENTURE, "venture-backed"),
    "NM:ZIPLINE INTERNATIONAL": (VENTURE, "venture-backed"),
    "ROW:130515": (VENTURE, "Caris Life Sciences; venture-backed"),
    "NM:CARIS LIFE": (VENTURE, "Caris Life Sciences, separate cluster"),
    "NM:TOAST": (VENTURE, "pre-IPO venture; cells end at the Sep-2021 listing"),
    "ROW:33217": (VENTURE, "Airbnb pre-IPO; cells end at the Dec-2020 listing"),
    "ROW:276077": (VENTURE, "Rappi; venture-backed"),
    "NM:SWEETGREEN": (VENTURE, "pre-IPO venture; cells end at the Nov-2021 listing"),
    "NM:MAPLEBEAR DBA INSTACART": (VENTURE, "Instacart pre-IPO; cells end Jun-2023"),
    "NM:XIAOJU KUAIZHI": (VENTURE, "Didi pre-IPO"),
    "NM:DIDI CHUXING": (VENTURE, "Didi, separate cluster"),
    "NM:WARBY PARKER": (VENTURE, "JAND Inc; pre-IPO venture"),
    "NM:UIPATH": (VENTURE, "pre-IPO venture; cells end at the Apr-2021 listing"),
    "NM:KOBOLD METALS": (VENTURE, "venture-backed"),
    "NM:ANDURIL": (VENTURE, "venture-backed"),
    "NM:GM CRUISE HLDG": (VENTURE, "Cruise; outside preferred alongside GM"),
    "NM:CONVOY": (VENTURE, "venture-backed; wound down 2023"),
    "NM:ROOFOODS": (VENTURE, "Deliveroo pre-IPO"),
    "NM:CAVA": (VENTURE, "pre-IPO growth equity"),
    "NM:THINK LEARN PRIVATE": (VENTURE, "Byju's; venture-backed"),
    "NM:AURORA INNOVATION": (VENTURE, "pre-merger venture"),
    "NM:SNYK": (VENTURE, "venture-backed"),
    "NM:KARDIUM": (VENTURE, "venture-backed medical devices"),
    "NM:SILA NANO": (VENTURE, "venture-backed"),
    "NM:SERVICETITAN": (VENTURE, "pre-IPO venture; cells end 2022"),
    "NM:GRAB": (VENTURE, "pre-merger venture"),
    "NM:ALLBIRDS": (VENTURE, "pre-IPO venture; cells end at the Nov-2021 listing"),
    "NM:ABL SPACE": (VENTURE, "venture-backed"),
    "NM:INSITRO": (VENTURE, "venture-backed"),
    "NM:CIRCLE INTERNET FINANCIAL": (VENTURE, "pre-IPO venture; cells end Mar-2025"),
    "NM:PAX": (VENTURE, "Juul Labs; venture and strategic capital, private"),
    "NM:SEISMIC SOFTWARE": (VENTURE, "venture-backed"),
    "NM:CELONIS SE": (VENTURE, "venture-backed"),
    "NM:BETA": (VENTURE, "Beta Technologies; venture-backed"),
    "NM:CLEERLY": (VENTURE, "venture-backed"),
    "NM:LOADSMART": (VENTURE, "venture-backed"),
    "NM:HONEST": (VENTURE, "pre-IPO venture; cells end at the May-2021 listing"),
    "NM:CEREBRAS": (VENTURE, "venture-backed"),
    "NM:SAMBANOVA SAFE": (VENTURE, "SambaNova Series D; venture-backed"),
    "NM:LIGHTMATTER": (VENTURE, "venture-backed"),
    "NM:FORMAGRID": (VENTURE, "Airtable; venture-backed"),
    "NM:ICAPITAL": (VENTURE, "growth-equity backed; private"),
    "NM:FREENOME": (VENTURE, "venture-backed"),
    "ROW:33117": (VENTURE, "Magic Leap; venture and sovereign capital, private"),
    "NM:RAD POWER BIKES": (VENTURE, "venture-backed"),
    "NM:WEWORK": (VENTURE, "venture and SoftBank capital; private over these cells"),
    "NM:DNA SCRIPT": (VENTURE, "venture-backed"),
    "NM:DISCORD": (VENTURE, "venture-backed"),
    "NM:SOCURE": (VENTURE, "venture-backed"),
    "NM:BENDING SPOONS SPA": (VENTURE, "growth-equity backed; private"),
    "NM:REVOLUT": (VENTURE, "venture-backed"),
    "NM:VERSA NETWORKS": (VENTURE, "venture-backed"),
    "ROW:260967": (VENTURE, "SB Technology; Series D and E convertible preferred, private"),
    "NM:INSCRIPTA": (VENTURE, "venture-backed"),
    "NM:SECURITYSCORECARD": (VENTURE, "venture-backed"),
    "NM:DOORDASH": (VENTURE, "pre-IPO venture; cells end at the Dec-2020 listing"),
    "NM:DOXIMITY": (VENTURE, "pre-IPO venture; cells end at the Jun-2021 listing"),
    "NM:FLEXE": (VENTURE, "venture-backed"),
    "NM:PALANTIR": (VENTURE, "pre-IPO preferred D/E/J; cells end at the Sep-2020 listing"),
    "NM:DRAFTKINGS": (VENTURE, "pre-merger private stock; cells end at the Apr-2020 listing"),
    "NM:VROOM": (VENTURE, "pre-IPO preferred; cells end at the Jun-2020 listing"),
    "NM:OUTSET MEDICAL": (VENTURE, "pre-IPO preferred; cells end at the Sep-2020 listing"),
    # -- private, but not venture-backed -------------------------------------------------
    "NM:AT T MOBILITY II": (NONVENTURE, "AT&T Mobility II LLC preferred interests; corporate structured preferred"),
    "NM:AMSURG": (NONVENTURE, "Ambulatory Topco; buyout portfolio company"),
    "ROW:287069": (NONVENTURE, "Intelsat; equity issued in the 2022 reorganisation"),
    "ROW:307758": (NONVENTURE, "NMG Parent, Neiman Marcus; equity from the 2020 reorganisation"),
    "NM:SOUTHEASTERN GROCERS": (NONVENTURE, "buyout portfolio company"),
    "NM:SEQUA": (NONVENTURE, "Carlyle buyout portfolio company"),
    "NM:VENTURE GLOBAL LNG SR C": (NONVENTURE, "LNG project developer; infrastructure capital, listed Jan 2025"),
    "NM:WINDSTREAM II": (NONVENTURE, "equity from the 2020 reorganisation"),
    "NM:WINDSTREAM": (NONVENTURE, "same issuer, separate cluster"),
    "NM:SYNIVERSE": (NONVENTURE, "Carlyle buyout portfolio company"),
    "NM:AMH NEW FINANCE": (NONVENTURE, "Associated Materials; buyout portfolio company"),
    "NM:SANCHEZ ENERGY": (NONVENTURE, "Mesquite Energy; equity from the 2020 bankruptcy"),
    "NM:FORESEA": (NONVENTURE, "Foresea Holding, ex-Constellation Oil; reorganisation equity"),
    "NM:QUARTERNORTH ENERGY IN": (NONVENTURE, "equity from the Fieldwood reorganisation"),
    "NM:TEXGEN POWER": (NONVENTURE, "power assets from a reorganisation"),
    "NM:CAYENNE AVIATION": (NONVENTURE, "aircraft leasing vehicle"),
    "NM:AIMBRIDGE TOPCO": (NONVENTURE, "buyout portfolio company"),
    # -- listed issuers carried at Level 3 ------------------------------------------------
    "NM:TAIWAN SEMICONDUCTOR MANUFACTURING": (LISTED, "listed on the TWSE; one Level-3 month"),
    "NM:IHEARTMEDIA": (LISTED, "listed after the 2019 reorganisation"),
    "NM:DREAM FINDERS HOMES": (LISTED, "listed on the NYSE"),
    "NM:CITRIX": (LISTED, "listed until the Sep-2022 take-private; the single cell is that month"),
    "NM:SAMSUNG BIOLOGICS": (LISTED, "listed on the KRX"),
    "NM:EMIRATES TELECOMMUNICATIONS ETISALAT": (LISTED, "listed on the ADX"),
    "NM:ABU DHABI COMMERCIAL BANK P J S C": (LISTED, "listed on the ADX"),
    "NM:MACQUARIE": (LISTED, "listed on the ASX"),
    "NM:RELIANCE STRATEGIC INVESTMENTS": (LISTED, "Jio Financial Services; listed on the NSE"),
    # A filer put the wrong issuer name on 219 rows: ISSUER_NAME reads "VENTURE CORP LTD"
    # while the security title reads "VENTURE GLOBAL LNG INC SR C PP". Those rows carry no
    # CUSIP and no LEI, so no identifier check can catch it, and the resolver clustered them
    # on the name it was given. One genuine Venture Corp row — the only one with an LEI — is
    # stuck to them. The cluster is Venture Global LNG in all but name.
    "NM:VENTURE": (NONVENTURE, "mostly Venture Global LNG under a filer's wrong issuer name; "
                               "LNG project developer, listed Jan 2025"),
    "NM:AVZ MINERALS": (LISTED, "listed on the ASX; suspended"),
    "NM:CORPORATE TRAVEL MANAGEMENT LT": (LISTED, "listed on the ASX"),
    "NM:ILYANG PHARMACEUTICAL": (LISTED, "listed on the KRX"),
    "NM:SRAX": (LISTED, "listed; delinquent filer"),
    # Albireo left the panel entirely when contra positions were excluded: every row that
    # kept its cluster above the five-fund bar was a "CONTRA ALBIREO PHARMA" line, which is
    # the acquisition's contingent residue rather than the company's stock. The label is
    # removed rather than kept dangling, and the removal is the exclusion working.
    # -- material but not established ------------------------------------------------------
    "ROW:276764": (UNKNOWN, "AH Parent Inc; the filings identify no operating company and "
                            "public sources do not resolve the name"),
}

# One issuer, several cluster keys. Entity resolution joins only on identifiers, exact
# normalised names and a declared alias list, and fails toward splitting — so a company whose
# filers spell it three ways lands on three keys, each of which then has to clear the
# five-fund two-house bar alone. That costs coverage and never invents a spread, which is the
# safe direction, but it inflates any count of *companies*. These are the splits among
# clusters that reach a reported cell; the value on the right is the issuer.
SAME_ISSUER: dict[str, str] = {
    "NM:X AI": "xAI", "NM:XAI": "xAI",
    "NM:ANT": "Ant Group", "NM:ANT INTERNATIONAL": "Ant Group",
    "ROW:130515": "Caris Life Sciences", "NM:CARIS LIFE": "Caris Life Sciences",
    "NM:XIAOJU KUAIZHI": "Didi", "NM:DIDI CHUXING": "Didi",
    "NM:RIVIAN AUTOMOTIVE": "Rivian", "NM:RIVIAN AUTO": "Rivian",
    "NM:WINDSTREAM": "Windstream", "NM:WINDSTREAM II": "Windstream",
    "NM:VENTURE": "Venture Global LNG", "NM:VENTURE GLOBAL LNG SR C": "Venture Global LNG",
}

# The rule fires only at the ends of the signal. `pp` is the share of a cluster's filings
# whose security title says private placement; `res` is the share flagged restricted.
PP_VENTURE, RES_VENTURE = 0.30, 0.75


def name_mismatch(d: pd.DataFrame) -> pd.Series:
    """Rows whose issuer name and security title name different issuers.

    A filing's issuer name can simply be wrong, and no identifier check will catch it when
    the row carries no identifier. Two hundred and nineteen rows here read "VENTURE CORP LTD"
    in the issuer field while the security title reads "VENTURE GLOBAL LNG INC SR C PP" — a
    listed Singapore electronics manufacturer's name on a private LNG developer's stock, with
    no CUSIP and no LEI to contradict it. The resolver clustered them on the name it was
    given, which is what it is supposed to do, and the one genuine Venture Corp row in the
    data ended up attached to them.

    Detecting it needs care, and the first attempt was useless: comparing the two fields
    word for word flagged one row in six, because most titles say "COMMON STOCK" and never
    repeat the issuer at all. A title that does not name a company is not evidence of
    anything. So the test fires only when the title DOES name one — it carries a corporate
    suffix — and the company it names is not the one in the issuer field. Reported rather
    than acted on, because the title is not automatically the truthful field either.
    """
    import entity_resolution as er

    # A holdco is not a different company, and neither is a declared alias. Both are stripped
    # before the comparison, or the flag fires on Fanatics against Fanatics Holdings and on
    # Douyin against ByteDance, which are the same issuers by construction.
    DROP = r"\b(?:HOLDINGS?|HLDGS?|HLDG|GROUP|GRP|PARENT|TOPCO|INTERNATIONAL|INTL)\b"

    def up(s: pd.Series) -> pd.Series:
        t = (s.astype(str).str.upper().str.replace(r"[^A-Z0-9 ]", " ", regex=True)
              .str.replace(DROP, " ", regex=True)
              .str.replace(r"\s+", " ", regex=True).str.strip())
        return t.where(~t.isin({"", "NAN", "NONE"}), "")

    name, title = up(d.ISSUER_NAME), up(d.ISSUER_TITLE)
    # er.ALIASES by name, not by getattr with a default: a default of {} would turn a rename
    # into a silently weaker check, which is the failure this file exists to avoid elsewhere.
    alias = {er.norm_name(k): er.norm_name(v) for k, v in er.ALIASES.items()}
    assert alias, "the alias list is empty; the mismatch check would be reporting noise"

    SUFFIX = r"\b(?:INC|LTD|LLC|LP|CORP|CORPORATION|CO|SA|SE|PLC|NV|AG|GMBH|PBC)\b"
    names_a_company = title.str.contains(SUFFIX, regex=True)
    lead = lambda s: s.str.split().str[:2].str.join(" ")
    a, b = lead(name), lead(title)
    # Equality of the first two words, not prefix containment, and not a shared first word.
    # Both looser tests were written first and both silently swallowed the case this exists
    # for: "VENTURE CORP" against "VENTURE GLOBAL" shares a first word and passes a prefix
    # test through the normalised forms. With HOLDINGS and GROUP already stripped above, the
    # holdco variants that should agree — Fanatics against Fanatics Holdings — still do.
    na, nb = name.map(er.norm_name), title.map(er.norm_name)

    def agrees(x: str, y: str, nx: str, ny: str) -> bool:
        if not x or not y:
            return True
        if x == y:
            return True
        return alias.get(nx, nx) == alias.get(ny, ny)

    same = np.array([agrees(x, y, nx, ny) for x, y, nx, ny in zip(a, b, na, nb)])
    return pd.Series(names_a_company.to_numpy() & ~same & name.ne("").to_numpy(),
                     index=d.index)


def features() -> pd.DataFrame:
    """One row per reported cluster: the two signals, the value at stake, and a readable name."""
    import entity_resolution as er

    d, c = pop.panel()
    g = c[c.guarded]
    x = pop.comparable(d)
    keys = set(zip(g.company, g.dt))
    ins = x[[k in keys for k in zip(x.company, x.dt)]].copy()
    txt = (ins.ISSUER_TITLE.astype(str).str.upper() + " | "
           + ins.ISSUER_NAME.astype(str).str.upper())
    ins["pp"] = txt.str.contains(r"\bPP\b|PRIVATE PLACEMENT|\b144A\b", regex=True)
    ins["res"] = ins.IS_RESTRICTED_SECURITY.astype(str).str.upper().eq("Y")

    name = ins.ISSUER_NAME.astype(str)
    name = name.where((name.str.len() > 2) & (name.str.lower() != "nan"),
                      ins.ISSUER_TITLE.astype(str))
    ins["nm"] = name

    f = ins.groupby("company").agg(pp=("pp", "mean"), res=("res", "mean"), rows=("pps", "size"))
    f["issuer"] = ins.groupby("company").nm.agg(er.modal)
    f["nav"] = g.groupby("company").nav.sum()
    f["cells"] = g.groupby("company").size()
    f["median_spread_pct"] = g.groupby("company").spread_pct.median()
    return f.sort_values("nav", ascending=False)


def rule(pp: float, res: float) -> str:
    """The unambiguous ends of the signal, and abstention in between.

    A cluster no filer ever called a private placement and no filer ever flagged restricted
    is an ordinary listed holding that happened to be marked Level 3. A cluster most filers
    called a private placement and nearly all flagged restricted is a private round. In
    between the filings do not say, and neither does this.
    """
    if pp == 0.0 and res == 0.0:
        return LISTED
    if pp >= PP_VENTURE and res >= RES_VENTURE:
        return VENTURE
    return UNKNOWN


def classify(f: pd.DataFrame | None = None) -> pd.DataFrame:
    """Label every cluster, and say where each label came from."""
    if f is None:
        f = features()
    out = f.copy()
    out["rule_label"] = [rule(p, r) for p, r in zip(out.pp, out.res)]
    lab, basis, note = [], [], []
    for k, r in out.iterrows():
        if k in VERIFIED:
            l, why = VERIFIED[k]
            lab.append(l)
            basis.append("verified" if l != UNKNOWN else "unresolved")
            note.append(why)
        else:
            lab.append(r.rule_label)
            basis.append("rule" if r.rule_label != UNKNOWN else "unclassified")
            note.append("")
    out["label"], out["basis"], out["note"] = lab, basis, note
    return out


def rule_accuracy(t: pd.DataFrame) -> dict:
    """How often does the rule agree with a label that was checked?

    This is the only honest statement about what the tail's labels are worth, and it has to
    be reported rather than assumed: the rule is applied precisely where nobody checked.
    """
    v = t[t.basis == "verified"]
    agree = (v.rule_label == v.label)
    fired = v[v.rule_label != UNKNOWN]
    return {
        "verified": len(v),
        "rule_abstained": int((v.rule_label == UNKNOWN).sum()),
        "rule_fired": len(fired),
        "rule_correct": int((fired.rule_label == fired.label).sum()),
        "accuracy_where_fired": float((fired.rule_label == fired.label).mean() * 100) if len(fired) else float("nan"),
        "agree_overall": float(agree.mean() * 100),
    }


def totals(t: pd.DataFrame) -> pd.DataFrame:
    """Cells, companies and booked value by label — the rows Table 11 gains."""
    _d, c = pop.panel()
    g = c[c.guarded].merge(t[["label"]], left_on="company", right_index=True, how="left")
    rows = []
    for lab in [VENTURE, NONVENTURE, LISTED, UNKNOWN]:
        s = g[g.label == lab]
        rows.append({
            "label": lab, "companies": int(s.company.nunique()), "cells": len(s),
            "nav_busd": float(s.nav.sum() / 1e9),
            "nav_pct": float(s.nav.sum() / g.nav.sum() * 100),
            "median_spread_pct": float(s.spread_pct.median()) if len(s) else float("nan"),
            "above_24_pct": float((s.spread_pct > 24).mean() * 100) if len(s) else float("nan"),
            "nav_above_24_busd": float(s[s.spread_pct > 24].nav.sum() / 1e9) if len(s) else float("nan"),
        })
    return pd.DataFrame(rows)


def issuer_counts(t: pd.DataFrame) -> dict:
    """Distinct issuers behind the clusters, once the known splits are folded together."""
    ven = t[t.label == VENTURE]
    names = [SAME_ISSUER.get(k, k) for k in ven.index]
    return {"venture_clusters": len(ven), "venture_issuers": len(set(names)),
            "split_issuers": len({v for k, v in SAME_ISSUER.items() if k in t.index})}


def mismatch_stats() -> dict:
    """How much of the panel rests on a filing whose two name fields disagree."""
    d, c = pop.panel()
    g = c[c.guarded]
    x = pop.comparable(d)
    keys = set(zip(g.company, g.dt))
    ins = x[[k in keys for k in zip(x.company, x.dt)]]
    m = name_mismatch(ins)
    return {"rows": int(m.sum()), "row_pct": float(m.mean() * 100),
            "clusters": int(ins[m].company.nunique())}


def main() -> None:
    t = classify()
    t.to_csv(OUT, index_label="company")
    acc = rule_accuracy(t)
    print(f"clusters {len(t)} · verified {acc['verified']} · "
          f"rule {int((t.basis == 'rule').sum())} · unclassified {int((t.basis == 'unclassified').sum())}")
    print(f"  the rule abstains on {acc['rule_abstained']} of the verified clusters and fires on "
          f"{acc['rule_fired']}, of which it gets {acc['rule_correct']} right "
          f"({acc['accuracy_where_fired']:.0f}%)")
    by_basis = t.groupby("basis").nav.sum() / t.nav.sum() * 100
    print("  share of booked value by basis: "
          + " · ".join(f"{k} {v:.1f}%" for k, v in by_basis.items()))
    print()
    print(totals(t).round(2).to_string(index=False))
    ic = issuer_counts(t)
    print(f"\n  the venture label covers {ic['venture_clusters']} clusters, which are "
          f"{ic['venture_issuers']} distinct issuers: {ic['split_issuers']} companies reach a "
          f"cell under more than one key")
    mm = mismatch_stats()
    print(f"  filings whose issuer name and security title name different issuers: "
          f"{mm['rows']} rows ({mm['row_pct']:.2f}%) over {mm['clusters']} clusters")
    print(f"\n  wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()


def listed_split() -> dict:
    """Why does the `listed` bucket disagree MORE than the venture one?

    Table 12 shows listed issuers at a wider median than venture-backed ones, which reads
    at first like a finding: that a Level-3 mark predicts disagreement whatever the company
    is. It is not. Split the bucket by whether the marks ever move and the two halves come
    apart completely. Where every house has frozen its number — a suspension, a halt, a
    delisting — the houses agree almost exactly. The dispersion is entirely in the half that
    is still being priced, and those are tiny positions: a twentieth of the value per cell
    of a venture one, in names like post-reorganisation stubs and delisted microcaps.

    So the bucket is a residue, not a result, and the manuscript says so in one sentence
    rather than a section.
    """
    d, c = pop.panel()
    g = c[c.guarded].merge(classify()[["label"]], left_on="company", right_index=True)
    lst, ven = g[g.label == LISTED], g[g.label == VENTURE]
    x = pop.comparable(d)
    moves = {}
    for co, grp in x[x.company.isin(lst.company.unique())].groupby("company"):
        h = grp.groupby(["house", grp.dt]).pps.median().groupby(level=0)
        moves[co] = any((v.pct_change().abs() > pop.REMARK_TOL).any() for _, v in h if len(v) > 1)
    lst = lst.assign(moves=lst.company.map(moves))
    mv, fz = lst[lst.moves], lst[~lst.moves]
    return {
        "listed_median": float(lst.spread_pct.median()),
        "frozen_companies": int(fz.company.nunique()), "frozen_cells": len(fz),
        "frozen_median": float(fz.spread_pct.median()),
        "frozen_above_24_pct": float((fz.spread_pct > 24).mean() * 100),
        "moving_companies": int(mv.company.nunique()), "moving_cells": len(mv),
        "moving_median": float(mv.spread_pct.median()),
        "listed_nav_per_cell_musd": float(lst.nav.median() / 1e6),
        "venture_nav_per_cell_musd": float(ven.nav.median() / 1e6),
    }
