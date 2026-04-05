import streamlit as st
import json
from visa_agent import screen_visa_eligibility, log_decision
from chatbot_backend import visa_chatbot_response

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------streamlit run app.py

st.set_page_config(
    page_title="SwiftVisa AI",
    page_icon="🌍",
    layout="centered"
)

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------

if "mode" not in st.session_state:
    st.session_state.mode = None

if "step" not in st.session_state:
    st.session_state.step = 1

if "personal" not in st.session_state:
    st.session_state.personal = {}

if "travel" not in st.session_state:
    st.session_state.travel = {}

if "financial" not in st.session_state:
    st.session_state.financial = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------------------------
# MODE SELECTION SCREEN
# -------------------------------------------------

if st.session_state.mode is None:

    st.title("🌍 SwiftVisa AI")
    st.subheader("Choose Application Mode")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧾 Visa Eligibility Checker"):
            st.session_state.mode = "eligibility"
            st.rerun()

    with col2:
        if st.button("💬 Visa Chatbot"):
            st.session_state.mode = "chatbot"
            st.rerun()

    st.stop()

# -------------------------------------------------
# BACK BUTTON (COMMON)
# -------------------------------------------------

if st.button("🔙 Back to Home"):
    st.session_state.mode = None
    st.session_state.step = 1
    st.rerun()

st.divider()

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():
    with open("countries_visa_types.json") as f:
        return json.load(f)

visa_data = load_data()
countries = list(visa_data.keys())

# -------------------------------------------------
# CHATBOT MODE
# -------------------------------------------------

if st.session_state.mode == "chatbot":

    st.title("💬 Visa Assistant Chatbot")

    user_query = st.text_input("Ask your visa-related question")

    if st.button("Ask") and user_query:
        with st.spinner("Thinking..."):
            answer = visa_chatbot_response(user_query)

        st.session_state.chat_history.append(("You", user_query))
        st.session_state.chat_history.append(("Bot", answer))

    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Bot:** {msg}")

# -------------------------------------------------
# ELIGIBILITY MODE
# -------------------------------------------------

elif st.session_state.mode == "eligibility":

    st.title("🧾 Visa Eligibility Checker")

    steps = [
        "Personal Information",
        "Travel Details",
        "Financial Background",
        "Review Application",
        "AI Decision"
    ]

    st.progress(st.session_state.step / 5)
    st.write(f"Step {st.session_state.step}: {steps[st.session_state.step-1]}")
    st.divider()

    # STEP 1
    if st.session_state.step == 1:

        age = st.number_input("Age *", 18, 80,
                              value=st.session_state.personal.get("age", 18))

        nationality = st.text_input("Nationality *",
                                   value=st.session_state.personal.get("nationality", ""))

        marital_status = st.selectbox(
            "Marital Status",
            ["Single", "Married", "Divorced"],
            index=["Single", "Married", "Divorced"].index(
                st.session_state.personal.get("marital_status", "Single")
            )
        )

        passport_validity = st.number_input(
            "Passport Validity (months) *",
            0, 120,
            value=st.session_state.personal.get("passport_validity", 0)
        )

        if st.button("Next ➡"):
            st.session_state.personal = {
                "age": age,
                "nationality": nationality,
                "marital_status": marital_status,
                "passport_validity": passport_validity
            }
            st.session_state.step = 2
            st.rerun()

    # STEP 2
    elif st.session_state.step == 2:

        destination_country = st.selectbox(
            "Destination Country *",
            countries,
            index=countries.index(
                st.session_state.travel.get("country", countries[0])
            ) if st.session_state.travel else 0
        )

        visa_type = st.selectbox(
            "Visa Type *",
            visa_data[destination_country]
        )

        purpose = st.text_input(
            "Purpose of Visit *",
            value=st.session_state.travel.get("purpose", "")
        )

        travel_duration = st.number_input(
            "Travel Duration (months)",
            1, 60,
            value=st.session_state.travel.get("travel_duration", 1)
        )

        previous_travel = st.selectbox(
            "Previous International Travel",
            ["Yes", "No"],
            index=["Yes", "No"].index(
                st.session_state.travel.get("travel_history", "No")
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous"):
                st.session_state.step = 1
                st.rerun()

        with col2:
            if st.button("Next ➡"):
                st.session_state.travel = {
                    "country": destination_country,
                    "visa_type": visa_type,
                    "purpose": purpose,
                    "travel_duration": travel_duration,
                    "travel_history": previous_travel
                }
                st.session_state.step = 3
                st.rerun()

    # STEP 3
    elif st.session_state.step == 3:

        education = st.selectbox(
            "Highest Education Level *",
            ["High School", "Bachelor's", "Master's", "PhD"],
            index=["High School", "Bachelor's", "Master's", "PhD"].index(
                st.session_state.financial.get("education", "High School")
            )
        )

        employment = st.selectbox(
            "Employment Status *",
            ["Student", "Employed", "Self-employed", "Unemployed"],
            index=["Student", "Employed", "Self-employed", "Unemployed"].index(
                st.session_state.financial.get("employment", "Student")
            )
        )

        work_experience = st.number_input(
            "Work Experience (Years)",
            0, 40,
            value=st.session_state.financial.get("experience", 0)
        )

        annual_income = st.number_input(
            "Annual Income (USD)",
            value=st.session_state.financial.get("income", 0)
        )

        bank_balance = st.number_input(
            "Bank Balance (USD)",
            value=st.session_state.financial.get("bank_balance", 0)
        )

        financial_proof = st.selectbox(
            "Financial Proof Available *",
            ["Yes", "No"],
            index=["Yes", "No"].index(
                st.session_state.financial.get("financial_proof", "No")
            )
        )

        english_level = st.selectbox(
            "English Proficiency",
            ["Basic", "Intermediate", "Advanced"],
            index=["Basic", "Intermediate", "Advanced"].index(
                st.session_state.financial.get("english", "Basic")
            )
        )

        criminal_record = st.selectbox(
            "Criminal Record",
            ["No", "Yes"],
            index=["No", "Yes"].index(
                st.session_state.financial.get("criminal_record", "No")
            )
        )

        sponsor = st.selectbox(
            "Sponsor Available",
            ["Yes", "No"],
            index=["Yes", "No"].index(
                st.session_state.financial.get("sponsor", "No")
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous"):
                st.session_state.step = 2
                st.rerun()

        with col2:
            if st.button("Next ➡"):
                st.session_state.financial = {
                    "education": education,
                    "employment": employment,
                    "experience": work_experience,
                    "income": annual_income,
                    "bank_balance": bank_balance,
                    "financial_proof": financial_proof,
                    "english": english_level,
                    "criminal_record": criminal_record,
                    "sponsor": sponsor
                }
                st.session_state.step = 4
                st.rerun()

    # STEP 4
    elif st.session_state.step == 4:

        data = {
            **st.session_state.personal,
            **st.session_state.travel,
            **st.session_state.financial
        }

        summary = f"""
A {data['age']}-year-old applicant from {data['nationality']} is planning to travel to {data['country']} to apply for a {data['visa_type']} visa for the purpose of {data['purpose']}, with an intended stay of around {data['travel_duration']} months. 

The applicant has completed {data['education']} education and is currently {data['employment']}, having {data['experience']} years of work experience. Financially, the applicant reports an annual income of ${data['income']} and maintains a bank balance of ${data['bank_balance']}. However, financial proof availability is marked as {data['financial_proof']}, and sponsor support is {data['sponsor']}.

In terms of background, the applicant has {data['travel_history']} previous international travel experience, possesses an English proficiency level of {data['english']}, and has a criminal record status of {data['criminal_record']}. The passport validity is {data['passport_validity']} months.
"""

        st.write(summary)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Edit"):
                st.session_state.step = 1
                st.rerun()

        with col2:
            if st.button("Submit"):
                st.session_state.step = 5
                st.rerun()

    # STEP 5
    elif st.session_state.step == 5:

        data = {
            **st.session_state.personal,
            **st.session_state.travel,
            **st.session_state.financial
        }

        query = str(data)

        with st.spinner("Analyzing..."):
            output, confidence = screen_visa_eligibility(query)

        st.success(output["result"])
        st.progress(int(confidence))
        st.write(f"{confidence:.2f}%")

        if st.button("Start New"):
            st.session_state.step = 1
            st.rerun()