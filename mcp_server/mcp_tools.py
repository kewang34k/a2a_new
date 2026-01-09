"""
MCP Server Tools for Customer Support System
Provides database access tools for customer and ticket management.
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class MCPTools:
    """MCP Server tools for customer support database operations."""

    def __init__(self, db_path: str = "support.db"):
        """Initialize MCP tools with database connection.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_connection()

    def _ensure_connection(self):
        """Ensure database connection is active."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def _dict_from_row(self, row) -> Dict:
        """Convert SQLite row to dictionary."""
        return {key: row[key] for key in row.keys()}

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get customer by ID.

        Args:
            customer_id: Customer ID

        Returns:
            Customer information as dictionary
        """
        try:
            self.cursor.execute(
                "SELECT * FROM customers WHERE id = ?",
                (customer_id,)
            )
            row = self.cursor.fetchone()

            if row:
                return {
                    "success": True,
                    "customer": self._dict_from_row(row)
                }
            else:
                return {
                    "success": False,
                    "error": f"Customer with ID {customer_id} not found"
                }
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def list_customers(self, status: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """List customers with optional filtering.

        Args:
            status: Filter by status ('active' or 'disabled')
            limit: Maximum number of customers to return

        Returns:
            List of customers
        """
        try:
            if status:
                self.cursor.execute(
                    "SELECT * FROM customers WHERE status = ? LIMIT ?",
                    (status, limit)
                )
            else:
                self.cursor.execute(
                    "SELECT * FROM customers LIMIT ?",
                    (limit,)
                )

            rows = self.cursor.fetchall()
            customers = [self._dict_from_row(row) for row in rows]

            return {
                "success": True,
                "count": len(customers),
                "customers": customers
            }
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information.

        Args:
            customer_id: Customer ID
            data: Dictionary with fields to update (name, email, phone, status)

        Returns:
            Updated customer information
        """
        try:
            # First check if customer exists
            existing = self.get_customer(customer_id)
            if not existing["success"]:
                return existing

            # Build update query
            allowed_fields = ["name", "email", "phone", "status"]
            update_fields = []
            values = []

            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    values.append(data[field])

            if not update_fields:
                return {
                    "success": False,
                    "error": "No valid fields to update"
                }

            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())

            # Add customer_id for WHERE clause
            values.append(customer_id)

            query = f"UPDATE customers SET {', '.join(update_fields)} WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()

            # Return updated customer
            return self.get_customer(customer_id)

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def create_ticket(self, customer_id: int, issue: str, priority: str = "medium") -> Dict[str, Any]:
        """Create a new support ticket.

        Args:
            customer_id: Customer ID
            issue: Issue description
            priority: Ticket priority ('low', 'medium', 'high')

        Returns:
            Created ticket information
        """
        try:
            # Verify customer exists
            customer = self.get_customer(customer_id)
            if not customer["success"]:
                return {
                    "success": False,
                    "error": f"Customer with ID {customer_id} not found"
                }

            # Validate priority
            if priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "error": f"Invalid priority: {priority}. Must be 'low', 'medium', or 'high'"
                }

            # Insert ticket
            self.cursor.execute(
                """
                INSERT INTO tickets (customer_id, issue, status, priority)
                VALUES (?, ?, 'open', ?)
                """,
                (customer_id, issue, priority)
            )
            self.conn.commit()

            ticket_id = self.cursor.lastrowid

            # Return created ticket
            self.cursor.execute(
                "SELECT * FROM tickets WHERE id = ?",
                (ticket_id,)
            )
            row = self.cursor.fetchone()

            return {
                "success": True,
                "ticket": self._dict_from_row(row)
            }

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """Get all tickets for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            Customer information and ticket history
        """
        try:
            # Get customer info
            customer = self.get_customer(customer_id)
            if not customer["success"]:
                return customer

            # Get all tickets for customer
            self.cursor.execute(
                """
                SELECT * FROM tickets
                WHERE customer_id = ?
                ORDER BY created_at DESC
                """,
                (customer_id,)
            )

            rows = self.cursor.fetchall()
            tickets = [self._dict_from_row(row) for row in rows]

            return {
                "success": True,
                "customer": customer["customer"],
                "ticket_count": len(tickets),
                "tickets": tickets
            }

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def get_tickets_by_priority(self, priority: str, status: Optional[str] = None) -> Dict[str, Any]:
        """Get tickets filtered by priority and optionally status.

        Args:
            priority: Ticket priority ('low', 'medium', 'high')
            status: Optional status filter ('open', 'in_progress', 'resolved')

        Returns:
            List of matching tickets with customer information
        """
        try:
            if status:
                query = """
                    SELECT t.*, c.name as customer_name, c.email, c.status as customer_status
                    FROM tickets t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE t.priority = ? AND t.status = ?
                    ORDER BY t.created_at DESC
                """
                self.cursor.execute(query, (priority, status))
            else:
                query = """
                    SELECT t.*, c.name as customer_name, c.email, c.status as customer_status
                    FROM tickets t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE t.priority = ?
                    ORDER BY t.created_at DESC
                """
                self.cursor.execute(query, (priority,))

            rows = self.cursor.fetchall()
            tickets = [self._dict_from_row(row) for row in rows]

            return {
                "success": True,
                "count": len(tickets),
                "tickets": tickets
            }

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def get_active_customers_with_open_tickets(self) -> Dict[str, Any]:
        """Get all active customers who have open tickets.

        Returns:
            List of customers with their open tickets
        """
        try:
            query = """
                SELECT DISTINCT c.*,
                       COUNT(t.id) as open_ticket_count
                FROM customers c
                JOIN tickets t ON c.id = t.customer_id
                WHERE c.status = 'active' AND t.status = 'open'
                GROUP BY c.id
                ORDER BY open_ticket_count DESC, c.name
            """
            self.cursor.execute(query)

            rows = self.cursor.fetchall()
            customers = []

            for row in rows:
                customer_data = self._dict_from_row(row)
                customer_id = customer_data['id']

                # Get open tickets for this customer
                self.cursor.execute(
                    """
                    SELECT * FROM tickets
                    WHERE customer_id = ? AND status = 'open'
                    ORDER BY priority DESC, created_at DESC
                    """,
                    (customer_id,)
                )
                ticket_rows = self.cursor.fetchall()
                customer_data['open_tickets'] = [self._dict_from_row(tr) for tr in ticket_rows]

                customers.append(customer_data)

            return {
                "success": True,
                "count": len(customers),
                "customers": customers
            }

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Cache instances by db_path (so different DBs don't share connections)
_mcp_instances: Dict[str, MCPTools] = {}

def get_mcp_tools(db_path: str = "support.db") -> MCPTools:
    """Get or create an MCPTools instance for a given db_path.

    Args:
        db_path: Path to database

    Returns:
        MCPTools instance
    """
    instance = _mcp_instances.get(db_path)
    if instance is None:
        instance = MCPTools(db_path)
        _mcp_instances[db_path] = instance
    return instance
