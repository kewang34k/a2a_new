# CLAUDE.MD - Multi-Agent Customer Support System

## Project Overview

This is a **Multi-Agent Customer Support System** that demonstrates **Agent-to-Agent (A2A) coordination** patterns using the **Model Context Protocol (MCP)** for tool integration. The system uses state-based message passing to coordinate multiple specialized AI agents working together to handle customer support queries.

## Core Concepts

### What is A2A Coordination?

Agent-to-Agent (A2A) coordination is a pattern where multiple specialized agents work together to solve complex problems. This project implements three coordination patterns:

1. **Simple (Task Allocation)**: Single agent handles the entire request
2. **Sequential (Task Chaining)**: Multiple agents work in sequence, each building on previous results
3. **Negotiation (Complex Coordination)**: Agents collaborate and negotiate on complex multi-step tasks

### Architecture

The system consists of **3 specialized agents** coordinated by a state-based orchestration system:

#### 1. Router Agent (`agents/router_agent.py`)
- **Role**: Orchestrator/Coordinator
- **Responsibilities**:
  - Analyzes incoming queries to detect intents and priority
  - Determines which specialist agents are needed
  - Routes requests to appropriate agents
  - Synthesizes final responses from agent results
- **Key Methods**:
  - `analyze_intent()`: Detects intents, priority, and coordination type
  - `determine_routing()`: Plans agent execution sequence
  - `synthesize_response()`: Combines results into user-facing response

#### 2. Customer Data Agent (`agents/customer_data_agent.py`)
- **Role**: Database Operations Specialist
- **Responsibilities**:
  - Accesses customer database via MCP tools
  - Retrieves and updates customer information
  - Handles data validation
- **MCP Tools Used**:
  - `get_customer()`, `list_customers()`, `update_customer()`, `get_customer_history()`

#### 3. Support Agent (`agents/support_agent.py`)
- **Role**: Customer Support Specialist
- **Responsibilities**:
  - Handles support queries
  - Creates and manages tickets
  - Escalates high-priority issues
  - Provides contextual support responses
- **MCP Tools Used**:
  - `create_ticket()`, `get_customer_history()`

## System Architecture

### State Management

The coordination system uses a `AgentState` dataclass (defined in `a2a_system.py:17-65`) that flows through the system:

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
    customer_data: Optional[Dict[str, Any]]
    support_data: Optional[Dict[str, Any]]
    agent_results: List[Dict[str, Any]]

    # Output
    final_response: str
    phase: str  # analyze, route, execute, synthesize, done

    # Logging
    coordination_log: List[str]
```

### Coordination Workflow

The `A2ACoordinationSystem` (`a2a_system.py:68-477`) orchestrates a 4-phase workflow:

1. **Analyze Phase** (`_analyze_phase()`): Router analyzes query intent, priority, and required agents
2. **Route Phase** (`_route_phase()`): Router determines execution strategy and agent sequence
3. **Execute Phase** (`_execute_phase()`): Agents execute tasks based on coordination type
4. **Synthesize Phase** (`_synthesize_phase()`): Router generates final user response

### MCP Integration

The MCP server (`mcp_server/mcp_tools.py`) provides database access tools:

**Tools Available:**
- `get_customer(customer_id)`: Retrieve customer by ID
- `list_customers(status, limit)`: List customers with filtering
- `update_customer(customer_id, data)`: Update customer information
- `create_ticket(customer_id, issue, priority)`: Create support ticket
- `get_customer_history(customer_id)`: Get customer + all tickets

**Database Schema** (`support.db`):
- **customers**: id, name, email, phone, status, created_at, updated_at
- **tickets**: id, customer_id, issue, status, priority, created_at

## Project Structure

```
a2a_new/
├── main.py                    # Entry point - demo application
├── a2a_system.py              # Core A2A coordination system
├── database_setup.py          # Database initialization with sample data
├── test_system.py             # Testing utilities
├── support.db                 # SQLite database (auto-created)
│
├── agents/
│   ├── router_agent.py        # Orchestrator agent
│   ├── customer_data_agent.py # Database specialist
│   └── support_agent.py       # Support specialist
│
├── mcp_server/
│   └── mcp_tools.py           # MCP tool implementations
│
└── logs/                      # Coordination logs (auto-created)
    └── a2a_coordination_*.log
```

## Development Guidelines

### Adding New Agents

To add a new specialist agent:

1. Create new file in `agents/` directory
2. Implement `process_request(request)` method that takes `{"action": str, "params": dict}`
3. Return dict with `{"success": bool, "data": any}` format
4. Register agent in `A2ACoordinationSystem.__init__()`
5. Update Router's `analyze_intent()` to detect when to use new agent
6. Add agent name to routing logic in `determine_routing()`

### Adding New Intents

To add new intent detection:

1. Update `RouterAgent.analyze_intent()` in `agents/router_agent.py`
2. Add pattern matching keywords for the new intent
3. Map intent to required agents
4. Update coordination type if needed (simple/sequential/negotiation)

### Adding New MCP Tools

To add new database operations:

1. Add method to `MCPTools` class in `mcp_server/mcp_tools.py`
2. Follow naming pattern: `tool_name(self, param1, param2, ...)`
3. Return dict format: `{"success": bool, "data": any}` or `{"success": bool, "error": str}`
4. Update agent methods to call new tool

### Debugging Tips

1. **Enable verbose logging**: Coordination logs are automatically printed to console
2. **Check state transitions**: Each phase logs state changes
3. **Export logs**: Use main menu option 1 to export detailed coordination logs
4. **Database inspection**: Use SQLite browser to inspect `support.db` directly
5. **Agent results**: Check `state.agent_results` list to see what each agent returned

## Important Code Patterns

### Intent Detection Pattern (Router Agent)

The Router uses keyword matching to detect intents:

```python
intents = []
if any(word in query_lower for word in ["get", "show", "find", "retrieve", "customer"]):
    if "id" in query_lower or re.search(r'\d+', query):
        intents.append("get_customer_data")
```

### State-Based Message Passing

Agents don't call each other directly. Instead, state flows through the coordination system:

```python
# Router analyzes and updates state
state.intents = ["get_customer_data"]
state.required_agents = ["CustomerDataAgent"]

# Coordinator calls agent with state-derived parameters
result = self.data_agent.process_request({
    "action": "get_customer",
    "params": {"customer_id": state.customer_id}
})

# Result updates state for next agent
state.customer_data = result
```

### MCP Tool Call Pattern

Agents call MCP tools through the `MCPTools` instance:

```python
result = self.mcp.get_customer(customer_id)
if result["success"]:
    customer = result["customer"]
    # Use customer data
else:
    error = result["error"]
    # Handle error
```

## Testing & Running

### Setup Database
```bash
python database_setup.py
```

This creates `support.db` with 15 sample customers and 25 sample tickets.

### Run Application
```bash
python main.py
```

**Menu Options:**
1. Run all 5 test scenarios - Demonstrates different coordination patterns
2. Interactive mode - Enter custom queries
3. Exit

### Test Scenarios

The system includes 5 pre-built test scenarios (`main.py:60-91`):

1. **Simple Query**: "Get customer information for ID 5"
   - Single agent, direct data retrieval

2. **Coordinated Query**: "I'm customer 12345 and need help upgrading my account"
   - Sequential: CustomerData → Support

3. **Complex Query**: "Show me all active customers who have open tickets"
   - Negotiation: Multi-step data gathering + synthesis

4. **Escalation**: "I've been charged twice, please refund immediately!"
   - High priority, auto-escalation with ticket creation

5. **Multi-Intent**: "Update my email to newemail@example.com and show my ticket history"
   - Parallel task execution

### Example Query Patterns

Use these patterns in interactive mode:
- "Get customer 1 information"
- "List all active customers"
- "I need help with my account, customer ID 5"
- "Show high priority tickets"
- "I've been overcharged for my subscription"
- "Update my phone number to 555-1234"

## Key Design Decisions

### Why No External LLM?

This implementation uses **rule-based intent detection** instead of LLM calls for:
- Educational clarity - easy to understand the logic
- No API costs or dependencies
- Fast execution
- Deterministic behavior for testing

**Extension Point**: The Router's `analyze_intent()` method can be replaced with LLM-based analysis for production use.

### Why State-Based Architecture?

State-based message passing provides:
- **Traceability**: Full audit log of all decisions and data transfers
- **Debuggability**: Can inspect state at any point in workflow
- **Extensibility**: Easy to add new agents without modifying existing ones
- **Testability**: Can test each phase independently
- **Scalability**: No tight coupling between agents

### Why MCP for Database Access?

MCP provides:
- **Standardized interface**: Consistent tool calling pattern
- **Type safety**: Structured inputs/outputs
- **Error handling**: Built-in error response format
- **Extensibility**: Easy to add new database operations
- **Separation of concerns**: Database logic isolated from agent logic

## Common Modifications

### Changing Database Path

Update the default path in:
- `main.py:17` - `MultiAgentDemo.__init__()`
- `a2a_system.py:71` - `A2ACoordinationSystem.__init__()`

### Adjusting Log Verbosity

The `AgentState.log()` method (`a2a_system.py:46-51`) both stores and prints logs. To disable console output:

```python
def log(self, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {message}"
    self.coordination_log.append(log_entry)
    # Remove or comment out the print statement
    # print(log_entry)
```

### Adding Custom Coordination Types

1. Add new type to Router's `analyze_intent()` return value
2. Create new execution method in `A2ACoordinationSystem`:
   ```python
   def _execute_custom(self, state: AgentState) -> AgentState:
       # Your coordination logic
       return state
   ```
3. Add case in `_execute_phase()`:
   ```python
   elif state.coordination_type == "custom":
       state = self._execute_custom(state)
   ```

## Dependencies

Required packages (should be in `requirements.txt`):
- `anthropic` - For Claude API if extending with LLM
- Standard library only for current implementation (sqlite3, dataclasses, datetime, etc.)

## Notes for Claude

When working with this codebase:

1. **Always check the state**: The `AgentState` object is the source of truth
2. **Follow the 4-phase pattern**: Don't skip phases or reorder them
3. **Preserve logging**: Always call `state.log()` for traceability
4. **Return success dicts**: All agent methods should return `{"success": bool, ...}`
5. **Update state immutably**: Create new state objects rather than mutating
6. **Test end-to-end**: Use `main.py` to test changes, not individual components
7. **Check database schema**: Ensure new queries align with schema in `database_setup.py`

## Troubleshooting

### "Database not found" error
- Run `python database_setup.py` first
- Check that `support.db` exists in project root

### Agent not receiving data
- Check `state.customer_data` or `state.support_data` is being set
- Verify agent sequence in routing phase
- Check coordination logs for data flow

### Intent not detected
- Add keywords to Router's `analyze_intent()` method
- Check query is lowercase when comparing
- Review intent detection logic in `agents/router_agent.py:30-95`

### No response generated
- Check synthesis phase logs
- Verify agents returned success=True
- Check `state.agent_results` is populated

## Future Extensions

Potential improvements:
- LLM-based intent detection for better accuracy
- Real-time streaming responses
- Web API with REST endpoints
- Authentication and user sessions
- More sophisticated ticket routing
- Email/SMS notification integration
- Analytics dashboard for ticket metrics
- Multi-language support
- Conversation history and context retention

---

**This is an educational project demonstrating A2A coordination patterns with MCP integration.**
