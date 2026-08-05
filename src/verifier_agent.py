"""Hard-gate verifier for K3 JSON outputs and grounded evidence."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class VerificationError(ValueError):
    pass


class VerifierAgent:
    VALID_ISSUES = {"canceled_order_paid", "unavailable_order_paid", "late_delivery_seller", "late_delivery_logistics", "valid_split_payment", "unsupported_late_claim"}
    VALID_STATUSES = {"action_required", "no_action"}
    VALID_POLICY_CODES = {"SELLER_HANDOFF_AFTER_LIMIT", "CARRIER_DELIVERED_AFTER_ESTIMATE", "ORDER_CANCELED_AFTER_PAYMENT", "ORDER_UNAVAILABLE_AFTER_PAYMENT", "MULTIPLE_PAYMENTS_RECONCILED", "DELIVERY_WITHIN_ESTIMATE"}
    EVIDENCE_PATTERN = re.compile(r"^(order:[^:]+|item:[^:]+:[^:]+|payment:[^:]+:[^:]+|seller:[^:]+|policy:[A-Z_]+)$")

    def verify_and_clean(self, output_json: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(output_json)
        result["case_id"] = str(result.get("case_id") or facts.get("case_id") or "")
        assessment = dict(result.get("assessment") or {})
        assessment["confidence"] = round(max(0.0, min(1.0, self._number(assessment.get("confidence"), 0.0))), 2)
        result["assessment"] = assessment
        entities = dict(result.get("affected_entities") or {})
        for name in ("order_ids", "item_ids", "seller_ids", "payment_ids"):
            entities[name] = self._string_list(entities.get(name), 5)
        result["affected_entities"] = entities
        rca = dict(result.get("root_cause_analysis") or {})
        rca["ranked_causes"] = list(rca.get("ranked_causes") or [])[:3]
        rca["responsible_parties"] = list(rca.get("responsible_parties") or [])[:3]
        result["root_cause_analysis"] = rca
        result["evidence_ids"] = self._string_list(result.get("evidence_ids"), 10)
        result["resolution_actions"] = self._string_list(result.get("resolution_actions"), 5)
        financial = dict(result.get("financial_resolution") or {})
        financial["currency"] = "BRL"
        for name in ("item_total_brl", "freight_total_brl", "payment_total_brl", "recommended_refund_brl"):
            financial[name] = round(self._number(financial.get(name), 0.0), 2)
        result["financial_resolution"] = financial
        errors = self.validate(result, facts)
        if errors:
            raise VerificationError("; ".join(errors))
        return result

    def validate(self, result: Dict[str, Any], facts: Dict[str, Any] | None = None) -> List[str]:
        errors: List[str] = []
        required = {"case_id", "assessment", "affected_entities", "root_cause_analysis", "evidence_ids", "financial_resolution", "resolution_actions"}
        errors.extend(f"missing field: {field}" for field in sorted(required - result.keys()))
        assessment = result.get("assessment", {})
        if assessment.get("primary_issue") not in self.VALID_ISSUES:
            errors.append("invalid primary_issue")
        if assessment.get("case_status") not in self.VALID_STATUSES:
            errors.append("invalid case_status")
        confidence = assessment.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            errors.append("confidence must be in [0, 1]")
        entities = result.get("affected_entities", {})
        for name in ("order_ids", "item_ids", "seller_ids", "payment_ids"):
            if not isinstance(entities.get(name), list) or len(entities.get(name, [])) > 5:
                errors.append(f"{name} must contain at most 5 IDs")
        rca = result.get("root_cause_analysis", {})
        for name, limit in (("ranked_causes", 3), ("responsible_parties", 3)):
            if not isinstance(rca.get(name), list) or len(rca.get(name, [])) > limit:
                errors.append(f"{name} must contain at most {limit} entries")
        evidence = result.get("evidence_ids")
        if not isinstance(evidence, list) or len(evidence) > 10:
            errors.append("evidence_ids must contain at most 10 entries")
        elif any(not isinstance(item, str) or not self.EVIDENCE_PATTERN.fullmatch(item) for item in evidence):
            errors.append("invalid evidence ID format")
        if not isinstance(result.get("resolution_actions"), list) or len(result.get("resolution_actions", [])) > 5:
            errors.append("resolution_actions must contain at most 5 entries")
        financial = result.get("financial_resolution", {})
        if financial.get("currency") != "BRL": errors.append("currency must be BRL")
        for name in ("item_total_brl", "freight_total_brl", "payment_total_brl", "recommended_refund_brl"):
            if not isinstance(financial.get(name), (int, float)) or isinstance(financial.get(name), bool): errors.append(f"{name} must be numeric")
        if facts:
            self._validate_grounding(result, facts, errors)
        return errors

    def _validate_grounding(self, result: Dict[str, Any], facts: Dict[str, Any], errors: List[str]) -> None:
        entities = result.get("affected_entities", {})
        order_id = facts.get("order_id")
        if facts.get("case_id") and result.get("case_id") != facts["case_id"]: errors.append("case_id does not match input")
        if order_id and order_id not in entities.get("order_ids", []): errors.append("claimed order missing from affected_entities.order_ids")
        allowed = set()
        if order_id: allowed.add(f"order:{order_id}")
        allowed.update(f"item:{item_id}" for item_id in facts.get("item_ids", []))
        allowed.update(f"payment:{payment_id}" for payment_id in facts.get("payment_ids", []))
        allowed.update(f"seller:{seller_id}" for seller_id in facts.get("seller_ids", []))
        allowed.update(f"policy:{code}" for code in self.VALID_POLICY_CODES)
        invalid = set(result.get("evidence_ids", [])) - allowed
        if invalid: errors.append("evidence IDs not grounded in order facts: " + ", ".join(sorted(invalid)))
        for key in ("item_total_brl", "freight_total_brl", "payment_total_brl"):
            if key in facts and abs(float(result["financial_resolution"].get(key, 0)) - float(facts[key])) > 0.01:
                errors.append(f"{key} does not match data facts")

    @staticmethod
    def _number(value: Any, default: float) -> float:
        try: return float(value)
        except (TypeError, ValueError): return default

    @staticmethod
    def _string_list(value: Any, limit: int) -> List[str]:
        return [item for item in (value or []) if isinstance(item, str)][:limit]
