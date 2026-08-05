"""
Member 2 Order & Seller Agent.

Inspects order status, item ownership, seller IDs, and seller handoff timing
using `order_delivered_carrier_date` versus each item's `shipping_limit_date`.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.data_engine import is_after, item_entity_id, parse_timestamp


class OrderSellerAgent:
    def __init__(self, data_engine):
        self.data_engine = data_engine

    def inspect(self, order_id: str) -> Dict[str, Any]:
        order = self.data_engine.get_order(order_id)
        items = self.data_engine.get_order_items(order_id)

        carrier_date = order.get("order_delivered_carrier_date", "")
        ordered_items = sorted(
            items,
            key=lambda row: (
                parse_timestamp(row.get("shipping_limit_date")) is None,
                parse_timestamp(row.get("shipping_limit_date")),
                row.get("order_item_id", ""),
            ),
        )

        seller_ids = self._unique([row.get("seller_id", "") for row in ordered_items])
        item_ids = [item_entity_id(row) for row in ordered_items]

        late_items = [
            row
            for row in ordered_items
            if is_after(carrier_date, row.get("shipping_limit_date", ""))
        ]
        late_seller_ids = self._unique([row.get("seller_id", "") for row in late_items])

        if late_seller_ids:
            seller_ids = late_seller_ids + [
                seller_id for seller_id in seller_ids if seller_id not in late_seller_ids
            ]

        selected_item = late_items[0] if late_items else (ordered_items[0] if ordered_items else {})
        shipping_limit_date = selected_item.get("shipping_limit_date", "")

        evidence_ids = []
        if order:
            evidence_ids.append(f"order:{order_id}")
        evidence_ids.extend(f"item:{entity_id}" for entity_id in item_ids[:5])
        evidence_ids.extend(f"seller:{seller_id}" for seller_id in seller_ids[:5])

        return {
            "order_status": order.get("order_status", ""),
            "order_delivered_carrier_date": carrier_date,
            "shipping_limit_date": shipping_limit_date,
            "item_ids": item_ids,
            "seller_ids": seller_ids,
            "seller_handoff_late": bool(late_items),
            "late_item_ids": [item_entity_id(row) for row in late_items],
            "late_seller_ids": late_seller_ids,
            "domain_evidence_ids": evidence_ids,
        }

    @staticmethod
    def _unique(values: List[str]) -> List[str]:
        return list(dict.fromkeys(value for value in values if value))
