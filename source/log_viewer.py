# log_viewer.py

import json
import pandas as pd
import streamlit as st
from config import LOG_PATH

# ================= CONFIG =================
st.set_page_config(page_title="SwiftVisa Logs", layout="wide")

MAX_ROWS_DISPLAY = 200
MAX_LOG_LINES = 500  # Prevent overload


# ================= LOAD LOGS (CACHED) =================
@st.cache_data
def load_logs(max_lines=MAX_LOG_LINES):
    records = []

    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):

                # Limit number of lines (prevents crash)
                if i >= max_lines:
                    break

                if line.strip():
                    try:
                        entry = json.loads(line)
                    except:
                        continue  # skip bad JSON

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
    structured_data = []

    for log in logs:
        profile = log.get("profile", {})
        reasoning = log.get("reasoning", {})

        # Fix decision field (dict OR string)
        decision_raw = log.get("decision", "UNKNOWN")
        if isinstance(decision_raw, dict):
            decision = decision_raw.get("final_decision", "UNKNOWN")
        else:
            decision = decision_raw

        # Ensure reasoning is dict
        if not isinstance(reasoning, dict):
            reasoning = {}

        structured_data.append({
            "name": profile.get("Personal Info", {}).get("Name", "UNKNOWN"),
            "visa_type": profile.get("Visa Details", {}).get("Visa Type", "UNKNOWN"),
            "destination": profile.get("Visa Details", {}).get("Destination", "UNKNOWN"),
            "decision": str(decision),
            "risk_level": str(reasoning.get("risk_level", "UNKNOWN")),
            "confidence": reasoning.get("confidence_score", 0),
            "timestamp": log.get("timestamp")
        })

    df = pd.DataFrame(structured_data)

    # ================= CLEAN DATA =================
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df = df.sort_values(by="timestamp", ascending=False)

    # ================= SUMMARY =================
    st.subheader("📊 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Applications", len(df))
    col2.metric("Unique Visa Types", df["visa_type"].nunique())
    col3.metric("Decisions", df["decision"].nunique())

    # ================= FILTER =================
    st.subheader("🔍 Filters")

    col1, col2 = st.columns(2)

    visa_options = sorted(df["visa_type"].dropna().unique())
    decision_options = sorted(df["decision"].dropna().unique())

    with col1:
        visa_filter = st.multiselect(
            "Visa Type",
            options=visa_options,
            default=visa_options
        )

    with col2:
        decision_filter = st.multiselect(
            "Decision",
            options=decision_options,
            default=decision_options
        )

    # Date filter
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()

    date_range = st.date_input(
        "Filter by Date",
        value=(min_date, max_date)
    )

    # Apply filters
    filtered_df = df[
        (df["visa_type"].isin(visa_filter)) &
        (df["decision"].isin(decision_filter)) &
        (df["timestamp"].dt.date >= date_range[0]) &
        (df["timestamp"].dt.date <= date_range[1])
    ]

    # ================= TABLE =================
    st.subheader("📄 Applications")

    st.dataframe(
        filtered_df.head(MAX_ROWS_DISPLAY),
        use_container_width=True
    )

    # ================= CHARTS =================
    st.subheader("📊 Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Decision Distribution**")
        st.bar_chart(filtered_df["decision"].value_counts())

    with col2:
        st.markdown("**Risk Distribution**")
        st.bar_chart(filtered_df["risk_level"].value_counts())

    # ================= DOWNLOAD =================
    st.subheader("📥 Export Data")

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="Download Filtered Logs CSV",
        data=csv,
        file_name="swiftvisa_logs.csv",
        mime="text/csv"
    )