"""
Support Agent with LLM Integration - Enhanced Support Specialist
Uses OpenAI for generating intelligent, contextual support responses.
"""

from typing import Dict, Any, List
import json
from mcp_server.mcp_tools import get_mcp_tools
from config import get_config


class SupportAgentLLM:
    """LLM-powered agent specialized in customer support operations."""

    def __init__(self, db_path: str = "support.db", use_llm: bool = True):
        """Initialize Support Agent.

        Args:
            db_path: Path to database
            use_llm: Whether to use LLM for response generation (requires API key)
        """
        self.mcp = get_mcp_tools(db_path)
        self.agent_name = "SupportAgent"
        self.use_llm = use_llm
        self.config = get_config()

        if self.use_llm:
            try:
                self.client = self.config.get_openai_client()
            except (ValueError, ImportError) as e:
                print(f"⚠️ Warning: LLM not available ({e}). Using template-based responses.")
                self.use_llm = False

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
        """Create a new support ticket."""
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
        """Analyze a customer query using LLM or rules."""
        query = params.get("query", "").lower()

        if self.use_llm:
            return self._analyze_query_with_llm(query)
        else:
            return self._analyze_query_with_rules(query)

    def _analyze_query_with_llm(self, query: str) -> Dict[str, Any]:
        """Use LLM to analyze query intent and priority."""
        system_prompt = """You are a customer support analyst. Analyze the customer query and return a JSON object with:

- intents: array of detected intents (e.g., ["billing", "technical_support", "account_management"])
- priority: "low", "medium", or "high" based on urgency
- needs_escalation: boolean indicating if issue requires escalation
- sentiment: "positive", "neutral", "negative", or "frustrated"

Return ONLY valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}"}
                ],
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            analysis["success"] = True
            analysis["query"] = query
            analysis["agent"] = self.agent_name

            return analysis

        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}. Falling back to rule-based.")
            return self._analyze_query_with_rules(query)

    def _analyze_query_with_rules(self, query: str) -> Dict[str, Any]:
        """Fallback rule-based query analysis."""
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
        """Get high priority tickets."""
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
        """Handle a support query with LLM or template-based response."""
        query = params.get("query", "")
        customer_context = params.get("customer_context", "")

        # Analyze query first
        analysis = self._analyze_query({"query": query})

        if self.use_llm:
            response_text = self._generate_llm_response(query, customer_context, analysis)
        else:
            response_text = self._generate_template_response(query, customer_context, analysis)

        return {
            "success": True,
            "query": query,
            "analysis": analysis,
            "response": response_text,
            "agent": self.agent_name
        }

    def _generate_llm_response(self, query: str, customer_context: str, analysis: Dict[str, Any]) -> str:
        """Generate intelligent response using LLM."""
        system_prompt = """You are a professional customer support agent. Generate a helpful, empathetic, and professional response to the customer query.

Guidelines:
- Be friendly and professional
- Address the customer's concern directly
- Offer specific next steps when possible
- Show empathy for urgent or frustrated customers
- Keep responses concise (2-3 sentences)
- Do not make promises you can't keep
- If escalation is needed, acknowledge it

Context available:
- Customer information (if provided)
- Query analysis with intents and priority"""

        user_prompt = f"""Customer Query: {query}

Customer Context: {customer_context or "No customer context available"}

Analysis: {json.dumps(analysis, indent=2)}

Generate a professional support response:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ LLM response generation failed: {e}. Using template.")
            return self._generate_template_response(query, customer_context, analysis)

    def _generate_template_response(self, query: str, customer_context: str, analysis: Dict[str, Any]) -> str:
        """Generate template-based response as fallback."""
        intents = analysis.get("intents", [])

        if "billing" in intents:
            return ("I understand you have a billing question. Let me review your account and provide assistance. "
                    "I'll make sure we resolve this issue for you promptly.")
        elif "account_management" in intents:
            return ("I'd be happy to help you manage your account. What specific changes would you like to make? "
                    "I can guide you through the process.")
        elif "technical_support" in intents:
            return ("I'm here to help resolve this technical issue. Based on your account history, "
                    "let me check if this is a known issue and provide you with solutions.")
        else:
            return "I understand you need assistance. Could you please provide more details about your request?"

    def _escalate_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate an issue to higher priority handling."""
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
