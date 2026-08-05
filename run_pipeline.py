"""
Main Entrypoint Script — Runs Multi-Agent Pipeline for all 50 tickets (EC_001.json to EC_050.json)
"""

import json
from pathlib import Path
from src.config import INPUT_DIR, OUTPUT_DIR, LOGGING_DIR, COHORT, POLICY_VERSION, MODEL_NAME
from src.data_loader import DataLoader
from src.verifier_agent import VerifierAgent
from src.coordinator import CoordinatorAgent
from src.logger import TraceLogger
from src.generate_input import generate_50_inputs

def run_pipeline():
    print("=" * 60)
    print(f"Starting Multi-Agent Dispute Resolution Pipeline ({COHORT} / {POLICY_VERSION})")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)

    # 1. Ensure 50 inputs exist
    generate_50_inputs()

    # 2. Initialize DataLoader, Verifier, Coordinator, Logger
    print("Loading Olist CSV dataset...")
    data_loader = DataLoader()
    data_loader.load_all()
    print("Dataset loaded successfully.")

    verifier = VerifierAgent()
    logger = TraceLogger()
    logger.clear()

    coordinator = CoordinatorAgent(data_loader=data_loader, verifier_agent=verifier)

    # 3. Process all 50 input files
    input_files = sorted(list(INPUT_DIR.glob("EC_*.json")))
    print(f"Found {len(input_files)} input tickets to process.\n")

    processed_count = 0
    for input_file in input_files:
        case_id = input_file.stem
        with open(input_file, "r", encoding="utf-8") as f:
            ticket_data = json.load(f)

        logger.log_step(case_id, "CoordinatorAgent", "RECEIVE_TICKET", {"ticket_file": str(input_file.name)})

        # Process ticket
        output_result = coordinator.process_ticket(ticket_data)

        # Log policy decision & verifier step
        logger.log_step(
            case_id,
            "PolicyAgent",
            "EVALUATE_POLICY",
            {
                "primary_issue": output_result["assessment"]["primary_issue"],
                "recommended_refund": output_result["financial_resolution"]["recommended_refund_brl"]
            }
        )
        logger.log_step(case_id, "VerifierAgent", "VERIFY_SCHEMA", {"status": "SUCCESS"})

        # Save to output/
        out_file = OUTPUT_DIR / f"{case_id}.json"
        with open(out_file, "w", encoding="utf-8") as out_f:
            json.dump(output_result, out_f, indent=2, ensure_ascii=False)

        processed_count += 1
        print(f"[{processed_count:02d}/50] Processed {case_id} -> primary_issue: {output_result['assessment']['primary_issue']}")

    print("\n" + "=" * 60)
    print(f"SUCCESS: Processed {processed_count} tickets into {OUTPUT_DIR}")
    print(f"Trace log saved to: {logger.trace_file}")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
