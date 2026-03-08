import json
from rag_pipeline import evaluate_eligibility


def get_user_profile():
    print("\n=== SwiftVisa - RAG Eligibility Test ===\n")

    country = input("Enter destination country (or type 'exit'): ").strip()
    if country.lower() == "exit":
        return None

    visa_type = input("Enter visa type: ").strip()

    if not country or not visa_type:
        print("Country and Visa Type are required.\n")
        return get_user_profile()

    name = input("Enter applicant name: ").strip()
    age_input = input("Enter age: ").strip()
    nationality = input("Enter nationality: ").strip()

    try:
        age = int(age_input)
    except:
        age = None

    print("\nEnter documents (comma separated):")
    docs_input = input("> ").strip()
    documents = [doc.strip() for doc in docs_input.split(",") if doc.strip()]

    return {
        "name": name,
        "age": age,
        "nationality": nationality,
        "destination_country": country,
        "visa_type": visa_type,
        "documents": documents
    }


def pretty_print(result):
    print("\n" + "=" * 75)

    if result.get("status") != "success":
        print("❌ Pipeline failed.\n")
        print(json.dumps(result, indent=2))
        print("=" * 75)
        return

    eligibility = result.get("eligibility_result", {})
    doc_eval = eligibility.get("document_evaluation", {})

    print("✅ Evaluation Successful\n")
    print(f"System Version       : {result.get('system_version')}")
    print(f"Model Used           : {result.get('model_used')}")
    print(f"Country              : {result.get('country')}")
    print(f"Visa Type            : {result.get('visa_type')}")
    print(f"Final Decision       : {eligibility.get('final_decision')}")
    print(f"Final Confidence     : {result.get('final_confidence')}%")

    ms = result.get("total_time_ms", 0)
    print(f"Processing Time      : {round(ms/1000, 2)} seconds")

    print("\n--- Criteria Evaluation ---")
    for item in eligibility.get("criteria_evaluation", []):
        print(f"• {item.get('criterion')} → {item.get('status')}")

    print("\n--- Provided Documents ---")
    for doc in doc_eval.get("provided", []):
        print(f"• {doc}")

    print("\n--- Missing Documents ---")
    missing_docs = doc_eval.get("missing", [])
    if missing_docs:
        for doc in missing_docs:
            print(f"• {doc}")
    else:
        print("None")

    print("\n--- Missing Information ---")
    missing_info = eligibility.get("missing_information", [])
    if missing_info:
        for info in missing_info:
            print(f"• {info}")
    else:
        print("None")

    print("\n--- Risk Level ---")
    print(f"{eligibility.get('risk_level')}")

    print("=" * 75)


def main():
    while True:
        user_profile = get_user_profile()

        if user_profile is None:
            print("\nExiting SwiftVisa Test.\n")
            break

        print("\n🔍 Running Optimized RAG Pipeline...\n")
        result = evaluate_eligibility(user_profile)
        pretty_print(result)


if __name__ == "__main__":
    main()