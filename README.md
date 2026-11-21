# greenwashing-measurement

**Status: Work in progress.**

## Research question

How can corporate climate-related claims be measured and compared with changes in reported greenhouse gas emissions?

## Approach

The pilot covers the five Energy-sector companies in Fortune's publicly accessible top-50 Explorer. See the [research design](docs/research-design.md) for selection rules and the [coding rubric](codebook/rubric.md) for passage-level labels.

| Step | Script | Output (not in Git) |
|---|---|---|
| Download EPA files and report PDFs | `src/01_collect.py` | `data/raw/` |
| Match companies to EPA facilities | `src/02_parse.py` | `data/interim/fortune_top50_energy_*.csv` |
| Split reports into climate passages | `src/03_extract.py` | `data/interim/passages.jsonl` |
| Label passages (dictionary or LLM) | `src/04_score.py` | `data/interim/scores/*.csv` |
| Compare labels with human coding | `src/05_validate.py` | `outputs/validation.md` |
| Join claims to emissions change | `src/06_merge.py` | `outputs/*.csv`, `outputs/*.png` |

The dictionary baseline uses the keyword lists in `codebook/climate_dictionary.json`. LLM scoring works with any OpenAI-compatible endpoint, including a local open model through Ollama. Prompts are versioned in `prompts/`; the model, temperature, and seed are fixed per run; responses are cached in `data/cache/llm/`; and token use and estimated cost are logged in `data/interim/scores/llm_runs.jsonl`. Validation reports Cohen's kappa against human labels and across prompt and model runs.

## Running the code

```powershell
python -m pip install -r requirements.txt   # or: conda env create -f environment.yml
python src/01_collect.py --reports
python src/02_parse.py
python src/03_extract.py
python src/04_score.py dictionary
$env:LLM_API_KEY = "..."                     # never commit keys
python src/04_score.py llm --model MODEL --prompt prompts/claim_status_v1.md
python src/05_validate.py
python src/06_merge.py --scores data/interim/scores/dictionary_v0.1.csv
python -m unittest discover -s tests
```

The `Makefile` wraps the same commands. Some company sites block scripted PDF downloads; save those reports manually as `data/raw/reports/{fortune_rank}.pdf`. For a local open model, pass `--base-url http://localhost:11434/v1`.

## Scope and limitations

The [EPA Greenhouse Gas Reporting Program](https://www.epa.gov/ghgreporting/what-ghgrp) reports direct emissions at the facility level and does not capture all emissions associated with a parent company. Differences between a company's claims and these emissions are signals for further investigation, not conclusive evidence of greenwashing.

## Status

The code pipeline is complete and tested with synthetic examples. Human annotation has not started, so no validation results or claims-versus-emissions findings are reported. The EPA crosswalk has been source-reviewed for RY2023; review year-specific ownership and coverage before interpreting 2019-2023 trends. The EPA screens are not corporate emissions inventories or greenwashing findings.
