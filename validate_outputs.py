"""Final read-only QA before packaging."""
import json
from src.config import INPUT_DIR, OUTPUT_DIR
from src.data_engine import DataEngine
from src.verifier_agent import VerifierAgent
def main():
    expected=[f"EC_{i:03d}.json" for i in range(1,51)]; actual=sorted(p.name for p in OUTPUT_DIR.glob("EC_*.json")); errors=[]
    if actual!=expected: errors.append(f"expected 50 outputs, found {len(actual)}")
    engine=DataEngine(); verifier=VerifierAgent()
    for name in expected:
        source, target=INPUT_DIR/name, OUTPUT_DIR/name
        if not source.exists() or not target.exists(): continue
        ticket=json.loads(source.read_text(encoding="utf-8")); facts=engine.get_order_facts(ticket["customer_request"]["claimed_order_id"]); facts["case_id"]=ticket["case_id"]
        errors += [f"{name}: {err}" for err in verifier.validate(json.loads(target.read_text(encoding="utf-8")),facts)]
    if errors: print("VALIDATION FAILED\n"+"\n".join(errors)); return 1
    print("VALIDATION PASSED: 50 output files meet the QA contract."); return 0
if __name__=="__main__": raise SystemExit(main())
