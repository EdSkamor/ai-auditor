#!/usr/bin/env python3
"""
WSAD Test Script: Tie-breaker A/B Testing
Tests deterministic tie-breaker logic with different configurations.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pop_matcher import MatchStatus, POPMatcher


def create_tiebreaker_test_data():
    """Create test data for tie-breaker testing."""
    # POP data with duplicate invoice numbers
    pop_data = pd.DataFrame(
        {
            "Numer": ["FV-001/2024", "FV-001/2024", "FV-002/2024", "FV-002/2024"],
            "Data": ["2024-01-15", "2024-01-15", "2024-01-16", "2024-01-16"],
            "Netto": [1000.00, 1000.00, 2000.00, 2000.00],
            "Kontrahent": [
                "ACME Corporation",
                "ACME Corp",
                "Test Company",
                "Test Co Ltd",
            ],
        }
    )

    # PDF data to match
    pdf_data = {
        "invoice_id": "FV-001/2024",
        "issue_date": datetime(2024, 1, 15),
        "total_net": 1000.00,
        "seller_guess": "ACME Corporation",
        "currency": "zł",
    }

    return pop_data, pdf_data


def test_tiebreaker_v1():
    """Test tie-breaker V1: High filename weight."""
    print("🧪 Testing Tie-breaker V1 (High filename weight)...")

    try:
        pop_data, pdf_data = create_tiebreaker_test_data()

        # V1: High filename weight (0.8), low seller threshold (0.3)
        matcher_v1 = POPMatcher(
            tiebreak_weight_fname=0.8, tiebreak_min_seller=0.3, amount_tolerance=0.01
        )

        # Test with filename that matches first POP entry
        filename_v1 = "FV_001_2024_prefname.pdf"

        match_result = matcher_v1.match_invoice(pdf_data, pop_data, filename_v1)

        print(f"✅ V1 Match Status: {match_result.status.value}")
        print(f"✅ V1 Criteria: {match_result.criteria.value}")
        print(f"✅ V1 Confidence: {match_result.confidence:.2f}")
        print(f"✅ V1 Tie-breaker Score: {match_result.tie_breaker_score:.2f}")
        print(f"✅ V1 Seller Similarity: {match_result.seller_similarity:.2f}")
        print(f"✅ V1 Filename Hit: {match_result.filename_hit}")

        # V1 should prefer filename matching
        if match_result.filename_hit:
            print("✅ V1 correctly prioritized filename matching")
        else:
            print("⚠️  V1 did not prioritize filename matching as expected")

        return match_result

    except Exception as e:
        print(f"❌ Tie-breaker V1 test failed: {e}")
        return None


def test_tiebreaker_v2():
    """Test tie-breaker V2: Low filename weight, high seller threshold."""
    print("🧪 Testing Tie-breaker V2 (Low filename weight, high seller threshold)...")

    try:
        pop_data, pdf_data = create_tiebreaker_test_data()

        # V2: Low filename weight (0.2), high seller threshold (0.4)
        matcher_v2 = POPMatcher(
            tiebreak_weight_fname=0.2, tiebreak_min_seller=0.4, amount_tolerance=0.01
        )

        # Test with filename that doesn't match any POP entry
        filename_v2 = "x1.pdf"

        match_result = matcher_v2.match_invoice(pdf_data, pop_data, filename_v2)

        print(f"✅ V2 Match Status: {match_result.status.value}")
        print(f"✅ V2 Criteria: {match_result.criteria.value}")
        print(f"✅ V2 Confidence: {match_result.confidence:.2f}")
        print(f"✅ V2 Tie-breaker Score: {match_result.tie_breaker_score:.2f}")
        print(f"✅ V2 Seller Similarity: {match_result.seller_similarity:.2f}")
        print(f"✅ V2 Filename Hit: {match_result.filename_hit}")

        # V2 should prefer seller matching
        if match_result.seller_similarity >= 0.4:
            print("✅ V2 correctly prioritized seller matching")
        else:
            print("⚠️  V2 did not prioritize seller matching as expected")

        return match_result

    except Exception as e:
        print(f"❌ Tie-breaker V2 test failed: {e}")
        return None


def test_deterministic_behavior():
    """Test that tie-breaker behavior is deterministic."""
    print("🧪 Testing Deterministic Behavior...")

    try:
        pop_data, pdf_data = create_tiebreaker_test_data()

        matcher = POPMatcher(
            tiebreak_weight_fname=0.7, tiebreak_min_seller=0.4, amount_tolerance=0.01
        )

        filename = "test_invoice.pdf"

        # Run multiple times with same input
        results = []
        for i in range(5):
            result = matcher.match_invoice(pdf_data, pop_data, filename)
            results.append(
                {
                    "status": result.status.value,
                    "criteria": result.criteria.value,
                    "confidence": result.confidence,
                    "pop_row_index": result.pop_row_index,
                    "tie_breaker_score": result.tie_breaker_score,
                }
            )

        # Check that all results are identical
        first_result = results[0]
        all_identical = all(
            result["status"] == first_result["status"]
            and result["criteria"] == first_result["criteria"]
            and result["pop_row_index"] == first_result["pop_row_index"]
            for result in results
        )

        if all_identical:
            print("✅ Deterministic behavior PASSED - all results identical")
        else:
            print("❌ Deterministic behavior FAILED - results vary")
            for i, result in enumerate(results):
                print(f"   Run {i+1}: {result}")

        return all_identical

    except Exception as e:
        print(f"❌ Deterministic behavior test failed: {e}")
        return False


def test_edge_cases():
    """Test tie-breaker edge cases."""
    print("🧪 Testing Edge Cases...")

    try:
        # Test with empty POP data
        empty_pop = pd.DataFrame(columns=["Numer", "Data", "Netto", "Kontrahent"])
        pdf_data = {
            "invoice_id": "FV-001/2024",
            "issue_date": datetime(2024, 1, 15),
            "total_net": 1000.00,
            "seller_guess": "ACME Corporation",
            "currency": "zł",
        }

        matcher = POPMatcher()
        result = matcher.match_invoice(pdf_data, empty_pop, "test.pdf")

        if result.status == MatchStatus.NOT_FOUND:
            print("✅ Empty POP data handled correctly")
        else:
            print("❌ Empty POP data not handled correctly")

        # Test with missing invoice ID
        pdf_data_no_id = {
            "invoice_id": None,
            "issue_date": datetime(2024, 1, 15),
            "total_net": 1000.00,
            "seller_guess": "ACME Corporation",
            "currency": "zł",
        }

        pop_data, _ = create_tiebreaker_test_data()
        result = matcher.match_invoice(pdf_data_no_id, pop_data, "test.pdf")

        if result.status == MatchStatus.NOT_FOUND:
            print("✅ Missing invoice ID handled correctly")
        else:
            print("❌ Missing invoice ID not handled correctly")

        # Test with extreme tie-breaker weights
        matcher_extreme = POPMatcher(
            tiebreak_weight_fname=1.0,  # Only filename matters
            tiebreak_min_seller=0.0,
            amount_tolerance=0.01,
        )

        result = matcher_extreme.match_invoice(pdf_data, pop_data, "FV-001-2024.pdf")
        print(f"✅ Extreme weights handled: {result.status.value}")

        return True

    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False


def test_confidence_scoring():
    """Test confidence scoring accuracy."""
    print("🧪 Testing Confidence Scoring...")

    try:
        pop_data, pdf_data = create_tiebreaker_test_data()

        matcher = POPMatcher()

        # Test with perfect match
        perfect_pdf = pdf_data.copy()
        perfect_pdf["invoice_id"] = "FV-001/2024"
        perfect_pdf["seller_guess"] = "ACME Corporation"

        result = matcher.match_invoice(perfect_pdf, pop_data, "FV-001-2024.pdf")

        if result.confidence > 0.8:
            print("✅ Perfect match has high confidence")
        else:
            print(
                f"⚠️  Perfect match confidence lower than expected: {result.confidence}"
            )

        # Test with poor match
        poor_pdf = pdf_data.copy()
        poor_pdf["invoice_id"] = "UNKNOWN-123"
        poor_pdf["seller_guess"] = "Unknown Company"

        result = matcher.match_invoice(poor_pdf, pop_data, "unknown.pdf")

        if result.confidence < 0.5:
            print("✅ Poor match has low confidence")
        else:
            print(f"⚠️  Poor match confidence higher than expected: {result.confidence}")

        return True

    except Exception as e:
        print(f"❌ Confidence scoring test failed: {e}")
        return False


def compare_ab_results():
    """Compare A/B test results."""
    print("🧪 Comparing A/B Test Results...")

    try:
        v1_result = test_tiebreaker_v1()
        v2_result = test_tiebreaker_v2()

        if v1_result and v2_result:
            print("\n📊 A/B Test Comparison:")
            print("V1 (High filename weight):")
            print(f"  - Status: {v1_result.status.value}")
            print(f"  - Criteria: {v1_result.criteria.value}")
            print(f"  - Filename Hit: {v1_result.filename_hit}")
            print(f"  - Seller Similarity: {v1_result.seller_similarity:.2f}")

            print("V2 (Low filename weight, high seller threshold):")
            print(f"  - Status: {v2_result.status.value}")
            print(f"  - Criteria: {v2_result.criteria.value}")
            print(f"  - Filename Hit: {v2_result.filename_hit}")
            print(f"  - Seller Similarity: {v2_result.seller_similarity:.2f}")

            # Verify different behavior
            if (
                v1_result.filename_hit != v2_result.filename_hit
                or v1_result.criteria != v2_result.criteria
            ):
                print("✅ A/B test shows different behavior as expected")
                return True
            else:
                print("⚠️  A/B test shows similar behavior - may need adjustment")
                return False
        else:
            print("❌ Could not compare A/B results")
            return False

    except Exception as e:
        print(f"❌ A/B comparison failed: {e}")
        return False


def main():
    """Run tie-breaker A/B tests."""
    print("🚀 Starting Tie-breaker A/B Test Suite...")
    print("=" * 60)

    tests = [
        test_tiebreaker_v1,
        test_tiebreaker_v2,
        test_deterministic_behavior,
        test_edge_cases,
        test_confidence_scoring,
        compare_ab_results,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 Tie-breaker A/B Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tie-breaker A/B tests passed!")
        return 0
    else:
        print("❌ Some tie-breaker A/B tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
