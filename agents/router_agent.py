"""
Router Agent - Orchestrator for multi-agent coordination
Analyzes queries, routes to appropriate agents, and coordinates responses.
"""

from typing import Dict, Any, List, Optional
import json
import re


class RouterAgent:
    """Agent responsible for routing and coordinating between specialist agents."""

    def __init__(self):
        """Initialize Router Agent."""
        self.agent_name = "RouterAgent"

    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query intent and determine routing strategy.

        Args:
            query: User query string

        Returns:
            Intent analysis with routing recommendations
        """
        query_lower = query.lower()

        print(f"\n[{self.agent_name}] Analyzing query: '{query}'")

        # Extract customer ID if present
        customer_id = self._extract_customer_id(query)

        # Determine intents
        intents = []
        required_agents = []
        coordination_type = "simple"  # simple, sequential, parallel, negotiation

        # Data retrieval intents
        if any(word in query_lower for word in ["get customer", "customer information", "customer info", "customer id"]):
            intents.append("get_customer_data")
            required_agents.append("CustomerDataAgent")

        if any(word in query_lower for word in ["list customers", "show customers", "all customers"]):
            intents.append("list_customers")
            required_agents.append("CustomerDataAgent")

        if any(word in query_lower for word in ["update", "change", "modify"]):
            intents.append("update_data")
            required_agents.append("CustomerDataAgent")
            if customer_id:
                coordination_type = "sequential"

        if any(word in query_lower for word in ["ticket history", "show tickets", "my tickets", "ticket status"]):
            intents.append("get_history")
            required_agents.append("CustomerDataAgent")

        # Support intents
        if any(word in query_lower for word in ["help", "support", "issue", "problem", "need assistance"]):
            intents.append("support_request")
            required_agents.append("SupportAgent")
            if "CustomerDataAgent" in required_agents:
                coordination_type = "sequential"

        if any(word in query_lower for word in ["upgrade", "downgrade", "cancel", "subscription"]):
            intents.append("account_management")
            required_agents.extend(["CustomerDataAgent", "SupportAgent"])
            coordination_type = "sequential"

        if any(word in query_lower for word in ["billing", "charged", "refund", "payment"]):
            intents.append("billing_issue")
            required_agents.extend(["CustomerDataAgent", "SupportAgent"])
            coordination_type = "sequential"

        # Complex queries requiring multiple agents
        if any(phrase in query_lower for phrase in ["high priority", "premium customers", "active customers with open tickets", "active customers who have open"]):
            intents.append("complex_query")
            required_agents = ["CustomerDataAgent", "SupportAgent"]
            coordination_type = "negotiation"
        elif "open tickets" in query_lower and "customers" in query_lower:
            intents.append("complex_query")
            required_agents = ["CustomerDataAgent", "SupportAgent"]
            coordination_type = "negotiation"

        # Remove duplicates while preserving order
        required_agents = list(dict.fromkeys(required_agents))

        # Determine priority
        priority = "medium"
        if any(word in query_lower for word in ["urgent", "immediately", "asap", "critical"]):
            priority = "high"
        elif any(word in query_lower for word in ["charged twice", "can't login", "website down"]):
            priority = "high"

        result = {
            "query": query,
            "customer_id": customer_id,
            "intents": intents,
            "required_agents": required_agents,
            "coordination_type": coordination_type,
            "priority": priority,
            "agent": self.agent_name
        }

        print(f"[{self.agent_name}] Analysis: {json.dumps(result, indent=2)}")
        return result

    def _extract_customer_id(self, query: str) -> Optional[int]:
        """Extract customer ID from query.

        Args:
            query: Query string

        Returns:
            Customer ID if found, None otherwise
        """
        # Look for patterns like "customer 123", "ID 123", "customer ID 123"
        patterns = [
            r'customer\s+id\s+(\d+)',
            r'customer\s+(\d+)',
            r'id\s+(\d+)',
            r'#(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))

        return None

    def determine_routing(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the routing strategy based on intent analysis.

        Args:
            intent_analysis: Results from analyze_intent

        Returns:
            Routing plan with agent sequence and coordination strategy
        """
        required_agents = intent_analysis["required_agents"]
        coordination_type = intent_analysis["coordination_type"]
        intents = intent_analysis["intents"]

        routing_plan = {
            "strategy": coordination_type,
            "agent_sequence": [],
            "parallel_tasks": [],
            "requires_negotiation": False
        }

        if coordination_type == "simple":
            # Single agent handles the request
            routing_plan["agent_sequence"] = required_agents
            routing_plan["steps"] = [
                {
                    "agent": required_agents[0] if required_agents else "CustomerDataAgent",
                    "action": self._determine_action(intents),
                    "description": "Handle request directly"
                }
            ]

        elif coordination_type == "sequential":
            # Multiple agents work in sequence
            routing_plan["agent_sequence"] = required_agents

            steps = []
            if "CustomerDataAgent" in required_agents:
                steps.append({
                    "agent": "CustomerDataAgent",
                    "action": self._determine_data_action(intents),
                    "description": "Retrieve customer data"
                })

            if "SupportAgent" in required_agents:
                steps.append({
                    "agent": "SupportAgent",
                    "action": self._determine_support_action(intents),
                    "description": "Process support request with customer context"
                })

            routing_plan["steps"] = steps

        elif coordination_type == "parallel":
            # Multiple agents work in parallel (not currently used but available)
            routing_plan["agent_sequence"] = required_agents
            routing_plan["parallel_tasks"] = [
                {
                    "agent": agent,
                    "action": "parallel_task"
                }
                for agent in required_agents
            ]

        elif coordination_type == "negotiation":
            # Complex coordination requiring negotiation between agents
            routing_plan["requires_negotiation"] = True
            routing_plan["agent_sequence"] = required_agents
            routing_plan["steps"] = [
                {
                    "agent": "CustomerDataAgent",
                    "action": "gather_data",
                    "description": "Gather initial data"
                },
                {
                    "agent": "SupportAgent",
                    "action": "analyze_and_process",
                    "description": "Analyze data and generate insights"
                },
                {
                    "agent": "RouterAgent",
                    "action": "synthesize",
                    "description": "Synthesize final response"
                }
            ]

        print(f"\n[{self.agent_name}] Routing Plan: {json.dumps(routing_plan, indent=2)}")
        return routing_plan

    def _determine_action(self, intents: List[str]) -> str:
        """Determine specific action based on intents."""
        if "get_customer_data" in intents:
            return "get_customer"
        elif "list_customers" in intents:
            return "list_customers"
        elif "get_history" in intents:
            return "get_customer_history"
        elif "update_data" in intents:
            return "update_customer"
        elif "support_request" in intents:
            return "handle_support_query"
        else:
            return "analyze_query"

    def _determine_data_action(self, intents: List[str]) -> str:
        """Determine CustomerDataAgent action."""
        if "get_customer_data" in intents:
            return "get_customer"
        elif "list_customers" in intents:
            return "list_customers"
        elif "get_history" in intents:
            return "get_customer_history"
        elif "update_data" in intents:
            return "update_customer"
        elif "complex_query" in intents:
            return "get_active_customers_with_open_tickets"
        else:
            return "get_customer"

    def _determine_support_action(self, intents: List[str]) -> str:
        """Determine SupportAgent action."""
        if "billing_issue" in intents:
            return "escalate_issue"
        elif "support_request" in intents:
            return "handle_support_query"
        elif "complex_query" in intents:
            return "get_high_priority_tickets"
        else:
            return "analyze_query"

    def synthesize_response(self, agent_results: List[Dict[str, Any]], original_query: str) -> str:
        """Synthesize final response from multiple agent results.

        Args:
            agent_results: List of results from different agents
            original_query: Original user query

        Returns:
            Synthesized response string
        """
        print(f"\n[{self.agent_name}] Synthesizing response from {len(agent_results)} agent(s)")

        response_parts = []

        for result in agent_results:
            agent_name = result.get("agent", "Unknown")

            if agent_name == "CustomerDataAgent":
                response_parts.append(self._format_data_response(result))
            elif agent_name == "SupportAgent":
                response_parts.append(self._format_support_response(result))

        if response_parts:
            return "\n\n".join(response_parts)
        else:
            return "I was unable to process your request. Please try again or contact support."

    def _format_data_response(self, result: Dict[str, Any]) -> str:
        """Format CustomerDataAgent response."""
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error occurred')}"

        response = ""

        # Customer data
        if "customer" in result:
            customer = result["customer"]
            response += f"Customer Information:\n"
            response += f"  Name: {customer['name']}\n"
            response += f"  Email: {customer['email']}\n"
            response += f"  Phone: {customer['phone']}\n"
            response += f"  Status: {customer['status']}\n"

        # Customer list
        elif "customers" in result:
            customers = result["customers"]
            count = result.get("count", len(customers))
            response += f"Found {count} customer(s):\n"
            for customer in customers[:5]:  # Show first 5
                response += f"  - {customer['name']} (ID: {customer['id']}) - {customer['status']}\n"
            if count > 5:
                response += f"  ... and {count - 5} more\n"

        # Ticket history
        if "tickets" in result:
            tickets = result["tickets"]
            count = result.get("ticket_count", len(tickets))
            response += f"\nTicket History ({count} ticket(s)):\n"
            for ticket in tickets[:3]:  # Show first 3
                response += f"  - Ticket #{ticket['id']}: {ticket['issue']} ({ticket['status']}, {ticket['priority']} priority)\n"
            if count > 3:
                response += f"  ... and {count - 3} more\n"

        return response

    def _format_support_response(self, result: Dict[str, Any]) -> str:
        """Format SupportAgent response."""
        if not result.get("success"):
            return f"Support Error: {result.get('error', 'Unknown error occurred')}"

        response = ""

        # Support response
        if "response" in result:
            response += f"Support Response:\n{result['response']}\n"

        # Ticket creation
        if "ticket" in result:
            ticket = result["ticket"]
            response += f"\nTicket #{ticket['id']} created successfully.\n"
            response += f"  Priority: {ticket['priority']}\n"
            response += f"  Status: {ticket['status']}\n"

        # Escalation
        if result.get("escalated"):
            response += f"\n⚠️ Issue escalated: {result.get('message', '')}\n"

        return response
