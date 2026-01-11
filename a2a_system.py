"""
A2A (Agent-to-Agent) Coordination System
Multi-agent system using message passing and state management for customer support.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime

from agents.router_agent import RouterAgent
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
from utils.query_parsing import extract_email


@dataclass
class AgentState:
    """State shared between agents during coordination."""

    # Input
    query: str = ""
    customer_id: Optional[int] = None

    # Intent analysis
    intents: List[str] = field(default_factory=list)
    priority: str = "medium"
    coordination_type: str = "simple"

    # Routing
    required_agents: List[str] = field(default_factory=list)
    current_agent: str = "RouterAgent"
    agent_sequence: List[str] = field(default_factory=list)

    # Data collection
    customer_data: Optional[Dict[str, Any]] = None
    support_data: Optional[Dict[str, Any]] = None
    agent_results: List[Dict[str, Any]] = field(default_factory=list)

    # Output
    final_response: str = ""
    phase: str = "analyze"  # analyze, route, execute, synthesize, done

    # Logging
    coordination_log: List[str] = field(default_factory=list)

    def log(self, message: str):
        """Add message to coordination log."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.coordination_log.append(log_entry)
        print(log_entry)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "query": self.query,
            "customer_id": self.customer_id,
            "intents": self.intents,
            "priority": self.priority,
            "coordination_type": self.coordination_type,
            "required_agents": self.required_agents,
            "current_agent": self.current_agent,
            "phase": self.phase,
            "final_response": self.final_response
        }


class A2ACoordinationSystem:
    """Agent-to-Agent coordination system using state-based message passing."""

    def __init__(self, db_path: str = "support.db"):
        """Initialize A2A system with all agents.

        Args:
            db_path: Path to database
        """
        self.router = RouterAgent()
        self.data_agent = CustomerDataAgent(db_path)
        self.support_agent = SupportAgent(db_path)

        self.system_name = "A2A-CoordinationSystem"

    def process_query(self, query: str, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """Process a user query through the multi-agent system.

        Args:
            query: User query string
            customer_id: Optional customer ID

        Returns:
            Final response with coordination details
        """
        # Initialize state
        state = AgentState(
            query=query,
            customer_id=customer_id
        )

        state.log(f"\n{'='*80}")
        state.log(f"[{self.system_name}] Processing query: '{query}'")
        state.log(f"{'='*80}\n")

        # Execute coordination workflow
        state = self._analyze_phase(state)
        state = self._route_phase(state)
        state = self._execute_phase(state)
        state = self._synthesize_phase(state)

        state.phase = "done"
        state.log(f"\n[{self.system_name}] Query processing complete")
        state.log(f"{'='*80}\n")

        return {
            "query": state.query,
            "response": state.final_response,
            "coordination_log": state.coordination_log,
            "state": state.to_dict()
        }

    def _analyze_phase(self, state: AgentState) -> AgentState:
        """Phase 1: Analyze query intent.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("\n🧠 PHASE 1: ANALYZING QUERY")
        state.phase = "analyze"

        # Router analyzes intent
        analysis = self.router.analyze_intent(state.query)

        # Update state with analysis
        state.intents = analysis["intents"]
        state.priority = analysis["priority"]
        state.coordination_type = analysis["coordination_type"]
        state.required_agents = analysis["required_agents"]

        if analysis["customer_id"] and not state.customer_id:
            state.customer_id = analysis["customer_id"]

        state.log(f"  Intents detected: {', '.join(state.intents)}")
        state.log(f"  Priority: {state.priority}")
        state.log(f"  Coordination type: {state.coordination_type}")
        state.log(f"  Required agents: {', '.join(state.required_agents)}")

        return state

    def _route_phase(self, state: AgentState) -> AgentState:
        """Phase 2: Determine routing strategy.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("\n🔀 PHASE 2: ROUTING")
        state.phase = "route"

        # Router determines routing plan
        routing_plan = self.router.determine_routing({
            "intents": state.intents,
            "required_agents": state.required_agents,
            "coordination_type": state.coordination_type
        })

        state.agent_sequence = routing_plan["agent_sequence"]

        state.log(f"  Strategy: {routing_plan['strategy']}")
        state.log(f"  Agent sequence: {' → '.join(state.agent_sequence)}")

        if "steps" in routing_plan:
            state.log("  Execution steps:")
            for i, step in enumerate(routing_plan["steps"], 1):
                state.log(f"    {i}. {step['agent']}: {step['description']}")

        return state

    def _execute_phase(self, state: AgentState) -> AgentState:
        """Phase 3: Execute agent tasks.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("\n⚙️  PHASE 3: EXECUTING AGENT TASKS")
        state.phase = "execute"

        if state.coordination_type == "simple":
            state = self._execute_simple(state)
        elif state.coordination_type == "sequential":
            state = self._execute_sequential(state)
        elif state.coordination_type == "negotiation":
            state = self._execute_negotiation(state)
        else:
            state.log(f"  Unknown coordination type: {state.coordination_type}")

        return state

    def _execute_simple(self, state: AgentState) -> AgentState:
        """Execute simple single-agent task.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("  Execution mode: SIMPLE (single agent)")

        if not state.required_agents:
            state.log("  Warning: No agents required")
            return state

        agent_name = state.required_agents[0]
        state.current_agent = agent_name

        # Determine action and parameters
        action = self._determine_action(state)
        params = self._build_params(state, action)

        # Execute
        result = self._call_agent(agent_name, action, params, state)
        state.agent_results.append(result)

        return state

    def _execute_sequential(self, state: AgentState) -> AgentState:
        """Execute sequential multi-agent coordination.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("  Execution mode: SEQUENTIAL (agent chaining)")

        for i, agent_name in enumerate(state.agent_sequence, 1):
            state.log(f"\n  Step {i}/{len(state.agent_sequence)}: {agent_name}")
            state.current_agent = agent_name

            # Determine action based on agent and current state
            action = self._determine_action_for_agent(agent_name, state)
            params = self._build_params(state, action)

            # Execute
            result = self._call_agent(agent_name, action, params, state)
            state.agent_results.append(result)

            # Update state with results for next agent
            if agent_name == "CustomerDataAgent":
                state.customer_data = result
            elif agent_name == "SupportAgent":
                state.support_data = result

        return state

    def _execute_negotiation(self, state: AgentState) -> AgentState:
        """Execute negotiation-based multi-agent coordination.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("  Execution mode: NEGOTIATION (complex coordination)")

        # Step 1: CustomerDataAgent gathers data
        state.log("\n  Negotiation Step 1: Data gathering")
        state.current_agent = "CustomerDataAgent"

        action = self._determine_action_for_agent("CustomerDataAgent", state)
        params = self._build_params(state, action)
        result = self._call_agent("CustomerDataAgent", action, params, state)
        state.agent_results.append(result)
        state.customer_data = result

        # Step 2: SupportAgent analyzes
        state.log("\n  Negotiation Step 2: Analysis and processing")
        state.current_agent = "SupportAgent"

        action = self._determine_action_for_agent("SupportAgent", state)
        params = self._build_params(state, action)

        # Add customer data context if available
        if state.customer_data and state.customer_data.get("success"):
            if "customers" in state.customer_data:
                customer_ids = [c["id"] for c in state.customer_data["customers"]]
                params["customer_ids"] = customer_ids

        result = self._call_agent("SupportAgent", action, params, state)
        state.agent_results.append(result)
        state.support_data = result

        # Step 3: Router synthesizes (happens in synthesize phase)
        state.log("\n  Negotiation Step 3: Synthesis (will occur in next phase)")

        return state

    def _synthesize_phase(self, state: AgentState) -> AgentState:
        """Phase 4: Synthesize final response.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        state.log("\n🎯 PHASE 4: SYNTHESIZING RESPONSE")
        state.phase = "synthesize"

        # Router synthesizes final response from all agent results
        state.final_response = self.router.synthesize_response(
            state.agent_results,
            state.query
        )

        state.log(f"  Final response generated ({len(state.final_response)} characters)")

        return state

    def _call_agent(self, agent_name: str, action: str, params: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Call an agent with specified action and parameters.

        Args:
            agent_name: Name of agent to call
            action: Action to perform
            params: Parameters for action
            state: Current state

        Returns:
            Agent result
        """
        state.log(f"    → Calling {agent_name}.{action}()")
        state.log(f"    → Parameters: {json.dumps(params, indent=6)}")

        request = {
            "action": action,
            "params": params
        }

        if agent_name == "CustomerDataAgent":
            result = self.data_agent.process_request(request)
        elif agent_name == "SupportAgent":
            result = self.support_agent.process_request(request)
        else:
            result = {
                "success": False,
                "error": f"Unknown agent: {agent_name}"
            }

        state.log(f"    ← Result: success={result.get('success', False)}")

        return result

    def _determine_action(self, state: AgentState) -> str:
        """Determine action based on state."""
        if "get_customer_data" in state.intents:
            return "get_customer"
        elif "list_customers" in state.intents:
            return "list_customers"
        elif "get_history" in state.intents:
            return "get_customer_history"
        elif "update_data" in state.intents:
            return "update_customer"
        elif "support_request" in state.intents:
            return "handle_support_query"
        else:
            return "get_customer"

    def _determine_action_for_agent(self, agent_name: str, state: AgentState) -> str:
        """Determine specific action for an agent based on context."""
        if agent_name == "CustomerDataAgent":
            if "get_customer_data" in state.intents or "support_request" in state.intents:
                return "get_customer"
            elif "list_customers" in state.intents:
                return "list_customers"
            elif "get_history" in state.intents:
                return "get_customer_history"
            elif "update_data" in state.intents:
                return "update_customer"
            elif "complex_query" in state.intents:
                return "get_active_customers_with_open_tickets"
            else:
                return "get_customer"

        elif agent_name == "SupportAgent":
            if "billing_issue" in state.intents:
                return "escalate_issue"
            elif "support_request" in state.intents or "account_management" in state.intents:
                return "handle_support_query"
            elif "complex_query" in state.intents:
                return "get_high_priority_tickets"
            else:
                return "analyze_query"

        return "analyze_query"

    def _build_params(self, state: AgentState, action: str) -> Dict[str, Any]:
        """Build parameters for an action based on current state."""
        params = {}

        # Add customer_id if available
        if state.customer_id:
            params["customer_id"] = state.customer_id

        # Add query for analysis/support actions
        if action in ["analyze_query", "handle_support_query"]:
            params["query"] = state.query

        # Add customer context if we have it
        if action == "handle_support_query" and state.customer_data:
            if "customer" in state.customer_data:
                customer = state.customer_data["customer"]
                params["customer_context"] = f"Customer: {customer['name']} ({customer['status']})"

        # Add specific parameters based on intent
        if "update_data" in state.intents:
            # Extract update data from query (simplified - in production, use LLM)
            if "email" in state.query.lower():
                email = extract_email(state.query)
                if email:
                    params["data"] = {"email": email}

        if "billing_issue" in state.intents:
            params["issue"] = state.query
            params["reason"] = "Billing issue - requires immediate attention"

        # For list operations
        if action == "list_customers":
            if "active" in state.query.lower():
                params["status"] = "active"
            elif "disabled" in state.query.lower():
                params["status"] = "disabled"

        return params

    def get_coordination_summary(self, result: Dict[str, Any]) -> str:
        """Get a summary of the coordination process.

        Args:
            result: Result from process_query

        Returns:
            Human-readable summary
        """
        summary = "\n" + "="*80 + "\n"
        summary += "A2A COORDINATION SUMMARY\n"
        summary += "="*80 + "\n\n"

        state = result["state"]
        summary += f"Query: {result['query']}\n"
        summary += f"Intents: {', '.join(state['intents'])}\n"
        summary += f"Priority: {state['priority']}\n"
        summary += f"Coordination Type: {state['coordination_type']}\n"
        summary += f"Agents Involved: {', '.join(state['required_agents'])}\n\n"

        summary += "RESPONSE:\n"
        summary += "-"*80 + "\n"
        summary += result['response'] + "\n"
        summary += "-"*80 + "\n\n"

        summary += "COORDINATION LOG:\n"
        summary += "-"*80 + "\n"
        for log_entry in result['coordination_log']:
            summary += log_entry + "\n"
        summary += "="*80 + "\n"

        return summary
