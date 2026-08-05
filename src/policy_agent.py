"""
Policy Agent Module — EC_POLICY_V1 Evaluator for K3
Member 1 (Leader / Policy Architect) Ownership
"""

from typing import Dict, Any, List

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

        delivered_customer_date = facts.get("order_delivered_customer_date", "")
        estimated_delivery_date = facts.get("order_estimated_delivery_date", "")
        delivered_carrier_date = facts.get("order_delivered_carrier_date", "")
        shipping_limit_date = facts.get("shipping_limit_date", "")
        
        seller_ids = facts.get("seller_ids", [])
        seller_id = seller_ids[0] if seller_ids else "UNKNOWN_SELLER"

        item_ids = facts.get("item_ids", [])
        payment_ids = facts.get("payment_ids", [])
        
        # Primary Issue Evaluation Order
        primary_issue = None
        case_status = "no_action"
        confidence = 0.95
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
        elif delivered_customer_date and estimated_delivery_date and delivered_customer_date > estimated_delivery_date:
            # Check seller vs carrier handoff
            if delivered_carrier_date and shipping_limit_date and delivered_carrier_date > shipping_limit_date:
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
        elif payment_count >= 2 and abs(payment_total - (item_total + freight_total)) <= 0.10:
            primary_issue = "valid_split_payment"
            case_status = "no_action"
            root_cause_code = "MULTIPLE_PAYMENTS_RECONCILED"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["explain_valid_split_payment"]

        # 6. unsupported_late_claim (Default for on-time delivered orders)
        else:
            primary_issue = "unsupported_late_claim"
            case_status = "no_action"
            root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["reject_late_refund"]

        # Build Standard Evidence IDs
        evidence_ids = []
        if order_id:
            evidence_ids.append(f"order:{order_id}")
        for i_id in item_ids[:5]:
            evidence_ids.append(f"item:{i_id}")
        for p_id in payment_ids[:5]:
            evidence_ids.append(f"payment:{p_id}")
        for s_id in seller_ids[:5]:
            evidence_ids.append(f"seller:{s_id}")
        if root_cause_code:
            evidence_ids.append(f"policy:{root_cause_code}")

        # Limit evidence_ids to 10 max
        evidence_ids = evidence_ids[:10]

        return {
            "assessment": {
                "primary_issue": primary_issue,
                "case_status": case_status,
                "confidence": confidence
            },
            "affected_entities": {
                "order_ids": [order_id] if order_id else [],
                "item_ids": item_ids[:5],
                "seller_ids": seller_ids[:5],
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
