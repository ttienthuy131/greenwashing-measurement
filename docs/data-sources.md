# Data source register

**Last checked:** November 21, 2026

| Source | Coverage and purpose | Access and handling |
|---|---|---|
| [Fortune 500 Explorer, 2026 edition](https://fortune.com/ranking/fortune500/2026/explore/) | Publicly accessible top-50 revenue frame; the Explorer identifies five Energy-sector candidates. | Candidate ranks and names are recorded in `data/inputs/fortune_top50_energy_candidates.csv`. Do not automate extraction from Fortune. This pilot frame is narrower than the initially proposed top 200. |
| [EPA GHGRP 2023 Data Summary Spreadsheets](https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip) | Public reporting-year summary files, including facility-level emissions and multi-year tables. | Download with `python src/01_collect.py`. The file is stored locally under ignored `data/raw/`; do not commit the binary source. |
| [EPA Reported Parent Companies](https://www.epa.gov/system/files/other-files/2024-10/ghgp_data_parent_company.xlsb) | Facility-reported highest-level U.S. parent names and reported ownership percentages. | Download with `python src/01_collect.py`. Preserve the source rows and record manual match decisions separately. Percent ownership is not necessarily a measure of emissions responsibility. |
| [e-GGRT FAQ Q742](https://ccdsupport.com/legacy/confluence/pages/viewpage.action?pageId=207454228) | Explains parent-company matching and limits of ownership percentages. | EPA's helpdesk notes that when multiple parents are reported, ownership percentage does not necessarily equal that parent's share of facility emissions. |
| [EPA GHGRP reported data](https://www.epa.gov/ghgreporting/ghgrp-reported-data) | Reporting-year definitions, coverage, sector summaries, and interpretation limits. | EPA identifies RY 2023 as the most recent publicly available year checked for this project. Recheck before freezing the sample. |

## Collection notes

- The downloader records the source URL, retrieval time, byte count, and SHA-256 digest in `data/raw/manifest.json`.
- Run `python src/02_parse.py` after installing `requirements.txt` to create the RY2023 screen and the retrospective RY2019-2023 trend table under ignored `data/interim/`. Review each year's ownership and facility coverage before interpreting the trend table at company level.
- Raw downloads are excluded from Git. Keep derived tables small and document their generation from the public sources.
- Do not commit sustainability-report PDFs or report text. `python src/01_collect.py --reports` saves PDFs from the register to ignored `data/raw/reports/{fortune_rank}.pdf`. Several company sites block scripted downloads; in that case save the PDF manually under the same name. Store report URLs, retrieval dates, covered fiscal years, and page references; check rights before retaining report text.
- Do not include supplier-reported potential emissions in direct facility-emissions totals.
- Manual parent-company matching must retain the EPA-reported name, the normalized candidate name, the evidence for the match, and a reviewer decision.
- Official report-page candidates and period-alignment notes are listed in `data/inputs/pilot_reports.csv`; no report PDFs are included in the repository.
