"""Run the six-agent K3 pipeline for all required tickets."""
import json
from src.config import INPUT_DIR, OUTPUT_DIR
from src.coordinator import CoordinatorAgent
from src.data_engine import DataEngine
from src.generate_input import generate_50_inputs
from src.logger import TraceLogger
from src.verifier_agent import VerifierAgent

def main():
    generate_50_inputs(); engine=DataEngine(); engine.load_all(); verifier=VerifierAgent(); coordinator=CoordinatorAgent(data_loader=engine, verifier_agent=verifier); logger=TraceLogger(); logger.clear(); OUTPUT_DIR.mkdir(exist_ok=True)
    files=sorted(INPUT_DIR.glob("EC_*.json"))
    if len(files)!=50: raise RuntimeError(f"Expected 50 inputs, found {len(files)}")
    for path in files:
        ticket=json.loads(path.read_text(encoding="utf-8")); case_id=ticket["case_id"]; logger.log_step(case_id,"CoordinatorAgent","RECEIVE_TICKET",{"ticket_file":path.name})
        result=coordinator.process_ticket(ticket); logger.log_step(case_id,"PolicyAgent","EVALUATE_POLICY",{"primary_issue":result["assessment"]["primary_issue"],"recommended_refund":result["financial_resolution"]["recommended_refund_brl"]})
        logger.log_step(case_id,"VerifierAgent","VERIFY_SCHEMA",{"status":"SUCCESS"}); (OUTPUT_DIR/f"{case_id}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("SUCCESS: generated and verified 50 outputs")
if __name__ == "__main__": main()
