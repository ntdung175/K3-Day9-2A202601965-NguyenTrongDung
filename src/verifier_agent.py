"""Hard-gate verifier: schema limits, financial values, and grounded evidence."""
import re
from typing import Any, Dict, List

class VerificationError(ValueError): pass

class VerifierAgent:
    issues = {"canceled_order_paid", "unavailable_order_paid", "late_delivery_seller", "late_delivery_logistics", "valid_split_payment", "unsupported_late_claim"}
    codes = {"SELLER_HANDOFF_AFTER_LIMIT", "CARRIER_DELIVERED_AFTER_ESTIMATE", "ORDER_CANCELED_AFTER_PAYMENT", "ORDER_UNAVAILABLE_AFTER_PAYMENT", "MULTIPLE_PAYMENTS_RECONCILED", "DELIVERY_WITHIN_ESTIMATE"}
    pattern = re.compile(r"^(order:[^:]+|item:[^:]+:[^:]+|payment:[^:]+:[^:]+|seller:[^:]+|policy:[A-Z_]+)$")
    def verify_and_clean(self, result: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(result); result["case_id"] = result.get("case_id") or facts.get("case_id", "")
        assessment = dict(result.get("assessment") or {}); assessment["confidence"] = round(max(0, min(1, float(assessment.get("confidence", 0)))), 2); result["assessment"] = assessment
        entities = dict(result.get("affected_entities") or {})
        for key in ("order_ids", "item_ids", "seller_ids", "payment_ids"): entities[key] = [v for v in entities.get(key, []) if isinstance(v, str)][:5]
        result["affected_entities"] = entities
        rca = dict(result.get("root_cause_analysis") or {}); rca["ranked_causes"] = list(rca.get("ranked_causes") or [])[:3]; rca["responsible_parties"] = list(rca.get("responsible_parties") or [])[:3]; result["root_cause_analysis"] = rca
        result["evidence_ids"] = [v for v in result.get("evidence_ids", []) if isinstance(v, str)][:10]; result["resolution_actions"] = [v for v in result.get("resolution_actions", []) if isinstance(v, str)][:5]
        fin = dict(result.get("financial_resolution") or {}); fin["currency"] = "BRL"
        for key in ("item_total_brl", "freight_total_brl", "payment_total_brl", "recommended_refund_brl"):
            try: fin[key] = round(float(fin.get(key, 0)), 2)
            except (TypeError, ValueError): fin[key] = 0.0
        result["financial_resolution"] = fin
        errors = self.validate(result, facts)
        if errors: raise VerificationError("; ".join(errors))
        return result
    def validate(self, result: Dict[str, Any], facts: Dict[str, Any]) -> List[str]:
        errors=[]; a=result.get("assessment", {}); e=result.get("affected_entities", {}); r=result.get("root_cause_analysis", {}); evidence=result.get("evidence_ids", []); fin=result.get("financial_resolution", {})
        if a.get("primary_issue") not in self.issues: errors.append("invalid primary_issue")
        if a.get("case_status") not in {"action_required", "no_action"}: errors.append("invalid case_status")
        if not isinstance(a.get("confidence"), (int,float)) or not 0 <= a["confidence"] <= 1: errors.append("invalid confidence")
        for key in ("order_ids","item_ids","seller_ids","payment_ids"):
            if not isinstance(e.get(key), list) or len(e[key]) > 5: errors.append(f"invalid {key}")
        if len(evidence)>10 or any(not self.pattern.fullmatch(x) for x in evidence): errors.append("invalid evidence IDs")
        if len(r.get("ranked_causes", []))>3 or len(r.get("responsible_parties", []))>3 or len(result.get("resolution_actions", []))>5: errors.append("array limit exceeded")
        if fin.get("currency") != "BRL": errors.append("invalid currency")
        order=facts.get("order_id"); allowed={f"order:{order}"} if order else set(); allowed |= {f"item:{x}" for x in facts.get("item_ids", [])}; allowed |= {f"payment:{x}" for x in facts.get("payment_ids", [])}; allowed |= {f"seller:{x}" for x in facts.get("seller_ids", [])}; allowed |= {f"policy:{x}" for x in self.codes}
        if order and order not in e.get("order_ids", []): errors.append("missing claimed order")
        if set(evidence)-allowed: errors.append("ungrounded evidence")
        for key in ("item_total_brl","freight_total_brl","payment_total_brl"):
            if key in facts and abs(float(fin.get(key, 0))-float(facts[key]))>0.01: errors.append(f"mismatched {key}")
        return errors
