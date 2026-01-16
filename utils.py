"""
Utility functions for the Multi-Agent Customer Support System
Common helper functions used across the system.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import json


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string.
    
    Args:
        dt: Datetime object (defaults to now)
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text.
    
    Args:
        text: Text to search
        
    Returns:
        Email address if found, None otherwise
    """
    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_customer_id(text: str) -> Optional[int]:
    """Extract customer ID from text.
    
    Args:
        text: Text to search
        
    Returns:
        Customer ID if found, None otherwise
    """
    patterns = [
        r'customer\s+id\s+(\d+)',
        r'customer\s+(\d+)',
        r'id\s+(\d+)',
        r'#(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    
    return None


def format_customer_info(customer: Dict[str, Any]) -> str:
    """Format customer information for display.
    
    Args:
        customer: Customer dictionary
        
    Returns:
        Formatted customer info string
    """
    lines = [
        f"Customer Information:",
        f"  Name: {customer.get('name', 'N/A')}",
        f"  Email: {customer.get('email', 'N/A')}",
        f"  Phone: {customer.get('phone', 'N/A')}",
        f"  Status: {customer.get('status', 'N/A')}",
    ]
    
    if 'created_at' in customer:
        lines.append(f"  Created: {customer['created_at']}")
    if 'updated_at' in customer:
        lines.append(f"  Updated: {customer['updated_at']}")
    
    return "\n".join(lines)


def format_ticket_info(ticket: Dict[str, Any]) -> str:
    """Format ticket information for display.
    
    Args:
        ticket: Ticket dictionary
        
    Returns:
        Formatted ticket info string
    """
    lines = [
        f"Ticket #{ticket.get('id', 'N/A')}:",
        f"  Issue: {ticket.get('issue', 'N/A')}",
        f"  Status: {ticket.get('status', 'N/A')}",
        f"  Priority: {ticket.get('priority', 'N/A')}",
    ]
    
    if 'created_at' in ticket:
        lines.append(f"  Created: {ticket['created_at']}")
    
    return "\n".join(lines)


def format_ticket_list(tickets: List[Dict[str, Any]], limit: int = 5) -> str:
    """Format list of tickets for display.
    
    Args:
        tickets: List of ticket dictionaries
        limit: Maximum number of tickets to display
        
    Returns:
        Formatted ticket list string
    """
    if not tickets:
        return "No tickets found."
    
    count = len(tickets)
    display_tickets = tickets[:limit]
    
    lines = [f"Ticket History ({count} ticket(s)):"]
    
    for ticket in display_tickets:
        lines.append(
            f"  - Ticket #{ticket['id']}: {ticket.get('issue', 'N/A')} "
            f"({ticket.get('status', 'N/A')}, {ticket.get('priority', 'N/A')} priority)"
        )
    
    if count > limit:
        lines.append(f"  ... and {count - limit} more")
    
    return "\n".join(lines)


def format_customer_list(customers: List[Dict[str, Any]], limit: int = 5) -> str:
    """Format list of customers for display.
    
    Args:
        customers: List of customer dictionaries
        limit: Maximum number of customers to display
        
    Returns:
        Formatted customer list string
    """
    if not customers:
        return "No customers found."
    
    count = len(customers)
    display_customers = customers[:limit]
    
    lines = [f"Found {count} customer(s):"]
    
    for customer in display_customers:
        lines.append(
            f"  - {customer.get('name', 'N/A')} (ID: {customer.get('id', 'N/A')}) - "
            f"{customer.get('status', 'N/A')}"
        )
    
    if count > limit:
        lines.append(f"  ... and {count - limit} more")
    
    return "\n".join(lines)


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic validation).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid format, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Remove null bytes and trim whitespace
    sanitized = text.replace('\x00', '').strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def create_response(success: bool, data: Optional[Dict[str, Any]] = None, 
                   error: Optional[str] = None, agent: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized agent response.
    
    Args:
        success: Whether the operation succeeded
        data: Response data dictionary
        error: Error message if failed
        agent: Agent name that generated the response
        
    Returns:
        Standardized response dictionary
    """
    response = {
        "success": success,
        "agent": agent
    }
    
    if success and data:
        response.update(data)
    elif not success:
        response["error"] = error or "Unknown error occurred"
    
    return response


def merge_agent_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge results from multiple agents.
    
    Args:
        results: List of agent result dictionaries
        
    Returns:
        Merged result dictionary
    """
    merged = {
        "success": True,
        "agents": [],
        "data": {}
    }
    
    for result in results:
        agent_name = result.get("agent", "Unknown")
        merged["agents"].append(agent_name)
        
        if not result.get("success", False):
            merged["success"] = False
            if "error" not in merged["data"]:
                merged["data"]["errors"] = []
            merged["data"]["errors"].append({
                "agent": agent_name,
                "error": result.get("error", "Unknown error")
            })
        else:
            # Merge successful results
            for key, value in result.items():
                if key not in ["success", "agent"]:
                    if key in merged["data"]:
                        # Handle duplicate keys
                        if isinstance(merged["data"][key], list):
                            merged["data"][key].append(value)
                        else:
                            merged["data"][key] = [merged["data"][key], value]
                    else:
                        merged["data"][key] = value
    
    return merged


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON string.
    
    Args:
        data: Data to format
        indent: JSON indentation level
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def detect_priority(text: str) -> str:
    """Detect priority level from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Priority level: 'high', 'medium', or 'low'
    """
    text_lower = text.lower()
    
    high_priority_keywords = [
        "urgent", "immediately", "asap", "critical", "emergency",
        "charged twice", "can't login", "website down", "refund"
    ]
    
    low_priority_keywords = [
        "whenever", "no rush", "low priority", "not urgent"
    ]
    
    if any(keyword in text_lower for keyword in high_priority_keywords):
        return "high"
    elif any(keyword in text_lower for keyword in low_priority_keywords):
        return "low"
    else:
        return "medium"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def create_separator(char: str = "=", length: int = 80) -> str:
    """Create a separator line.
    
    Args:
        char: Character to use
        length: Length of separator
        
    Returns:
        Separator string
    """
    return char * length


def format_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    """Format data as a simple table.
    
    Args:
        data: List of dictionaries to format
        headers: Optional list of header names (uses dict keys if not provided)
        
    Returns:
        Formatted table string
    """
    if not data:
        return "No data to display."
    
    if headers is None:
        headers = list(data[0].keys())
    
    # Calculate column widths
    col_widths = {header: len(str(header)) for header in headers}
    for row in data:
        for header in headers:
            value = str(row.get(header, ""))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Build table
    lines = []
    
    # Header
    header_line = " | ".join(str(header).ljust(col_widths[header]) for header in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Rows
    for row in data:
        row_line = " | ".join(str(row.get(header, "")).ljust(col_widths[header]) 
                             for header in headers)
        lines.append(row_line)
    
    return "\n".join(lines)
