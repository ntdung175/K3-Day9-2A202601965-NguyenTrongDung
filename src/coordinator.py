"""
Coordinator Agent Module — Multi-Agent Orchestrator for K3
Member 1 (Leader / Policy Architect) Ownership
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.data_engine import DataEngine
from src.policy_agent import PolicyAgent

class CoordinatorAgent:
    def __init__(self, data_loader=None, verifier_agent=None):
        self.data_loader = data_loader if data_loader is not None else DataEngine()
        self.policy_agent = PolicyAgent()
        self.verifier_agent = verifier_agent

    def create_handoff_packet(self, case_id: str, order_id: str, receiver: str, intent: str) -> Dict[str, Any]:
        """
        Build a structured A2A Handoff Packet.
        """
        return {
            "case_id": case_id,
            "claimed_order_id": order_id,
            "sender": "CoordinatorAgent",
            "receiver": receiver,
            "intent": intent,
            "facts_found": {},
            "evidence_ids": [],
            "missing_facts": [],
            "next_recommendation": ""
        }

    def process_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate ticket processing:
        1. Extract case_id and claimed_order_id
        2. Query domain facts via data_loader (or mock data if loader pending)
        3. Evaluate via PolicyAgent
        4. Pass through VerifierAgent if attached
        """
        case_id = ticket_data.get("case_id", "")
        customer_req = ticket_data.get("customer_request", {})
        order_id = customer_req.get("claimed_order_id", "")

        # 1. Gather Domain Facts
        facts = {
            "case_id": case_id,
            "order_id": order_id
        }

        if self.data_loader:
            domain_facts = self.data_loader.get_order_facts(order_id)
            facts.update(domain_facts)

        # 2. Evaluate Policy
        assessment_output = self.policy_agent.evaluate(facts)
        assessment_output["case_id"] = case_id

        # 3. Verify Output
        if self.verifier_agent:
            assessment_output = self.verifier_agent.verify_and_clean(assessment_output, facts)

        return assessment_output

    def process_file(self, input_path: Path) -> Dict[str, Any]:
        with open(input_path, "r", encoding="utf-8") as f:
            ticket_data = json.load(f)
        return self.process_ticket(ticket_data)
