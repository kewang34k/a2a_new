"""
Demo script showing both rule-based and LLM-powered multi-agent systems.
Run this to see the difference between the two approaches.
"""

import os
import sys

# Setup instructions
print("="*80)
print("MULTI-AGENT CUSTOMER SUPPORT SYSTEM - LLM DEMO")
print("="*80)
print()
print("This demo compares rule-based vs LLM-powered agent coordination.")
print()

# Check if API key is set
api_key = os.getenv('OPENAI_API_KEY', '')

if not api_key:
    print("⚠️ OpenAI API Key Not Found")
    print()
    print("To enable LLM features:")
    print("  1. Get an API key from: https://platform.openai.com/api-keys")
    print("  2. Set it in your environment:")
    print()
    print("     export OPENAI_API_KEY='sk-your-key-here'  # Linux/Mac")
    print("     set OPENAI_API_KEY=sk-your-key-here        # Windows")
    print()
    print("Or set it in this script:")
    print("     os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'")
    print()
    print("Running in RULE-BASED mode only...\n")
    use_llm = False
else:
    print(f"✓ OpenAI API Key found: {api_key[:10]}...{api_key[-4:]}")
    print()
    choice = input("Run with LLM-powered agents? (y/n): ").lower()
    use_llm = choice == 'y'
    print()

print("="*80)
print()

# Initialize database
from database_setup import DatabaseSetup

print("Setting up database...")
db = DatabaseSetup("support.db")
db.connect()
db.create_tables()
db.create_triggers()
db.insert_sample_data()
db.close()
print()

# Test queries
test_queries = [
    {
        "name": "Simple Query",
        "query": "Get customer information for ID 5",
        "customer_id": None
    },
    {
        "name": "Support Request",
        "query": "I need help with my account, customer ID 1",
        "customer_id": None
    },
    {
        "name": "Complex Query",
        "query": "Show me all active customers who have open tickets",
        "customer_id": None
    }
]

# Run with selected mode
if use_llm:
    print("🤖 Running LLM-POWERED Multi-Agent System")
    print("="*80)
    print()

    from a2a_system_llm import A2ACoordinationSystemLLM
    system = A2ACoordinationSystemLLM("support.db", use_llm=True)
else:
    print("📋 Running RULE-BASED Multi-Agent System")
    print("="*80)
    print()

    from a2a_system import A2ACoordinationSystem
    system = A2ACoordinationSystem("support.db")

# Run test scenarios
for i, test in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"Query: \"{test['query']}\"")
    print()

    result = system.process_query(test['query'], test['customer_id'])

    print(f"\n{'-'*80}")
    print("FINAL RESPONSE:")
    print(f"{'-'*80}")
    print(result['response'])
    print(f"{'-'*80}\n")

    if i < len(test_queries):
        input("Press Enter to continue...")

print("\n" + "="*80)
print("DEMO COMPLETE")
print("="*80)
print()

if not use_llm:
    print("💡 TIP: Set OPENAI_API_KEY to see the LLM-powered version!")
    print("   The LLM version provides:")
    print("   - Better intent understanding")
    print("   - More natural responses")
    print("   - Handles novel queries")
else:
    print("✓ You just saw the power of LLM-enhanced agents!")
    print("  Compare this to the rule-based version by setting use_llm=False")

print()
