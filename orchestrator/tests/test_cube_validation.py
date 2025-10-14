#!/usr/bin/env python3
# ABOUTME: Test script for cube query validation functionality
# ABOUTME: Verifies that the validator correctly identifies invalid parameters

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cube_query_validator import CubeQueryValidator, CubeQueryValidatorError


def test_validator_initialization():
    """Test that validator initializes correctly."""
    print("=" * 70)
    print("TEST 1: Validator Initialization")
    print("=" * 70)

    view_yml_path = Path(__file__).parent.parent / 'system-prompt-generator' / 'my-cube-views' / 'event_performance_overview.yml'

    try:
        validator = CubeQueryValidator(str(view_yml_path))
        print("✓ Validator initialized successfully")

        schema_summary = validator.get_schema_summary()
        print(f"\nSchema Summary:")
        print(f"  Cube Name: {schema_summary['cube_name']}")
        print(f"  Measures: {schema_summary['measures']}")
        print(f"  Dimensions: {schema_summary['dimensions']}")
        print(f"  Time Dimensions: {schema_summary['time_dimensions']}")

        return validator
    except Exception as e:
        print(f"✗ Validator initialization failed: {e}")
        return None


def test_valid_query(validator):
    """Test validation of a correct query."""
    print("\n" + "=" * 70)
    print("TEST 2: Valid Query Validation")
    print("=" * 70)

    valid_query = {
        "measures": ["FactOrders.tickets_sold"],
        "timeDimensions": [{
            "dimension": "FactOrders.order_date",
            "granularity": "day",
            "dateRange": "Last month"
        }]
    }

    print(f"\nQuery: {valid_query}")

    result = validator.validate_query(valid_query)

    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Warnings: {result['warnings']}")

    if result['valid']:
        print("✓ Valid query passed validation")
    else:
        print("✗ Valid query failed validation (unexpected)")

    return result['valid']


def test_invalid_measure(validator):
    """Test validation of query with invalid measure."""
    print("\n" + "=" * 70)
    print("TEST 3: Invalid Measure Detection")
    print("=" * 70)

    invalid_query = {
        "measures": ["EventPerformanceOverview.total_tickets_sold"],  # Wrong: should be tickets_sold
        "timeDimensions": [{
            "dimension": "FactOrders.order_date",
            "granularity": "day",
            "dateRange": "Last month"
        }]
    }

    print(f"\nQuery: {invalid_query}")

    result = validator.validate_query(invalid_query)

    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Invalid Measures: {result['invalid_measures']}")
    print(f"  Suggestions: {result['suggestions']}")

    if not result['valid'] and result['invalid_measures']:
        print("✓ Invalid measure correctly detected")
    else:
        print("✗ Invalid measure not detected (unexpected)")

    return not result['valid']


def test_correction_prompt(validator):
    """Test generation of correction prompt."""
    print("\n" + "=" * 70)
    print("TEST 4: Correction Prompt Generation")
    print("=" * 70)

    invalid_query = {
        "measures": ["EventPerformanceOverview.total_tickets_sold"],
        "dimensions": ["EventPerformanceOverview.wrong_dimension"]
    }

    original_user_query = "Show me daily tickets sold last month"

    result = validator.validate_query(invalid_query)

    if not result['valid']:
        correction_prompt = validator.generate_correction_prompt(result, original_user_query)
        print(f"\nGenerated Correction Prompt:")
        print("-" * 70)
        print(correction_prompt)
        print("-" * 70)
        print("✓ Correction prompt generated successfully")
        return True
    else:
        print("✗ Query unexpectedly valid, cannot generate correction prompt")
        return False


def test_mixed_valid_invalid(validator):
    """Test query with mix of valid and invalid parameters."""
    print("\n" + "=" * 70)
    print("TEST 5: Mixed Valid/Invalid Parameters")
    print("=" * 70)

    mixed_query = {
        "measures": [
            "FactOrders.tickets_sold",  # Valid
            "FactOrders.invalid_measure"  # Invalid
        ],
        "dimensions": [
            "FactOrders.order_id",  # Valid
            "FactOrders.nonexistent_dim"  # Invalid
        ]
    }

    print(f"\nQuery: {mixed_query}")

    result = validator.validate_query(mixed_query)

    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Invalid Measures: {result['invalid_measures']}")
    print(f"  Invalid Dimensions: {result['invalid_dimensions']}")

    if not result['valid'] and len(result['invalid_measures']) == 1 and len(result['invalid_dimensions']) == 1:
        print("✓ Mixed query correctly identified both valid and invalid parameters")
        return True
    else:
        print("✗ Mixed query validation did not work as expected")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CUBE QUERY VALIDATOR TEST SUITE" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Test 1: Initialize validator
    validator = test_validator_initialization()
    if not validator:
        print("\n❌ FATAL: Could not initialize validator. Stopping tests.")
        return

    # Test 2: Valid query
    test2_passed = test_valid_query(validator)

    # Test 3: Invalid measure
    test3_passed = test_invalid_measure(validator)

    # Test 4: Correction prompt
    test4_passed = test_correction_prompt(validator)

    # Test 5: Mixed parameters
    test5_passed = test_mixed_valid_invalid(validator)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    tests_passed = sum([test2_passed, test3_passed, test4_passed, test5_passed])
    total_tests = 4
    print(f"\nPassed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed")

    print()


if __name__ == "__main__":
    main()
