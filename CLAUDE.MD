# CLAUDE.MD - Project Guide for AI Assistants

## Project Overview

**Multi-Agent Customer Support System with A2A Coordination**

This is an educational implementation demonstrating Agent-to-Agent (A2A) coordination patterns for customer support operations. The system uses three specialized agents that collaborate through state-based message passing to handle complex customer queries.

## Quick Facts

- **Language**: Python 3.8+
- **Database**: SQLite (`support.db`)
- **Architecture**: Multi-agent system with MCP (Model Context Protocol) integration
- **Coordination**: State-based A2A patterns (Simple, Sequential, Negotiation)
- **No External LLM**: Uses rule-based intent detection

## Core Architecture

### Three-Agent System

1. **Router Agent** (`agents/router_agent.py`)
   - Orchestrates the entire workflow
   - Analyzes queries and detects intents
   - Routes to appropriate specialist agents
   - Synthesizes final responses

2. **Customer Data Agent** (`agents/customer_data_agent.py`)
   - Handles database operations via MCP tools
   - Retrieves and updates customer records
   - Manages customer history

3. **Support Agent** (`agents/support_agent.py`)
   - Handles support queries
   - Creates and manages tickets
   - Analyzes priority and escalation needs

### MCP Integration

The system uses MCP (Model Context Protocol) tools defined in `mcp_server/mcp_tools.py`:

- `get_customer(customer_id)` - Fetch customer by ID
- `list_customers(status, limit)` - List customers with filters
- `update_customer(customer_id, data)` - Update customer info
- `create_ticket(customer_id, issue, priority)` - Create support ticket
- `get_customer_history(customer_id)` - Get customer ticket history

## Key Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `main.py` | Application entry point, UI, test scenarios | Adding new test scenarios, UI changes |
| `a2a_system.py` | A2A coordination system core | Modifying coordination logic |
| `agents/router_agent.py` | Query analysis and routing | Changing routing logic, intent detection |
| `agents/customer_data_agent.py` | Customer data operations | Adding new data operations |
| `agents/support_agent.py` | Support operations | Adding support features |
| `mcp_server/mcp_tools.py` | MCP tool definitions | Adding new database tools |
| `database_setup.py` | Database schema and sample data | Changing schema, adding test data |
| `requirements.txt` | Python dependencies | Adding new libraries |

## A2A Coordination Patterns

### 1. Simple (Task Allocation)
- Single agent handles entire request
- Example: "Get customer information for ID 5"
- Flow: User → Router → Customer Data Agent → Response

### 2. Sequential (Task Chaining)
- Multiple agents work in sequence
- Example: "I'm customer 12345 and need help upgrading"
- Flow: User → Router → Data Agent → Support Agent → Router (synthesis)

### 3. Negotiation (Complex Coordination)
- Agents collaborate on complex tasks
- Example: "Show all active customers with open tickets"
- Flow: User → Router → Data Agent + Support Agent → Router (synthesis)

## State Management

The system uses `AgentState` dataclass (in `a2a_system.py`) to maintain:
- Query and customer ID
- Detected intents and priority
- Agent sequence
- Collected data from each agent
- Coordination logs
- Final response

**Important**: State is passed between agents to maintain context and enable traceability.

## Common Development Tasks

### Adding a New Agent

1. Create new agent class in `agents/` directory
2. Implement `process()` method that takes `AgentState`
3. Register agent in `A2ACoordinationSystem.__init__()` in `a2a_system.py`
4. Update router logic in `agents/router_agent.py` to route to new agent

### Adding a New MCP Tool

1. Add tool function to `MCPTools` class in `mcp_server/mcp_tools.py`
2. Register tool in `get_available_tools()` method
3. Update agent that will use the tool (usually `customer_data_agent.py`)

### Adding a New Test Scenario

1. Open `main.py`
2. Add scenario to `test_scenarios` list in `run_all_scenarios()`
3. Follow existing format with description and query

### Modifying Intent Detection

Intent detection is in `agents/router_agent.py`, `_detect_intents()` method:
- Uses keyword matching on query text
- Returns list of intent strings
- Add new intents by extending the keyword patterns

## Database Schema

### customers table
```sql
id              INTEGER PRIMARY KEY
name            TEXT NOT NULL
email           TEXT
phone           TEXT
status          TEXT ('active' or 'disabled')
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### tickets table
```sql
id              INTEGER PRIMARY KEY
customer_id     INTEGER (FK to customers.id)
issue           TEXT NOT NULL
status          TEXT ('open', 'in_progress', 'resolved')
priority        TEXT ('low', 'medium', 'high')
created_at      DATETIME
```

## Setup & Running

### Initial Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database with sample data
python database_setup.py
```

### Running the Application
```bash
python main.py
# Option 1: Run all test scenarios
# Option 2: Interactive mode
# Option 3: Exit
```

### Testing
```bash
# Automated testing with predefined scenarios
python main.py  # Choose option 1

# Custom queries in interactive mode
python main.py  # Choose option 2
```

## Logging

- Coordination logs are written to `logs/` directory
- Filename format: `a2a_coordination_YYYYMMDD_HHMMSS.log`
- Logs include timestamps, phases, agent actions, and results
- Use logs to debug coordination flow and agent behavior

## Code Style Guidelines

- **Agent methods**: Should accept `AgentState` and return modified state
- **MCP tools**: Should return dict with `success`, `data`, and optional `error`
- **Logging**: Use `self._log()` method in agents for consistency
- **Error handling**: Always validate inputs and handle exceptions gracefully

## Extension Ideas

- Add more specialist agents (billing, technical support, etc.)
- Integrate actual LLM for better intent detection
- Add REST API endpoints for external access
- Implement authentication and authorization
- Add real-time messaging (WebSocket support)
- Extend with more complex negotiation patterns
- Add agent performance metrics and monitoring

## Debugging Tips

1. **Check coordination logs**: Review `logs/` directory for execution flow
2. **State inspection**: Add print statements to see state between agents
3. **Database verification**: Use SQLite browser to check data
4. **Intent detection**: Print detected intents in router agent
5. **MCP tool calls**: Check return values from MCP tools

## Important Notes

- System is rule-based, not LLM-powered (for educational purposes)
- State management is inspired by LangGraph but implemented from scratch
- Database is SQLite for portability (no external DB server needed)
- All agents are synchronous (no async/await complexity)
- Sample data includes 15 customers and 25 tickets

## Architecture Principles

1. **Separation of Concerns**: Each agent has specific responsibilities
2. **State-Based Communication**: Agents communicate via shared state object
3. **Modularity**: Easy to add new agents or tools
4. **Traceability**: Full logging of coordination flow
5. **Simplicity**: No external dependencies beyond standard Python libraries

## When Working on This Project

**Before modifying code:**
- Understand which agent(s) are involved
- Check if MCP tools need changes
- Review existing coordination flow
- Consider impact on state management

**After making changes:**
- Test with all 5 scenarios
- Check coordination logs for correctness
- Verify database state if applicable
- Test in interactive mode with custom queries

## Contact & Resources

- **Project Type**: Educational multi-agent system
- **Documentation**: See README.md for detailed information
- **Code Examples**: See CONCLUSION.md for implementation notes
- **Notebook**: Colab_Notebook_Agentic_Patterns_with_LangGraph_Dr_Fouad_Bousetouane.ipynb for background

---

**For AI Assistants**: This file is designed to help you understand the project structure and provide better assistance. Always refer to this file when working on this codebase to understand the architecture, patterns, and best practices.
