import json
import os
import pandas as pd
import streamlit as st
from config import LOG_PATH

# ================= SAFE FLOAT =================
def safe_float(val):
    try:
        return float(str(val).replace("%", "").strip())
    except:
        return 0.0


# ================= LOAD LOGS =================
def load_logs():
    records = []

    # ✅ Handle missing file safely
    if not os.path.exists(LOG_PATH):
        return records

    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if line.strip():
                    try:
                        entry = json.loads(line)

                        # Fix profile if string
                        if isinstance(entry.get("profile"), str):
                            try:
                                entry["profile"] = json.loads(entry["profile"])
                            except:
                                entry["profile"] = {}

                        # Fix reasoning if string
                        if isinstance(entry.get("reasoning"), str):
                            try:
                                entry["reasoning"] = json.loads(entry["reasoning"])
                            except:
                                entry["reasoning"] = {}

                        records.append(entry)

                    except json.JSONDecodeError as e:
                        st.warning(f"⚠️ Skipped corrupted log at line {line_number}")

    except Exception as e:
        st.error(f"❌ Error loading logs: {e}")
        return []

    return records


# ================= UI =================
st.set_page_config(
    page_title="SwiftVisa Logs Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SwiftVisa Decision Logs Dashboard")

logs = load_logs()

if not logs:
    st.info("ℹ️ No logs found")
    st.stop()


# ================= STRUCTURED DATA =================
structured_data = []

for log in logs:
    profile = log.get("profile", {})
    reasoning = log.get("reasoning", {})

    structured_data.append({
        "name": profile.get("Personal Info", {}).get("Name", "UNKNOWN"),
        "visa_type": profile.get("Visa Details", {}).get("Visa Type", "UNKNOWN"),
        "destination": profile.get("Visa Details", {}).get("Destination", "UNKNOWN"),
        "decision": str(log.get("decision", "UNKNOWN")),
        "risk_level": str(reasoning.get("risk_level", "UNKNOWN")) if isinstance(reasoning, dict) else "UNKNOWN",
        "confidence": safe_float(reasoning.get("confidence_score", 0)) if isinstance(reasoning, dict) else 0.0,
        "timestamp": log.get("timestamp")
    })

df = pd.DataFrame(structured_data)

# ================= CLEAN DATA =================
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ✅ Sort latest first
df = df.sort_values(by="timestamp", ascending=False)

# ================= TABLE =================
st.subheader("📄 Applications Overview")
st.dataframe(df, use_container_width=True)

# ================= DOWNLOAD =================
csv = df.to_csv(index=False)
st.download_button("📥 Download Logs CSV", csv, "visa_logs.csv")

# ================= CHARTS =================
st.subheader("📊 Insights")

decision_counts = df["decision"].value_counts()
risk_counts = df["risk_level"].value_counts()

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Decision Distribution**")
    st.bar_chart(decision_counts)

with col2:
    st.markdown("**Risk Level Distribution**")
    st.bar_chart(risk_counts)

# ================= FILTER =================
st.subheader("🔍 Filter Applications")

col1, col2 = st.columns(2)

with col1:
    visa_filter = st.multiselect(
        "Visa Type",
        options=df["visa_type"].unique(),
        default=df["visa_type"].unique()
    )

with col2:
    decision_filter = st.multiselect(
        "Decision",
        options=df["decision"].unique(),
        default=df["decision"].unique()
    )

filtered_df = df[
    (df["visa_type"].isin(visa_filter)) &
    (df["decision"].isin(decision_filter))
]

st.subheader("📌 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)