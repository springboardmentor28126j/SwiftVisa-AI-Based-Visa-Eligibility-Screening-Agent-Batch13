import json
import pandas as pd
import streamlit as st
from config import LOG_PATH


def load_logs():
    records = []

    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)

                    # Fix profile
                    if isinstance(entry.get("profile"), str):
                        try:
                            entry["profile"] = json.loads(entry["profile"])
                        except:
                            entry["profile"] = {}

                    # Fix reasoning
                    if isinstance(entry.get("reasoning"), str):
                        try:
                            entry["reasoning"] = json.loads(entry["reasoning"])
                        except:
                            entry["reasoning"] = {}

                    records.append(entry)

    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return []

    return records


# ================= UI =================

st.title("📊 SwiftVisa Decision Logs")

logs = load_logs()

if not logs:
    st.info("No logs found")

else:
    # Extract structured fields
    structured_data = []

    for log in logs:
        profile = log.get("profile", {})
        reasoning = log.get("reasoning", {})

        structured_data.append({
            "name": profile.get("Personal Info", {}).get("Name", "UNKNOWN"),
            "visa_type": profile.get("Visa Details", {}).get("Visa Type", "UNKNOWN"),
            "destination": profile.get("Visa Details", {}).get("Destination", "UNKNOWN"),
            "decision": log.get("decision", "UNKNOWN"),
            "risk_level": reasoning.get("risk_level", "UNKNOWN") if isinstance(reasoning, dict) else "UNKNOWN",
            "confidence": reasoning.get("confidence_score", 0) if isinstance(reasoning, dict) else 0,
            "timestamp": log.get("timestamp")
        })

    df = pd.DataFrame(structured_data)

    # Fix timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # ================= TABLE =================
    st.subheader("📄 Applications")
    st.dataframe(df, use_container_width=True)

    # ================= CHARTS =================
    st.subheader("📊 Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Decision Distribution**")
        st.bar_chart(df["decision"].value_counts())

    with col2:
        st.markdown("**Risk Distribution**")
        st.bar_chart(df["risk_level"].value_counts())

    # ================= FILTER =================
    st.subheader("🔍 Filter")

    visa_filter = st.multiselect("Visa Type", df["visa_type"].unique(), default=df["visa_type"].unique())
    decision_filter = st.multiselect("Decision", df["decision"].unique(), default=df["decision"].unique())

    filtered_df = df[
        (df["visa_type"].isin(visa_filter)) &
        (df["decision"].isin(decision_filter))
    ]

    st.dataframe(filtered_df, use_container_width=True)