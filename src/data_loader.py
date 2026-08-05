"""
Data Loader Module for Olist Dataset
Loads CSV files and indexes orders by order_id for fast lookup.
"""

import csv
from pathlib import Path
from typing import Dict, Any, List
from src.config import DATA_DIR

class DataLoader:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.order_items: Dict[str, List[Dict[str, Any]]] = {}
        self.order_payments: Dict[str, List[Dict[str, Any]]] = {}
        self.loaded = False

    def load_all(self):
        if self.loaded:
            return

        # 1. Load orders
        orders_path = self.data_dir / "olist_orders_dataset.csv"
        if orders_path.exists():
            with open(orders_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row["order_id"]
                    self.orders[oid] = row

        # 2. Load order items
        items_path = self.data_dir / "olist_order_items_dataset.csv"
        if items_path.exists():
            with open(items_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row["order_id"]
                    if oid not in self.order_items:
                        self.order_items[oid] = []
                    self.order_items[oid].append(row)

        # 3. Load order payments
        payments_path = self.data_dir / "olist_order_payments_dataset.csv"
        if payments_path.exists():
            with open(payments_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row["order_id"]
                    if oid not in self.order_payments:
                        self.order_payments[oid] = []
                    self.order_payments[oid].append(row)

        self.loaded = True

    def get_order_facts(self, order_id: str) -> Dict[str, Any]:
        """
        Aggregate order, items, sellers, payments, and delivery milestones for an order.
        """
        if not self.loaded:
            self.load_all()

        order = self.orders.get(order_id, {})
        items = self.order_items.get(order_id, [])
        payments = self.order_payments.get(order_id, [])

        order_status = order.get("order_status", "unknown")
        purchase_time = order.get("order_purchase_timestamp", "")
        approved_at = order.get("order_approved_at", "")
        delivered_carrier_date = order.get("order_delivered_carrier_date", "")
        delivered_customer_date = order.get("order_delivered_customer_date", "")
        estimated_delivery_date = order.get("order_estimated_delivery_date", "")

        item_total = 0.0
        freight_total = 0.0
        item_ids = []
        seller_ids = []
        shipping_limit_dates = []

        for item in items:
            item_seq = item.get("order_item_id", "1")
            item_ids.append(f"{order_id}:{item_seq}")
            
            try:
                price = float(item.get("price", 0.0))
                freight = float(item.get("freight_value", 0.0))
            except ValueError:
                price, freight = 0.0, 0.0
                
            item_total += price
            freight_total += freight
            
            sid = item.get("seller_id", "")
            if sid and sid not in seller_ids:
                seller_ids.append(sid)
                
            slimit = item.get("shipping_limit_date", "")
            if slimit:
                shipping_limit_dates.append(slimit)

        # Determine overall shipping limit date (max date if multiple items)
        shipping_limit_date = max(shipping_limit_dates) if shipping_limit_dates else ""

        payment_total = 0.0
        payment_ids = []
        for payment in payments:
            seq = payment.get("payment_sequential", "1")
            payment_ids.append(f"{order_id}:{seq}")
            try:
                pval = float(payment.get("payment_value", 0.0))
            except ValueError:
                pval = 0.0
            payment_total += pval

        return {
            "order_id": order_id,
            "order_status": order_status,
            "order_purchase_timestamp": purchase_time,
            "order_approved_at": approved_at,
            "order_delivered_carrier_date": delivered_carrier_date,
            "order_delivered_customer_date": delivered_customer_date,
            "order_estimated_delivery_date": estimated_delivery_date,
            "shipping_limit_date": shipping_limit_date,
            "item_total_brl": round(item_total, 2),
            "freight_total_brl": round(freight_total, 2),
            "payment_total_brl": round(payment_total, 2),
            "payment_count": len(payments),
            "item_ids": item_ids,
            "seller_ids": seller_ids,
            "payment_ids": payment_ids
        }
