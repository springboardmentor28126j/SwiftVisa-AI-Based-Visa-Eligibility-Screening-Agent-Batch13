# test_retriever.py

from retriever import retrieve_policy


def print_separator():
    print("\n" + "=" * 80 + "\n")


def pretty_print(title, items):
    print(f"\n{title}:\n")
    if not items:
        print("  ❌ None found")
        return

    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")


def validate_success_result(result):
    errors = []

    required_fields = [
        "country",
        "visa_type",
        "eligibility",
        "required_documents",
        "policy_text",
        "confidence",
        "retrieval_time_ms"
    ]

    for field in required_fields:
        if field not in result:
            errors.append(f"Missing '{field}' field")

    return errors


def handle_failure(result):
    status = result.get("status")

    if status == "country_not_detected":
        print("❌ Country not detected in query.")
        print("Available Countries:")
        for c in result.get("available_countries", []):
            print(" -", c)

    elif status == "visa_type_not_detected":
        print(f"❌ Visa type not detected for country: {result.get('country')}")
        print("Available Visa Types:")
        for v in result.get("available_visa_types", []):
            print(" -", v)

    elif status == "no_result":
        print("❌ No matching policy found in vector database.")

    else:
        print("❌ Unknown Error:")
        print(result)


def main():

    print("🧪 SwiftVisa - Retriever Validation Test")
    print("Type 'exit' to quit.\n")

    while True:

        query = input("Enter visa query: ").strip()

        if query.lower() == "exit":
            print("\nExiting Retriever Validation Test.")
            break

        if not query:
            print("⚠ Please enter a valid query.")
            continue

        print_separator()

        result = retrieve_policy(query)

        if result.get("status") != "success":
            handle_failure(result)
            print_separator()
            continue

        # ==========================
        # VALIDATION CHECK
        # ==========================
        errors = validate_success_result(result)

        if errors:
            print("❌ TEST FAILED\n")
            for err in errors:
                print(" -", err)
        else:
            print("✅ TEST PASSED\n")

            print(f"🌍 Country        : {result['country']}")
            print(f"🛂 Visa Type      : {result['visa_type']}")
            print(f"📊 Confidence     : {result['confidence']} %")
            print(f"⏱ Retrieval Time : {result['retrieval_time_ms']} ms")

            pretty_print("📋 Eligibility Criteria", result["eligibility"])
            pretty_print("📄 Required Documents", result["required_documents"])

        print_separator()


if __name__ == "__main__":
    main()