"""
Quick test script to verify A2A system functionality
"""

from a2a_system import A2ACoordinationSystem
from database_setup import DatabaseSetup


def ensure_test_database(db_path: str = "support.db") -> None:
    """Ensure the SQLite database exists and is seeded with sample data."""
    db = DatabaseSetup(db_path)
    try:
        db.connect()
        db.create_tables()
        db.create_triggers()
        db.insert_sample_data()
    finally:
        db.close()


def test_simple_query():
    """Test simple single-agent query."""
    print("\n" + "="*80)
    print("TEST 1: Simple Query - Get Customer Information")
    print("="*80)

    ensure_test_database("support.db")
    system = A2ACoordinationSystem("support.db")
    result = system.process_query("Get customer information for ID 5")

    print("\n" + "-"*80)
    print("RESPONSE:")
    print("-"*80)
    print(result['response'])
    print("-"*80)

    assert result['response'], "Response should not be empty"
    assert 'Customer Information' in result['response'], "Should contain customer info"
    print("\n✓ Test passed!")


def test_coordinated_query():
    """Test multi-agent coordination."""
    print("\n" + "="*80)
    print("TEST 2: Coordinated Query - Support with Customer Context")
    print("="*80)

    ensure_test_database("support.db")
    system = A2ACoordinationSystem("support.db")
    result = system.process_query("I need help with my account, customer ID 1")

    print("\n" + "-"*80)
    print("RESPONSE:")
    print("-"*80)
    print(result['response'])
    print("-"*80)

    assert result['response'], "Response should not be empty"
    print("\n✓ Test passed!")


def test_complex_query():
    """Test complex negotiation query."""
    print("\n" + "="*80)
    print("TEST 3: Complex Query - Active Customers with Open Tickets")
    print("="*80)

    ensure_test_database("support.db")
    system = A2ACoordinationSystem("support.db")
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
        test_simple_query()
        test_coordinated_query()
        test_complex_query()

        print("\n" + "="*80)
        print("ALL TESTS PASSED! ✓")
        print("="*80)

        print("\nThe system is ready to use!")
        print("Run 'python3 main.py' to start the full application.")

    except Exception as e:
        print(f"\n\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
