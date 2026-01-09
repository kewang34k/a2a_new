# Multi-Agent Customer Support System
## A2A Coordination with MCP Integration

A sophisticated multi-agent system demonstrating Agent-to-Agent (A2A) coordination patterns for customer support operations. This system implements three specialized agents working together to handle complex customer queries through intelligent routing and coordination.

---

## 🏗️ System Architecture

### Agents

#### 1. Router Agent (Orchestrator)
- **Role**: Orchestrates the entire multi-agent workflow
- **Responsibilities**:
  - Receives and analyzes customer queries
  - Detects intents and determines priority
  - Routes requests to appropriate specialist agents
  - Coordinates responses from multiple agents
  - Synthesizes final responses

#### 2. Customer Data Agent (Specialist)
- **Role**: Database operations specialist
- **Responsibilities**:
  - Accesses customer database via MCP tools
  - Retrieves customer information
  - Updates customer records
  - Handles data validation
  - Provides customer history and context

#### 3. Support Agent (Specialist)
- **Role**: Customer support specialist
- **Responsibilities**:
  - Handles general customer support queries
  - Creates and manages support tickets
  - Escalates complex issues
  - Analyzes query intent and priority
  - Generates contextual support responses

---

## 🔧 MCP Integration

### MCP Server Tools

The system implements a Model Context Protocol (MCP) server with the following tools:

1. **`get_customer(customer_id)`**
   - Retrieves customer information by ID
   - Returns: Customer details (name, email, phone, status, timestamps)

2. **`list_customers(status, limit)`**
   - Lists customers with optional filtering
   - Parameters: status ('active'/'disabled'), limit (default: 10)
   - Returns: Array of customer objects

3. **`update_customer(customer_id, data)`**
   - Updates customer information
   - Parameters: customer_id, data (fields to update)
   - Returns: Updated customer object

4. **`create_ticket(customer_id, issue, priority)`**
   - Creates a new support ticket
   - Parameters: customer_id, issue description, priority (low/medium/high)
   - Returns: Created ticket object

5. **`get_customer_history(customer_id)`**
   - Retrieves all tickets for a customer
   - Returns: Customer info + array of tickets

### Database Schema

**Customers Table:**
```sql
id              INTEGER PRIMARY KEY
name            TEXT NOT NULL
email           TEXT
phone           TEXT
status          TEXT ('active' or 'disabled')
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**Tickets Table:**
```sql
id              INTEGER PRIMARY KEY
customer_id     INTEGER (FK to customers.id)
issue           TEXT NOT NULL
status          TEXT ('open', 'in_progress', 'resolved')
priority        TEXT ('low', 'medium', 'high')
created_at      DATETIME
```

---

## 🤝 A2A Coordination Patterns

The system implements three coordination patterns:

### 1. Simple (Task Allocation)
- Single agent handles the entire request
- Direct routing without coordination
- Example: "Get customer information for ID 5"

**Flow:**
```
User Query → Router Agent → Customer Data Agent → Response
```

### 2. Sequential (Task Chaining)
- Multiple agents work in sequence
- Each agent's output becomes input for the next
- Example: "I'm customer 12345 and need help upgrading my account"

**Flow:**
```
User Query → Router Agent
          ↓
Customer Data Agent (fetch context)
          ↓
Support Agent (handle request with context)
          ↓
Router Agent (synthesize response)
```

### 3. Negotiation (Complex Coordination)
- Agents negotiate and collaborate on complex tasks
- Requires data gathering, analysis, and synthesis
- Example: "Show all active customers who have open tickets"

**Flow:**
```
User Query → Router Agent
          ↓
Customer Data Agent (gather customer data)
          ↓
Support Agent (gather ticket data)
          ↓
Router Agent (negotiate & synthesize results)
```

---

## 📋 Test Scenarios

The system successfully handles these scenarios:

### Scenario 1: Simple Query
**Query:** "Get customer information for ID 5"
- **Type:** Simple, single-agent
- **Agents:** Customer Data Agent
- **Flow:** Direct MCP call to retrieve customer

### Scenario 2: Coordinated Query
**Query:** "I'm customer 12345 and need help upgrading my account"
- **Type:** Sequential coordination
- **Agents:** Customer Data Agent → Support Agent
- **Flow:** Fetch customer context, then provide support response

### Scenario 3: Complex Query
**Query:** "Show me all active customers who have open tickets"
- **Type:** Negotiation/complex coordination
- **Agents:** Customer Data Agent + Support Agent
- **Flow:** Multi-step data gathering and synthesis

### Scenario 4: Escalation
**Query:** "I've been charged twice, please refund immediately!"
- **Type:** High-priority escalation
- **Agents:** Customer Data Agent → Support Agent (escalation)
- **Flow:** Detect urgency, create high-priority ticket, escalate

### Scenario 5: Multi-Intent
**Query:** "Update my email to new@email.com and show my ticket history"
- **Type:** Parallel task execution
- **Agents:** Customer Data Agent (multiple operations)
- **Flow:** Update email, retrieve history, coordinate response

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/a2a_new
   ```

2. **Create a Python virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**

   On Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

The system includes an automated database setup script:

```bash
python3 database_setup.py
```

This will:
- Create SQLite database (`support.db`)
- Create customers and tickets tables
- Insert 15 sample customers
- Insert 25 sample tickets with various priorities
- Create indexes for performance

---

## 💻 Usage

### Running the Main Application

```bash
python3 main.py
```

### Main Menu Options

1. **Run all 5 test scenarios**
   - Executes all predefined test scenarios
   - Displays coordination logs
   - Shows A2A interaction patterns
   - Option to export logs

2. **Interactive mode**
   - Enter custom queries
   - Real-time A2A coordination
   - See live agent interactions

3. **Exit**
   - Clean shutdown

### Example Session

```
MULTI-AGENT CUSTOMER SUPPORT SYSTEM
A2A Coordination Demo
================================================================================

Step 1: Setting up database...
✓ Database setup complete!

Step 2: Initializing A2A system...
✓ Router Agent initialized
✓ Customer Data Agent initialized
✓ Support Agent initialized
✓ A2A Coordination System ready

MAIN MENU
================================================================================

1. Run all 5 test scenarios
2. Interactive mode (custom queries)
3. Exit

Select option (1-3): 1
```

---

## 📁 Project Structure

```
a2a_new/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── database_setup.py                  # Database setup script
├── main.py                            # Main application entry point
├── a2a_system.py                      # A2A coordination system
│
├── mcp_server/                        # MCP Server implementation
│   ├── __init__.py
│   └── mcp_tools.py                   # MCP tools for database access
│
├── agents/                            # Agent implementations
│   ├── __init__.py
│   ├── router_agent.py                # Router/Orchestrator agent
│   ├── customer_data_agent.py         # Data specialist agent
│   └── support_agent.py               # Support specialist agent
│
├── logs/                              # Coordination logs (auto-created)
│   └── a2a_coordination_*.log
│
└── support.db                         # SQLite database (auto-created)
```

---

## 🔍 How It Works

### A2A Coordination Flow

1. **Analysis Phase** 🧠
   - Router Agent analyzes the query
   - Detects intents (billing, support, data retrieval, etc.)
   - Determines priority (low, medium, high)
   - Identifies required agents

2. **Routing Phase** 🔀
   - Router determines coordination strategy
   - Creates agent sequence
   - Plans execution steps

3. **Execution Phase** ⚙️
   - Agents execute in determined order
   - Data flows between agents
   - Each agent logs its actions
   - State is maintained throughout

4. **Synthesis Phase** 🎯
   - Router synthesizes final response
   - Combines results from all agents
   - Formats user-friendly output

### State Management

The system uses a shared `AgentState` object that tracks:
- Original query and customer ID
- Detected intents and priority
- Agent sequence and current agent
- Data collected by each agent
- Coordination logs
- Final response

This state-based approach ensures:
- ✅ No data loss between agent transfers
- ✅ Full traceability of decisions
- ✅ Easy debugging and logging
- ✅ Scalable to more agents

---

## 🧪 Testing

### Manual Testing

Run individual scenarios in interactive mode:

```bash
python3 main.py
# Select option 2 for interactive mode
```

Example queries:
- "Get customer 1 information"
- "List all active customers"
- "I need help with my account, customer ID 5"
- "Show high priority tickets"
- "I've been charged twice for subscription"

### Automated Testing

The main application includes 5 predefined test scenarios that can be run automatically:

```bash
python3 main.py
# Select option 1
```

---

## 📊 Output Examples

### Coordination Log Example

```
[12:34:56.789] ================================================================================
[12:34:56.790] [A2A-CoordinationSystem] Processing query: 'Get customer information for ID 5'
[12:34:56.791] ================================================================================

[12:34:56.792]
[12:34:56.793] 🧠 PHASE 1: ANALYZING QUERY
[12:34:56.794] [RouterAgent] Analyzing query: 'Get customer information for ID 5'
[12:34:56.795]   Intents detected: get_customer_data
[12:34:56.796]   Priority: medium
[12:34:56.797]   Coordination type: simple
[12:34:56.798]   Required agents: CustomerDataAgent

[12:34:56.799]
[12:34:56.800] 🔀 PHASE 2: ROUTING
[12:34:56.801]   Strategy: simple
[12:34:56.802]   Agent sequence: CustomerDataAgent

[12:34:56.803]
[12:34:56.804] ⚙️  PHASE 3: EXECUTING AGENT TASKS
[12:34:56.805]   Execution mode: SIMPLE (single agent)
[12:34:56.806]     → Calling CustomerDataAgent.get_customer()
[12:34:56.807]     ← Result: success=True

[12:34:56.808]
[12:34:56.809] 🎯 PHASE 4: SYNTHESIZING RESPONSE
[12:34:56.810]   Final response generated (156 characters)
```

### Response Example

```
Customer Information:
  Name: Charlie Brown
  Email: charlie.brown@email.com
  Phone: +1-555-0105
  Status: active

Ticket History (2 tickets):
  - Ticket #15: Feature request: dark mode (open, low priority)
  - Ticket #10: Billing question about invoice (resolved, low priority)
```

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **Multi-Agent Coordination**
   - State-based message passing
   - Agent-to-agent communication
   - Coordinated decision making

2. **MCP Integration**
   - Database access through tools
   - Structured data operations
   - Error handling and validation

3. **Software Architecture**
   - Separation of concerns
   - Modular agent design
   - Scalable system structure

4. **A2A Patterns**
   - Simple task allocation
   - Sequential coordination
   - Complex negotiation

---

## 🚧 Common Issues & Solutions

### Issue: Database not found
**Solution:** Run `python database_setup.py` first

### Issue: Import errors
**Solution:** Ensure virtual environment is activated and dependencies are installed

### Issue: Permission errors
**Solution:** Ensure write permissions for database and logs directories

---

## 📝 Implementation Notes

### Design Decisions

1. **No External LLM Required**
   - System uses rule-based intent detection
   - Pattern matching for query analysis
   - Suitable for educational purposes
   - Can be extended with LLM integration

2. **State-Based Coordination**
   - Uses dataclasses for state management
   - Inspired by LangGraph patterns
   - No external graph library required
   - Lightweight and fast

3. **Comprehensive Logging**
   - Timestamped coordination logs
   - Agent-level logging
   - Exportable for analysis
   - Helps understand A2A flow

### Extensibility

The system can be extended with:
- Additional specialist agents
- LLM integration for better intent detection
- More complex coordination patterns
- API endpoints for web integration
- Authentication and authorization
- Real-time messaging integration

---

## 📚 References

- **A2A Coordination Patterns**: State-based message passing inspired by LangGraph
- **MCP Protocol**: Model Context Protocol for tool integration
- **Database**: SQLite for lightweight, portable data storage

---

## 👥 Credits

**Course**: Multi-Agent Systems
**Assignment**: Multi-Agent Customer Support System with A2A Coordination
**Implementation**: State-based coordination with MCP integration

---

## 📄 License

This is an educational project for learning multi-agent systems and A2A coordination patterns.

---

## 🎯 Next Steps

1. Run the database setup: `python database_setup.py`
2. Start the application: `python main.py`
3. Try test scenarios (option 1)
4. Experiment in interactive mode (option 2)
5. Review coordination logs in `logs/` directory
6. Extend with your own agents and scenarios!

---

**Happy Learning! 🚀**
