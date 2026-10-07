# Data rights and sourcing method

## What data this paper uses

**The private-side signals are public-only.** SEC N-PORT fund marks, Forge secondary prices, and public unicorn lists carry every result. The paper's edge is that anyone can rebuild it, so a gated source in the core would defeat the point.

**PitchBook: declined.** Its academic license caps exports at 10 records a day and 25 a month, bars programmatic access, and prohibits publishing the data to a public forum. Any one of those rules it out for a paper whose replication package is public; together they also make it useless as a private check, since a number I cannot show is a number I cannot defend.

**WRDS: considered, not used.** CRSP/Compustat would have given cleaner post-IPO price series for the validation leg (§4.3), but raw WRDS data may not be redistributed, which would have put a gated dependency in the middle of an otherwise open pipeline. The realized IPO prices come from contemporaneous public reporting instead, each carrying its source and date in `data/ipo_validation.csv`. The paper reproduces with no licensed data at all.

## Sourcing rules

1. **Two independent sources before a number enters a data file.** One source is a lead, not a fact.
2. **Read the source, not the summary.** Search snippets and preview cards drop qualifiers and misattribute dates.
3. **Cross-check across source *types*, not just sources.** A fund mark, a secondary quote, a filing and a news report fail in different ways, so agreement across kinds is worth more than agreement across several outlets of the same kind.
4. **Every number carries provenance** — source and access date, recorded in the data file itself rather than in prose.

## A coverage limit worth stating plainly

The N-PORT harvester (`src/nport_fetch.py`) pages EDGAR full-text search and stops once it has downloaded 18 filings for a company or found marks from 14 distinct funds, whichever comes first. That keeps the harvest inside SEC fair-access limits, but it does not guarantee every filer holding a given name is found. The direction of that error is fixed: a filer the sweep never reached is one this paper failed to count, so the dispersion figures sit at the bottom of the range the full filing record would support. Appendix D documents a case where a deeper sweep on one company surfaced five more funds and a much wider spread than the capped harvest recorded.
