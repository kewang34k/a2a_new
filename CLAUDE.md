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

## Advanced Topics

### Multi-Turn Conversations

**Current State**: System processes single queries in isolation.

**To Add Conversation Context:**

```python
# Extend AgentState with conversation history
@dataclass
class AgentState:
    # ... existing fields ...
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    session_id: Optional[str] = None
```

**Implementation Pattern:**
1. Store conversation history in session storage (file, Redis, database)
2. Pass previous context to router for better intent detection
3. Support follow-up queries like "and what about tickets?"
4. Implement conversation memory management (limit to last N turns)

### Parallel Agent Execution

**Current**: Sequential execution for all multi-agent scenarios
**Enhancement**: Execute independent agents in parallel

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def _execute_parallel(self, state: AgentState) -> AgentState:
    """Execute multiple agents in parallel."""
    state.log("  Execution mode: PARALLEL")

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for agent_name in state.required_agents:
            action = self._determine_action_for_agent(agent_name, state)
            params = self._build_params(state, action)
            future = executor.submit(
                self._call_agent, agent_name, action, params, state
            )
            futures.append((agent_name, future))

        for agent_name, future in futures:
            result = future.result()
            state.agent_results.append(result)

    return state
```

**Use Cases:**
- Fetching customer data and ticket statistics simultaneously
- Running multiple independent queries
- Gathering data from multiple sources

### Agent Self-Correction

**Pattern**: Agents can validate their own outputs and retry

```python
def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Process request with self-correction."""
    max_retries = 3

    for attempt in range(max_retries):
        result = self._execute_action(request)

        # Validate result
        if self._validate_result(result):
            return result

        # Log retry
        print(f"[{self.agent_name}] Retry {attempt + 1}/{max_retries}")

        # Adjust parameters for retry
        request = self._adjust_for_retry(request, result)

    return {"success": False, "error": "Max retries exceeded"}
```

### Dynamic Agent Loading

**Pattern**: Load agents dynamically based on available modules

```python
import importlib
from pathlib import Path

def _load_agents_dynamically(self):
    """Dynamically load all agent modules."""
    agents_dir = Path("agents")
    self.agents = {}

    for agent_file in agents_dir.glob("*_agent.py"):
        module_name = agent_file.stem
        module = importlib.import_module(f"agents.{module_name}")

        # Get the agent class (assume class name matches file)
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        agent_class = getattr(module, class_name)

        # Instantiate
        self.agents[class_name] = agent_class(self.db_path)
```

### Conditional Routing

**Advanced routing based on runtime conditions:**

```python
def _dynamic_routing(self, state: AgentState) -> AgentState:
    """Route based on runtime conditions."""

    # Check customer status first
    if state.customer_id:
        customer_result = self.data_agent.process_request({
            "action": "get_customer",
            "params": {"customer_id": state.customer_id}
        })

        if customer_result.get("success"):
            customer = customer_result["customer"]

            # VIP customers get priority routing
            if customer.get("status") == "vip":
                state.priority = "high"
                state.required_agents = ["VIPSupportAgent"]
            # Disabled customers get different flow
            elif customer.get("status") == "disabled":
                state.required_agents = ["AccountRecoveryAgent"]

    return state
```

### Agent Composition Patterns

**Decorator Pattern for Agents:**

```python
class LoggingAgentDecorator:
    """Adds detailed logging to any agent."""

    def __init__(self, agent):
        self.agent = agent
        self.agent_name = f"{agent.agent_name}_Logged"

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.now()

        print(f"[{self.agent_name}] Starting: {request['action']}")
        result = self.agent.process_request(request)

        duration = (datetime.now() - start_time).total_seconds()
        print(f"[{self.agent_name}] Completed in {duration:.2f}s")

        return result

# Usage
self.data_agent = LoggingAgentDecorator(CustomerDataAgent(db_path))
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "Customer with ID X not found"

**Cause**: Customer ID doesn't exist in database or wrong ID extracted

**Debug Steps:**
1. Check database: `sqlite3 support.db "SELECT * FROM customers WHERE id = X;"`
2. Verify customer ID extraction in router
3. Check if customer was deleted

**Solution:**
```python
# Add customer existence check before operations
def _validate_customer_exists(self, customer_id: int) -> bool:
    result = self.mcp.get_customer(customer_id)
    return result.get("success", False)
```

#### Issue 2: Agent Not Called in Sequence

**Cause**: Intent detection didn't add agent to required_agents list

**Debug Steps:**
1. Check coordination log for intent analysis phase
2. Verify query keywords match intent detection patterns
3. Check if coordination_type is correct

**Solution:**
```python
# In router_agent.py, add debug logging
print(f"Query keywords: {query_lower.split()}")
print(f"Detected intents: {intents}")
print(f"Required agents: {required_agents}")
```

#### Issue 3: State Data Lost Between Agents

**Cause**: State not properly updated or passed

**Debug Steps:**
1. Check `_execute_sequential` method
2. Verify agent results are added to `state.agent_results`
3. Check state logging for data flow

**Solution:**
```python
# Always update state with agent-specific data
if agent_name == "CustomerDataAgent":
    state.customer_data = result  # Store for next agent
    print(f"Stored customer_data: {result.keys()}")
```

#### Issue 4: Database Locked Error

**Cause**: Multiple threads accessing SQLite simultaneously

**Solution:**
```python
# Ensure connection uses check_same_thread=False
self.conn = sqlite3.connect(
    self.db_path,
    check_same_thread=False,
    timeout=10.0  # Add timeout
)
```

#### Issue 5: Coordination Type Always "Simple"

**Cause**: Intent detection logic doesn't trigger multi-agent patterns

**Debug Steps:**
1. Check query keywords
2. Review coordination_type assignment logic
3. Test with known multi-agent queries

**Solution:**
```python
# Add explicit multi-agent triggers
if len(required_agents) > 1:
    coordination_type = "sequential"

# Or for complex queries
if "complex_query" in intents or len(required_agents) >= 2:
    coordination_type = "negotiation"
```

#### Issue 6: MCP Tools Return Empty Results

**Cause**: Database queries returning no rows

**Debug Steps:**
1. Run SQL directly: `sqlite3 support.db "SELECT * FROM customers;"`
2. Check if sample data was inserted
3. Verify table names and column names

**Solution:**
```bash
# Reset database
rm support.db
python database_setup.py
# Select 'y' to insert sample data
```

#### Issue 7: Import Errors

**Cause**: Python path issues or missing __init__.py files

**Solution:**
```bash
# Ensure you're in the project root
cd /home/user/a2a_new

# Check __init__.py files exist
ls agents/__init__.py
ls mcp_server/__init__.py

# Run from project root
python main.py
```

#### Issue 8: Logs Not Showing

**Cause**: Logging configuration or output buffering

**Solution:**
```python
# Force flush after logging
import sys
print(f"[{self.agent_name}] Message", flush=True)

# Or disable buffering
sys.stdout.flush()
```

---

## Detailed Code Examples

### Example 1: Complete Custom Agent Implementation

```python
# agents/billing_agent.py
from typing import Dict, Any, Optional
from mcp_server.mcp_tools import get_mcp_tools

class BillingAgent:
    """Specialized agent for billing operations."""

    def __init__(self, db_path: str = "support.db"):
        self.mcp = get_mcp_tools(db_path)
        self.agent_name = "BillingAgent"
        self.billing_rules = self._load_billing_rules()

    def _load_billing_rules(self) -> Dict[str, Any]:
        """Load billing rules and policies."""
        return {
            "refund_window_days": 30,
            "auto_refund_threshold": 100.00,
            "requires_approval": ["subscription", "annual"]
        }

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process billing requests."""
        action = request.get("action")
        params = request.get("params", {})

        print(f"[{self.agent_name}] Processing: {action}")

        # Route to handler
        handlers = {
            "process_refund": self._process_refund,
            "calculate_charges": self._calculate_charges,
            "validate_payment": self._validate_payment,
            "check_subscription": self._check_subscription
        }

        handler = handlers.get(action, self._unknown_action)
        result = handler(params)
        result["agent"] = self.agent_name
        return result

    def _process_refund(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a refund request."""
        customer_id = params.get("customer_id")
        amount = params.get("amount", 0.0)
        reason = params.get("reason", "Customer request")

        # Validate customer
        customer = self.mcp.get_customer(customer_id)
        if not customer["success"]:
            return {"success": False, "error": "Customer not found"}

        # Check refund eligibility
        if amount > self.billing_rules["auto_refund_threshold"]:
            # Create ticket for manual review
            ticket_result = self.mcp.create_ticket(
                customer_id,
                f"Refund request: ${amount:.2f} - {reason}",
                "high"
            )
            return {
                "success": True,
                "requires_approval": True,
                "ticket_id": ticket_result["ticket"]["id"],
                "message": "Refund requires approval - ticket created"
            }
        else:
            # Auto-approve small refunds
            return {
                "success": True,
                "approved": True,
                "amount": amount,
                "message": f"Refund of ${amount:.2f} approved automatically"
            }

    def _calculate_charges(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate billing charges."""
        customer_id = params.get("customer_id")
        plan_type = params.get("plan_type", "basic")

        rates = {
            "basic": 9.99,
            "pro": 29.99,
            "enterprise": 99.99
        }

        return {
            "success": True,
            "plan_type": plan_type,
            "monthly_charge": rates.get(plan_type, 0.0),
            "annual_charge": rates.get(plan_type, 0.0) * 12 * 0.9  # 10% discount
        }

    def _validate_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment information."""
        # Placeholder - would integrate with payment gateway
        return {
            "success": True,
            "valid": True,
            "message": "Payment method validated"
        }

    def _check_subscription(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check subscription status."""
        customer_id = params.get("customer_id")

        # Get customer
        customer = self.mcp.get_customer(customer_id)
        if not customer["success"]:
            return {"success": False, "error": "Customer not found"}

        # Placeholder - would check actual subscription data
        return {
            "success": True,
            "active": customer["customer"]["status"] == "active",
            "plan": "pro",
            "renewal_date": "2025-01-23"
        }

    def _unknown_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown actions."""
        return {
            "success": False,
            "error": "Unknown billing action"
        }
```

### Example 2: Complex Query Handler

```python
# In router_agent.py - add complex query handler
def handle_complex_query(self, query: str) -> Dict[str, Any]:
    """Handle queries requiring multiple data points."""

    query_lower = query.lower()

    # Pattern: "show customers with X tickets and Y status"
    if "customers with" in query_lower and "tickets" in query_lower:
        # Extract conditions
        ticket_count = self._extract_number(query)
        status = "active" if "active" in query_lower else None
        priority = None

        if "high priority" in query_lower:
            priority = "high"
        elif "open" in query_lower:
            status_filter = "open"

        return {
            "query_type": "filtered_customers_with_tickets",
            "filters": {
                "min_tickets": ticket_count,
                "customer_status": status,
                "ticket_priority": priority
            }
        }

    # Pattern: "what's the status of customer X's tickets"
    elif "status" in query_lower and "tickets" in query_lower:
        customer_id = self._extract_customer_id(query)
        return {
            "query_type": "customer_ticket_status",
            "customer_id": customer_id
        }

    return {"query_type": "unknown"}
```

### Example 3: Agent State Persistence

```python
# Save and restore agent state
import json
from pathlib import Path

class StatePersistence:
    """Handle state persistence for multi-turn conversations."""

    def __init__(self, storage_dir: str = "state_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_state(self, session_id: str, state: AgentState) -> bool:
        """Save agent state to disk."""
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            state_dict = {
                "query": state.query,
                "customer_id": state.customer_id,
                "intents": state.intents,
                "priority": state.priority,
                "coordination_type": state.coordination_type,
                "agent_results": state.agent_results,
                "final_response": state.final_response,
                "timestamp": datetime.now().isoformat()
            }

            with open(file_path, 'w') as f:
                json.dump(state_dict, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state from disk."""
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if not file_path.exists():
                return None

            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
            return None

    def cleanup_old_states(self, max_age_hours: int = 24):
        """Remove state files older than max_age_hours."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    state = json.load(f)
                    timestamp = datetime.fromisoformat(state["timestamp"])

                    if timestamp < cutoff:
                        file_path.unlink()
                        print(f"Cleaned up old state: {file_path.name}")
            except Exception as e:
                print(f"Error cleaning up {file_path}: {e}")
```

### Example 4: Advanced Response Formatting

```python
# In router_agent.py - add rich response formatting
def _format_rich_response(self, result: Dict[str, Any]) -> str:
    """Format response with rich text elements."""

    if "customers" in result:
        customers = result["customers"]

        # Create table-like output
        response = "┌" + "─" * 78 + "┐\n"
        response += "│" + " CUSTOMER LIST".center(78) + "│\n"
        response += "├" + "─" * 78 + "┤\n"

        for customer in customers[:10]:
            name = customer['name'][:25].ljust(25)
            email = customer['email'][:30].ljust(30)
            status = customer['status'].upper().center(10)

            response += f"│ {name} │ {email} │ {status} │\n"

        response += "└" + "─" * 78 + "┘\n"

        if len(customers) > 10:
            response += f"\n... and {len(customers) - 10} more customers\n"

        return response

    return self._format_data_response(result)
```

---

## Performance Optimization

### Database Optimization

**1. Connection Pooling:**
```python
from queue import Queue
import threading

class ConnectionPool:
    """Simple connection pool for SQLite."""

    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()

        # Initialize pool
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)

    def get_connection(self):
        """Get connection from pool."""
        return self.pool.get()

    def return_connection(self, conn):
        """Return connection to pool."""
        self.pool.put(conn)
```

**2. Query Optimization:**
```python
# Use prepared statements
self.get_customer_stmt = self.conn.prepare(
    "SELECT * FROM customers WHERE id = ?"
)

# Add covering indexes
self.cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_tickets_customer_status
    ON tickets(customer_id, status, priority)
""")

# Use query hints
self.cursor.execute("""
    SELECT * FROM customers
    INDEXED BY idx_customers_email
    WHERE email = ?
""")
```

**3. Batch Operations:**
```python
def batch_update_customers(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Update multiple customers in one transaction."""
    try:
        self.conn.execute("BEGIN TRANSACTION")

        for update in updates:
            customer_id = update["customer_id"]
            data = update["data"]
            self.update_customer(customer_id, data)

        self.conn.commit()
        return {"success": True, "updated_count": len(updates)}
    except Exception as e:
        self.conn.rollback()
        return {"success": False, "error": str(e)}
```

### Agent Performance

**1. Caching:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedMCPTools(MCPTools):
    """MCP Tools with caching."""

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get customer with caching."""
        cache_key = f"customer_{customer_id}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        # Fetch from database
        result = super().get_customer(customer_id)

        # Cache result
        if result["success"]:
            self.cache[cache_key] = (result, datetime.now())

        return result

    def invalidate_cache(self, customer_id: int):
        """Invalidate cache for customer."""
        cache_key = f"customer_{customer_id}"
        self.cache.pop(cache_key, None)
```

**2. Lazy Loading:**
```python
class LazyAgent:
    """Agent that loads resources on-demand."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._mcp = None
        self._rules = None

    @property
    def mcp(self):
        """Lazy-load MCP tools."""
        if self._mcp is None:
            self._mcp = get_mcp_tools(self.db_path)
        return self._mcp

    @property
    def rules(self):
        """Lazy-load business rules."""
        if self._rules is None:
            self._rules = self._load_rules()
        return self._rules
```

### Coordination Optimization

**1. Early Exit:**
```python
def _execute_with_early_exit(self, state: AgentState) -> AgentState:
    """Execute agents with early exit on critical errors."""

    for agent_name in state.agent_sequence:
        result = self._call_agent(agent_name, action, params, state)
        state.agent_results.append(result)

        # Early exit on critical errors
        if not result.get("success") and result.get("critical", False):
            state.log(f"  Critical error in {agent_name}, stopping execution")
            state.phase = "error"
            return state

        # Early exit if we have enough information
        if self._has_sufficient_data(state):
            state.log("  Sufficient data collected, skipping remaining agents")
            break

    return state
```

**2. Result Streaming:**
```python
def process_query_streaming(self, query: str) -> Generator[str, None, None]:
    """Stream results as they become available."""
    state = AgentState(query=query)

    yield "Starting analysis...\n"
    state = self._analyze_phase(state)
    yield f"Detected intents: {', '.join(state.intents)}\n"

    yield "Routing request...\n"
    state = self._route_phase(state)
    yield f"Agents: {' → '.join(state.agent_sequence)}\n"

    for agent_name in state.agent_sequence:
        yield f"Calling {agent_name}...\n"
        result = self._call_agent(agent_name, action, params, state)
        yield f"{agent_name} completed\n"

    yield "Synthesizing response...\n"
    state = self._synthesize_phase(state)
    yield f"\n{state.final_response}\n"
```

---

## Security Considerations

### Input Validation

**1. Query Sanitization:**
```python
def sanitize_query(self, query: str) -> str:
    """Sanitize user input."""
    # Remove control characters
    sanitized = ''.join(char for char in query if char.isprintable())

    # Limit length
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove SQL injection attempts
    dangerous_patterns = [
        "DROP TABLE", "DELETE FROM", "INSERT INTO",
        "UPDATE ", "--", "/*", "*/"
    ]

    query_upper = sanitized.upper()
    for pattern in dangerous_patterns:
        if pattern in query_upper:
            raise ValueError(f"Potentially dangerous input detected: {pattern}")

    return sanitized
```

**2. Parameter Validation:**
```python
def validate_customer_id(self, customer_id: Any) -> int:
    """Validate customer ID parameter."""
    try:
        cid = int(customer_id)
        if cid <= 0:
            raise ValueError("Customer ID must be positive")
        if cid > 1000000:  # Reasonable upper bound
            raise ValueError("Customer ID out of range")
        return cid
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid customer ID: {e}")
```

**3. SQL Injection Prevention:**
```python
# ALWAYS use parameterized queries
def get_customer_safe(self, customer_id: int) -> Dict[str, Any]:
    """Safe customer retrieval."""
    # GOOD - parameterized
    self.cursor.execute(
        "SELECT * FROM customers WHERE id = ?",
        (customer_id,)
    )

    # NEVER do this:
    # BAD - string interpolation
    # self.cursor.execute(f"SELECT * FROM customers WHERE id = {customer_id}")
```

### Access Control

**1. Role-Based Access:**
```python
class SecureAgent:
    """Agent with role-based access control."""

    def __init__(self, db_path: str):
        self.mcp = get_mcp_tools(db_path)
        self.agent_name = "SecureAgent"
        self.permissions = self._load_permissions()

    def _load_permissions(self) -> Dict[str, List[str]]:
        """Load role permissions."""
        return {
            "read_only": ["get_customer", "list_customers"],
            "support": ["get_customer", "list_customers", "create_ticket"],
            "admin": ["*"]  # All actions
        }

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process with access control."""
        action = request.get("action")
        role = request.get("role", "read_only")

        # Check permissions
        if not self._has_permission(role, action):
            return {
                "success": False,
                "error": f"Permission denied: {role} cannot perform {action}"
            }

        # Process request
        return self._execute_action(action, request.get("params", {}))

    def _has_permission(self, role: str, action: str) -> bool:
        """Check if role has permission for action."""
        allowed = self.permissions.get(role, [])
        return "*" in allowed or action in allowed
```

**2. Rate Limiting:**
```python
from collections import defaultdict
from time import time

class RateLimiter:
    """Simple rate limiter for agent requests."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def allow_request(self, identifier: str) -> bool:
        """Check if request is allowed."""
        now = time()
        cutoff = now - self.window_seconds

        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # Record request
        self.requests[identifier].append(now)
        return True
```

### Data Privacy

**1. PII Redaction:**
```python
import re

def redact_pii(self, text: str) -> str:
    """Redact personally identifiable information."""
    # Redact email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL REDACTED]',
        text
    )

    # Redact phone numbers
    text = re.sub(
        r'\+?\d{1,3}[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',
        '[PHONE REDACTED]',
        text
    )

    # Redact credit card numbers
    text = re.sub(
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        '[CARD REDACTED]',
        text
    )

    return text
```

**2. Audit Logging:**
```python
class AuditLogger:
    """Log all agent actions for security audits."""

    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file

    def log_action(self, agent: str, action: str, user: str, result: str):
        """Log an agent action."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": agent,
            "action": action,
            "user": user,
            "result": result
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
```

---

## FAQ (Frequently Asked Questions)

### General Questions

**Q: Can I use this with an actual LLM like GPT-4 or Claude?**

A: Yes! The architecture is designed to support LLM integration. Replace the rule-based intent detection in `router_agent.py` with LLM calls. The state-based coordination and MCP layer will work the same way.

**Q: How do I add more coordination patterns?**

A: 1) Define the pattern logic in `router_agent.py:analyze_intent()`
   2) Add execution method in `a2a_system.py:_execute_phase()`
   3) Follow existing patterns (simple/sequential/negotiation) as templates

**Q: Can agents call each other directly?**

A: No, and this is intentional. All coordination goes through the A2ACoordinationSystem. This centralized approach makes the system easier to debug and reason about.

**Q: How do I persist conversation state?**

A: Implement a state storage layer (see "Advanced Topics" section). Store state in Redis, database, or files keyed by session ID.

### Technical Questions

**Q: Why SQLite instead of PostgreSQL/MySQL?**

A: Educational simplicity. SQLite requires no setup. For production, swap out the MCPTools connection to use any database - the agent code won't change.

**Q: Can I run agents in parallel?**

A: Yes, see "Advanced Topics > Parallel Agent Execution". Use ThreadPoolExecutor or asyncio for independent agents.

**Q: How do I handle agent failures?**

A: Agents return `{"success": False, "error": "..."}` instead of raising exceptions. Check the `success` field before using results.

**Q: Can I add authentication?**

A: Yes, add authentication middleware before the A2A system. Pass user context in the request and check permissions in agents.

**Q: How do I test new agents?**

A: 1) Unit test the agent's process_request method
   2) Add a test scenario in main.py
   3) Run in interactive mode for manual testing
   4) Check coordination logs for correctness

### Debugging Questions

**Q: How do I debug intent detection?**

A: Add debug logging in `router_agent.py:analyze_intent()`. Print detected keywords, intents, and required agents.

**Q: Why isn't my agent being called?**

A: Check: 1) Agent is in required_agents list
        2) Agent is registered in A2ACoordinationSystem.__init__
        3) Agent name matches in _call_agent method
        4) Check coordination logs

**Q: How do I see all SQL queries?**

A: Add logging to MCPTools:
```python
self.conn.set_trace_callback(print)  # Prints all SQL
```

**Q: Agent state seems wrong, how to debug?**

A: 1) Enable verbose logging: `state.log()` everywhere
   2) Export logs after run
   3) Check state.to_dict() at each phase
   4) Verify agent results are being stored

### Architecture Questions

**Q: When should I use simple vs sequential vs negotiation?**

A: - **Simple**: Single data operation, no context needed
   - **Sequential**: One agent needs output from another
   - **Negotiation**: Multiple independent data sources combined

**Q: Can I modify the state structure?**

A: Yes, but carefully. Add fields to AgentState dataclass. Existing fields maintain backward compatibility.

**Q: Should I create one agent or multiple?**

A: Follow Single Responsibility Principle. If responsibilities are distinct (data vs support vs billing), use separate agents.

**Q: How do I handle backward compatibility?**

A: 1) Add new fields as Optional
   2) Provide defaults for new parameters
   3) Check field existence with .get()
   4) Version your agent APIs

---

**Last Updated**: 2025-12-23
**Version**: 2.0
**Maintainer**: Multi-Agent Systems Course Project
