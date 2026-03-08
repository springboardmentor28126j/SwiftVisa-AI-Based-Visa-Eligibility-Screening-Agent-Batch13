import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go

from rag_pipeline import evaluate_eligibility
from config import LOG_PATH


st.set_page_config(
    page_title="SwiftVisa AI",
    page_icon="✈️",
    layout="wide"
)


# ==============================
# Gauge Chart
# ==============================

def confidence_gauge(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Confidence Score"},
        gauge={
            "axis": {"range": [0,100]},
            "steps":[
                {"range":[0,40],"color":"red"},
                {"range":[40,70],"color":"orange"},
                {"range":[70,100],"color":"green"},
            ]
        }
    ))

    return fig


# ==============================
# Explanation Generator
# ==============================

def generate_explanation(eligibility):

    criteria = eligibility.get("criteria_evaluation", [])
    docs = eligibility.get("document_evaluation", {})

    passed = [c["criterion"] for c in criteria if c["status"] == "PASSED"]
    failed = [c["criterion"] for c in criteria if c["status"] == "FAILED"]

    provided = docs.get("provided", [])
    missing = docs.get("missing", [])

    text = ""

    if passed:
        text += "✔ Passed Criteria\n"
        for p in passed:
            text += f"- {p}\n"

    if failed:
        text += "\n❌ Failed Criteria\n"
        for f in failed:
            text += f"- {f}\n"

    if provided:
        text += "\n📄 Documents Provided\n"
        for d in provided:
            text += f"- {d}\n"

    if missing:
        text += "\n⚠ Missing Documents\n"
        for m in missing:
            text += f"- {m}\n"

    return text


# ==============================
# Header
# ==============================

st.title("✈️ SwiftVisa AI")
st.subheader("AI Visa Eligibility Screening System")

st.markdown("""
This platform evaluates visa applications using:

- Retrieval Augmented Generation (RAG)
- FAISS Vector Search
- Gemini AI reasoning
- Immigration policy datasets
""")


st.divider()


# ==============================
# Applicant Form
# ==============================

with st.form("visa_form"):

    st.header("👤 Applicant Information")

    col1,col2 = st.columns(2)

    with col1:
        name = st.text_input("Applicant Name")
        age = st.number_input("Age",18,80)
        nationality = st.text_input("Nationality")

    with col2:
        destination = st.text_input("Destination Country")
        visa_type = st.text_input("Visa Type")

    docs = st.text_area(
        "Documents (comma separated)",
        placeholder="Passport, Bank statement, Travel itinerary"
    )

    submit = st.form_submit_button("🚀 Evaluate Application")


st.divider()


# ==============================
# Run Pipeline
# ==============================

if submit:

    documents = [d.strip() for d in docs.split(",") if d.strip()]

    user_profile = {
        "name":name,
        "age":age,
        "nationality":nationality,
        "destination_country":destination,
        "visa_type":visa_type,
        "documents":documents
    }

    with st.spinner("Running AI evaluation..."):

        result = evaluate_eligibility(user_profile)

    if result.get("status") != "success":

        st.error("Pipeline error")
        st.json(result)
        st.stop()


    eligibility = result["eligibility_result"]
    policy = result["policy_summary"]

    decision = eligibility.get("final_decision","Unknown")


# ==============================
# Final Decision
# ==============================

    st.header("🎯 Final Decision")

    if decision == "APPROVED":
        st.success("✅ Visa Likely Approved")

    elif decision == "REVIEW":
        st.warning("⚠ Requires Manual Review")

    else:
        st.error("❌ Visa Likely Rejected")


    col1,col2,col3 = st.columns(3)

    col1.metric("Confidence", f"{result['final_confidence']}%")
    col2.metric("Risk Level", eligibility.get("risk_level","Unknown"))
    col3.metric("Model Used", result["model_used"])


    st.plotly_chart(
        confidence_gauge(result["final_confidence"]),
        use_container_width=True
    )


# ==============================
# AI Explanation
# ==============================

    st.header("🧠 AI Explanation")

    explanation = generate_explanation(eligibility)

    st.info(explanation)


# ==============================
# Criteria Table
# ==============================

    st.header("📋 Eligibility Criteria")

    rows = []

    for c in eligibility["criteria_evaluation"]:

        icon = "❌"

        if c["status"] == "PASSED":
            icon = "✅"

        rows.append({
            "Criterion": c["criterion"],
            "Status": icon + " " + c["status"],
            "Reason": c["reason"]
        })

    df = pd.DataFrame(rows)

    st.dataframe(df,use_container_width=True)


# ==============================
# Document Check
# ==============================

    st.header("📄 Document Verification")

    doc_eval = eligibility["document_evaluation"]

    col1,col2 = st.columns(2)

    with col1:

        st.subheader("Provided Documents")

        for d in doc_eval["provided"]:
            st.markdown(f"✔ {d}")

    with col2:

        st.subheader("Missing Documents")

        if not doc_eval["missing"]:
            st.success("No missing documents")
        else:
            for m in doc_eval["missing"]:
                st.markdown(f"❗ {m}")


# ==============================
# Policy Summary
# ==============================

    st.header("📘 Visa Policy Summary")

    col1,col2 = st.columns(2)

    with col1:

        st.subheader("Eligibility Rules")

        for r in policy["eligibility"]:
            st.markdown(f"- {r}")

    with col2:

        st.subheader("Required Documents")

        for d in policy["required_documents"]:
            st.markdown(f"- {d}")


# ==============================
# Analytics Dashboard
# ==============================

st.divider()

st.header("📊 Decision Analytics Dashboard")

if os.path.exists(LOG_PATH):

    logs = []

    with open(LOG_PATH,"r") as f:
        for line in f:
            logs.append(json.loads(line))

    if logs:

        df = pd.json_normalize(logs)

        total = len(df)

        approvals = df["eligibility_result.final_decision"].str.upper().eq("APPROVED").sum()
        rejects = df["eligibility_result.final_decision"].str.upper().eq("REJECTED").sum()

        avg_conf = round(df["final_confidence"].mean(),2)

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Total Applications", total)
        col2.metric("Approved", approvals)
        col3.metric("Rejected", rejects)
        col4.metric("Avg Confidence", f"{avg_conf}%")

        st.subheader("Risk Distribution")

        risk_counts = df["eligibility_result.risk_level"].value_counts()

        st.bar_chart(risk_counts)

        st.subheader("Recent Decisions")

        display_cols = [
            "country",
            "visa_type",
            "final_confidence",
            "eligibility_result.final_decision",
            "eligibility_result.risk_level"
        ]

        st.dataframe(df[display_cols].tail(10),use_container_width=True)

else:

    st.info("Run evaluations to generate analytics data")