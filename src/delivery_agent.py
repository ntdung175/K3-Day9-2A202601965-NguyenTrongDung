"""
Member 2 Delivery Agent.

Compares actual customer delivery date against the estimated delivery date.
"""

from __future__ import annotations

from typing import Any, Dict

from src.data_engine import elapsed_days, is_after


class DeliveryAgent:
    def __init__(self, data_engine):
        self.data_engine = data_engine

    def inspect(self, order_id: str) -> Dict[str, Any]:
        order = self.data_engine.get_order(order_id)

        delivered_customer_date = order.get("order_delivered_customer_date", "")
        estimated_delivery_date = order.get("order_estimated_delivery_date", "")
        is_late_delivery = is_after(delivered_customer_date, estimated_delivery_date)
        delay_days = elapsed_days(delivered_customer_date, estimated_delivery_date)

        evidence_ids = [f"order:{order_id}"] if order else []

        return {
            "order_delivered_customer_date": delivered_customer_date,
            "order_estimated_delivery_date": estimated_delivery_date,
            "is_late_delivery": is_late_delivery,
            "delivery_delay_days": delay_days if is_late_delivery else 0.0,
            "domain_evidence_ids": evidence_ids,
        }
