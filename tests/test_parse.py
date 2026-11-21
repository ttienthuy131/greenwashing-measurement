import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "src" / "02_parse.py"
SPEC = importlib.util.spec_from_file_location("parse_ghgrp", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
parse_ghgrp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parse_ghgrp)


class AttributionTests(unittest.TestCase):
    def test_single_full_owner_is_primary(self):
        owners = [
            {"parent_company_name": "EXXON MOBIL CORP", "ownership_percent": 100.0}
        ]
        self.assertEqual(
            parse_ghgrp.classify_attribution(owners, "Exxon Mobil Corp"),
            "sole_100pct_parent",
        )

    def test_partial_ownership_is_not_allocated(self):
        owners = [
            {"parent_company_name": "CHEVRON CORP", "ownership_percent": 50.0}
        ]
        self.assertEqual(
            parse_ghgrp.classify_attribution(owners, "CHEVRON CORP"),
            "unallocated_shared_or_partial",
        )

    def test_multiple_parents_are_not_allocated(self):
        owners = [
            {"parent_company_name": "PHILLIPS 66", "ownership_percent": 50.0},
            {"parent_company_name": "OTHER PARENT", "ownership_percent": 50.0},
        ]
        self.assertEqual(
            parse_ghgrp.classify_attribution(owners, "PHILLIPS 66"),
            "unallocated_shared_or_partial",
        )

    def test_zero_percent_second_parent_still_prevents_allocation(self):
        owners = [
            {"parent_company_name": "CHEVRON USA INC", "ownership_percent": 100.0},
            {"parent_company_name": "OTHER PARENT", "ownership_percent": 0.0},
        ]
        self.assertEqual(
            parse_ghgrp.classify_attribution(owners, "CHEVRON USA INC"),
            "unallocated_shared_or_partial",
        )

    def test_unrelated_parent_does_not_match(self):
        owners = [
            {"parent_company_name": "OTHER PARENT", "ownership_percent": 100.0}
        ]
        self.assertEqual(
            parse_ghgrp.classify_attribution(owners, "PHILLIPS 66"),
            "not_matched",
        )


if __name__ == "__main__":
    unittest.main()
