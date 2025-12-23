# CLAUDE.md - AI Assistant Guide

**Project**: Multi-Agent Customer Support System with A2A Coordination
**Last Updated**: 2025-12-23
**Purpose**: Comprehensive guide for AI assistants working on this codebase

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Key Components](#key-components)
5. [Development Workflows](#development-workflows)
6. [Coding Conventions](#coding-conventions)
7. [Testing Strategy](#testing-strategy)
8. [Common Tasks](#common-tasks)
9. [Important Notes for AI Assistants](#important-notes-for-ai-assistants)

---

## Project Overview

### What This System Does

This is a **multi-agent customer support system** that demonstrates Agent-to-Agent (A2A) coordination patterns. The system uses three specialized agents working together to handle customer queries through intelligent routing and coordination.

**Key Features:**
- State-based message passing for agent coordination
- Model Context Protocol (MCP) for database access
- Three coordination patterns: Simple, Sequential, Negotiation
- Rule-based intent detection (no external LLM required)
- Comprehensive logging and observability
- Interactive demo with test scenarios

**NOT an LLM-based system**: This implementation uses rule-based intent detection and pattern matching, making it lightweight and educational. It can be extended with LLM integration in the future.

---

## Codebase Structure

```
a2a_new/
├── README.md                          # User-facing documentation
├── CLAUDE.md                          # This file - AI assistant guide
├── CONCLUSION.md                      # Learning outcomes and reflections
├── requirements.txt                   # Python dependencies (minimal)
├── .gitignore                         # Git ignore rules
│
├── main.py                            # Main entry point - demo application
├── a2a_system.py                      # A2A coordination system (core logic)
├── database_setup.py                  # Database initialization and setup
├── test_system.py                     # Test scenarios
│
├── agents/                            # Agent implementations
│   ├── __init__.py
│   ├── router_agent.py                # Orchestrator agent
│   ├── customer_data_agent.py         # Database specialist
│   └── support_agent.py               # Support specialist
│
├── mcp_server/                        # MCP server implementation
│   ├── __init__.py
│   └── mcp_tools.py                   # Database access tools
│
├── logs/                              # Generated coordination logs (auto-created)
└── support.db                         # SQLite database (auto-created)
```

### File Responsibilities

**Core System Files:**
- `a2a_system.py`: A2A coordination engine, state management, phase execution
- `main.py`: User interface, demo scenarios, interactive mode
- `database_setup.py`: Database schema, sample data, migrations

**Agent Files:**
- `agents/router_agent.py`: Intent analysis, routing decisions, response synthesis
- `agents/customer_data_agent.py`: Customer CRUD operations via MCP
- `agents/support_agent.py`: Support queries, ticket creation, escalation

**MCP Files:**
- `mcp_server/mcp_tools.py`: Database abstraction, tool implementations

---

## Architecture & Design Patterns

### 1. State-Based Coordination

The system uses a **shared state object** (`AgentState`) that flows through all agents:

```python
@dataclass
class AgentState:
    # Input
    query: str
    customer_id: Optional[int]

    # Intent analysis
    intents: List[str]
    priority: str
    coordination_type: str

    # Routing
    required_agents: List[str]
    agent_sequence: List[str]

    # Data collection
    customer_data: Optional[Dict]
    support_data: Optional[Dict]
    agent_results: List[Dict]

    # Output
    final_response: str
    phase: str
    coordination_log: List[str]
```

**Why this matters:**
- State is the **single source of truth**
- Agents don't call each other directly
- All communication happens through state updates
- Makes the system debuggable and testable

### 2. Four-Phase Execution Pipeline

Every query goes through these phases:

1. **ANALYZE** (Router): Detect intents, priority, required agents
2. **ROUTE** (Router): Determine coordination strategy and agent sequence
3. **EXECUTE** (Agents): Run agents based on coordination type
4. **SYNTHESIZE** (Router): Combine results into final response

**Key Pattern**: The router orchestrates everything, agents are stateless workers.

### 3. Three Coordination Patterns

**Simple (Task Allocation):**
- Single agent handles the request
- Direct routing, no context needed
- Example: "Get customer information for ID 5"
- Flow: `User → Router → CustomerDataAgent → Response`

**Sequential (Task Chaining):**
- Multiple agents work in sequence
- Each agent's output feeds the next
- Example: "I'm customer 12345 and need help upgrading"
- Flow: `User → Router → CustomerDataAgent → SupportAgent → Response`

**Negotiation (Complex Coordination):**
- Agents collaborate on multi-faceted problems
- Requires data gathering, analysis, synthesis
- Example: "Show all active customers with open tickets"
- Flow: `User → Router → CustomerDataAgent + SupportAgent → Router synthesis`

### 4. MCP (Model Context Protocol) Integration

**Purpose**: Abstract database operations into reusable tools

**Available Tools:**
- `get_customer(customer_id)` - Retrieve customer by ID
- `list_customers(status, limit)` - List customers with filters
- `update_customer(customer_id, data)` - Update customer info
- `create_ticket(customer_id, issue, priority)` - Create support ticket
- `get_customer_history(customer_id)` - Get all tickets for customer
- `get_tickets_by_priority(priority, status)` - Query tickets
- `get_active_customers_with_open_tickets()` - Complex query

**Key Pattern**: Agents never directly access the database - they always go through MCP tools.

---

## Key Components

### 1. A2ACoordinationSystem (`a2a_system.py`)

**Location**: `a2a_system.py:68-478`

**Core Methods:**
- `process_query(query, customer_id)` - Main entry point, executes full pipeline
- `_analyze_phase(state)` - Phase 1: Intent analysis
- `_route_phase(state)` - Phase 2: Routing strategy
- `_execute_phase(state)` - Phase 3: Agent execution
- `_synthesize_phase(state)` - Phase 4: Response synthesis

**Internal Execution Methods:**
- `_execute_simple(state)` - Single agent execution
- `_execute_sequential(state)` - Multi-agent chain
- `_execute_negotiation(state)` - Complex coordination
- `_call_agent(agent_name, action, params, state)` - Agent invocation

**Helper Methods:**
- `_determine_action(state)` - Map intents to actions
- `_determine_action_for_agent(agent_name, state)` - Agent-specific actions
- `_build_params(state, action)` - Build action parameters from state

### 2. RouterAgent (`agents/router_agent.py`)

**Location**: `agents/router_agent.py:11-351`

**Responsibilities:**
- Analyze query intent and detect customer IDs
- Determine required agents and coordination type
- Set priority based on urgency keywords
- Create routing plans with execution steps
- Synthesize final responses from agent results

**Key Methods:**
- `analyze_intent(query)` - Returns intent analysis dict
- `determine_routing(intent_analysis)` - Returns routing plan
- `synthesize_response(agent_results, original_query)` - Returns formatted response

**Intent Detection:**
Uses keyword matching for:
- Data retrieval: "get customer", "list customers", "show tickets"
- Updates: "update", "change", "modify"
- Support: "help", "issue", "problem"
- Account management: "upgrade", "downgrade", "subscription"
- Billing: "charged", "refund", "payment"
- Complex queries: "active customers with open tickets"

### 3. CustomerDataAgent (`agents/customer_data_agent.py`)

**Location**: `agents/customer_data_agent.py:11-185`

**Responsibilities:**
- All customer database operations
- Ticket history retrieval
- Customer context analysis for support agents

**Supported Actions:**
- `get_customer` - Retrieve single customer
- `list_customers` - List with filters
- `update_customer` - Update customer fields
- `get_customer_history` - Customer + tickets
- `get_active_customers_with_open_tickets` - Complex query

**Pattern**: All requests go through `process_request(request)` which routes to internal methods.

### 4. SupportAgent (`agents/support_agent.py`)

**Location**: `agents/support_agent.py:11-287`

**Responsibilities:**
- Query analysis for support intents
- Support response generation
- Ticket creation and escalation
- Priority ticket queries

**Supported Actions:**
- `analyze_query` - Intent and priority detection
- `handle_support_query` - Generate contextual response
- `create_ticket` - Create new ticket
- `escalate_issue` - Create high-priority ticket
- `get_high_priority_tickets` - Query high-priority tickets

**Response Generation:**
Generates context-aware responses for:
- Billing issues
- Account management
- Technical support
- Account updates
- Information requests

### 5. MCPTools (`mcp_server/mcp_tools.py`)

**Location**: `mcp_server/mcp_tools.py:12-370`

**Database Schema:**

```sql
-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'disabled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tickets table
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    issue TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved')),
    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);
```

**Return Format:**
All MCP tools return dictionaries with:
- `success` (bool) - Operation success status
- `error` (str) - Error message if success=False
- Data fields specific to the operation

---

## Development Workflows

### Initial Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python database_setup.py

# 5. Run the application
python main.py
```

### Running the Application

**Main Menu Options:**
1. **Run all 5 test scenarios** - Executes predefined scenarios with logging
2. **Interactive mode** - Enter custom queries in real-time
3. **Exit** - Clean shutdown

**Test Scenarios:**
- Scenario 1: Simple query (single agent)
- Scenario 2: Coordinated query (sequential)
- Scenario 3: Complex query (negotiation)
- Scenario 4: Escalation (high priority)
- Scenario 5: Multi-intent (multiple operations)

### Database Management

**Reset Database:**
```bash
# Delete existing database
rm support.db

# Recreate with fresh data
python database_setup.py
```

**View Database Schema:**
```python
# In database_setup.py main(), it displays schema automatically
python database_setup.py
# Select 'n' when asked about sample data to just see schema
```

**Sample Queries:**
The database setup includes 10 sample query functions demonstrating:
- Open tickets by priority
- Customer ticket history
- Active customers with open tickets
- Ticket statistics

---

## Coding Conventions

### Naming Conventions

**Files:**
- Snake_case for Python files: `customer_data_agent.py`
- Module names match class names: `RouterAgent` in `router_agent.py`

**Classes:**
- PascalCase: `RouterAgent`, `A2ACoordinationSystem`, `MCPTools`
- Agent classes end with "Agent": `CustomerDataAgent`, `SupportAgent`

**Methods:**
- Snake_case: `process_query()`, `analyze_intent()`
- Private methods start with underscore: `_execute_simple()`, `_build_params()`
- MCP tool methods match their purpose: `get_customer()`, `create_ticket()`

**Variables:**
- Snake_case: `customer_id`, `agent_results`, `coordination_type`
- Constants in CAPS: Not used in this codebase (no constants)

### Code Organization Patterns

**1. Agent Request Processing:**
```python
def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """All agents follow this pattern."""
    action = request.get("action")
    params = request.get("params", {})

    # Log the action
    print(f"[{self.agent_name}] Processing action: {action}")

    # Route to action handler
    if action == "specific_action":
        result = self._specific_action(params)
    else:
        result = {"success": False, "error": f"Unknown action: {action}"}

    # Add agent identifier to result
    result["agent"] = self.agent_name
    return result
```

**2. MCP Tool Response Format:**
```python
# Success response
{
    "success": True,
    "customer": {...},  # or "customers", "ticket", etc.
    # Additional fields as needed
}

# Error response
{
    "success": False,
    "error": "Descriptive error message"
}
```

**3. State Logging:**
```python
state.log(f"Message about what's happening")
# This adds timestamp automatically and prints to console
```

### Error Handling

**Pattern 1: Validation at Entry Points**
```python
def _get_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
    customer_id = params.get("customer_id")
    if not customer_id:
        return {
            "success": False,
            "error": "customer_id is required",
            "agent": self.agent_name
        }
    # Proceed with operation...
```

**Pattern 2: Database Error Handling**
```python
try:
    self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    # ... operation ...
    return {"success": True, "customer": result}
except sqlite3.Error as e:
    return {"success": False, "error": f"Database error: {str(e)}"}
```

**Pattern 3: Graceful Degradation**
- Agents return error results rather than raising exceptions
- Router checks `success` field before using results
- Final response includes error messages from failed operations

### Type Hints

**Consistent Usage:**
- All public methods have type hints
- Return types are always specified
- Dict and List use typing module: `Dict[str, Any]`, `List[str]`
- Optional values use `Optional[T]`

```python
from typing import Dict, Any, List, Optional

def analyze_intent(self, query: str) -> Dict[str, Any]:
    """Type hints on all parameters and return values."""
    pass
```

### Documentation Strings

**Format:**
```python
def process_query(self, query: str, customer_id: Optional[int] = None) -> Dict[str, Any]:
    """Process a user query through the multi-agent system.

    Args:
        query: User query string
        customer_id: Optional customer ID

    Returns:
        Final response with coordination details
    """
```

**Requirements:**
- All public methods have docstrings
- Private methods may omit docstrings if purpose is clear
- Class docstrings describe purpose and responsibilities

---

## Testing Strategy

### Test Scenarios

**Location**: `main.py:54-126` (in `run_test_scenarios()`)

**Predefined Scenarios:**
1. Simple Query: Single agent, direct retrieval
2. Coordinated Query: Sequential coordination with context
3. Complex Query: Negotiation between multiple agents
4. Escalation: High-priority ticket creation
5. Multi-Intent: Multiple operations in one query

### Manual Testing

**Interactive Mode:**
```bash
python main.py
# Select option 2
# Enter queries like:
# - "Get customer 1 information"
# - "I need help with my account, customer ID 5"
# - "Show all active customers with open tickets"
```

**Database Queries:**
```bash
# Use database_setup.py to run sample queries
python database_setup.py
# Select 'y' for sample data
# Select 'y' for sample queries
```

### Debugging

**Coordination Logs:**
- Every action is logged with timestamps
- Logs show phase transitions clearly
- Agent inputs/outputs are logged
- Exportable to `logs/` directory

**Log Format:**
```
[HH:MM:SS.mmm] [AgentName] Message
```

**Viewing Logs:**
```bash
# Logs are printed to console during execution
# Export logs from main menu after running scenarios
# Files saved to: logs/a2a_coordination_YYYYMMDD_HHMMSS.log
```

---

## Common Tasks

### Adding a New Agent

**1. Create Agent File:**
```python
# agents/new_agent.py
from typing import Dict, Any

class NewAgent:
    """Agent specialized in new_capability."""

    def __init__(self, db_path: str = "support.db"):
        self.agent_name = "NewAgent"

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action")
        params = request.get("params", {})
        # Handle actions...
        return {"success": True, "agent": self.agent_name}
```

**2. Register in A2A System:**
```python
# a2a_system.py - in __init__
self.new_agent = NewAgent(db_path)

# a2a_system.py - in _call_agent
elif agent_name == "NewAgent":
    result = self.new_agent.process_request(request)
```

**3. Update Router Intent Detection:**
```python
# agents/router_agent.py - in analyze_intent
if any(word in query_lower for word in ["new_intent_keywords"]):
    intents.append("new_intent")
    required_agents.append("NewAgent")
```

### Adding a New MCP Tool

**1. Add Method to MCPTools:**
```python
# mcp_server/mcp_tools.py
def new_tool(self, param1: str, param2: int) -> Dict[str, Any]:
    """New tool description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Tool result
    """
    try:
        # Database operation
        self.cursor.execute("SELECT ...", (param1, param2))
        result = self.cursor.fetchone()

        return {
            "success": True,
            "data": self._dict_from_row(result)
        }
    except sqlite3.Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
```

**2. Use in Agent:**
```python
# agents/customer_data_agent.py
def _new_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
    result = self.mcp.new_tool(params['param1'], params['param2'])
    result["agent"] = self.agent_name
    return result
```

### Adding a New Coordination Pattern

**1. Define Pattern in Router:**
```python
# agents/router_agent.py - in analyze_intent
if meets_new_pattern_criteria:
    coordination_type = "new_pattern"
```

**2. Implement Execution:**
```python
# a2a_system.py - in _execute_phase
elif state.coordination_type == "new_pattern":
    state = self._execute_new_pattern(state)

# Add new execution method
def _execute_new_pattern(self, state: AgentState) -> AgentState:
    """Execute new coordination pattern."""
    state.log("  Execution mode: NEW_PATTERN")
    # Pattern-specific logic...
    return state
```

### Modifying Intent Detection

**Location**: `agents/router_agent.py:18-108`

**Pattern:**
```python
# Add new keywords for existing intent
if any(word in query_lower for word in ["existing", "keywords", "new_keyword"]):
    intents.append("intent_name")
    required_agents.append("AgentName")

# Add new intent category
if any(word in query_lower for word in ["new", "intent", "keywords"]):
    intents.append("new_intent_category")
    required_agents.append("ResponsibleAgent")
    coordination_type = "sequential"  # or "simple" or "negotiation"
```

### Database Schema Changes

**1. Modify Schema:**
```python
# database_setup.py - in create_tables()
self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field1 TEXT NOT NULL,
        field2 INTEGER
    )
""")
```

**2. Add Indexes:**
```python
# database_setup.py - in create_tables()
self.cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_new_table_field1
    ON new_table(field1)
""")
```

**3. Add Sample Data:**
```python
# database_setup.py - in insert_sample_data()
data = [
    ("value1", 123),
    ("value2", 456),
]
self.cursor.executemany("""
    INSERT INTO new_table (field1, field2)
    VALUES (?, ?)
""", data)
```

**4. Reset Database:**
```bash
rm support.db
python database_setup.py
```

---

## Important Notes for AI Assistants

### Critical Patterns to Maintain

**1. Agents NEVER call other agents directly**
- All coordination goes through the A2ACoordinationSystem
- Agents are stateless - they receive state, process, return results
- Inter-agent communication happens via state updates

**2. Always use MCP tools for database access**
- Agents never directly execute SQL queries
- MCP tools handle all database operations
- This maintains separation of concerns and testability

**3. State is immutable from agent perspective**
- Agents read from state
- Agents return new data
- Router updates state with agent results
- Never modify state in-place within agents

**4. Error handling must be graceful**
- Return `{"success": False, "error": "message"}` instead of raising
- Check `success` field before using results
- Propagate errors up through the call chain

**5. Logging is mandatory**
- Use `state.log()` for coordination-level logging
- Use `print(f"[{self.agent_name}] ...")` for agent-level logging
- Every phase, action, and transition should be logged

### What NOT to Do

**❌ Don't add external dependencies lightly**
- This system is intentionally lightweight
- No external LLM APIs required
- Keep dependencies in `requirements.txt` minimal

**❌ Don't bypass the MCP layer**
```python
# BAD - Direct database access
self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))

# GOOD - Use MCP tools
result = self.mcp.get_customer(customer_id)
```

**❌ Don't make agents stateful**
```python
# BAD - Storing state in agent
class CustomerDataAgent:
    def __init__(self):
        self.last_customer = None  # Don't do this!

# GOOD - Pass everything through request/response
def process_request(self, request: Dict) -> Dict:
    # Process and return, no instance variables
```

**❌ Don't skip type hints or docstrings**
```python
# BAD - No type hints
def process_query(query, customer_id):
    pass

# GOOD - Full type hints and docstring
def process_query(self, query: str, customer_id: Optional[int] = None) -> Dict[str, Any]:
    """Process a user query through the multi-agent system."""
    pass
```

**❌ Don't create complex nested coordination**
- Keep coordination patterns simple and explicit
- Maximum 3 agents in a sequence
- If you need more, consider creating a specialized agent

### Performance Considerations

**Database Connection:**
- MCP tools use a singleton pattern (`get_mcp_tools()`)
- Connection is reused across agents
- Set `check_same_thread=False` for SQLite multi-threading

**Logging:**
- Coordination logs can grow large
- Consider adding log rotation for production use
- Current implementation stores full logs in memory

**State Object:**
- State object grows with each agent's results
- For very long agent chains, consider pruning old results
- Current implementation is fine for 3-5 agents

### Extending to LLM-Based System

**If adding LLM integration:**

1. **Replace intent detection:**
```python
# Current: Rule-based in router_agent.py
# Replace with: LLM prompt for intent classification
```

2. **Enhance response synthesis:**
```python
# Current: Template-based in router_agent.py
# Replace with: LLM-generated natural responses
```

3. **Improve query understanding:**
```python
# Current: Regex for customer ID extraction
# Replace with: LLM entity extraction
```

4. **Keep the architecture:**
- State-based coordination still applies
- Agent boundaries remain the same
- MCP tools stay unchanged

### Common Pitfalls

**1. Forgetting to add agent identifier:**
```python
# All agent results must include:
result["agent"] = self.agent_name
```

**2. Not checking success before using data:**
```python
# BAD
customer = result["customer"]

# GOOD
if result.get("success"):
    customer = result["customer"]
else:
    # Handle error
```

**3. Inconsistent parameter naming:**
```python
# Use consistent names:
# - customer_id (not id, cust_id, customerId)
# - ticket_id (not id, tid)
# - query (not question, prompt, text)
```

**4. Missing required parameters:**
```python
# Always validate required parameters first:
def _get_customer(self, params):
    customer_id = params.get("customer_id")
    if not customer_id:
        return {"success": False, "error": "customer_id is required"}
```

### Testing Checklist

Before committing changes:

- [ ] All new methods have type hints
- [ ] All public methods have docstrings
- [ ] Error cases return `{"success": False, "error": "..."}`
- [ ] Agent results include `"agent": self.agent_name`
- [ ] Database changes are reflected in `database_setup.py`
- [ ] New intents are added to router's `analyze_intent()`
- [ ] Manual testing in interactive mode works
- [ ] Coordination logs show expected flow
- [ ] No direct database access (use MCP tools)
- [ ] No agent-to-agent direct calls

### Useful Code Locations

**Adding new intent:**
- `agents/router_agent.py:28-106`

**Adding new coordination pattern:**
- `a2a_system.py:182-306`

**Adding new MCP tool:**
- `mcp_server/mcp_tools.py:34-370`

**Modifying database schema:**
- `database_setup.py:26-86`

**Adding test scenario:**
- `main.py:54-126`

**Response formatting:**
- `agents/router_agent.py:263-351`

---

## Quick Reference

### Agent Communication Flow

```
1. User Query
   ↓
2. A2ACoordinationSystem.process_query()
   ↓
3. Router.analyze_intent() → Update state with intents
   ↓
4. Router.determine_routing() → Update state with plan
   ↓
5. Execute agents based on coordination_type:
   - Simple: One agent
   - Sequential: Agents in order
   - Negotiation: Multiple agents + synthesis
   ↓
6. Router.synthesize_response() → Format final output
   ↓
7. Return to user
```

### State Fields Reference

```python
# Input fields
state.query: str                    # User's original query
state.customer_id: Optional[int]    # Extracted or provided customer ID

# Analysis fields
state.intents: List[str]            # Detected intents
state.priority: str                 # "low", "medium", "high"
state.coordination_type: str        # "simple", "sequential", "negotiation"

# Routing fields
state.required_agents: List[str]    # Agents needed
state.agent_sequence: List[str]     # Order of execution
state.current_agent: str            # Currently executing agent

# Data fields
state.customer_data: Optional[Dict] # CustomerDataAgent results
state.support_data: Optional[Dict]  # SupportAgent results
state.agent_results: List[Dict]     # All agent results

# Output fields
state.final_response: str           # Synthesized response
state.phase: str                    # Current execution phase
state.coordination_log: List[str]   # Full execution log
```

### Common Error Patterns

```python
# Error: Customer not found
{"success": False, "error": "Customer with ID X not found"}

# Error: Missing required parameter
{"success": False, "error": "customer_id is required"}

# Error: Database error
{"success": False, "error": "Database error: <sqlite3 error>"}

# Error: Unknown action
{"success": False, "error": "Unknown action: <action>"}

# Error: Invalid value
{"success": False, "error": "Invalid priority: X. Must be 'low', 'medium', or 'high'"}
```

---

## Summary

This multi-agent system demonstrates clean architectural patterns for agent coordination:

**Key Takeaways:**
1. State-based message passing keeps agents decoupled
2. Phase-based execution provides clear structure
3. MCP layer abstracts data operations
4. Comprehensive logging enables debugging
5. Graceful error handling maintains robustness

**For AI Assistants:**
- Follow existing patterns strictly
- Maintain separation of concerns
- Keep agents stateless
- Use MCP tools for database access
- Log everything
- Handle errors gracefully
- Test thoroughly before committing

**Resources:**
- README.md - User documentation and setup guide
- CONCLUSION.md - Learning outcomes and challenges
- Code comments - Implementation details
- Test scenarios in main.py - Usage examples

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: Multi-Agent Systems Course Project
