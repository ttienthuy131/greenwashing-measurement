# Pilot research design

**Status:** Design stage. The sample has not yet been assembled, and no empirical results are available.

## Question

How do the content and evidentiary support of large U.S. energy companies' climate claims compare with changes in their reported direct greenhouse gas emissions?

## Sampling frame

Use the 2026 Fortune 500 as the company universe. It ranks U.S. companies by revenue reported for fiscal year 2025. Record the Fortune rank, company name as listed, fiscal year, and source URL for every screened firm.

1. Start with ranks 1–200.
2. Screen for companies whose core operations include oil and gas production, integrated oil and gas, petroleum refining, natural gas or petroleum pipelines, or electric power generation and utilities. Record the evidence and classification for each included company. Do not include an energy-equipment or financial company solely because it serves or invests in the energy sector.
3. Match the screened companies to EPA Greenhouse Gas Reporting Program (GHGRP) direct-emitter facilities using the EPA reported-parent-company file. Keep a documented alias and ownership crosswalk; do not match on company-name similarity alone.
4. For each firm and reporting year, calculate ownership-attributable direct emissions by multiplying each matched facility's direct emissions by the EPA-reported ownership percentage. Deduplicate facility-parent-year rows. Rank matched firms by this measure for reporting year 2023. Retain the gross emissions at matched facilities as a separate descriptive measure.
5. Select the five highest-ranked firms with a usable climate or sustainability report whose stated period can be aligned with reporting year 2023. If a candidate cannot be matched or has no usable, alignable report, record the reason and move to the next firm.
6. Report the full screening and attrition counts. Describe the pilot as a feasibility sample of large emitters, not as representative of all U.S. firms or energy companies.

The Fortune 500 supplies a revenue-based company frame, not an emissions ranking. GHGRP coverage supplies a separate facility-level emissions screen. As of November 21, 2026, EPA identifies reporting year (RY) 2023 as the most recent publicly available GHGRP data. Recheck this before freezing the sample.

## Unit of analysis and time alignment

- **Text unit:** A climate-related claim and the minimum surrounding context needed to interpret it, with a report identifier and page or section.
- **Emissions unit:** EPA facility and reporting year. Preserve the facility ID and parent-company attribution used in each match.
- **Firm-year:** Aggregate matched facility observations to a firm-year only after deduplicating facilities and resolving parent-company ownership.
- **Alignment:** Start with report periods that overlap the available EPA years. Record publication year separately from the report's covered fiscal year. Do not compare unlike periods without labeling the lag.

The primary selection metric is ownership-attributable emissions, not operational-control emissions. State this distinction and retain both attributable and gross figures so readers can see how the attribution choice affects results. EPA's reported parent-company file includes parent-company names and ownership percentages. Do not combine supplier-reported potential emissions with facility direct emissions.

## Interpretation limits

GHGRP captures reported emissions from covered facilities; it is not a complete corporate greenhouse-gas inventory. It does not by itself measure all operational sources, purchased electricity, value-chain emissions, or the accuracy of public claims. A rise or fall in reported emissions alone cannot establish greenwashing. Treat a gap between claims and measured emissions as a signal for investigation, and present coverage, missing matches, organizational changes, and reporting boundaries alongside the comparison.

## Pilot deliverables

1. A source and sample register with Fortune rank, business-line rationale, report coverage, GHGRP facility IDs, parent-company match evidence, and exclusions.
2. A documented, versioned passage-level codebook and a small manually labeled set.
3. A reproducible comparison of human labels, a transparent dictionary baseline, and an LLM score. Report agreement and errors; do not assume the LLM is better.
4. A firm-level claims-versus-emissions visualization with the matching and coverage caveats visible.

Defer panel regressions until the pilot establishes adequate firm-year coverage and a defensible measure. Do not treat the initial three-to-five-firm pilot as enough observations for causal claims.

## Public sources

- [Fortune 500 ranking](https://fortune.com/ranking/fortune500/): revenue-ranked U.S. company universe. Record the edition and rank used.
- [EPA GHGRP reported data](https://www.epa.gov/ghgreporting/ghgrp-reported-data): descriptions of the program and reported data.
- [EPA GHGRP data sets](https://www.epa.gov/ghgreporting/data-sets): downloadable data, including the reported parent-company file.
- [SEC EDGAR company facts](https://www.sec.gov/edgar/sec-api-documentation): possible source for later firm financial controls; not required for pilot selection.

Do not commit copyrighted report PDFs. Keep source URLs, retrieval dates, and permitted derived data instead. Never commit API keys or other credentials.
