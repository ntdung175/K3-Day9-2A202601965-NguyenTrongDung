"""Read-only final QA check for the required 50 output JSON files."""

import json
from pathlib import Path

from src.config import INPUT_DIR, OUTPUT_DIR
from src.data_loader import DataLoader
from src.verifier_agent import VerifierAgent


def main() -> int:
    verifier, errors = VerifierAgent(), []
    data_loader = DataLoader()
    data_loader.load_all()
    expected = [f"EC_{number:03d}.json" for number in range(1, 51)]
    actual = sorted(path.name for path in OUTPUT_DIR.glob("EC_*.json"))
    if actual != expected:
        errors.append(f"expected exactly 50 outputs EC_001.json..EC_050.json; found {len(actual)}")
    for name in expected:
        source, output = INPUT_DIR / name, OUTPUT_DIR / name
        if not source.exists() or not output.exists():
            continue
        try:
            ticket = json.loads(source.read_text(encoding="utf-8"))
            result = json.loads(output.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{name}: invalid JSON ({error.msg})")
            continue
        order_id = ticket.get("customer_request", {}).get("claimed_order_id", "")
        facts = data_loader.get_order_facts(order_id)
        facts["case_id"] = ticket.get("case_id", "")
        errors.extend(f"{name}: {error}" for error in verifier.validate(result, facts))
    if errors:
        print("VALIDATION FAILED\n" + "\n".join(errors))
        return 1
    print("VALIDATION PASSED: 50 output files meet the QA contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
