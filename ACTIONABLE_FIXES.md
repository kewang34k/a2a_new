# Actionable Fixes for Multi-Agent System

**Priority Order**: Fix these issues in the order listed for maximum impact

---

## 🔴 CRITICAL FIX #1: Router Intent Classification

**Problem**: Router is misclassifying 67% of queries, routing to wrong agents

**File**: `agents/router_agent.py`
**Lines**: 18-108

### Immediate Fix - Add Debug Logging

```python
def analyze_intent(self, query: str) -> Dict[str, Any]:
    """Analyze query intent and determine routing strategy."""
    query_lower = query.lower()

    print(f"\n[{self.agent_name}] Analyzing query: '{query}'")
    print(f"[DEBUG] query_lower: '{query_lower}'")  # ADD THIS

    # Extract customer ID if present
    customer_id = self._extract_customer_id(query)
    print(f"[DEBUG] customer_id extracted: {customer_id}")  # ADD THIS

    # Determine intents
    intents = []
    required_agents = []
    coordination_type = "simple"

    # CRITICAL FIX: If customer_id present, ALWAYS include Data Agent
    if customer_id:
        print(f"[DEBUG] Customer ID found - adding CustomerDataAgent")  # ADD THIS
        intents.append("get_customer_data")
        required_agents.append("CustomerDataAgent")

    # Data retrieval intents
    if any(word in query_lower for word in ["get customer", "customer information", "customer info", "customer id"]):
        print(f"[DEBUG] Matched get_customer_data pattern")  # ADD THIS
        intents.append("get_customer_data")
        required_agents.append("CustomerDataAgent")

    # Add similar debug prints for ALL intent checks
    # ...
```

### Why This Fixes It:
- Debug logging will reveal why pattern matching is failing
- Fallback logic ensures customer IDs always trigger Data Agent
- Can identify if different code version is running

### Test After Fix:
```bash
python test_system.py
```
Look for debug output showing which patterns match

---

## 🔴 CRITICAL FIX #2: Support Agent Context Utilization

**Problem**: Support Agent ignores customer data passed to it

**File**: `agents/support_agent.py`
**Lines**: 156-195, 225-262

### Immediate Fix - Use Customer Context

Replace the generic response generators with context-aware ones:

```python
def _handle_support_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a general support query with customer context."""
    query = params.get("query", "")
    customer_context = params.get("customer_context", "")

    # PARSE CUSTOMER CONTEXT
    customer_name = "valued customer"
    customer_status = "unknown"

    if customer_context:
        # Extract name: "Customer: Alice Johnson (active)"
        import re
        name_match = re.search(r'Customer: (\w+)', customer_context)
        status_match = re.search(r'\((\w+)\)', customer_context)

        if name_match:
            customer_name = name_match.group(1)
        if status_match:
            customer_status = status_match.group(1)

    # Analyze query
    analysis = self._analyze_query({"query": query})

    response = {
        "success": True,
        "query": query,
        "analysis": analysis,
        "response": "",
        "agent": self.agent_name
    }

    # Generate appropriate response based on intents
    intents = analysis.get("intents", [])

    if "billing" in intents:
        response["response"] = self._generate_billing_response(
            query, customer_name, customer_status
        )
    elif "account_management" in intents:
        response["response"] = self._generate_account_management_response(
            query, customer_name, customer_status
        )
    # ... etc

    return response


def _generate_billing_response(self, query: str, name: str, status: str) -> str:
    """Generate billing-related response WITH CONTEXT."""
    greeting = f"Hello {name}, " if name != "valued customer" else "Hello, "

    if "charged twice" in query.lower():
        return (f"{greeting}I understand you've been charged twice. "
                f"This is a serious issue that needs immediate attention. "
                f"I'm escalating this to our billing team for priority review and refund processing. "
                f"You should receive a response within 24 hours.")
    # ... etc
```

### Why This Fixes It:
- Extracts customer name and status from context
- Personalizes all responses
- Demonstrates proper context utilization

---

## 🟡 MAJOR FIX #3: Add Comprehensive Unit Tests

**Problem**: No tests to catch intent classification failures

**New File**: `tests/test_router_intent.py`

```python
"""Unit tests for Router Agent intent classification."""

import pytest
from agents.router_agent import RouterAgent


class TestRouterIntentClassification:
    """Test intent classification accuracy."""

    def setup_method(self):
        """Setup router for each test."""
        self.router = RouterAgent()

    def test_customer_data_query(self):
        """Test: 'Get customer information for ID 5' should route to Data Agent."""
        query = "Get customer information for ID 5"
        result = self.router.analyze_intent(query)

        assert result['customer_id'] == 5, "Should extract customer ID"
        assert "get_customer_data" in result['intents'], "Should identify data intent"
        assert "CustomerDataAgent" in result['required_agents'], "Should route to Data Agent"
        assert "SupportAgent" not in result['required_agents'], "Should NOT route to Support for pure data query"

    def test_billing_with_customer_id(self):
        """Test: Billing issue with customer ID should route to both agents."""
        query = "I want to cancel my subscription but I'm having billing issues. Customer ID 2"
        result = self.router.analyze_intent(query)

        assert result['customer_id'] == 2, "Should extract customer ID"
        assert "account_management" in result['intents'], "Should identify cancellation intent"
        assert "billing_issue" in result['intents'], "Should identify billing intent"
        assert "CustomerDataAgent" in result['required_agents'], "Should route to Data Agent"
        assert "SupportAgent" in result['required_agents'], "Should route to Support Agent"
        assert result['coordination_type'] == "sequential", "Should use sequential coordination"

    def test_account_help_with_id(self):
        """Test: Help request with customer ID should route to both agents."""
        query = "I need help with my account, customer ID 1"
        result = self.router.analyze_intent(query)

        assert result['customer_id'] == 1, "Should extract customer ID"
        assert "support_request" in result['intents'], "Should identify support intent"
        assert "CustomerDataAgent" in result['required_agents'], "Should route to Data Agent when customer ID present"
        assert "SupportAgent" in result['required_agents'], "Should route to Support Agent"

    def test_complex_query(self):
        """Test: Complex multi-step query should use negotiation."""
        query = "Show me all active customers who have open tickets"
        result = self.router.analyze_intent(query)

        assert "complex_query" in result['intents'], "Should identify complex query"
        assert "CustomerDataAgent" in result['required_agents'], "Should route to Data Agent"
        assert result['coordination_type'] == "negotiation", "Should use negotiation coordination"

    def test_customer_id_extraction_patterns(self):
        """Test various customer ID patterns are extracted."""
        test_cases = [
            ("Customer ID 123", 123),
            ("customer 456", 456),
            ("ID 789", 789),
            ("customer id 999", 999),
        ]

        for query, expected_id in test_cases:
            result = self.router.analyze_intent(query)
            assert result['customer_id'] == expected_id, f"Failed to extract ID from: {query}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Run Tests:
```bash
pip install pytest
python tests/test_router_intent.py
```

This will immediately show which intent classifications are failing.

---

## 🟡 MAJOR FIX #4: Enhance A2A Context Building

**Problem**: Minimal customer context passed between agents

**File**: `a2a_system.py`
**Lines**: 406-444

### Immediate Fix - Build Richer Context

```python
def _build_params(self, state: AgentState, action: str) -> Dict[str, Any]:
    """Build parameters for an action based on current state."""
    params = {}

    # Add customer_id if available
    if state.customer_id:
        params["customer_id"] = state.customer_id

    # Add query for analysis/support actions
    if action in ["analyze_query", "handle_support_query"]:
        params["query"] = state.query

    # ENHANCED: Add rich customer context if we have it
    if action == "handle_support_query" and state.customer_data:
        if state.customer_data.get("success"):
            context_parts = []

            # Customer info
            if "customer" in state.customer_data:
                customer = state.customer_data["customer"]
                context_parts.append(f"Customer: {customer['name']} ({customer['status']})")
                context_parts.append(f"Email: {customer['email']}")
                context_parts.append(f"Member since: {customer.get('created_at', 'N/A')}")

            # Ticket info
            if "tickets" in state.customer_data:
                tickets = state.customer_data["tickets"]
                open_tickets = [t for t in tickets if t['status'] == 'open']
                context_parts.append(f"Open tickets: {len(open_tickets)}")

                if open_tickets:
                    latest = open_tickets[0]
                    context_parts.append(f"Latest issue: {latest['issue']} ({latest['priority']} priority)")

            params["customer_context"] = " | ".join(context_parts)
        else:
            params["customer_context"] = "No customer data available"

    # ... rest of method
```

### Why This Fixes It:
- Provides complete customer picture to Support Agent
- Includes recent ticket history for context
- Enables truly personalized responses

---

## 🟢 NICE-TO-HAVE: Replace Keyword Matching with LLM

**Long-term improvement for better accuracy**

**File**: `agents/router_agent.py`

### Future Enhancement:

```python
def analyze_intent_llm(self, query: str) -> Dict[str, Any]:
    """Analyze query intent using LLM for better accuracy."""
    from anthropic import Anthropic

    client = Anthropic()

    prompt = f"""Analyze this customer support query and extract:
1. Customer ID (if mentioned)
2. Intents (list): get_customer_data, support_request, billing_issue, account_management, complex_query
3. Required agents: CustomerDataAgent, SupportAgent
4. Priority: low, medium, high
5. Coordination type: simple, sequential, negotiation

Query: "{query}"

Respond in JSON format."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    result = json.loads(response.content[0].text)

    # Convert to expected format
    return {
        "query": query,
        "customer_id": result.get("customer_id"),
        "intents": result["intents"],
        "required_agents": result["required_agents"],
        "coordination_type": result["coordination_type"],
        "priority": result["priority"],
        "agent": self.agent_name
    }
```

---

## Testing Checklist

After applying fixes, verify:

- [ ] `python tests/test_router_intent.py` - All tests pass
- [ ] Test: "Get customer information for ID 5"
  - [ ] Routes to CustomerDataAgent
  - [ ] Returns customer data
  - [ ] Response includes customer details
- [ ] Test: "Cancel subscription, billing issues, Customer ID 2"
  - [ ] Routes to both CustomerDataAgent and SupportAgent
  - [ ] Retrieves customer data
  - [ ] Response uses customer context
  - [ ] Identifies both intents
- [ ] Test: "I need help with my account, customer ID 1"
  - [ ] Routes to both agents
  - [ ] Response addresses customer by name
  - [ ] References existing open ticket
- [ ] Complex query test still works
  - [ ] Multi-step coordination executes
  - [ ] Report generated correctly

---

## Quick Win Summary

**Fix in this order for fastest improvement:**

1. **Add fallback logic** (5 minutes):
   ```python
   # In analyze_intent(), add after customer_id extraction:
   if customer_id:
       if "CustomerDataAgent" not in required_agents:
           required_agents.append("CustomerDataAgent")
   ```

2. **Add debug logging** (10 minutes):
   - Add print statements to see what's matching
   - Run tests to see output

3. **Fix Support Agent context usage** (30 minutes):
   - Modify `_generate_*_response()` methods to accept name parameter
   - Parse customer_context in `_handle_support_query()`

4. **Add unit tests** (1 hour):
   - Copy test file above
   - Run to verify fixes

**Total time to critical fixes**: ~2 hours

---

## Expected Results After Fixes

| Test | Before | After |
|------|--------|-------|
| Get customer info ID 5 | ❌ FAIL | ✅ PASS |
| Cancel + billing ID 2 | ❌ FAIL | ✅ PASS |
| Help with account ID 1 | ⚠️ PARTIAL | ✅ PASS |
| Complex query | ✅ PASS | ✅ PASS |
| **Overall Success Rate** | **25%** | **100%** |

---

**Questions?** Review `MODEL_EVALUATION_REPORT.md` for detailed analysis.
