# Claude Context: Multi-Agent Customer Support System

## Project Overview

This is a **Multi-Agent Customer Support System** demonstrating Agent-to-Agent (A2A) coordination patterns with Model Context Protocol (MCP) integration. The system is an educational implementation showing how multiple specialized AI agents can coordinate to handle complex customer support scenarios.

**Key Purpose**: Demonstrate three A2A coordination patterns:
1. **Simple** (Task Allocation): Single agent handles request
2. **Sequential** (Task Chaining): Multiple agents work in sequence
3. **Negotiation** (Complex Coordination): Agents collaborate on complex tasks

## System Architecture

### Core Components

1. **Router Agent** (`agents/router_agent.py`)
   - Orchestrator for the entire system
   - Analyzes queries for intent and priority
   - Routes requests to appropriate specialist agents
   - Synthesizes final responses from multiple agent outputs

2. **Customer Data Agent** (`agents/customer_data_agent.py`)
   - Database operations specialist
   - Uses MCP tools to access SQLite database
   - Handles customer data retrieval, updates, and validation

3. **Support Agent** (`agents/support_agent.py`)
   - Customer support specialist
   - Creates and manages support tickets
   - Handles escalations and priority detection
   - Generates contextual support responses

4. **A2A Coordination System** (`a2a_system.py`)
   - Manages agent communication and state
   - Implements coordination patterns
   - Provides comprehensive logging
   - State-based message passing (inspired by LangGraph)

5. **MCP Server** (`mcp_server/mcp_tools.py`)
   - Implements Model Context Protocol tools
   - Provides database access layer
   - Tools: get_customer, list_customers, update_customer, create_ticket, get_customer_history

### Database Schema

**SQLite Database**: `support.db`

Tables:
- `customers`: id, name, email, phone, status, created_at, updated_at
- `tickets`: id, customer_id, issue, status, priority, created_at

## Key Design Decisions

1. **No External LLM Required**
   - Uses rule-based intent detection via pattern matching
   - Suitable for educational purposes
   - Can be extended with actual LLM integration (Anthropic Claude, OpenAI, etc.)

2. **State-Based Coordination**
   - Uses Python dataclasses for state management
   - `AgentState` object tracks: query, intents, priority, agent sequence, collected data, logs
   - Ensures traceability and prevents data loss between agent transfers

3. **Comprehensive Logging**
   - Timestamped coordination logs in `logs/` directory
   - Four-phase logging: Analysis → Routing → Execution → Synthesis
   - Helps understand A2A interaction patterns

4. **Educational Focus**
   - Clear separation of concerns
   - Well-commented code
   - Multiple test scenarios included
   - Interactive mode for experimentation

## Important Files

### Core Application
- `main.py` - Entry point, handles UI and test scenarios
- `database_setup.py` - Creates database and sample data
- `requirements.txt` - Python dependencies (anthropic-mcp)

### Agents Directory
- `router_agent.py` - Orchestrator (350+ lines)
- `customer_data_agent.py` - Database specialist (200+ lines)
- `support_agent.py` - Support specialist (250+ lines)

### System Files
- `a2a_system.py` - Coordination logic, state management (400+ lines)
- `mcp_server/mcp_tools.py` - MCP tools implementation (250+ lines)

## Development Guidelines

### Code Conventions
- **Python 3.8+** required
- Type hints used where appropriate
- Dataclasses for state objects
- Comprehensive error handling with try/except blocks
- Logging at multiple levels (INFO, DEBUG)

### Adding New Agents
1. Create new file in `agents/` directory
2. Inherit from base agent pattern (if one exists) or follow existing structure
3. Implement required methods: `process()`, `_detect_intent()`, etc.
4. Register agent in `a2a_system.py`
5. Update router logic to include new agent in routing decisions

### Adding New MCP Tools
1. Add function to `mcp_server/mcp_tools.py`
2. Include tool metadata (name, description, parameters)
3. Implement database logic
4. Add error handling
5. Update relevant agent to use new tool

### Testing Strategy
- 5 predefined test scenarios cover all coordination patterns
- Interactive mode for custom queries
- Coordination logs for debugging
- Sample data includes 15 customers and 25 tickets

## Common Development Tasks

### Running the System
```bash
# Setup (first time)
python database_setup.py
source venv/bin/activate  # if using venv
pip install -r requirements.txt

# Run application
python main.py
```

### Database Operations
- Database auto-created by `database_setup.py`
- Located at `./support.db`
- Use SQLite CLI or browser for manual inspection
- Reset database: delete `support.db` and run setup again

### Viewing Logs
- Coordination logs in `logs/a2a_coordination_*.log`
- Timestamped filenames for each session
- Export option available in main menu

### Debugging A2A Flow
1. Check coordination logs for agent sequence
2. Verify state object passes correctly between agents
3. Check intent detection in router agent
4. Validate MCP tool responses
5. Review phase transitions (Analysis → Routing → Execution → Synthesis)

## Known Considerations

### Limitations
- **No actual LLM**: Intent detection is pattern-based, not intelligent
- **No authentication**: All operations are unauthenticated
- **Single database**: SQLite is not suitable for production
- **No concurrent requests**: Processes one query at a time
- **Limited error recovery**: Basic error handling only

### Extensibility Opportunities
- Integrate with Anthropic Claude API for real LLM-based routing
- Add authentication and authorization layer
- Implement REST API for web integration
- Add more specialist agents (billing, technical, escalation)
- Implement async processing for concurrent requests
- Add caching layer for frequently accessed data
- Implement more sophisticated negotiation patterns

## Testing Scenarios

### Scenario Coverage
1. **Simple**: "Get customer information for ID 5"
2. **Sequential**: "I'm customer 12345 and need help upgrading"
3. **Complex**: "Show all active customers with open tickets"
4. **Escalation**: "I've been charged twice, refund immediately!"
5. **Multi-Intent**: "Update my email and show my ticket history"

### Expected Behavior
- Router correctly identifies intent and priority
- Appropriate agents are selected
- Data flows correctly between agents
- Final response is coherent and complete
- All actions logged with timestamps

## Dependencies

### Required
- `anthropic-mcp` - MCP protocol implementation
- Python 3.8+ standard library (sqlite3, datetime, dataclasses, typing)

### Optional (for future extensions)
- `anthropic` - For Claude API integration
- `openai` - For OpenAI integration
- `fastapi` - For REST API
- `uvicorn` - For API server

## Environment Setup

### Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Database Location
- Default: `./support.db` in project root
- Configurable via database path in MCP tools

## File Organization

```
a2a_new/
├── agents/              # Agent implementations
├── mcp_server/          # MCP tools and database access
├── logs/                # Coordination logs (auto-created)
├── main.py              # Entry point
├── a2a_system.py        # Coordination logic
├── database_setup.py    # DB initialization
├── support.db           # SQLite database (auto-created)
├── requirements.txt     # Dependencies
├── README.md            # User documentation
└── CLAUDE.MD            # This file (Claude context)
```

## Working with This Project

### When Making Changes
1. **Read first**: Review relevant agent code before modifying
2. **Test incrementally**: Run test scenarios after each change
3. **Check logs**: Review coordination logs to verify A2A flow
4. **Update docs**: Keep README.md and CLAUDE.MD in sync
5. **Maintain patterns**: Follow existing code structure and conventions

### When Debugging
1. Check coordination logs first
2. Verify database state with SQLite browser
3. Add debug logging to specific agents
4. Test with simple scenarios first
5. Use interactive mode for experimentation

### When Extending
1. Follow existing agent structure
2. Update router logic for new capabilities
3. Add test scenarios for new features
4. Document new A2A patterns
5. Update both README and CLAUDE.MD

## Important Notes for Claude

- This is an **educational project**, not production code
- Focus on **clarity and demonstration** over optimization
- **State management** is critical - maintain AgentState integrity
- **Logging** is essential for understanding A2A flow
- The system is **synchronous and single-threaded** by design
- **No external API calls** - everything runs locally
- Pattern matching for intents is **intentionally simple** for educational purposes

## Quick Reference

### Starting Points for Common Tasks
- Adding agent: `agents/` + `a2a_system.py`
- Adding MCP tool: `mcp_server/mcp_tools.py`
- Modifying routing: `agents/router_agent.py`
- Changing coordination: `a2a_system.py`
- Adding test scenario: `main.py`

### Key Classes
- `AgentState`: State object passed between agents
- `RouterAgent`: Orchestration and routing
- `CustomerDataAgent`: Database operations
- `SupportAgent`: Support logic
- `A2ACoordinationSystem`: Coordination engine

---

**Last Updated**: 2026-01-06
**Project Type**: Educational Multi-Agent System
**Status**: Complete and functional
