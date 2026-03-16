import json
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.lm_client import LMStudioClient


def _extract_json_payload(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].strip() == "```":
        body = lines[1:-1]
        if body and body[0].strip().lower() == "json":
            body = body[1:]
        return "\n".join(body).strip()

    return stripped


def main() -> int:
    client = LMStudioClient()

    print(f"LM Studio URL: {client.base_url}")
    print(f"LM Studio model: {client.model}")
    print("LM Studio must be running with a model loaded before this test will pass.")

    try:
        ping_ok = client.ping()
        print(f"Ping result: {ping_ok}")
    except Exception as exc:
        print("Ping result: False")
        print(f"Ping failed: {exc}")
        return 1

    extraction_prompt = """
Extract the following case summary into JSON only.
Use this schema:
{
  "applicant_name": string,
  "decision": string,
  "reasons": [string]
}
""".strip()

    case_summary = (
        "Applicant Maya Patel was denied a housing application because the credit "
        "score was 610 and the submitted pay stubs could not verify stable income."
    )

    try:
        response = client.chat(
            system_prompt="You extract structured data and return valid JSON only.",
            user_message=f"{extraction_prompt}\n\nCase summary:\n{case_summary}",
            temperature=0.1,
        )
    except Exception as exc:
        print(f"JSON extraction failed: {exc}")
        return 1

    print("JSON extraction response:")
    print(response)

    try:
        parsed = json.loads(_extract_json_payload(response))
        print("Parsed JSON:")
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as exc:
        print(f"JSON parse failed: {exc}")
        return 1

    return 0 if ping_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
