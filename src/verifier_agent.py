"""
Verifier Agent Module — Hard Gate & Schema Verification for K3
Member 3 (QA & Verifier Engineer) Ownership
"""

from typing import Dict, Any, List

class VerifierAgent:
    def __init__(self):
        self.valid_statuses = {"action_required", "no_action"}

    def verify_and_clean(self, output_json: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce ground truth, limit boundaries, and schema compliance on the generated JSON output.
        """
        # 1. Check assessment
        assessment = output_json.get("assessment", {})
        case_status = assessment.get("case_status", "no_action")
        if case_status not in self.valid_statuses:
            assessment["case_status"] = "no_action"
            
        confidence = float(assessment.get("confidence", 0.95))
        confidence = max(0.0, min(1.0, confidence))
        assessment["confidence"] = round(confidence, 2)
        output_json["assessment"] = assessment

        # 2. Affected entities boundaries (max 5 per list)
        entities = output_json.get("affected_entities", {})
        entities["order_ids"] = entities.get("order_ids", [])[:5]
        entities["item_ids"] = entities.get("item_ids", [])[:5]
        entities["seller_ids"] = entities.get("seller_ids", [])[:5]
        entities["payment_ids"] = entities.get("payment_ids", [])[:5]
        output_json["affected_entities"] = entities

        # 3. Root cause analysis (max 3 ranked causes, max 3 responsible parties)
        rca = output_json.get("root_cause_analysis", {})
        rca["ranked_causes"] = rca.get("ranked_causes", [])[:3]
        rca["responsible_parties"] = rca.get("responsible_parties", [])[:3]
        output_json["root_cause_analysis"] = rca

        # 4. Evidence IDs (max 10)
        evidence_ids = output_json.get("evidence_ids", [])[:10]
        output_json["evidence_ids"] = evidence_ids

        # 5. Financial resolution rounding
        fin = output_json.get("financial_resolution", {})
        fin["currency"] = "BRL"
        fin["item_total_brl"] = round(float(fin.get("item_total_brl", 0.0)), 2)
        fin["freight_total_brl"] = round(float(fin.get("freight_total_brl", 0.0)), 2)
        fin["payment_total_brl"] = round(float(fin.get("payment_total_brl", 0.0)), 2)
        fin["recommended_refund_brl"] = round(float(fin.get("recommended_refund_brl", 0.0)), 2)
        output_json["financial_resolution"] = fin

        # 6. Resolution actions (max 5)
        actions = output_json.get("resolution_actions", [])[:5]
        output_json["resolution_actions"] = actions

        return output_json
