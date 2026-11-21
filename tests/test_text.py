import importlib.util
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(SRC))

from dictionary import load_dictionary  # noqa: E402

SPEC = importlib.util.spec_from_file_location("extract", SRC / "03_extract.py")
assert SPEC is not None and SPEC.loader is not None
extract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extract)

# Synthetic sentences written for tests; they are not quotations from any report.
DICTIONARY = load_dictionary()


class DictionaryTests(unittest.TestCase):
    def test_codes_follow_rubric_order(self):
        cases = {
            "Our cafeterias serve local food.": "0",
            "We are committed to a lower-carbon future.": "1",
            "We set a target to cut methane intensity by 2030.": "2",
            "We reduced Scope 1 emissions by 12% from 2019 to 2023.": "3",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(DICTIONARY.classify(text), expected)

    def test_terms_match_whole_words_only(self):
        self.assertFalse(DICTIONARY.is_climate("The carbonated drinks were cold."))
        self.assertTrue(DICTIONARY.is_climate("Carbon capture began in 2023."))

    def test_outcome_cue_without_number_is_not_a_reported_outcome(self):
        self.assertEqual(DICTIONARY.classify("We reduced emissions."), "1")


class PassageTests(unittest.TestCase):
    def test_blank_lines_separate_passages_and_hyphenation_is_joined(self):
        page = "First para-\ngraph about emissions.\n\nSecond paragraph."
        self.assertEqual(
            extract.split_passages(page),
            ["First paragraph about emissions.", "Second paragraph."],
        )

    def test_long_blocks_are_split_at_sentence_boundaries(self):
        page = " ".join(["Emissions fell this year."] * 10)
        passages = extract.split_passages(page, max_words=8)
        self.assertTrue(all(len(p.split()) <= 8 for p in passages))
        self.assertEqual(" ".join(passages), page)

    def test_only_climate_passages_meeting_length_are_kept(self):
        pages = ["Methane emissions fell.\n\nBoard meeting held.", "Carbon goal."]
        kept = list(extract.climate_passages(pages, DICTIONARY, 3, 150))
        self.assertEqual(kept, [(1, "Methane emissions fell.")])

    def test_passage_id_is_stable(self):
        self.assertEqual(
            extract.passage_id("9", 4, "text"),
            extract.passage_id("9", 4, "text"),
        )
        self.assertTrue(extract.passage_id("9", 4, "text").startswith("9-p004-"))


if __name__ == "__main__":
    unittest.main()
