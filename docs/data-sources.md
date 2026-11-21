# Data source register

**Last checked:** November 21, 2026

| Source | Coverage and purpose | Access and handling |
|---|---|---|
| [Fortune 500, 2026 edition](https://fortune.com/ranking/fortune500/) | Revenue-ranked U.S. company frame; the pilot protocol proposes ranks 1–200. | The public page shows the ranking introduction and top entries, and links to purchase the full data. Do not scrape Fortune. Obtain the data through authorized access or choose a fully accessible alternative before finalizing the top-200 frame. |
| [EPA GHGRP 2023 Data Summary Spreadsheets](https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip) | Public reporting-year summary files, including facility-level emissions and multi-year tables. | Download with `python src/01_collect.py`. The file is stored locally under ignored `data/raw/`; do not commit the binary source. |
| [EPA Reported Parent Companies](https://www.epa.gov/system/files/other-files/2024-10/ghgp_data_parent_company.xlsb) | Facility-reported highest-level U.S. parent names and reported ownership percentages. | Download with `python src/01_collect.py`. Preserve the source rows and record manual match decisions separately. Percent ownership is not necessarily a measure of emissions responsibility. |
| [EPA GHGRP reported data](https://www.epa.gov/ghgreporting/ghgrp-reported-data) | Reporting-year definitions, coverage, sector summaries, and interpretation limits. | EPA identifies RY 2023 as the most recent publicly available year checked for this project. Recheck before freezing the sample. |

## Collection notes

- The downloader records the source URL, retrieval time, byte count, and SHA-256 digest in `data/raw/manifest.json`.
- Raw downloads are excluded from Git. Keep derived tables small and document their generation from the public sources.
- Do not collect or commit sustainability-report PDFs. Store report URLs, retrieval dates, covered fiscal years, and page references; check rights before retaining report text.
- Do not include supplier-reported potential emissions in direct facility-emissions totals.
- Manual parent-company matching must retain the EPA-reported name, the normalized candidate name, the evidence for the match, and a reviewer decision.
