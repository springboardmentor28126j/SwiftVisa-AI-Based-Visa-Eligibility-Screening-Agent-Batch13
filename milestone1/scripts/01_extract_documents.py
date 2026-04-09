"""
Script to extract and organize visa policy documents from raw JSON data.
This creates structured text documents for each visa type.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / 'rawData' / 'visaRequirements.json'
DOCS_DIR = PROJECT_ROOT / 'data' / 'documents'

# Load the raw visa requirements data
def load_visa_data():
    """Load visa requirements from JSON file"""
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_visa_document(country_code, country_name, visa_category):
    """Create a structured text document for a visa category"""
    
    document = f"""
VISA POLICY DOCUMENT
====================

Country: {country_name} ({country_code})
Visa Type: {visa_category['visa_name']} ({visa_category['visa_id']})
Official Source: {visa_category['official_source']}

ELIGIBILITY REQUIREMENTS
------------------------
"""
    
    for idx, field in enumerate(visa_category['eligibility_fields'], 1):
        document += f"{idx}. {field}\n"
    
    document += f"""
REQUIRED DOCUMENTS
------------------
"""
    
    for idx, doc in enumerate(visa_category['documents_required'], 1):
        document += f"{idx}. {doc}\n"
    
    document += f"""
METADATA
--------
- Country Code: {country_code}
- Country Name: {country_name}
- Visa ID: {visa_category['visa_id']}
- Visa Name: {visa_category['visa_name']}
"""
    
    return document

def main():
    """Main function to extract and save visa documents"""
    
    print("📋 Loading visa requirements data...")
    visa_data = load_visa_data()
    
    # Create documents directory if it doesn't exist
    docs_dir = DOCS_DIR
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    total_visas = 0
    
    print(f"\n📝 Extracting visa documents for {len(visa_data['countries'])} countries...")
    
    for country in visa_data['countries']:
        country_code = country['country_code']
        country_name = country['country_name']
        
        # Create a subdirectory for each country
        country_dir = docs_dir / country_code
        country_dir.mkdir(exist_ok=True)
        
        for visa_category in country['visa_categories']:
            # Create document content
            doc_content = create_visa_document(country_code, country_name, visa_category)
            
            # Save to file
            filename = f"{visa_category['visa_id'].replace('/', '_')}.txt"
            filepath = country_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            total_visas += 1
            print(f"  ✓ Created: {country_code}/{filename}")
    
    print(f"\n✅ Successfully extracted {total_visas} visa documents across {len(visa_data['countries'])} countries")
    print(f"📁 Documents saved in: {docs_dir.absolute()}")

if __name__ == "__main__":
    main()
