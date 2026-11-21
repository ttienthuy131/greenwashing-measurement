"""Keyword dictionary baseline shared by passage extraction and scoring."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DICTIONARY = Path(__file__).parents[1] / "codebook" / "climate_dictionary.json"
NUMBER = re.compile(r"\d")


def _pattern(terms: list[str]) -> re.Pattern[str]:
    alternatives = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.IGNORECASE)


@dataclass(frozen=True)
class Dictionary:
    version: str
    topic: re.Pattern[str]
    outcome: re.Pattern[str]
    target: re.Pattern[str]

    def is_climate(self, text: str) -> bool:
        return bool(self.topic.search(text))

    def classify(self, text: str) -> str:
        """Assign a rubric Label A code (0-3) from keyword cues."""
        if not self.is_climate(text):
            return "0"
        has_number = bool(NUMBER.search(text))
        if has_number and self.outcome.search(text):
            return "3"
        if self.target.search(text):
            return "2"
        return "1"


def load_dictionary(path: Path = DEFAULT_DICTIONARY) -> Dictionary:
    spec = json.loads(path.read_text(encoding="utf-8"))
    return Dictionary(
        version=spec["version"],
        topic=_pattern(spec["topic_terms"]),
        outcome=_pattern(spec["outcome_cues"]),
        target=_pattern(spec["target_cues"]),
    )
