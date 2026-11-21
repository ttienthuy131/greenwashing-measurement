# Pilot research design

**Status:** Initial RY2023 facility screen complete for all five Fortune top-50 Energy candidates. Report-period candidates are registered; human claim annotation and claims-versus-emissions analysis have not started.

## Question

How do the content and evidentiary support of large U.S. energy companies' climate claims compare with changes in their reported direct greenhouse gas emissions?

## Sampling frame

Use Fortune's 2026 Explorer pilot frame: the 50 highest-revenue U.S. companies, ranked using revenue for the latest fiscal year. The Explorer identifies five of these companies in its Energy sector. Record the Fortune rank, company name as listed, fiscal year, and source URL for each candidate.

1. Start with the Explorer's Energy-sector candidates in the top-50 frame.
2. Confirm that each candidate's core operations include oil and gas production, integrated oil and gas, petroleum refining, natural gas or petroleum pipelines, or electric power generation and utilities. Record the evidence and classification. Do not include an energy-equipment or financial company solely because it serves or invests in the energy sector.
3. Match the screened companies to EPA Greenhouse Gas Reporting Program (GHGRP) direct-emitter facilities using the EPA reported-parent-company file. Keep a documented alias and ownership crosswalk; do not match on company-name similarity alone.
4. For each firm and reporting year, identify facilities with exactly one reported highest-level U.S. parent that matches the firm and has 100% reported ownership. Deduplicate facility-year records and rank firms by those facilities' direct emissions in reporting year 2023. Do not multiply emissions by EPA-reported ownership percentages: when multiple parents are reported, EPA notes that these percentages do not necessarily represent each parent's share of facility emissions. Keep multi-parent and partial-ownership facilities in a separate matched-but-unallocated file for sensitivity analysis.
5. Select three to five firms with the highest eligible GHGRP emissions and a usable climate or sustainability report whose stated period can be aligned with reporting year 2023. If a candidate cannot be matched or has no usable, alignable report, record the reason and move to the next firm.
6. Report the full screening and attrition counts. Describe the pilot as a feasibility sample of large emitters, not as representative of all U.S. firms or energy companies.

The Fortune Explorer supplies a small revenue-based pilot frame, not an emissions ranking. GHGRP coverage supplies a separate facility-level emissions screen. The five Fortune energy-sector candidates in this frame are a feasibility sample, not a representative sample of U.S. energy companies. As of November 21, 2026, EPA identifies reporting year (RY) 2023 as the most recent publicly available GHGRP data. Recheck this before freezing the sample.

## Unit of analysis and time alignment

- **Text unit:** A climate-related claim and the minimum surrounding context needed to interpret it, with a report identifier and page or section.
- **Emissions unit:** EPA facility and reporting year. Preserve the facility ID and parent-company attribution used in each match.
- **Firm-year:** Aggregate matched facility observations to a firm-year only after deduplicating facilities and resolving parent-company ownership.
- **Alignment:** Start with report periods that overlap the available EPA years. Record publication year separately from the report's covered fiscal year. Do not compare unlike periods without labeling the lag.

The primary selection metric is direct emissions at facilities with a sole, fully reported parent match. This conservative rule avoids allocating shared facility emissions using ownership percentages that may not represent emissions responsibility, but it can understate firms with joint ownership. Report the separate multi-parent and partial-ownership facility coverage and do not combine supplier-reported potential emissions with facility direct emissions.

## Initial screen

The source-reviewed crosswalk and downloaded EPA RY2023 files produce the following descriptive screen. Results are facility emissions for records meeting the stated sole-parent rule, not complete company inventories. Matched facilities that fail that rule remain unallocated; neither group establishes whether a climate claim is misleading.

| Fortune rank | Company | Sole-parent facilities | Sole-parent direct emissions (mtCO2e) | Matched but unallocated facilities |
|---:|---|---:|---:|---:|
| 9 | Exxon Mobil Holdings | 15 | 31,058,673 | 20 |
| 30 | Marathon Petroleum | 21 | 28,273,366 | 5 |
| 40 | Valero Energy | 26 | 23,500,508 | 1 |
| 29 | Phillips 66 | 16 | 22,312,816 | 47 |
| 21 | Chevron | 9 | 13,717,367 | 23 |

These are all five Energy candidates in the chosen Fortune frame, not a random or representative sample. Company report candidates and the evidence for aligning them to 2023 are in `data/inputs/pilot_reports.csv`. In particular, EPA lists both CHEVRON USA INC (100%) and PETROBRAS AMERICA INC (0%) for facility 1005903, so that facility remains unallocated under the exactly-one-reported-parent rule.

## Interpretation limits

GHGRP captures reported emissions from covered facilities; it is not a complete corporate greenhouse-gas inventory. It does not by itself measure all operational sources, purchased electricity, value-chain emissions, or the accuracy of public claims. A rise or fall in reported emissions alone cannot establish greenwashing. Treat a gap between claims and measured emissions as a signal for investigation, and present coverage, missing matches, organizational changes, and reporting boundaries alongside the comparison.

## Pilot deliverables

1. A source and sample register with Fortune rank, business-line rationale, report coverage, GHGRP facility IDs, parent-company match evidence, and exclusions.
2. A documented, versioned passage-level codebook and a small manually labeled set.
3. A reproducible comparison of human labels, a transparent dictionary baseline, and an LLM score. Report agreement and errors; do not assume the LLM is better.
4. A firm-level claims-versus-emissions visualization with the matching and coverage caveats visible.

Defer panel regressions until the pilot establishes adequate firm-year coverage and a defensible measure. Do not treat the initial three-to-five-firm pilot as enough observations for causal claims.

The blank annotation schema is `data/templates/annotation_template.csv`. Human coders must complete it using the rubric; do not fill human-label fields with model-generated values. Keep report PDFs and report text out of Git unless retention and sharing rights have been checked.

## Public sources

- [Fortune 500 Explorer](https://fortune.com/ranking/fortune500/2026/explore/): public top-50 pilot frame and Energy-sector count. The exact candidate ranks used are recorded in `data/inputs/fortune_top50_energy_candidates.csv`; do not scrape the site. See [data source notes](data-sources.md).
- [EPA GHGRP reported data](https://www.epa.gov/ghgreporting/ghgrp-reported-data): descriptions of the program and reported data.
- [EPA GHGRP data sets](https://www.epa.gov/ghgreporting/data-sets): downloadable data, including the reported parent-company file.
- [SEC EDGAR company facts](https://www.sec.gov/edgar/sec-api-documentation): possible source for later firm financial controls; not required for pilot selection.

Do not commit copyrighted report PDFs. Keep source URLs, retrieval dates, and permitted derived data instead. Never commit API keys or other credentials.
