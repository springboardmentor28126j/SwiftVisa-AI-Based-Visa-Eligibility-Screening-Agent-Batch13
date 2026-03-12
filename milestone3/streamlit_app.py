"""Milestone 3 Streamlit app."""

import sys
from pathlib import Path

import streamlit as st

try:
	from milestone3.ui.form_renderer import init_session_state, render_user_form, render_submission_preview
except ModuleNotFoundError:
	project_root = Path(__file__).resolve().parents[1]
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))
	from milestone3.ui.form_renderer import init_session_state, render_user_form, render_submission_preview


st.set_page_config(page_title="Swift Visa", page_icon="🛂", layout="wide")

st.title("Swift Visa")
st.caption("AI-assisted Visa Eligibility Checker")
with st.expander("💡 How Swift Visa Helps", expanded=False):

    st.markdown(
        "This tool provides an **AI-assisted direction** for visa eligibility "
        "based on your profile and visa policy documents."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📄 Policy Matching")
        st.write(
            "Your information is checked against local visa "
            "requirements and official policy documents."
        )

    with col2:
        st.markdown("#### 🤖 AI Analysis")
        st.write(
            "AI models analyze your profile to estimate "
            "eligibility likelihood and possible concerns."
        )

    with col3:
        st.markdown("#### 📊 Clear Insights")
        st.write(
            "See strengths, risks, and suggested next steps "
            "before submitting a formal application."
        )

    st.divider()

    st.caption("⚠️ Results are for reference only and are not legal advice.")
st.info(
	"Complete the form step-by-step using Next/Back. "
	"Results are guidance-only and should be verified on official embassy/government websites."
)


init_session_state()
_ = render_user_form()
render_submission_preview()
