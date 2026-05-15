"""
Unit 5 Test: Constants + Validation Demonstration

Shows how constants eliminate magic numbers and validation fails fast on bad data.
"""

import sys
import pandas as pd
import numpy as np

# Import our modules
try:
    from constants import (
        PACKAGE_SIZE_DOCS,
        REQUIRED_DATA_COLUMNS,
        REQUIRED_PRICING_COLUMNS,
        VALID_TYPES,
        VALID_VATS,
        validate_data_columns,
        validate_pricing_columns,
        normalize_type,
        normalize_vat,
    )
    from calculate_new_prices import calculate_price_with_packages
    from price_manager import get_default_pricing, apply_global_modification
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def test_constants():
    """Test that constants are defined correctly."""
    print("\n" + "="*60)
    print("TEST 1: Constants Definition")
    print("="*60)
    
    assert PACKAGE_SIZE_DOCS == 25, "Package size should be 25"
    assert 'tak' in VALID_VATS, "Valid VAT should include 'tak'"
    assert 'nie' in VALID_VATS, "Valid VAT should include 'nie'"
    assert len(VALID_TYPES) == 3, "Should have 3 valid types"
    
    print(f"✓ PACKAGE_SIZE_DOCS = {PACKAGE_SIZE_DOCS}")
    print(f"✓ VALID_TYPES = {VALID_TYPES}")
    print(f"✓ VALID_VATS = {VALID_VATS}")
    print(f"✓ REQUIRED_DATA_COLUMNS = {len(REQUIRED_DATA_COLUMNS)} columns")
    print(f"✓ REQUIRED_PRICING_COLUMNS = {len(REQUIRED_PRICING_COLUMNS)} columns")
    
    return True


def test_pricing_validation():
    """Test pricing table validation."""
    print("\n" + "="*60)
    print("TEST 2: Pricing Validation (Fail-Fast)")
    print("="*60)
    
    # Valid pricing table
    pricing_df = get_default_pricing()
    
    try:
        validate_pricing_columns(pricing_df)
        print("✓ Valid pricing table passes validation")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Invalid: missing column
    pricing_bad = pricing_df.drop(columns=['100+'])
    try:
        validate_pricing_columns(pricing_bad)
        print("✗ Should have raised ValueError for missing column")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected missing column: {e}")
    
    return True


def test_data_validation():
    """Test client data validation."""
    print("\n" + "="*60)
    print("TEST 3: Client Data Validation")
    print("="*60)
    
    # Valid data
    valid_df = pd.DataFrame({
        'ID': [1, 2],
        'Nazwa': ['Client A', 'Client B'],
        'Typ_Umowy': ['KH', 'KPIR'],
        'VAT': ['tak', 'nie'],
        'Doc_Marzec': [10, 20],
        'Doc_Luty': [15, 25],
        'Doc_Styczeń': [12, 22],
        'Doc_Avg': [12.3, 22.3],
        'Cena_Stara': [500, 600],
        'Miał_Rabat_10%': [1, 0],
    })
    
    try:
        validate_data_columns(valid_df)
        print("✓ Valid data passes validation")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Invalid: missing column
    invalid_df = valid_df.drop(columns=['Cena_Stara'])
    try:
        validate_data_columns(invalid_df)
        print("✗ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected missing columns")
    
    return True


def test_normalize_functions():
    """Test type and VAT normalization."""
    print("\n" + "="*60)
    print("TEST 4: Type/VAT Normalization")
    print("="*60)
    
    # Type normalization
    test_cases = [
        ('kh', 'KH'),
        ('KH', 'KH'),
        ('kpir', 'KPIR'),
        ('KPIR', 'KPIR'),
        ('ryczałt', 'Ryczałt'),
        ('RYCZAŁT', 'Ryczałt'),
    ]
    
    for input_val, expected in test_cases:
        result = normalize_type(input_val)
        assert result == expected, f"Failed: {input_val} -> {result} (expected {expected})"
        print(f"✓ normalize_type('{input_val}') = '{result}'")
    
    # VAT normalization
    vat_cases = [
        ('tak', 'tak'),
        ('TAK', 'tak'),
        ('true', 'tak'),
        ('1', 'tak'),
        ('nie', 'nie'),
        ('NIE', 'nie'),
        ('false', 'nie'),
        ('0', 'nie'),
    ]
    
    for input_val, expected in vat_cases:
        result = normalize_vat(input_val)
        assert result == expected, f"Failed: {input_val} -> {result}"
        print(f"✓ normalize_vat('{input_val}') = '{result}'")
    
    return True


def test_price_calculation():
    """Test unified price calculation with constants."""
    print("\n" + "="*60)
    print("TEST 5: Unified Price Calculation (Uses PACKAGE_SIZE_DOCS)")
    print("="*60)
    
    pricing_df = get_default_pricing()
    
    test_cases = [
        {
            'typ': 'KH',
            'vat': 'tak',
            'doc_count': 5,
            'expected_range': '1-10',
            'expected_price': 760,
        },
        {
            'typ': 'KH',
            'vat': 'tak',
            'doc_count': 75,
            'expected_range': '51-100',
            'expected_price': 2250,
        },
        {
            'typ': 'KH',
            'vat': 'tak',
            'doc_count': 110,
            'expected_range': '100+',
            'expected_price': 2250 + (1 * 500),  # base + 1 package
            'packages': 1,
        },
        {
            'typ': 'KH',
            'vat': 'tak',
            'doc_count': 135,
            'expected_range': '100+',
            'expected_price': 2250 + (2 * 500),  # base + 2 packages (ceil(35/25)=2)
            'packages': 2,
        },
        {
            'typ': 'KPIR',
            'vat': 'nie',
            'doc_count': 130,
            'expected_range': '100+',
            'expected_price': 650 + (2 * 120),  # base + 2 packages
            'packages': 2,
        },
    ]
    
    for test in test_cases:
        price = calculate_price_with_packages(
            test['typ'],
            test['vat'],
            test['doc_count'],
            pricing_df
        )
        
        expected = test['expected_price']
        status = "✓" if price == expected else "✗"
        pkg_info = f" ({test.get('packages', 0)} packages)" if test['doc_count'] > 100 else ""
        
        print(f"{status} {test['typ']}/{test['vat']}: {test['doc_count']} docs "
              f"→ {price} PLN (expected {expected}){pkg_info}")
        
        assert price == expected, f"Price mismatch for {test}"
    
    return True


def test_apply_modification_validation():
    """Test that apply_global_modification validates inputs."""
    print("\n" + "="*60)
    print("TEST 6: apply_global_modification Validation")
    print("="*60)
    
    pricing_df = get_default_pricing()
    
    # Valid modification
    try:
        result = apply_global_modification(pricing_df, 'KH', 'tak', 5)
        print("✓ Valid modification (KH/tak +5%) accepted")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Invalid type
    try:
        apply_global_modification(pricing_df, 'INVALID', 'tak', 5)
        print("✗ Should have rejected invalid type")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid type: {e}")
    
    # Invalid VAT
    try:
        apply_global_modification(pricing_df, 'KH', 'invalid', 5)
        print("✗ Should have rejected invalid VAT")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid VAT: {e}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "🎯 " * 20)
    print("UNIT 5 VALIDATION TESTS")
    print("Constants + DataFrame Contracts (Fail-Fast)")
    print("🎯 " * 20)
    
    tests = [
        ("Constants Definition", test_constants),
        ("Pricing Validation", test_pricing_validation),
        ("Data Validation", test_data_validation),
        ("Normalize Functions", test_normalize_functions),
        ("Price Calculation", test_price_calculation),
        ("apply_global_modification Validation", test_apply_modification_validation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result is False or result is None:
                failed += 1
            else:
                passed += 1
        except AssertionError as e:
            print(f"\n✗ {name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {name} ERROR: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
