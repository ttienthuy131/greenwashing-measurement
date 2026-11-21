PYTHON ?= python
MODEL ?= gpt-4o-mini
PROMPT ?= prompts/claim_status_v1.md

.PHONY: all collect epa reports extract score llm validate merge test

all: collect epa extract score validate merge

collect:
	$(PYTHON) src/01_collect.py

epa:
	$(PYTHON) src/02_parse.py

reports:
	$(PYTHON) src/01_collect.py --reports

extract:
	$(PYTHON) src/03_extract.py

score:
	$(PYTHON) src/04_score.py dictionary

llm:
	$(PYTHON) src/04_score.py llm --model $(MODEL) --prompt $(PROMPT)

validate:
	$(PYTHON) src/05_validate.py

merge:
	$(PYTHON) src/06_merge.py --scores data/interim/scores/dictionary_v0.1.csv

test:
	$(PYTHON) -m unittest discover -s tests
