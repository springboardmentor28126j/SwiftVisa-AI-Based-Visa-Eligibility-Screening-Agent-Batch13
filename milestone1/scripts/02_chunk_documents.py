"""
Script to clean and chunk visa policy documents for embedding.
Chunks are created with metadata for better retrieval.
"""

import json
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / 'data' / 'documents'
OUTPUT_FILE = PROJECT_ROOT / 'data' / 'processed_chunks.json'

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove multiple newlines
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text

def chunk_document(doc_path: Path, country_code: str, visa_id: str) -> List[Dict]:
    """
    Chunk a visa document into smaller pieces with metadata.
    For visa documents, we'll create chunks for different sections.
    """
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract visa name from content
    visa_name = ""
    for line in content.split('\n'):
        if line.startswith('Visa Type:'):
            visa_name = line.split('Visa Type:')[1].strip()
            break
    
    chunks = []
    
    # Split document into sections
    sections = content.split('\n\n')
    current_section = ""
    section_name = ""
    
    for section in sections:
        if not section.strip():
            continue
            
        # Detect section headers
        if section.strip() in ['VISA POLICY DOCUMENT', 'ELIGIBILITY REQUIREMENTS', 
                                'REQUIRED DOCUMENTS', 'METADATA']:
            if current_section:
                # Save previous section
                chunk = {
                    'text': clean_text(current_section),
                    'country_code': country_code,
                    'visa_id': visa_id,
                    'visa_name': visa_name,
                    'section': section_name,
                    'doc_path': str(doc_path)
                }
                chunks.append(chunk)
            
            section_name = section.strip()
            current_section = ""
        else:
            current_section += section + "\n\n"
    
    # Add last section
    if current_section:
        chunk = {
            'text': clean_text(current_section),
            'country_code': country_code,
            'visa_id': visa_id,
            'visa_name': visa_name,
            'section': section_name,
            'doc_path': str(doc_path)
        }
        chunks.append(chunk)
    
    # Also create a combined overview chunk
    overview_lines = []
    in_overview = False
    for line in content.split('\n'):
        if 'Country:' in line or 'Visa Type:' in line or 'Official Source:' in line:
            overview_lines.append(line)
            in_overview = True
        elif in_overview and line.startswith('ELIGIBILITY'):
            break
    
    if overview_lines:
        overview_chunk = {
            'text': clean_text('\n'.join(overview_lines)),
            'country_code': country_code,
            'visa_id': visa_id,
            'visa_name': visa_name,
            'section': 'OVERVIEW',
            'doc_path': str(doc_path)
        }
        chunks.insert(0, overview_chunk)
    
    return chunks

def main():
    """Main function to process all documents"""
    
    print("🔄 Starting document cleaning and chunking process...")
    
    docs_dir = DOCS_DIR
    output_file = OUTPUT_FILE
    
    all_chunks = []
    total_docs = 0
    
    # Process each country directory
    for country_dir in sorted(docs_dir.iterdir()):
        if not country_dir.is_dir():
            continue
        
        country_code = country_dir.name
        print(f"\n📂 Processing country: {country_code}")
        
        # Process each visa document
        for doc_file in sorted(country_dir.glob('*.txt')):
            visa_id = doc_file.stem.replace('_', '/')
            
            chunks = chunk_document(doc_file, country_code, visa_id)
            all_chunks.extend(chunks)
            total_docs += 1
            
            print(f"  ✓ Chunked: {visa_id} ({len(chunks)} chunks)")
    
    # Save all chunks to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully processed {total_docs} documents")
    print(f"📦 Created {len(all_chunks)} total chunks")
    print(f"💾 Saved to: {output_file.absolute()}")
    
    # Print sample chunk
    if all_chunks:
        print(f"\n📋 Sample chunk:")
        print(f"   Country: {all_chunks[0]['country_code']}")
        print(f"   Visa: {all_chunks[0]['visa_id']}")
        print(f"   Section: {all_chunks[0]['section']}")
        print(f"   Text preview: {all_chunks[0]['text'][:100]}...")

if __name__ == "__main__":
    main()
