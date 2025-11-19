"""
Support Agent - Specialist for customer support queries
Handles general customer support, escalation, and ticket management.
"""

from typing import Dict, Any, List
import json
from mcp_server.mcp_tools import get_mcp_tools


class SupportAgent:
    """Agent specialized in customer support operations."""

    def __init__(self, db_path: str = "support.db"):
        """Initialize Support Agent.

        Args:
            db_path: Path to database
        """
        self.mcp = get_mcp_tools(db_path)
        self.agent_name = "SupportAgent"

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a support request.

        Args:
            request: Request dictionary with 'action' and parameters

        Returns:
            Response dictionary with results
        """
        action = request.get("action")
        params = request.get("params", {})

        print(f"\n[{self.agent_name}] Processing action: {action}")
        print(f"[{self.agent_name}] Parameters: {json.dumps(params, indent=2)}")

        if action == "create_ticket":
            result = self._create_ticket(params)
        elif action == "analyze_query":
            result = self._analyze_query(params)
        elif action == "get_high_priority_tickets":
            result = self._get_high_priority_tickets(params)
        elif action == "handle_support_query":
            result = self._handle_support_query(params)
        elif action == "escalate_issue":
            result = self._escalate_issue(params)
        else:
            result = {
                "success": False,
                "error": f"Unknown action: {action}",
                "agent": self.agent_name
            }

        print(f"[{self.agent_name}] Result: {json.dumps(result, indent=2)[:200]}...")
        return result

    def _create_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new support ticket.

        Args:
            params: Must contain 'customer_id', 'issue', and optionally 'priority'

        Returns:
            Created ticket data
        """
        customer_id = params.get("customer_id")
        issue = params.get("issue")
        priority = params.get("priority", "medium")

        if not customer_id or not issue:
            return {
                "success": False,
                "error": "customer_id and issue are required",
                "agent": self.agent_name
            }

        result = self.mcp.create_ticket(customer_id, issue, priority)
        result["agent"] = self.agent_name
        return result

    def _analyze_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a customer query to determine intent and priority.

        Args:
            params: Must contain 'query'

        Returns:
            Analysis results
        """
        query = params.get("query", "").lower()

        # Detect intents
        intents = []
        priority = "medium"

        # Check for various intents
        if any(word in query for word in ["cancel", "refund", "charged twice", "billing"]):
            intents.append("billing")
            if "urgent" in query or "immediately" in query or "charged twice" in query:
                priority = "high"

        if any(word in query for word in ["upgrade", "downgrade", "plan", "subscription"]):
            intents.append("account_management")

        if any(word in query for word in ["help", "issue", "problem", "broken", "not working"]):
            intents.append("technical_support")

        if any(word in query for word in ["update", "change", "modify"]):
            intents.append("account_update")

        if any(word in query for word in ["status", "ticket", "history"]):
            intents.append("information_request")

        # Detect urgency
        urgent_keywords = ["urgent", "immediately", "asap", "critical", "emergency"]
        if any(word in query for word in urgent_keywords):
            priority = "high"

        # Determine if escalation needed
        needs_escalation = priority == "high" or "billing" in intents

        return {
            "success": True,
            "query": query,
            "intents": intents,
            "priority": priority,
            "needs_escalation": needs_escalation,
            "agent": self.agent_name
        }

    def _get_high_priority_tickets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get high priority tickets.

        Args:
            params: Optional 'customer_ids' to filter by specific customers

        Returns:
            List of high priority tickets
        """
        customer_ids = params.get("customer_ids")

        result = self.mcp.get_tickets_by_priority("high")

        # Filter by customer IDs if provided
        if customer_ids and result["success"]:
            tickets = result["tickets"]
            filtered = [t for t in tickets if t["customer_id"] in customer_ids]
            result["tickets"] = filtered
            result["count"] = len(filtered)
            result["filtered_by_customers"] = customer_ids

        result["agent"] = self.agent_name
        return result

    def _handle_support_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a general support query with customer context.

        Args:
            params: Must contain 'query' and optionally 'customer_context'

        Returns:
            Support response
        """
        query = params.get("query", "")
        customer_context = params.get("customer_context", "")

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
            response["response"] = self._generate_billing_response(query, customer_context)
        elif "account_management" in intents:
            response["response"] = self._generate_account_management_response(query, customer_context)
        elif "technical_support" in intents:
            response["response"] = self._generate_technical_support_response(query, customer_context)
        elif "account_update" in intents:
            response["response"] = self._generate_update_response(query, customer_context)
        elif "information_request" in intents:
            response["response"] = self._generate_info_response(query, customer_context)
        else:
            response["response"] = "I understand you need assistance. Could you please provide more details about your request?"

        return response

    def _escalate_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate an issue to higher priority handling.

        Args:
            params: Must contain 'customer_id', 'issue', and 'reason'

        Returns:
            Escalation result
        """
        customer_id = params.get("customer_id")
        issue = params.get("issue")
        reason = params.get("reason", "Customer request")

        # Create high priority ticket
        ticket_result = self.mcp.create_ticket(customer_id, issue, "high")

        if ticket_result["success"]:
            return {
                "success": True,
                "escalated": True,
                "ticket": ticket_result["ticket"],
                "escalation_reason": reason,
                "agent": self.agent_name,
                "message": f"Issue escalated to high priority. Ticket #{ticket_result['ticket']['id']} created."
            }
        else:
            return ticket_result

    def _generate_billing_response(self, query: str, context: str) -> str:
        """Generate billing-related response."""
        if "charged twice" in query.lower():
            return ("I understand you've been charged twice. This is a serious issue that needs immediate attention. "
                    "I'm escalating this to our billing team for priority review and refund processing. "
                    "You should receive a response within 24 hours.")
        elif "refund" in query.lower():
            return ("I can help you with the refund process. Let me escalate this to our billing department "
                    "who will review your account and process the refund if applicable.")
        else:
            return ("I can help with your billing question. Let me review your account details and provide assistance.")

    def _generate_account_management_response(self, query: str, context: str) -> str:
        """Generate account management response."""
        if "upgrade" in query.lower():
            return ("I'd be happy to help you upgrade your account. Let me pull up your current subscription details "
                    "and show you the available upgrade options that would best suit your needs.")
        elif "cancel" in query.lower():
            return ("I understand you're considering cancellation. Before we proceed, I'd like to understand if "
                    "there are any issues we can help resolve. If you'd still like to cancel, I can guide you through the process.")
        else:
            return ("I can help you manage your account. What specific changes would you like to make?")

    def _generate_technical_support_response(self, query: str, context: str) -> str:
        """Generate technical support response."""
        return ("I understand you're experiencing a technical issue. I'm here to help resolve this. "
                "Based on your account history, let me check if this is a known issue and provide you with solutions.")

    def _generate_update_response(self, query: str, context: str) -> str:
        """Generate account update response."""
        if "email" in query.lower():
            return "I can help you update your email address. For security purposes, I'll need to verify your identity first."
        else:
            return "I can help you update your account information. What would you like to change?"

    def _generate_info_response(self, query: str, context: str) -> str:
        """Generate information request response."""
        return "I can help you find that information. Let me retrieve the details you requested."

    def generate_support_summary(self, tickets: List[Dict]) -> str:
        """Generate a summary of support tickets.

        Args:
            tickets: List of ticket dictionaries

        Returns:
            Human-readable summary
        """
        if not tickets:
            return "No tickets found."

        summary = f"Found {len(tickets)} ticket(s):\n\n"

        for ticket in tickets:
            summary += f"Ticket #{ticket['id']} - {ticket['priority'].upper()} Priority\n"
            summary += f"  Customer: {ticket.get('customer_name', 'N/A')}\n"
            summary += f"  Status: {ticket['status']}\n"
            summary += f"  Issue: {ticket['issue']}\n"
            summary += f"  Created: {ticket['created_at']}\n"
            summary += "\n"

        return summary
