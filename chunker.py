from email.mime import text
import json
def load_chunks():
    with open("visa_requirements.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    for country in data["countries"]:
        for visa in country["visa_categories"]:

            text = f"""
Country: {country['country_name']}
Visa Type: {visa['visa_name']}
Category: {visa['visa_id']}
Eligibility Fields: {", ".join(visa['eligibility_fields'])}
Documents Required: {", ".join(visa['documents_required'])}
Official Source: {visa['official_source']}
"""

            chunks.append({
                "text": text,
                "search_text": text.lower()
            })
    return chunks 
