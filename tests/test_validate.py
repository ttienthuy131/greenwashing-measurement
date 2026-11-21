import importlib.util
import unittest
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("validate", SRC / "05_validate.py")
assert SPEC is not None and SPEC.loader is not None
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class KappaTests(unittest.TestCase):
    def test_perfect_agreement_is_one(self):
        self.assertEqual(validate.cohen_kappa([("1", "1"), ("2", "2"), ("3", "3")]), 1.0)

    def test_known_value(self):
        # Synthetic 2x2 table: 20 yes/yes, 5 yes/no, 10 no/yes, 15 no/no.
        pairs = [("1", "1")] * 20 + [("1", "0")] * 5 + [("0", "1")] * 10 + [("0", "0")] * 15
        self.assertAlmostEqual(validate.cohen_kappa(pairs), 0.4)

    def test_single_category_and_empty(self):
        self.assertEqual(validate.cohen_kappa([("1", "1")] * 3), 1.0)
        self.assertIsNone(validate.cohen_kappa([]))


class ReportTests(unittest.TestCase):
    def test_per_class_precision_recall(self):
        pairs = [("2", "2"), ("2", "1"), ("1", "1")]
        metrics = validate.per_class(pairs)
        self.assertEqual(metrics["1"]["precision"], 0.5)
        self.assertEqual(metrics["2"]["recall"], 0.5)

    def test_report_only_compares_shared_passages(self):
        human = {"coder_a": {"p1": "1", "p2": "2"}, "coder_b": {"p1": "1"}}
        runs = {"dictionary": {"p1": "1", "p2": "3", "p3": "0"}, "llm": {"p1": "1", "p2": "2"}}
        report = validate.build_report(human, runs, "coder_a")
        self.assertIn("| coder_a | coder_b | 1 |", report)
        self.assertIn("### dictionary\n\nn = 2", report)
        self.assertIn("| dictionary | llm | 2 |", report)

    def test_report_without_human_labels(self):
        report = validate.build_report({}, {"a": {"p": "1"}, "b": {"p": "1"}}, None)
        self.assertIn("No human labels found", report)
        self.assertIn("Stability across scoring runs", report)


if __name__ == "__main__":
    unittest.main()
