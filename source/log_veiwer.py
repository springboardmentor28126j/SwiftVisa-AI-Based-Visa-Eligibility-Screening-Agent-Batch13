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
                    records.append(json.loads(line))
    except:
        return []

    return records


st.title("📊 SwiftVisa Decision Logs")

logs = load_logs()

if not logs:
    st.info("No logs found")
else:

    df = pd.DataFrame(logs)

    st.dataframe(df)

    st.subheader("Risk Distribution")

    risk_levels = [
        log["eligibility_result"]["risk_level"]
        for log in logs
    ]

    risk_df = pd.Series(risk_levels).value_counts()

    st.bar_chart(risk_df)