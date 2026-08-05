"""
Input Generator Script
Generates 50 realistic input JSON files (EC_001.json to EC_050.json) from Olist dataset
if input/ is empty.
"""

import csv
import json
from pathlib import Path
from src.config import DATA_DIR, INPUT_DIR

def generate_50_inputs():
    orders_csv = DATA_DIR / "olist_orders_dataset.csv"
    if not orders_csv.exists():
        print(f"Error: {orders_csv} not found.")
        return

    orders_by_type = {
        "canceled": [],
        "unavailable": [],
        "late": [],
        "normal": []
    }

    with open(orders_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row["order_status"]
            oid = row["order_id"]
            cust_deliv = row["order_delivered_customer_date"]
            est_deliv = row["order_estimated_delivery_date"]

            if status == "canceled":
                orders_by_type["canceled"].append(oid)
            elif status == "unavailable":
                orders_by_type["unavailable"].append(oid)
            elif cust_deliv and est_deliv and cust_deliv > est_deliv:
                orders_by_type["late"].append(oid)
            elif status == "delivered":
                orders_by_type["normal"].append(oid)

    selected_order_ids = []
    # Balance cases to cover all policy rules:
    selected_order_ids.extend(orders_by_type["canceled"][:8])
    selected_order_ids.extend(orders_by_type["unavailable"][:6])
    selected_order_ids.extend(orders_by_type["late"][:20])
    selected_order_ids.extend(orders_by_type["normal"][:16])

    # Ensure exactly 50
    if len(selected_order_ids) < 50:
        remaining = 50 - len(selected_order_ids)
        selected_order_ids.extend(orders_by_type["normal"][16:16+remaining])

    selected_order_ids = selected_order_ids[:50]

    messages = [
        "Đơn hàng của tôi có dấu hiệu giao trễ. Hãy kiểm tra nguyên nhân và quyền lợi phù hợp.",
        "Tôi chưa nhận được sản phẩm mặc dù đơn hàng bị báo hủy. Đề nghị hoàn tiền.",
        "Đơn hàng bị báo không có sẵn. Tôi muốn làm thủ tục refund đầy đủ.",
        "Vui lòng kiểm tra lại phí vận chuyển và số tiền thanh toán của đơn hàng này.",
        "Tôi cần hỗ trợ đối soát giao dịch thanh toán cho đơn hàng đã đặt."
    ]

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    for idx, oid in enumerate(selected_order_ids, start=1):
        case_id = f"EC_{idx:03d}"
        file_path = INPUT_DIR / f"{case_id}.json"
        
        # Keep existing input file if already provided by user/BTC
        if file_path.exists() and file_path.stat().st_size > 0:
            continue

        msg = messages[(idx - 1) % len(messages)]
        ticket_json = {
            "case_id": case_id,
            "opened_at": "2018-10-18T00:00:00-03:00",
            "customer_request": {
                "language": "vi",
                "message": msg,
                "claimed_order_id": oid
            },
            "policy_version": "EC_POLICY_V1"
        }

        with open(file_path, "w", encoding="utf-8") as out_f:
            json.dump(ticket_json, out_f, indent=2, ensure_ascii=False)

    print(f"Generated {len(selected_order_ids)} input files in {INPUT_DIR}")

if __name__ == "__main__":
    generate_50_inputs()
