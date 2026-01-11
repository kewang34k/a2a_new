"""
Main Application - Multi-Agent Customer Support System
Demonstrates A2A coordination with 5 test scenarios.
"""

import sys
import re
from pathlib import Path
from datetime import datetime

from a2a_system import A2ACoordinationSystem
from database_setup import DatabaseSetup


class MultiAgentDemo:
    """Demo application for multi-agent customer support system."""

    def __init__(self, db_path: str = "support.db"):
        """Initialize demo application.

        Args:
            db_path: Path to database
        """
        self.db_path = db_path
        self.a2a_system = None

    def setup_database(self):
        """Setup database with test data."""
        print("\n" + "="*80)
        print("DATABASE SETUP")
        print("="*80 + "\n")

        db = DatabaseSetup(self.db_path)
        try:
            db.connect()
            db.create_tables()
            db.create_triggers()
            db.insert_sample_data()
            print("\n✓ Database setup complete!")
        finally:
            db.close()

    def initialize_system(self):
        """Initialize A2A coordination system."""
        print("\n" + "="*80)
        print("INITIALIZING A2A COORDINATION SYSTEM")
        print("="*80 + "\n")

        self.a2a_system = A2ACoordinationSystem(self.db_path)
        print("✓ Router Agent initialized")
        print("✓ Customer Data Agent initialized")
        print("✓ Support Agent initialized")
        print("✓ A2A Coordination System ready\n")

    def run_test_scenarios(self):
        """Run all 5 test scenarios."""
        print("\n" + "="*80)
        print("RUNNING TEST SCENARIOS")
        print("="*80 + "\n")

        scenarios = [
            {
                "name": "Scenario 1: Simple Query",
                "description": "Get customer information for ID 5",
                "query": "Get customer information for ID 5",
                "customer_id": None
            },
            {
                "name": "Scenario 2: Coordinated Query",
                "description": "Customer needs help upgrading account",
                "query": "I'm customer 12345 and need help upgrading my account",
                "customer_id": None
            },
            {
                "name": "Scenario 3: Complex Query",
                "description": "Show all active customers who have open tickets",
                "query": "Show me all active customers who have open tickets",
                "customer_id": None
            },
            {
                "name": "Scenario 4: Escalation",
                "description": "Urgent billing issue requiring immediate attention",
                "query": "I've been charged twice, please refund immediately!",
                "customer_id": 1
            },
            {
                "name": "Scenario 5: Multi-Intent",
                "description": "Update email and show ticket history",
                "query": "Update my email to newemail@example.com and show my ticket history",
                "customer_id": 2
            }
        ]

        results = []
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*80}")
            print(f"TEST SCENARIO {i}: {scenario['name']}")
            print(f"{'='*80}")
            print(f"Description: {scenario['description']}")
            print(f"Query: '{scenario['query']}'")
            if scenario['customer_id']:
                print(f"Customer ID: {scenario['customer_id']}")
            print()

            # Process query
            result = self.a2a_system.process_query(
                scenario['query'],
                scenario['customer_id']
            )

            # Display result
            print(f"\n{'─'*80}")
            print("FINAL RESPONSE:")
            print(f"{'─'*80}")
            print(result['response'])
            print(f"{'─'*80}\n")

            results.append({
                "scenario": scenario['name'],
                "result": result
            })

            # Pause between scenarios
            if i < len(scenarios):
                input("\nPress Enter to continue to next scenario...")

        return results

    def display_summary(self, results: list):
        """Display summary of all test scenarios.

        Args:
            results: List of scenario results
        """
        print("\n" + "="*80)
        print("TEST SCENARIOS SUMMARY")
        print("="*80 + "\n")

        for i, result_data in enumerate(results, 1):
            scenario_name = result_data['scenario']
            result = result_data['result']
            state = result['state']

            print(f"{i}. {scenario_name}")
            print(f"   Query: {result['query']}")
            print(f"   Intents: {', '.join(state['intents'])}")
            print(f"   Coordination: {state['coordination_type']}")
            print(f"   Agents: {', '.join(state['required_agents'])}")
            print(f"   Status: ✓ Completed")
            print()

    def run_interactive_mode(self):
        """Run interactive mode for custom queries."""
        print("\n" + "="*80)
        print("INTERACTIVE MODE")
        print("="*80)
        print("\nEnter your queries (type 'exit' to quit)\n")

        while True:
            try:
                query = input("Query: ").strip()

                if query.lower() in ['exit', 'quit', 'q']:
                    print("\nExiting interactive mode...")
                    break

                if not query:
                    continue

                # Check if customer ID is provided
                customer_id = None
                if "customer" in query.lower() and "id" in query.lower():
                    match = re.search(r'(\d+)', query)
                    if match:
                        customer_id = int(match.group(1))

                # Process query
                result = self.a2a_system.process_query(query, customer_id)

                # Display result
                print(f"\n{'─'*80}")
                print("RESPONSE:")
                print(f"{'─'*80}")
                print(result['response'])
                print(f"{'─'*80}\n")

            except KeyboardInterrupt:
                print("\n\nExiting interactive mode...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")

    def export_logs(self, results: list, filename: str = None):
        """Export coordination logs to file.

        Args:
            results: List of scenario results
            filename: Optional output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/a2a_coordination_{timestamp}.log"

        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)

        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("A2A COORDINATION SYSTEM - TEST LOGS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            for i, result_data in enumerate(results, 1):
                scenario_name = result_data['scenario']
                result = result_data['result']

                f.write(f"\n{'='*80}\n")
                f.write(f"SCENARIO {i}: {scenario_name}\n")
                f.write(f"{'='*80}\n\n")

                f.write(f"Query: {result['query']}\n\n")

                f.write("COORDINATION LOG:\n")
                f.write("-"*80 + "\n")
                for log_entry in result['coordination_log']:
                    f.write(log_entry + "\n")
                f.write("-"*80 + "\n\n")

                f.write("FINAL RESPONSE:\n")
                f.write("-"*80 + "\n")
                f.write(result['response'] + "\n")
                f.write("-"*80 + "\n\n")

        print(f"\n✓ Logs exported to: {filename}")


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("MULTI-AGENT CUSTOMER SUPPORT SYSTEM")
    print("A2A Coordination Demo")
    print("="*80)

    demo = MultiAgentDemo()

    # Setup database
    print("\nStep 1: Setting up database...")
    demo.setup_database()

    # Initialize system
    print("\nStep 2: Initializing A2A system...")
    demo.initialize_system()

    # Menu
    while True:
        print("\n" + "="*80)
        print("MAIN MENU")
        print("="*80)
        print("\n1. Run all 5 test scenarios")
        print("2. Interactive mode (custom queries)")
        print("3. Exit")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            results = demo.run_test_scenarios()
            demo.display_summary(results)

            # Ask if user wants to export logs
            export = input("\nExport coordination logs to file? (y/n): ").lower()
            if export == 'y':
                demo.export_logs(results)

        elif choice == "2":
            demo.run_interactive_mode()

        elif choice == "3":
            print("\nThank you for using the Multi-Agent Customer Support System!")
            print("Goodbye!\n")
            break

        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}\n")
        sys.exit(1)
