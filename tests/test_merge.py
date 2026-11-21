import importlib.util
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("merge", SRC / "06_merge.py")
assert SPEC is not None and SPEC.loader is not None
merge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merge)

# Synthetic firms and labels for testing only.
PASSAGES = [
    {"passage_id": f"p{i}", "fortune_rank": 1, "company_name": "Firm A"} for i in range(5)
] + [{"passage_id": "q0", "fortune_rank": 2, "company_name": "Firm B"}]
LABELS = {"p0": "1", "p1": "1", "p2": "3", "p3": "0", "p4": "U", "q0": "0"}
TRENDS = [
    {"fortune_rank": "1", "reporting_year": "2019", "sole_100pct_emissions_mtco2e": "200"},
    {"fortune_rank": "1", "reporting_year": "2023", "sole_100pct_emissions_mtco2e": "150"},
    {"fortune_rank": "2", "reporting_year": "2019", "sole_100pct_emissions_mtco2e": "0"},
    {"fortune_rank": "2", "reporting_year": "2023", "sole_100pct_emissions_mtco2e": "10"},
]


class MergeTests(unittest.TestCase):
    def test_shares_use_claim_passages_only(self):
        firm = merge.claim_measures(PASSAGES, LABELS)["1"]
        self.assertEqual(firm["claim_passages"], 3)
        self.assertAlmostEqual(firm["general_share"], 2 / 3)
        self.assertAlmostEqual(firm["outcome_share"], 1 / 3)
        self.assertEqual(firm["unclear_or_invalid"], 1)

    def test_no_claims_and_zero_baseline_give_missing_values(self):
        rows = merge.merge(merge.claim_measures(PASSAGES, LABELS), merge.emissions_change(TRENDS, 2019, 2023))
        self.assertEqual(rows[0]["emissions_pct_change"], -25.0)
        self.assertIsNone(rows[1]["general_share"])
        self.assertIsNone(rows[1]["emissions_pct_change"])

    def test_plot_skips_incomplete_firms(self):
        rows = merge.merge(merge.claim_measures(PASSAGES, LABELS), merge.emissions_change(TRENDS, 2019, 2023))
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / "figure.png"
            self.assertEqual(merge.plot(rows, path, "synthetic", 2019, 2023), 1)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
