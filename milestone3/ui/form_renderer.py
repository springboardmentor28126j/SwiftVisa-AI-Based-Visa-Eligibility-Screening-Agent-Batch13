"""Dynamic Streamlit form renderer for Milestone 3."""

import json
import uuid
from pathlib import Path
from typing import Dict, Any

import streamlit as st

try:
    from milestone3.config.form_options import (
        COUNTRY_OPTIONS,
        COUNTRY_NAME_BY_CODE,
        VISA_OPTIONS_BY_COUNTRY,
        AGE_GROUP_OPTIONS,
        PURPOSE_OPTIONS,
        ENGLISH_TEST_OPTIONS,
        TRAVEL_HISTORY_OPTIONS,
        EMPLOYMENT_STATUS_OPTIONS,
        MARITAL_STATUS_OPTIONS,
        EDUCATION_LEVEL_OPTIONS,
        STAY_DURATION_OPTIONS,
        DEPENDENTS_OPTIONS,
        ACCOMMODATION_OPTIONS,
        FUNDS_LEVEL_OPTIONS,
        YES_NO_OPTIONS,
        WIZARD_STEPS,
    )
except ModuleNotFoundError:
    from config.form_options import (
        COUNTRY_OPTIONS,
        COUNTRY_NAME_BY_CODE,
        VISA_OPTIONS_BY_COUNTRY,
        AGE_GROUP_OPTIONS,
        PURPOSE_OPTIONS,
        ENGLISH_TEST_OPTIONS,
        TRAVEL_HISTORY_OPTIONS,
        EMPLOYMENT_STATUS_OPTIONS,
        MARITAL_STATUS_OPTIONS,
        EDUCATION_LEVEL_OPTIONS,
        STAY_DURATION_OPTIONS,
        DEPENDENTS_OPTIONS,
        ACCOMMODATION_OPTIONS,
        FUNDS_LEVEL_OPTIONS,
        YES_NO_OPTIONS,
        WIZARD_STEPS,
    )

try:
    from milestone3.ui.inference_service import run_eligibility_inference, get_dynamic_form_suggestions
except ModuleNotFoundError:
    from ui.inference_service import run_eligibility_inference, get_dynamic_form_suggestions


def _country_label(code: str) -> str:
    return f"{code} - {COUNTRY_NAME_BY_CODE.get(code, code)}"


def _default_form_payload() -> Dict[str, Any]:
    default_country = "CAN" if "CAN" in COUNTRY_OPTIONS else COUNTRY_OPTIONS[0]
    default_visa_options = VISA_OPTIONS_BY_COUNTRY.get(default_country, ["Visitor"])
    return {
        "name": "",
        "age_group": AGE_GROUP_OPTIONS[0],
        "nationality": default_country,
        "destination_country": default_country,
        "visa_type": default_visa_options[0],
        "purpose": PURPOSE_OPTIONS[0],
        "employment_status": EMPLOYMENT_STATUS_OPTIONS[0],
        "marital_status": MARITAL_STATUS_OPTIONS[0],
        "education_level": EDUCATION_LEVEL_OPTIONS[2],
        "dependents": DEPENDENTS_OPTIONS[0],
        "english_test": ENGLISH_TEST_OPTIONS[0],
        "travel_history": TRAVEL_HISTORY_OPTIONS[0],
        "intended_stay_duration": STAY_DURATION_OPTIONS[1],
        "accommodation_status": ACCOMMODATION_OPTIONS[0],
        "funds_level": "Medium ($3,000 - $10,000)",
        "has_passport": YES_NO_OPTIONS[0],
        "has_admission_or_offer_letter": YES_NO_OPTIONS[1],
        "has_financial_proof": YES_NO_OPTIONS[1],
        "has_health_insurance": YES_NO_OPTIONS[1],
        "prior_visa_refusal": YES_NO_OPTIONS[1],
        "has_criminal_record": YES_NO_OPTIONS[1],
        "document_focus": "Passport",
    }


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRAFTS_DIR = PROJECT_ROOT / "milestone3" / "data" / "drafts"
DRAFT_STATE_KEYS = [
    "current_step",
    "submitted",
    "form_payload",
    "inference_result",
    "inference_error",
    "saved_profiles",
    "dynamic_options",
    "dynamic_context_key",
]


def _draft_file_path(draft_id: str) -> Path:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_draft_id = "".join(ch for ch in str(draft_id) if ch.isalnum() or ch in ("-", "_"))
    return DRAFTS_DIR / f"{safe_draft_id or 'default'}.json"


def _ensure_draft_id() -> str:
    query_value = st.query_params.get("draft", "")
    draft_id = query_value[0] if isinstance(query_value, list) and query_value else str(query_value)
    draft_id = str(draft_id).strip()

    if not draft_id:
        draft_id = uuid.uuid4().hex[:12]
        st.query_params["draft"] = draft_id

    return draft_id


def _load_draft(draft_id: str) -> Dict[str, Any]:
    path = _draft_file_path(draft_id)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_draft() -> None:
    draft_id = str(st.session_state.get("draft_id", "")).strip()
    if not draft_id:
        return

    snapshot = {key: st.session_state.get(key) for key in DRAFT_STATE_KEYS}
    try:
        with open(_draft_file_path(draft_id), "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
    except Exception:
        return


def _delete_draft(draft_id: str) -> None:
    if not draft_id:
        return
    try:
        _draft_file_path(draft_id).unlink(missing_ok=True)
    except Exception:
        return


def _restore_draft_if_available() -> None:
    if st.session_state.get("draft_loaded"):
        return

    draft_id = st.session_state.get("draft_id", "")
    draft_data = _load_draft(str(draft_id))
    if draft_data:
        for key in DRAFT_STATE_KEYS:
            if key in draft_data:
                if key == "form_payload" and isinstance(draft_data[key], dict):
                    merged_payload = _default_form_payload()
                    merged_payload.update(draft_data[key])
                    st.session_state[key] = merged_payload
                else:
                    st.session_state[key] = draft_data[key]

    st.session_state["draft_loaded"] = True


def init_session_state() -> None:
    defaults = {
        "current_step": 1,
        "submitted": False,
        "form_payload": _default_form_payload(),
        "inference_result": None,
        "inference_error": "",
        "saved_profiles": [],
        "dynamic_options": {
            "purpose_options": PURPOSE_OPTIONS,
            "stay_duration_options": STAY_DURATION_OPTIONS,
            "funds_options": [
                "Low (< $3,000)",
                "Medium ($3,000 - $10,000)",
                "High (> $10,000)",
            ],
            "document_focus_options": ["Passport", "Application Form"],
            "eligibility_hint": "",
        },
        "dynamic_context_key": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "draft_id" not in st.session_state:
        st.session_state["draft_id"] = _ensure_draft_id()

    _restore_draft_if_available()
    _save_draft()


def _validate_step(step: int, payload: Dict[str, Any]) -> str:
    if step == 1:
        name = str(payload.get("name", "")).strip()
        if len(name) < 2:
            return "Please enter your full name (at least 2 characters)."
        if not any(char.isalpha() for char in name):
            return "Name should contain alphabetic characters."
    elif step == 2:
        destination_country = payload.get("destination_country")
        visa_type = payload.get("visa_type")
        valid_visas = VISA_OPTIONS_BY_COUNTRY.get(destination_country, [])
        if not valid_visas:
            return "No visa options found for selected destination country."
        if visa_type not in valid_visas:
            return "Selected visa type is not valid for destination country."
    elif step == 3:
        if payload.get("has_passport") != "Yes":
            return "A valid passport is required to continue eligibility checks."
        if payload.get("purpose") == "Study" and payload.get("has_admission_or_offer_letter") != "Yes":
            return "For study intent, admission/offer letter is usually required."
        if payload.get("has_criminal_record") == "Yes":
            return "Criminal record may strongly affect approval. Please verify with official embassy guidance."
    return ""


def _render_step_indicator() -> None:
    current_step = st.session_state["current_step"]
    st.progress(current_step / len(WIZARD_STEPS))
    st.caption(f"Step {current_step} of {len(WIZARD_STEPS)} - {WIZARD_STEPS[current_step - 1]}")
    st.caption(f"Saved user profiles in this session: {len(st.session_state.get('saved_profiles', []))}")


def _refresh_dynamic_options(payload: Dict[str, Any]) -> None:
    context_key = "|".join(
        [
            str(payload.get("nationality", "")),
            str(payload.get("destination_country", "")),
            str(payload.get("visa_type", "")),
        ]
    )

    if context_key == st.session_state.get("dynamic_context_key"):
        return

    options = get_dynamic_form_suggestions(
        nationality=str(payload.get("nationality", "")),
        destination_country=str(payload.get("destination_country", "")),
        visa_id=str(payload.get("visa_type", "")),
        use_ai_hints=True,
    )

    if options:
        st.session_state["dynamic_options"] = options
        st.session_state["dynamic_context_key"] = context_key


def _render_step_personal(payload: Dict[str, Any]) -> None:
    
    st.subheader("Step 1: Personal Information")


    payload["name"] = st.text_input("Full Name *", value=payload.get("name", ""), max_chars=80)

    c1, c2 = st.columns(2)
    with c1:
        payload["age_group"] = st.selectbox("Age Group", AGE_GROUP_OPTIONS, index=AGE_GROUP_OPTIONS.index(payload["age_group"]))
        payload["nationality"] = st.selectbox(
            "Nationality",
            COUNTRY_OPTIONS,
            index=COUNTRY_OPTIONS.index(payload["nationality"]),
            format_func=_country_label,
        )
    with c2:
        payload["employment_status"] = st.selectbox(
            "Employment Status",
            EMPLOYMENT_STATUS_OPTIONS,
            index=EMPLOYMENT_STATUS_OPTIONS.index(payload["employment_status"]),
        )
        payload["marital_status"] = st.selectbox(
            "Marital Status",
            MARITAL_STATUS_OPTIONS,
            index=MARITAL_STATUS_OPTIONS.index(payload["marital_status"]),
        )
        payload["education_level"] = st.selectbox(
            "Education Level",
            EDUCATION_LEVEL_OPTIONS,
            index=EDUCATION_LEVEL_OPTIONS.index(payload["education_level"]),
        )


def _render_step_travel(payload: Dict[str, Any]) -> None:
    st.subheader("Step 2: Travel & Visa Preferences")
    payload["destination_country"] = st.selectbox(
        "Destination Country",
        COUNTRY_OPTIONS,
        index=COUNTRY_OPTIONS.index(payload["destination_country"]),
        format_func=_country_label,
    )

    visa_options = VISA_OPTIONS_BY_COUNTRY.get(payload["destination_country"], [])
    if not visa_options:
        st.error("No visa types available for selected country in local corpus.")
        payload["visa_type"] = ""
    else:
        if payload.get("visa_type") not in visa_options:
            payload["visa_type"] = visa_options[0]
        payload["visa_type"] = st.selectbox(
            "Visa Type",
            visa_options,
            index=visa_options.index(payload["visa_type"]),
        )

    _refresh_dynamic_options(payload) 
    dynamic_options = st.session_state.get("dynamic_options", {})
    purpose_options = dynamic_options.get("purpose_options", PURPOSE_OPTIONS)
    stay_options = dynamic_options.get("stay_duration_options", STAY_DURATION_OPTIONS)

    if payload.get("purpose") not in purpose_options:
        payload["purpose"] = purpose_options[0]
    if payload.get("intended_stay_duration") not in stay_options:
        payload["intended_stay_duration"] = stay_options[0]

    c1, c2 = st.columns(2)
    with c1:
        payload["purpose"] = st.selectbox("Purpose of Visit", purpose_options, index=purpose_options.index(payload["purpose"]))
        payload["intended_stay_duration"] = st.selectbox(
            "Intended Stay Duration",
            stay_options,
            index=stay_options.index(payload["intended_stay_duration"]),
        )
    with c2:
        payload["travel_history"] = st.selectbox(
            "Travel History",
            TRAVEL_HISTORY_OPTIONS,
            index=TRAVEL_HISTORY_OPTIONS.index(payload["travel_history"]),
        )
        payload["dependents"] = st.selectbox(
            "Traveling Dependents",
            DEPENDENTS_OPTIONS,
            index=DEPENDENTS_OPTIONS.index(payload["dependents"]),
        )
        payload["accommodation_status"] = st.selectbox(
            "Accommodation Status",
            ACCOMMODATION_OPTIONS,
            index=ACCOMMODATION_OPTIONS.index(payload["accommodation_status"]),
        )

    hint = dynamic_options.get("eligibility_hint", "")
    if hint:
        st.caption(f"Policy hint for selected visa: {hint}")


def _render_step_documents(payload: Dict[str, Any]) -> None:
    st.subheader("Step 3: Documents & Financial Snapshot")
    st.info("Provide current document readiness. This improves eligibility assessment quality.")

    dynamic_options = st.session_state.get("dynamic_options", {})
    funds_options = dynamic_options.get(
        "funds_options",
        ["Low (< $3,000)", "Medium ($3,000 - $10,000)", "High (> $10,000)"],
    )
    document_focus_options = dynamic_options.get("document_focus_options", ["Passport", "Application Form"])

    if payload.get("funds_level") not in funds_options:
        payload["funds_level"] = funds_options[0]
    if payload.get("document_focus") not in document_focus_options:
        payload["document_focus"] = document_focus_options[0]

    c1, c2 = st.columns(2)
    with c1:
        payload["english_test"] = st.selectbox(
            "English Test",
            ENGLISH_TEST_OPTIONS,
            index=ENGLISH_TEST_OPTIONS.index(payload["english_test"]),
        )
        payload["funds_level"] = st.selectbox(
            "Financial Capacity",
            funds_options,
            index=funds_options.index(payload["funds_level"]),
        )
        payload["document_focus"] = st.selectbox(
            "Most Important Supporting Document You Can Provide",
            document_focus_options,
            index=document_focus_options.index(payload["document_focus"]),
        )
        payload["has_financial_proof"] = st.radio(
            "Bank/Financial Proof Ready?",
            YES_NO_OPTIONS,
            index=YES_NO_OPTIONS.index(payload["has_financial_proof"]),
            horizontal=True,
        )
    with c2:
        payload["has_passport"] = st.radio(
            "Valid Passport Available?",
            YES_NO_OPTIONS,
            index=YES_NO_OPTIONS.index(payload["has_passport"]),
            horizontal=True,
        )
        payload["has_admission_or_offer_letter"] = st.radio(
            "Admission/Offer Letter Available?",
            YES_NO_OPTIONS,
            index=YES_NO_OPTIONS.index(payload["has_admission_or_offer_letter"]),
            horizontal=True,
        )
        payload["has_health_insurance"] = st.radio(
            "Health Insurance Available?",
            YES_NO_OPTIONS,
            index=YES_NO_OPTIONS.index(payload["has_health_insurance"]),
            horizontal=True,
        )
        payload["prior_visa_refusal"] = st.radio(
            "Any Prior Visa Refusal?",
            YES_NO_OPTIONS,
            index=YES_NO_OPTIONS.index(payload["prior_visa_refusal"]),
            horizontal=True,
        )
        payload["has_criminal_record"] = st.radio(
            "Any Criminal Record?",
            YES_NO_OPTIONS,
            index=YES_NO_OPTIONS.index(payload["has_criminal_record"]),
            horizontal=True,
        )


def _render_step_review(payload: Dict[str, Any]) -> None:
    st.subheader("Step 4: Review & Eligibility Check")
    st.write("Please review your details, then run the eligibility check.")

    with st.container(border=True):
        st.markdown("#### 👤 Applicant Profile")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {payload.get('name', 'N/A')}")
            st.write(f"**Nationality:** {_country_label(payload.get('nationality', ''))}")
            st.write(f"**Age Group:** {payload.get('age_group', 'N/A')}")
            st.write(f"**Employment:** {payload.get('employment_status', 'N/A')}")
            st.write(f"**Education:** {payload.get('education_level', 'N/A')}")
        with c2:
            st.write(f"**Destination:** {_country_label(payload.get('destination_country', ''))}")
            st.write(f"**Visa Type:** {payload.get('visa_type', 'N/A')}")
            st.write(f"**Purpose:** {payload.get('purpose', 'N/A')}")
            st.write(f"**Funds Level:** {payload.get('funds_level', 'N/A')}")
            st.write(f"**Stay Duration:** {payload.get('intended_stay_duration', 'N/A')}")

    if st.button("Run Eligibility Check", type="primary"):
        with st.spinner("Analyzing local policy documents and generating your personalized eligibility report..."):
            result, error = run_eligibility_inference(payload, top_k=5)
            st.session_state["inference_result"] = result if result else None
            st.session_state["inference_error"] = error
            st.session_state["submitted"] = bool(result)
            _save_draft()
            st.rerun()


def _status_visual(status: str) -> tuple[str, str]:
    status = (status or "").upper()
    if status == "ELIGIBLE":
        return "🟢", "You appear strongly aligned with policy requirements."
    if status == "PARTIAL":
        return "🟠", "You may qualify, but some requirements are still missing or unclear."
    if status == "NOT_ELIGIBLE":
        return "🔴", "Current profile shows major policy gaps."
    return "🟡", "Available information is not enough for a final decision."


def _normalize_list_field(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []

        if "\n" in text:
            lines = []
            for line in text.splitlines():
                cleaned = line.strip().lstrip("-•*0123456789. ").strip()
                if cleaned:
                    lines.append(cleaned)
            if lines:
                return lines

        parts = [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]
        if len(parts) > 1:
            return parts

        return [text]
    return []


def render_user_form() -> Dict[str, Any]:
    payload = st.session_state["form_payload"]
    current_step = st.session_state["current_step"]

    _render_step_indicator()

    if current_step == 1:
        _render_step_personal(payload)
    elif current_step == 2:
        _render_step_travel(payload)
    elif current_step == 3:
        _render_step_documents(payload)
    else:
        _render_step_review(payload)

    col_back, col_next = st.columns([1, 1])

    with col_back:
        if current_step > 1 and st.button("⬅ Back"):
            st.session_state["current_step"] -= 1
            _save_draft()
            st.rerun()

    with col_next:
        if current_step < len(WIZARD_STEPS) and st.button("Next ➡", type="primary"):
            error = _validate_step(current_step, payload)
            if error:
                st.error(error)
            else:
                st.session_state["current_step"] += 1
                _save_draft()
                st.rerun()

    _save_draft()
    return payload


def render_submission_preview() -> None:
    error = st.session_state.get("inference_error", "")
    result = st.session_state.get("inference_result")

    if error:
        st.error(error)

    if not result:
        return

    response = result.get("response", {})
    ui_report = result.get("ui_report", {})
    payload = st.session_state.get("form_payload", {})

    st.success("Eligibility assessment generated successfully.")

    status = str(response.get("eligibility_status", "N/A"))
    confidence = float(response.get("confidence_score", 0.0) or 0.0)

    icon, status_note = _status_visual(status)

    with st.container(border=True):
        st.markdown("### 1) Final Decision")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Eligibility", f"{icon} {status}")
            st.metric("Confidence", f"{confidence*100:.1f} %")
        with col2:
            st.markdown("#### Decision Summary")
            st.write(ui_report.get("headline", response.get("explanation", "No summary available.")))
            st.info(status_note)
            st.progress(min(max(confidence, 0.0), 1.0))
            st.caption(ui_report.get("confidence_note", "Confidence is estimated from model + retrieval alignment."))

    with st.container(border=True):
        st.markdown("### 2) Applicant Snapshot")
        user_name = payload.get("name", "Applicant")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {user_name}")
            st.write(f"**Nationality:** {_country_label(payload.get('nationality', ''))}")
            st.write(f"**Destination:** {_country_label(payload.get('destination_country', ''))}")
        with c2:
            st.write(f"**Visa Type:** {payload.get('visa_type', 'N/A')}")
            st.write(f"**Purpose:** {payload.get('purpose', 'N/A')}")
            st.write(f"**Intended Stay:** {payload.get('intended_stay_duration', 'N/A')}")

    with st.container(border=True):
        st.markdown("### 3) What This Means For You")
        st.write(ui_report.get("overview", response.get("explanation", "No overview available.")))

    strengths = _normalize_list_field(ui_report.get("strengths", []))
    risks = _normalize_list_field(ui_report.get("risks", []))
    action_plan = _normalize_list_field(ui_report.get("action_plan", []))

    with st.container(border=True):
        st.markdown("### 4) Strengths, Risks & Action Plan")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ✅ Strengths")
            if strengths:
                for item in strengths:
                    st.write(f"- {item}")
            else:
                st.write("- No strengths identified yet.")
        with c2:
            st.markdown("#### ⚠️ Risks / Gaps")
            if risks:
                for item in risks:
                    st.write(f"- {item}")
            else:
                st.write("- No major risks identified.")

        st.markdown("#### 🎯 Recommended Next Actions")
        if action_plan:
            for idx, item in enumerate(action_plan, 1):
                st.write(f"{idx}. {item}")
        else:
            st.write("1. Review your documents and proceed with official application steps.")

    with st.container(border=True):
        st.markdown("### 5) AI Usage Notice")
        st.info("This result is AI-assisted and provided for reference only.")
        st.caption("Always validate requirements on official embassy or immigration websites before applying.")

    with st.expander("🧠 AI Recommendation Notes", expanded=False):
        st.write("This guidance is generated from local policy documents and AI reasoning.")
        st.write("Always verify final requirements on official embassy/government websites before applying.")
        st.warning("Do not rely only on AI for legal/immigration decisions.")

    st.divider()
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("🔄 Reset App (Erase all current data)"):
            _delete_draft(str(st.session_state.get("draft_id", "")))
            st.query_params.clear()
            st.session_state.clear()
            st.rerun()

    with action_col2:
        if st.button("💾 Save Current & Check Another User"):
            saved_profiles = st.session_state.get("saved_profiles", [])
            saved_profiles.append(
                {
                    "profile": payload,
                    "result_summary": {
                        "eligibility_status": status,
                        "confidence_score": confidence,
                        "headline": ui_report.get("headline", ""),
                    },
                }
            )
            st.session_state["saved_profiles"] = saved_profiles
            st.session_state["current_step"] = 1
            st.session_state["submitted"] = False
            st.session_state["inference_result"] = None
            st.session_state["inference_error"] = ""
            st.session_state["form_payload"] = _default_form_payload()
            _save_draft()
            st.success("Current user saved. You can now enter details for a new user.")
            st.rerun()
