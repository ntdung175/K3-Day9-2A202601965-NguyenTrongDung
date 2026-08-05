"""
Member 2 Payment Agent.

Reconciles payment rows against item price plus freight for the claimed order.
"""

from __future__ import annotations

from typing import Any, Dict

from src.data_engine import item_entity_id, payment_entity_id, round_brl, to_float


class PaymentAgent:
    def __init__(self, data_engine):
        self.data_engine = data_engine

    def inspect(self, order_id: str) -> Dict[str, Any]:
        items = self.data_engine.get_order_items(order_id)
        payments = self.data_engine.get_order_payments(order_id)

        item_total = round_brl(sum(to_float(row.get("price")) for row in items))
        freight_total = round_brl(sum(to_float(row.get("freight_value")) for row in items))
        payment_total = round_brl(sum(to_float(row.get("payment_value")) for row in payments))
        expected_total = round_brl(item_total + freight_total)
        reconciliation_delta = round_brl(payment_total - expected_total)

        item_ids = [item_entity_id(row) for row in items]
        payment_ids = [payment_entity_id(row) for row in payments]

        evidence_ids = []
        evidence_ids.extend(f"item:{entity_id}" for entity_id in item_ids[:5])
        evidence_ids.extend(f"payment:{entity_id}" for entity_id in payment_ids[:5])

        return {
            "item_total_brl": item_total,
            "freight_total_brl": freight_total,
            "payment_total_brl": payment_total,
            "expected_order_total_brl": expected_total,
            "payment_count": len(payments),
            "payment_ids": payment_ids,
            "payment_reconciled": abs(reconciliation_delta) <= 0.10,
            "payment_reconciliation_delta_brl": reconciliation_delta,
            "is_split_payment": len(payments) >= 2,
            "domain_evidence_ids": evidence_ids,
        }
