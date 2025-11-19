"""
Customer Data Agent - Specialist for database operations
Handles all customer data retrieval and updates via MCP tools.
"""

from typing import Dict, Any, Optional
import json
from mcp_server.mcp_tools import get_mcp_tools


class CustomerDataAgent:
    """Agent specialized in customer data operations."""

    def __init__(self, db_path: str = "support.db"):
        """Initialize Customer Data Agent.

        Args:
            db_path: Path to database
        """
        self.mcp = get_mcp_tools(db_path)
        self.agent_name = "CustomerDataAgent"

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a customer data request.

        Args:
            request: Request dictionary with 'action' and parameters

        Returns:
            Response dictionary with results
        """
        action = request.get("action")
        params = request.get("params", {})

        print(f"\n[{self.agent_name}] Processing action: {action}")
        print(f"[{self.agent_name}] Parameters: {json.dumps(params, indent=2)}")

        if action == "get_customer":
            result = self._get_customer(params)
        elif action == "list_customers":
            result = self._list_customers(params)
        elif action == "update_customer":
            result = self._update_customer(params)
        elif action == "get_customer_history":
            result = self._get_customer_history(params)
        elif action == "get_active_customers_with_open_tickets":
            result = self._get_active_customers_with_open_tickets()
        else:
            result = {
                "success": False,
                "error": f"Unknown action: {action}",
                "agent": self.agent_name
            }

        print(f"[{self.agent_name}] Result: {json.dumps(result, indent=2)[:200]}...")
        return result

    def _get_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer by ID.

        Args:
            params: Must contain 'customer_id'

        Returns:
            Customer data
        """
        customer_id = params.get("customer_id")
        if not customer_id:
            return {
                "success": False,
                "error": "customer_id is required",
                "agent": self.agent_name
            }

        result = self.mcp.get_customer(customer_id)
        result["agent"] = self.agent_name
        return result

    def _list_customers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List customers with optional filters.

        Args:
            params: Optional 'status' and 'limit'

        Returns:
            List of customers
        """
        status = params.get("status")
        limit = params.get("limit", 10)

        result = self.mcp.list_customers(status=status, limit=limit)
        result["agent"] = self.agent_name
        return result

    def _update_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information.

        Args:
            params: Must contain 'customer_id' and 'data'

        Returns:
            Updated customer data
        """
        customer_id = params.get("customer_id")
        data = params.get("data", {})

        if not customer_id:
            return {
                "success": False,
                "error": "customer_id is required",
                "agent": self.agent_name
            }

        result = self.mcp.update_customer(customer_id, data)
        result["agent"] = self.agent_name
        return result

    def _get_customer_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer ticket history.

        Args:
            params: Must contain 'customer_id'

        Returns:
            Customer history data
        """
        customer_id = params.get("customer_id")
        if not customer_id:
            return {
                "success": False,
                "error": "customer_id is required",
                "agent": self.agent_name
            }

        result = self.mcp.get_customer_history(customer_id)
        result["agent"] = self.agent_name
        return result

    def _get_active_customers_with_open_tickets(self) -> Dict[str, Any]:
        """Get all active customers with open tickets.

        Returns:
            List of customers with open tickets
        """
        result = self.mcp.get_active_customers_with_open_tickets()
        result["agent"] = self.agent_name
        return result

    def analyze_customer_context(self, customer_id: int) -> str:
        """Analyze customer context for support agents.

        Args:
            customer_id: Customer ID

        Returns:
            Human-readable customer context summary
        """
        # Get customer info
        customer_result = self.mcp.get_customer(customer_id)
        if not customer_result["success"]:
            return f"Customer {customer_id} not found."

        customer = customer_result["customer"]

        # Get history
        history_result = self.mcp.get_customer_history(customer_id)
        tickets = history_result.get("tickets", [])

        # Build context summary
        context = f"Customer: {customer['name']} (ID: {customer['id']})\n"
        context += f"Email: {customer['email']}\n"
        context += f"Phone: {customer['phone']}\n"
        context += f"Status: {customer['status']}\n"
        context += f"Account created: {customer['created_at']}\n\n"

        if tickets:
            context += f"Ticket History ({len(tickets)} tickets):\n"
            for ticket in tickets[:5]:  # Show last 5 tickets
                context += f"  - Ticket #{ticket['id']} [{ticket['status']}] ({ticket['priority']} priority)\n"
                context += f"    Issue: {ticket['issue']}\n"
        else:
            context += "No previous tickets.\n"

        return context
