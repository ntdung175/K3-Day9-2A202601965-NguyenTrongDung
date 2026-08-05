"""Generate the required 50 K3 ticket files from grounded Olist orders."""
import csv, json
from src.config import DATA_DIR, INPUT_DIR
def generate_50_inputs():
    groups={"canceled":[],"unavailable":[],"late":[],"normal":[]}
    with (DATA_DIR / "olist_orders_dataset.csv").open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["order_status"] == "canceled": groups["canceled"].append(row["order_id"])
            elif row["order_status"] == "unavailable": groups["unavailable"].append(row["order_id"])
            elif row["order_delivered_customer_date"] and row["order_delivered_customer_date"] > row["order_estimated_delivery_date"]: groups["late"].append(row["order_id"])
            elif row["order_status"] == "delivered": groups["normal"].append(row["order_id"])
    selected=(groups["canceled"][:8]+groups["unavailable"][:6]+groups["late"][:20]+groups["normal"][:16])[:50]
    if len(selected)!=50: raise RuntimeError("Could not select 50 orders")
    INPUT_DIR.mkdir(exist_ok=True)
    for i, order_id in enumerate(selected, 1):
        target = INPUT_DIR / f"EC_{i:03d}.json"
        # Official inputs supplied from Git must never be overwritten.
        if target.exists() and target.stat().st_size > 0:
            continue
        ticket={"case_id":f"EC_{i:03d}","opened_at":"2018-10-18T00:00:00-03:00","customer_request":{"language":"vi","message":"Vui lòng kiểm tra đơn hàng và quyền lợi phù hợp.","claimed_order_id":order_id},"policy_version":"EC_POLICY_V1"}
        target.write_text(json.dumps(ticket,ensure_ascii=False,indent=2),encoding="utf-8")
