"""
Member 2 Data Engine for Olist CSV lookup and domain fact aggregation.

This module owns the data-facing contract used by the multi-agent pipeline:
`get_order_facts(order_id)` returns grounded facts for the Policy Agent while
keeping order/seller, delivery, and payment checks separated by domain.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import DATA_DIR


def to_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def round_brl(value: float) -> float:
    return round(float(value), 2)


def parse_timestamp(value: Any) -> Optional[datetime]:
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


def is_after(left: Any, right: Any) -> bool:
    left_dt = parse_timestamp(left)
    right_dt = parse_timestamp(right)
    return bool(left_dt and right_dt and left_dt > right_dt)


def elapsed_days(left: Any, right: Any) -> float:
    left_dt = parse_timestamp(left)
    right_dt = parse_timestamp(right)
    if not left_dt or not right_dt:
        return 0.0
    return round((left_dt - right_dt).total_seconds() / 86400, 2)


def item_entity_id(item_row: Dict[str, Any]) -> str:
    return f"{item_row.get('order_id', '')}:{item_row.get('order_item_id', '')}"


def payment_entity_id(payment_row: Dict[str, Any]) -> str:
    return f"{payment_row.get('order_id', '')}:{payment_row.get('payment_sequential', '')}"


class DataEngine:
    CSV_FILES = {
        "customers": "olist_customers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "order_payments": "olist_order_payments_dataset.csv",
        "order_reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._tables: Dict[str, List[Dict[str, Any]]] = {}
        self._single_indexes: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._many_indexes: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self._ensure_csv_files_exist()

        from src.delivery_agent import DeliveryAgent
        from src.order_seller_agent import OrderSellerAgent
        from src.payment_agent import PaymentAgent

        self.order_seller_agent = OrderSellerAgent(self)
        self.delivery_agent = DeliveryAgent(self)
        self.payment_agent = PaymentAgent(self)

    def _ensure_csv_files_exist(self) -> None:
        missing = [
            filename
            for filename in self.CSV_FILES.values()
            if not (self.data_dir / filename).exists()
        ]
        if missing:
            raise FileNotFoundError(
                "Missing required Olist CSV files: " + ", ".join(missing)
            )

    def available_tables(self) -> List[str]:
        return list(self.CSV_FILES.keys())

    def load_all(self) -> None:
        for table_name in self.CSV_FILES:
            self.load_table(table_name)

    def load_table(self, table_name: str) -> List[Dict[str, Any]]:
        if table_name not in self.CSV_FILES:
            raise KeyError(f"Unknown Olist table: {table_name}")

        if table_name not in self._tables:
            csv_path = self.data_dir / self.CSV_FILES[table_name]
            with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
                self._tables[table_name] = list(csv.DictReader(csv_file))
        return self._tables[table_name]

    def _single_index(self, table_name: str, field_name: str) -> Dict[str, Dict[str, Any]]:
        index_key = f"{table_name}:{field_name}"
        if index_key not in self._single_indexes:
            self._single_indexes[index_key] = {
                row[field_name]: row
                for row in self.load_table(table_name)
                if row.get(field_name)
            }
        return self._single_indexes[index_key]

    def _many_index(self, table_name: str, field_name: str) -> Dict[str, List[Dict[str, Any]]]:
        index_key = f"{table_name}:{field_name}"
        if index_key not in self._many_indexes:
            grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            for row in self.load_table(table_name):
                value = row.get(field_name)
                if value:
                    grouped[value].append(row)
            self._many_indexes[index_key] = dict(grouped)
        return self._many_indexes[index_key]

    def get_order(self, order_id: str) -> Dict[str, Any]:
        return self._single_index("orders", "order_id").get(order_id, {})

    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        rows = self._many_index("order_items", "order_id").get(order_id, [])
        return sorted(rows, key=lambda row: to_int(row.get("order_item_id")))

    def get_order_payments(self, order_id: str) -> List[Dict[str, Any]]:
        rows = self._many_index("order_payments", "order_id").get(order_id, [])
        return sorted(rows, key=lambda row: to_int(row.get("payment_sequential")))

    def get_order_reviews(self, order_id: str) -> List[Dict[str, Any]]:
        return self._many_index("order_reviews", "order_id").get(order_id, [])

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        return self._single_index("customers", "customer_id").get(customer_id, {})

    def get_product(self, product_id: str) -> Dict[str, Any]:
        return self._single_index("products", "product_id").get(product_id, {})

    def get_seller(self, seller_id: str) -> Dict[str, Any]:
        return self._single_index("sellers", "seller_id").get(seller_id, {})

    def get_geolocations(self, zip_code_prefix: str) -> List[Dict[str, Any]]:
        return self._many_index("geolocation", "geolocation_zip_code_prefix").get(
            str(zip_code_prefix),
            [],
        )

    def translate_category(self, category_name: str) -> str:
        row = self._single_index("category_translation", "product_category_name").get(
            category_name,
            {},
        )
        return row.get("product_category_name_english", "")

    def get_order_facts(self, order_id: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "order_id": order_id,
            "order_found": bool(self.get_order(order_id)),
        }

        domain_outputs = [
            self.order_seller_agent.inspect(order_id),
            self.delivery_agent.inspect(order_id),
            self.payment_agent.inspect(order_id),
        ]

        evidence_ids: List[str] = []
        for output in domain_outputs:
            evidence_ids.extend(output.pop("domain_evidence_ids", []))
            facts.update(output)

        facts["domain_evidence_ids"] = list(dict.fromkeys(evidence_ids))[:10]
        return facts
