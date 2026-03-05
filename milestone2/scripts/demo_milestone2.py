"""
Milestone 2 demo script: RAG + Groq eligibility pipeline
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from milestone2 import VisaEligibilityRAGPipeline


def main() -> None:
    pipeline = VisaEligibilityRAGPipeline(top_k=5)

    query = "I am from India and want to apply for a Canada study permit. What is my eligibility?"
    profile = {
        "nationality": "Indian",
        "destination_country": "CAN",
        "target_visa": "StudyPermit",
        "purpose": "Master's in Computer Science",
        "documents_available": "Passport, Admission letter",
        "financial_status": "USD 35,000 equivalent funds",
        "english_proof": "IELTS 7.0",
    }

    result = pipeline.evaluate(
        user_query=query,
        user_profile=profile,
        country_code="CAN",
        visa_id="StudyPermit",
    )

    response = result["response"]

    print("=" * 80)
    print("MILESTONE 2 DEMO")
    print("=" * 80)
    print(f"Query: {result['query']}")
    print(f"Status: {response['eligibility_status']}")
    print(f"Confidence: {response['confidence_score']}")
    print(f"Grounded: {response['grounded']}")
    print("\nExplanation:")
    print(response["explanation"])

    print("\nRequirements Met:")
    for item in response["requirements_met"]:
        print(f"- {item}")

    print("\nMissing Requirements:")
    for item in response["missing_requirements"]:
        print(f"- {item}")

    print("\nRequired Documents:")
    for item in response["required_documents"]:
        print(f"- {item}")

    print("\nNext Steps:")
    for item in response["next_steps"]:
        print(f"- {item}")

    print("\nCitations:")
    for citation in response["citations"]:
        print(
            f"- {citation['citation_id']}: {citation['country_code']} {citation['visa_id']} | "
            f"{citation['doc_path']} | section={citation['section'] or 'N/A'}"
        )

    print("\nRetrieval:")
    print(json.dumps(result["retrieval"], indent=2))

    print("\nDecision log updated.")


if __name__ == "__main__":
    main()
