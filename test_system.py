"""
Quick test script to verify A2A system functionality
"""

import os
import tempfile
from pathlib import Path

from a2a_system import A2ACoordinationSystem
from database_setup import DatabaseSetup


def _create_test_db(db_path: str) -> None:
    """Create a fresh sqlite db populated with sample data."""
    # Ensure a clean slate for repeatable tests
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass

    db = DatabaseSetup(db_path)
    try:
        db.connect()
        db.create_tables()
        db.create_triggers()
        db.insert_sample_data()
    finally:
        db.close()


def test_simple_query(db_path: str):
    """Test simple single-agent query."""
    print("\n" + "="*80)
    print("TEST 1: Simple Query - Get Customer Information")
    print("="*80)

    system = A2ACoordinationSystem(db_path)
    result = system.process_query("Get customer information for ID 5")

    print("\n" + "-"*80)
    print("RESPONSE:")
    print("-"*80)
    print(result['response'])
    print("-"*80)

    assert result['response'], "Response should not be empty"
    assert 'Customer Information' in result['response'], "Should contain customer info"
    print("\n✓ Test passed!")


def test_coordinated_query(db_path: str):
    """Test multi-agent coordination."""
    print("\n" + "="*80)
    print("TEST 2: Coordinated Query - Support with Customer Context")
    print("="*80)

    system = A2ACoordinationSystem(db_path)
    result = system.process_query("I need help with my account, customer ID 1")

    print("\n" + "-"*80)
    print("RESPONSE:")
    print("-"*80)
    print(result['response'])
    print("-"*80)

    assert result['response'], "Response should not be empty"
    print("\n✓ Test passed!")


def test_complex_query(db_path: str):
    """Test complex negotiation query."""
    print("\n" + "="*80)
    print("TEST 3: Complex Query - Active Customers with Open Tickets")
    print("="*80)

    system = A2ACoordinationSystem(db_path)
    result = system.process_query("Show me all active customers who have open tickets")

    print("\n" + "-"*80)
    print("RESPONSE:")
    print("-"*80)
    print(result['response'])
    print("-"*80)

    assert result['response'], "Response should not be empty"
    print("\n✓ Test passed!")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("A2A COORDINATION SYSTEM - QUICK TESTS")
    print("="*80)

    try:
        db_path = str(Path(tempfile.gettempdir()) / "a2a_support_test.db")
        _create_test_db(db_path)

        test_simple_query(db_path)
        test_coordinated_query(db_path)
        test_complex_query(db_path)

        print("\n" + "="*80)
        print("ALL TESTS PASSED! ✓")
        print("="*80)

        print("\nThe system is ready to use!")
        print("Run 'python main.py' to start the full application.")

    except Exception as e:
        print(f"\n\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
