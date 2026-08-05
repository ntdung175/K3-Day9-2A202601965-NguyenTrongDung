"""
Policy Agent Module — EC_POLICY_V1 Evaluator for K3
Member 1 (Leader / Policy Architect) Ownership
"""

from datetime import datetime
from typing import Dict, Any, List


def _parse_timestamp(value):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None

    for date_format in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            continue
    return None


def _is_after(left, right):
    left_dt = _parse_timestamp(left)
    right_dt = _parse_timestamp(right)
    return bool(left_dt and right_dt and left_dt > right_dt)


def _is_on_or_before(left, right):
    left_dt = _parse_timestamp(left)
    right_dt = _parse_timestamp(right)
    return bool(left_dt and right_dt and left_dt <= right_dt)

class PolicyAgent:
    def __init__(self):
        self.policy_version = "EC_POLICY_V1"

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate aggregated facts from Domain Agents using EC_POLICY_V1 decision matrix.
        """
        order_id = facts.get("order_id", "")
        order_status = facts.get("order_status", "")
        
        item_total = round(float(facts.get("item_total_brl", 0.0)), 2)
        freight_total = round(float(facts.get("freight_total_brl", 0.0)), 2)
        payment_total = round(float(facts.get("payment_total_brl", 0.0)), 2)
        payment_count = int(facts.get("payment_count", 0))
        payment_reconciled = facts.get("payment_reconciled")
        if payment_reconciled is None:
            payment_reconciled = abs(payment_total - (item_total + freight_total)) <= 0.10

        delivered_customer_date = facts.get("order_delivered_customer_date", "")
        estimated_delivery_date = facts.get("order_estimated_delivery_date", "")
        delivered_carrier_date = facts.get("order_delivered_carrier_date", "")
        shipping_limit_date = facts.get("shipping_limit_date", "")
        delivery_late = _is_after(delivered_customer_date, estimated_delivery_date)
        delivery_on_time = _is_on_or_before(delivered_customer_date, estimated_delivery_date)
        seller_handoff_late = _is_after(delivered_carrier_date, shipping_limit_date)
        
        seller_ids = facts.get("seller_ids", [])
        seller_id = seller_ids[0] if seller_ids else "UNKNOWN_SELLER"

        item_ids = facts.get("item_ids", [])
        payment_ids = facts.get("payment_ids", [])
        
        # Primary Issue Evaluation Order
        primary_issue = None
        case_status = "no_action"
        # The six official policy branches are deterministic and fully grounded
        # in CSV facts. Use maximum confidence once a branch is proven; the
        # unknown/fallback branch below remains deliberately lower confidence.
        confidence = 1.0
        root_cause_code = ""
        responsible_parties = []
        recommended_refund_brl = 0.0
        resolution_actions = []

        # 1. canceled_order_paid
        if order_status == "canceled" and payment_total > 0:
            primary_issue = "canceled_order_paid"
            case_status = "action_required"
            root_cause_code = "ORDER_CANCELED_AFTER_PAYMENT"
            responsible_parties = [{"party_type": "platform", "party_id": "OLIST_PLATFORM"}]
            recommended_refund_brl = payment_total
            resolution_actions = ["issue_full_refund"]

        # 2. unavailable_order_paid
        elif order_status == "unavailable" and payment_total > 0:
            primary_issue = "unavailable_order_paid"
            case_status = "action_required"
            root_cause_code = "ORDER_UNAVAILABLE_AFTER_PAYMENT"
            responsible_parties = [{"party_type": "platform", "party_id": "OLIST_PLATFORM"}]
            recommended_refund_brl = payment_total
            resolution_actions = ["issue_full_refund"]

        # 3 & 4. Late delivery evaluations (Delivered > Estimated)
        elif delivery_late:
            # Check seller vs carrier handoff
            if seller_handoff_late:
                primary_issue = "late_delivery_seller"
                case_status = "action_required"
                root_cause_code = "SELLER_HANDOFF_AFTER_LIMIT"
                responsible_parties = [{"party_type": "seller", "party_id": seller_id}]
                recommended_refund_brl = freight_total
                resolution_actions = ["refund_freight"]
            else:
                primary_issue = "late_delivery_logistics"
                case_status = "action_required"
                root_cause_code = "CARRIER_DELIVERED_AFTER_ESTIMATE"
                responsible_parties = [{"party_type": "logistics_provider", "party_id": "LOGISTICS_PROVIDER"}]
                recommended_refund_brl = freight_total
                resolution_actions = ["refund_freight"]

        # 5. valid_split_payment
        elif payment_count >= 2 and payment_reconciled:
            primary_issue = "valid_split_payment"
            case_status = "no_action"
            root_cause_code = "MULTIPLE_PAYMENTS_RECONCILED"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["explain_valid_split_payment"]

        # 6. unsupported_late_claim
        elif delivery_on_time and payment_reconciled:
            primary_issue = "unsupported_late_claim"
            case_status = "no_action"
            root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["reject_late_refund"]

        # Official K3 inputs are expected to match one of the six policy cases.
        # Keep unknown edge cases no-action with lower confidence instead of
        # pretending the high-confidence unsupported-late rule was proven.
        else:
            primary_issue = "unsupported_late_claim"
            case_status = "no_action"
            confidence = 0.55
            root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["reject_late_refund"]

        # Build Standard Evidence IDs
        evidence_ids = []
        def add_evidence(evidence_id: str):
            if evidence_id and evidence_id not in evidence_ids and len(evidence_ids) < 10:
                evidence_ids.append(evidence_id)

        # Follow the canonical ordering shown in README: order, items,
        # payments, sellers, then the policy evidence.
        add_evidence(f"order:{order_id}" if order_id else "")
        for i_id in item_ids[:5]:
            add_evidence(f"item:{i_id}")
        for p_id in payment_ids[:5]:
            add_evidence(f"payment:{p_id}")
        # Seller evidence is causal only when seller handoff caused the delay.
        if primary_issue == "late_delivery_seller":
            for s_id in seller_ids[:5]:
                add_evidence(f"seller:{s_id}")
        add_evidence(f"policy:{root_cause_code}" if root_cause_code else "")

        return {
            "assessment": {
                "primary_issue": primary_issue,
                "case_status": case_status,
                "confidence": confidence
            },
            "affected_entities": {
                "order_ids": [order_id] if order_id else [],
                "item_ids": item_ids[:5],
                "seller_ids": seller_ids[:5] if primary_issue == "late_delivery_seller" else [],
                "payment_ids": payment_ids[:5]
            },
            "root_cause_analysis": {
                "ranked_causes": [
                    {"cause_code": root_cause_code, "rank": 1}
                ],
                "responsible_parties": responsible_parties[:3]
            },
            "evidence_ids": evidence_ids,
            "financial_resolution": {
                "currency": "BRL",
                "item_total_brl": item_total,
                "freight_total_brl": freight_total,
                "payment_total_brl": payment_total,
                "recommended_refund_brl": round(recommended_refund_brl, 2)
            },
            "resolution_actions": resolution_actions[:5]
        }
