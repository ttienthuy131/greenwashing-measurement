# greenwashing-measurement

**Status: Work in progress.**

## Research question

How can corporate climate-related claims be measured and compared with changes in reported greenhouse gas emissions?

## Planned approach

The pilot will begin with three to five companies selected from energy-related firms in the top 200 of the 2026 Fortune 500, which ranks U.S. companies by revenue. Eligible firms will be screened and ranked using the latest publicly available EPA GHGRP direct-emissions data. See the [research design](docs/research-design.md) for selection rules and the [coding rubric](codebook/rubric.md) for passage-level labels.

1. Collect sustainability reports and extract climate-related passages.
2. Develop a scoring rubric and compare model and dictionary-based scores with independently hand-labeled passages.
3. Match companies to reported U.S. facility emissions and examine differences between their claims and emissions trends.

## Scope and limitations

The [EPA Greenhouse Gas Reporting Program](https://www.epa.gov/ghgreporting/what-ghgrp) reports direct emissions at the facility level and does not capture all emissions associated with a parent company. Differences between a company's claims and these emissions are signals for further investigation, not conclusive evidence of greenwashing.

## Data status

Run `python src/01_collect.py` to download and checksum the public EPA source files locally. Raw files are excluded from Git. The company sample and report set are not assembled, and no scores or empirical results have been produced.
