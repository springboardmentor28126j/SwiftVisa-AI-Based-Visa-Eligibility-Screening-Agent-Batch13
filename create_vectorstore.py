"""
SwiftVisa - Milestone 1: Create FAISS Vector Store
Generates embeddings for all policy chunks and stores in FAISS index

Author: [Your Name]
Date: 2026
Milestone: 1 - Knowledge Base Creation
"""

import json
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def load_chunks_from_json(json_file: str = "data/all_extracted_policies.json"):
    """Load chunks from consolidated JSON file"""
    chunks = []
    
    if not Path(json_file).exists():
        print(f"❌ JSON file not found: {json_file}")
        print("   Run extract_raw_data.py first!")
        return chunks
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    policies = data.get('policies', [])
    
    for policy in policies:
        country = policy.get('country', 'Unknown')
        visa_type = policy.get('visa_type', 'Unknown')
        policy_id = policy.get('id', 'unknown')
        
        # Build content from structured data
        content = policy.get('content', {})
        full_text = content.get('full_text', '')
        
        if not full_text:
            full_text = f"""## {country} - {visa_type} Visa

REQUIREMENTS:
{content.get('requirements', 'Not specified')}

REQUIRED DOCUMENTS:
{content.get('required_documents', 'Not specified')}

PROCESSING TIME:
{content.get('processing_time', 'Not specified')}

FEES:
{content.get('fees', 'Not specified')}
"""
        
        # Create metadata
        metadata = {
            'chunk_id': policy_id,
            'country': country,
            'visa_type': visa_type,
            'source_file': policy.get('source_file', 'unknown'),
            'extraction_date': policy.get('extraction_date', 'unknown')
        }
        
        # Create document
        doc = Document(page_content=full_text, metadata=metadata)
        chunks.append(doc)
    
    return chunks


def load_chunks_from_txt(txt_file: str = "data/chunks/policy_chunks.txt"):
    """Load chunks from chunked text file (alternative method)"""
    chunks = []
    
    if not Path(txt_file).exists():
        return chunks
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunk_blocks = content.split('---CHUNK:')
    
    for block in chunk_blocks[1:]:
        if not block.strip():
            continue
        
        parts = block.split('---\n', 1)
        if len(parts) < 2:
            continue
        
        chunk_id = parts[0].strip()
        chunk_content = parts[1].strip()
        
        metadata = {'chunk_id': chunk_id, 'source': 'policy_chunks.txt'}
        
        # Extract country and visa from content
        lines = chunk_content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if line.startswith('## ') and '-' in line:
                header_parts = line.replace('##', '').strip().split('-')
                if len(header_parts) >= 2:
                    metadata['country'] = header_parts[0].strip()
                    metadata['visa_type'] = header_parts[1].replace('Visa', '').strip()
        
        doc = Document(page_content=chunk_content, metadata=metadata)
        chunks.append(doc)
    
    return chunks


def main():
    """Main entry point for creating FAISS vector store"""
    print("🗄️  SwiftVisa - Create FAISS Vector Store")
    print("=" * 70)
    
    JSON_INPUT = "data/all_extracted_policies.json"
    CHUNKS_INPUT = "data/chunks/policy_chunks.txt"
    OUTPUT_DIR = "vectorstore"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    print(f"JSON Input:  {JSON_INPUT}")
    print(f"Chunks Input: {CHUNKS_INPUT}")
    print(f"Output: {OUTPUT_DIR}/")
    print(f"Model:  {EMBEDDING_MODEL}")
    print("=" * 70)
    
    # Try to load from JSON first (from extract_raw_data.py)
    print(f"\n📖 Loading chunks from JSON...")
    chunks = load_chunks_from_json(JSON_INPUT)
    
    # If no JSON, try chunks file (from chunk_policies.py)
    if not chunks:
        print(f"   ⚠️  No chunks from JSON, trying chunks file...")
        chunks = load_chunks_from_txt(CHUNKS_INPUT)
    
    # If still no chunks, check policies folder (from create_document_index.py)
    if not chunks:
        print(f"   ⚠️  No chunks file, checking policies folder...")
        policy_files = list(Path("data/policies").glob("*.txt"))
        if policy_files:
            print(f"   📄 Found {len(policy_files)} policy files")
            print(f"   ⚠️  You need to run chunk_policies.py first!")
            print(f"\n   Recommended workflow:")
            print(f"   1. python extract_raw_data.py  OR  python create_document_index.py")
            print(f"   2. python chunk_policies.py")
            print(f"   3. python create_vectorstore.py")
            return
        else:
            print(f"   ❌ No policy files found!")
            print(f"   Run extract_raw_data.py or create_document_index.py first!")
            return
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Load embedding model
    print(f"\n🧠 Generating embeddings with model: {EMBEDDING_MODEL}")
    print("   (This may take 2-5 minutes)")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Create vector store
    print(f"\n💾 Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save vector store
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(OUTPUT_DIR)
    
    print(f"\n✨ Vector store creation complete!")
    print(f"📁 Files created:")
    print(f"   • {OUTPUT_DIR}/index.faiss")
    print(f"   • {OUTPUT_DIR}/index.pkl")
    
    # Show statistics
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Embedding dimensions: 384")
    
    # Show country distribution
    country_count = {}
    for chunk in chunks:
        country = chunk.metadata.get('country', 'Unknown')
        country_count[country] = country_count.get(country, 0) + 1
    
    print(f"\n📋 Chunks by country (top 5):")
    for country, count in sorted(country_count.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {country}: {count} chunks")
    
    print("\n" + "=" * 70)
    print("✅ MILESTONE 1 COMPLETE - Ready for Milestone 2!")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("   1. Verify: Test-Path vectorstore/index.faiss")
    print("   2. Milestone 2: python test_rag_line_by_line.py")
    print("   3. Milestone 2: python eligibility_screener.py")
    print("   4. Milestone 3: streamlit run app.py")
    print("=" * 70)


if __name__ == "__main__":
    main()