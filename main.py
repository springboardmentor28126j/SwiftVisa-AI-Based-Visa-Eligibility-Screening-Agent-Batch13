# main.py

from retrieval import retrieve_documents
from prompt_builder import build_prompt
from llm import load_llm


def main():

    print("========================================")
    print("     SWIFT VISA ASSISTANT (Gemini)")
    print("========================================\n")

    

    while True:

        question = input("Enter your visa question (type 'exit' to quit): ")

        if question.lower() == "exit":
            print("\nExiting SWIFTVISA...")
            break

        try:
            # 1️⃣ Retrieve Top 3 Documents
            docs = retrieve_documents(question, k=3)

            if not docs:
                print("\nNo relevant policy found.\n")
                continue

            # 2️⃣ Build Prompt Using Best Chunk
            final_prompt = build_prompt(question, docs, user_profile)

            # 3️⃣ Load Gemini Model
            llm = load_llm()

            # 4️⃣ Generate Response
            response = llm.invoke(final_prompt)

            print("\n========== FINAL ANSWER ==========\n")
            print(response.content)
            print("\n==================================\n")

        except Exception as e:
            print("\nError occurred:", str(e))
            print("Please check configuration.\n")


if __name__ == "__main__":
    main()
