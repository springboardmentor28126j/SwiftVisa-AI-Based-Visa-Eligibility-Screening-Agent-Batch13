"""Options for Milestone 3 Streamlit user input form.

Country and visa options are loaded from Milestone 1/2 index artifacts so UI
always reflects the latest corpus.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def _read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_document_index_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        project_root / "milestone1" / "data" / "index" / "document_index.json",
        project_root / "data" / "index" / "document_index.json",
        project_root / "milestone2" / "data" / "index" / "document_index.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("No document_index.json found in milestone1/data, data, or milestone2/data")


def _resolve_metadata_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        project_root / "milestone1" / "data" / "embeddings" / "metadata.json",
        project_root / "data" / "embeddings" / "metadata.json",
        project_root / "milestone2" / "data" / "embeddings" / "metadata.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("No metadata.json found in milestone1/data, data, or milestone2/data")


def _resolve_eligibility_index_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        project_root / "milestone1" / "data" / "index" / "eligibility_index.json",
        project_root / "data" / "index" / "eligibility_index.json",
        project_root / "milestone2" / "data" / "index" / "eligibility_index.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("No eligibility_index.json found in milestone1/data, data, or milestone2/data")


def _load_country_visa_options() -> Tuple[List[str], Dict[str, List[str]]]:
    document_index = _read_json(_resolve_document_index_path())
    by_country = document_index.get("by_country", {})

    if by_country:
        country_options = sorted(by_country.keys())
        visa_options_by_country: Dict[str, List[str]] = {}
        for country_code, visas in by_country.items():
            visa_ids = sorted({item.get("visa_id", "").strip() for item in visas if item.get("visa_id")})
            visa_options_by_country[country_code] = visa_ids if visa_ids else ["Visitor"]
        return country_options, visa_options_by_country

    metadata = _read_json(_resolve_metadata_path())
    visa_options_by_country: Dict[str, set] = {}
    for row in metadata:
        country_code = str(row.get("country_code", "")).strip().upper()
        visa_id = str(row.get("visa_id", "")).strip()
        if not country_code or not visa_id:
            continue
        if country_code not in visa_options_by_country:
            visa_options_by_country[country_code] = set()
        visa_options_by_country[country_code].add(visa_id)

    country_options = sorted(visa_options_by_country.keys())
    visa_options = {key: sorted(value) for key, value in visa_options_by_country.items()}
    return country_options, visa_options


def _load_country_names(country_codes: List[str]) -> Dict[str, str]:
    try:
        eligibility_index = _read_json(_resolve_eligibility_index_path())
        name_by_code: Dict[str, str] = {}
        for item in eligibility_index.values():
            code = str(item.get("country_code", "")).strip().upper()
            name = str(item.get("country_name", "")).strip()
            if code and name and code not in name_by_code:
                name_by_code[code] = name
        return {code: name_by_code.get(code, code) for code in country_codes}
    except Exception:
        return {code: code for code in country_codes}


try:
    COUNTRY_OPTIONS, VISA_OPTIONS_BY_COUNTRY = _load_country_visa_options()
except Exception:
    COUNTRY_OPTIONS, VISA_OPTIONS_BY_COUNTRY = ["CAN"], {"CAN": ["StudyPermit"]}

if not COUNTRY_OPTIONS:
    COUNTRY_OPTIONS = ["CAN"]
if not VISA_OPTIONS_BY_COUNTRY:
    VISA_OPTIONS_BY_COUNTRY = {"CAN": ["StudyPermit"]}

COUNTRY_NAME_BY_CODE = _load_country_names(COUNTRY_OPTIONS)

PURPOSE_OPTIONS = [
    "Study",
    "Tourism",
    "Business",
    "Employment",
    "Family Visit",
    "Transit",
]

ENGLISH_TEST_OPTIONS = ["None", "IELTS", "TOEFL", "PTE", "Duolingo"]

TRAVEL_HISTORY_OPTIONS = ["No prior travel", "Limited travel", "Frequent travel"]

EMPLOYMENT_STATUS_OPTIONS = ["Student", "Employed", "Self-employed", "Unemployed"]

MARITAL_STATUS_OPTIONS = ["Single", "Married", "Divorced", "Widowed"]

EDUCATION_LEVEL_OPTIONS = [
    "High School",
    "Diploma",
    "Bachelor's",
    "Master's",
    "PhD",
]

STAY_DURATION_OPTIONS = [
    "< 1 month",
    "1-3 months",
    "3-6 months",
    "6-12 months",
    "> 12 months",
]

DEPENDENTS_OPTIONS = ["None", "With spouse", "With children", "With spouse and children"]

ACCOMMODATION_OPTIONS = [
    "Not decided",
    "Hotel booking",
    "University housing",
    "Family/Friend invitation",
    "Rental agreement",
]

AGE_GROUP_OPTIONS = ["18-24", "25-34", "35-44", "45+"]
FUNDS_LEVEL_OPTIONS = [
    "Low (< $3,000)",
    "Medium ($3,000 - $10,000)",
    "High (> $10,000)",
]
YES_NO_OPTIONS = ["Yes", "No"]

WIZARD_STEPS = [
    "Personal Information",
    "Travel & Visa Preferences",
    "Documents & Financial Snapshot",
    "Review & Eligibility Check",
]
