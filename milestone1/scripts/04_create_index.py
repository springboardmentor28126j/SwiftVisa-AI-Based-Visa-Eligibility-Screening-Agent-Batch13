"""
Script to create a searchable document index organized by visa type and country.
This creates a structured index for easy navigation and retrieval.
"""

import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EMBEDDINGS_METADATA_PATH = PROJECT_ROOT / 'data' / 'embeddings' / 'metadata.json'
RAW_DATA_PATH = PROJECT_ROOT / 'rawData' / 'visaRequirements.json'
INDEX_DIR = PROJECT_ROOT / 'data' / 'index'

def create_document_index():
    """Create an organized index of all visa documents"""
    
    # Load metadata
    metadata_path = EMBEDDINGS_METADATA_PATH
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Organize by country
    by_country = defaultdict(list)
    by_visa_type = defaultdict(list)
    
    # Track unique visa categories
    all_countries = set()
    all_visa_types = set()
    
    for item in metadata:
        country_code = item['country_code']
        visa_id = item['visa_id']
        visa_name = item['visa_name']
        
        all_countries.add(country_code)
        all_visa_types.add(visa_name)
        
        # Organize by country
        if not any(v['visa_id'] == visa_id for v in by_country[country_code]):
            by_country[country_code].append({
                'visa_id': visa_id,
                'visa_name': visa_name,
                'chunk_ids': []
            })
        
        # Add chunk ID to visa
        for visa in by_country[country_code]:
            if visa['visa_id'] == visa_id:
                visa['chunk_ids'].append(item['id'])
        
        # Organize by visa type
        by_visa_type[visa_name].append({
            'country_code': country_code,
            'visa_id': visa_id,
            'chunk_ids': [item['id']]
        })
    
    # Create comprehensive index
    document_index = {
        'summary': {
            'total_countries': len(all_countries),
            'total_visa_types': len(set([v['visa_id'] for country in by_country.values() for v in country])),
            'total_chunks': len(metadata),
            'countries': sorted(all_countries),
            'visa_categories': sorted(all_visa_types)
        },
        'by_country': dict(by_country),
        'by_visa_type': dict(by_visa_type)
    }
    
    return document_index

def create_quick_lookup():
    """Create a quick lookup table for common queries"""
    
    metadata_path = EMBEDDINGS_METADATA_PATH
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    quick_lookup = {}
    
    for item in metadata:
        key = f"{item['country_code']}_{item['visa_id']}"
        if key not in quick_lookup:
            quick_lookup[key] = {
                'country_code': item['country_code'],
                'visa_id': item['visa_id'],
                'visa_name': item['visa_name'],
                'chunk_ids': []
            }
        quick_lookup[key]['chunk_ids'].append(item['id'])
    
    return quick_lookup

def create_eligibility_fields_index():
    """Extract and index eligibility fields from documents"""
    
    # Load raw data
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        visa_data = json.load(f)
    
    eligibility_index = {}
    
    for country in visa_data['countries']:
        country_code = country['country_code']
        
        for visa in country['visa_categories']:
            key = f"{country_code}_{visa['visa_id']}"
            eligibility_index[key] = {
                'country_code': country_code,
                'country_name': country['country_name'],
                'visa_id': visa['visa_id'],
                'visa_name': visa['visa_name'],
                'eligibility_fields': visa['eligibility_fields'],
                'documents_required': visa['documents_required'],
                'official_source': visa['official_source']
            }
    
    return eligibility_index

def main():
    """Main function to create and save all indexes"""
    
    print("📊 Creating document indexes...\n")
    
    index_dir = INDEX_DIR
    index_dir.mkdir(parents=True, exist_ok=True)
    
    # Create main document index
    print("1️⃣  Creating main document index...")
    document_index = create_document_index()
    
    index_path = index_dir / 'document_index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(document_index, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {index_path}")
    
    # Create quick lookup table
    print("\n2️⃣  Creating quick lookup table...")
    quick_lookup = create_quick_lookup()
    
    lookup_path = index_dir / 'quick_lookup.json'
    with open(lookup_path, 'w', encoding='utf-8') as f:
        json.dump(quick_lookup, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {lookup_path}")
    
    # Create eligibility fields index
    print("\n3️⃣  Creating eligibility fields index...")
    eligibility_index = create_eligibility_fields_index()
    
    eligibility_path = index_dir / 'eligibility_index.json'
    with open(eligibility_path, 'w', encoding='utf-8') as f:
        json.dump(eligibility_index, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {eligibility_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("📋 INDEX SUMMARY")
    print("="*60)
    print(f"Total Countries: {document_index['summary']['total_countries']}")
    print(f"Total Visa Types: {document_index['summary']['total_visa_types']}")
    print(f"Total Document Chunks: {document_index['summary']['total_chunks']}")
    print(f"Quick Lookup Entries: {len(quick_lookup)}")
    print(f"Eligibility Index Entries: {len(eligibility_index)}")
    print("="*60)
    
    print("\n✅ All indexes created successfully!")

if __name__ == "__main__":
    main()
