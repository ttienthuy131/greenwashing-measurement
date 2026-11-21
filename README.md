# greenwashing-measurement

**Status: Work in progress.**

## Research question

How can corporate climate-related claims be measured and compared with changes in reported greenhouse gas emissions?

## Planned approach

The pilot will begin with three to five companies from the five Energy-sector candidates in Fortune's publicly accessible top-50 Explorer. Eligible firms will be screened using EPA GHGRP direct-emissions data. See the [research design](docs/research-design.md) for selection rules and the [coding rubric](codebook/rubric.md) for passage-level labels.

1. Collect sustainability reports and extract climate-related passages.
2. Develop a scoring rubric and compare model and dictionary-based scores with independently hand-labeled passages.
3. Match companies to reported U.S. facility emissions and examine differences between their claims and emissions trends.

## Scope and limitations

The [EPA Greenhouse Gas Reporting Program](https://www.epa.gov/ghgreporting/what-ghgrp) reports direct emissions at the facility level and does not capture all emissions associated with a parent company. Differences between a company's claims and these emissions are signals for further investigation, not conclusive evidence of greenwashing.

## Data status

Install the parser dependencies with `python -m pip install -r requirements.txt`, then run `python src/01_collect.py` and `python src/02_parse.py` to download, checksum, and screen the public EPA source files locally. Raw and interim files are excluded from Git. The Fortune-to-EPA parent-name crosswalk has been source-reviewed for RY2023 and documented aliases are included for the 2019-2023 screen. Review year-specific ownership and coverage before interpreting historical trends. These screens are not corporate emissions inventories or greenwashing findings. Reports have not been collected, and human annotation has not started.
