"""
SwiftVisa - Milestone 1: Policy Document Chunking
Reads extracted policies from JSON and splits into chunks for RAG

Author: [Your Name]
Date: 2026
Milestone: 1 - Knowledge Base Creation
"""

import json
from pathlib import Path
from typing import List, Dict


class PolicyChunker:
    """Chunk policy documents into smaller pieces for RAG"""
    
    def __init__(self, 
                 input_file: str = "data/all_extracted_policies.json",
                 output_dir: str = "data/chunks",
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Input: {self.input_file}")
        print(f"📁 Output: {self.output_dir}")
        print(f"📏 Chunk size: {chunk_size} characters")
        print(f"📏 Chunk overlap: {chunk_overlap} characters")
        print("=" * 70)
    
    def load_policies_from_json(self) -> List[Dict]:
        """Load policies from consolidated JSON file"""
        if not self.input_file.exists():
            return []
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('policies', [])
    
    def chunk_text(self, text: str, policy_id: str, country: str, visa_type: str) -> List[Dict]:
        """Split text into overlapping chunks with metadata"""
        chunks = []
        chunk_id = 0
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # If paragraph fits in current chunk
            if current_length + para_length <= self.chunk_size:
                current_chunk += para + "\n\n"
                current_length += para_length + 2
            else:
                # Save current chunk if not empty
                if current_chunk.strip():
                    chunks.append({
                        "chunk_id": f"{policy_id}_chunk_{chunk_id}",
                        "content": current_chunk.strip(),
                        "country": country,
                        "visa_type": visa_type,
                        "length": len(current_chunk)
                    })
                    chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                current_chunk = overlap_text + para + "\n\n"
                current_length = len(current_chunk)
        
        # Save last chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": f"{policy_id}_chunk_{chunk_id}",
                "content": current_chunk.strip(),
                "country": country,
                "visa_type": visa_type,
                "length": len(current_chunk)
            })
        
        return chunks
    
    def process_all_policies(self) -> int:
        """Process all policies and create chunks"""
        total_chunks = 0
        
        # Load policies from JSON
        print(f"\n📖 Loading policies from: {self.input_file}")
        policies = self.load_policies_from_json()
        
        if not policies:
            print(f"❌ No policies found in {self.input_file}")
            print("   Run extract_raw_data.py first!")
            return 0
        
        print(f"✅ Loaded {len(policies)} policies")
        
        all_chunks = []
        
        for policy in policies:
            country = policy.get('country', 'Unknown')
            visa_type = policy.get('visa_type', 'Unknown')
            policy_id = policy.get('id', 'unknown')
            
            # Get full text content
            content = policy.get('content', {})
            full_text = content.get('full_text', '')
            
            if not full_text:
                # Try to build text from sections
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
            
            print(f"\n📄 Chunking: {country} - {visa_type}")
            
            # Chunk the text
            chunks = self.chunk_text(full_text, policy_id, country, visa_type)
            all_chunks.extend(chunks)
            
            print(f"   ✅ Created {len(chunks)} chunks")
            total_chunks += len(chunks)
        
        # Save all chunks to single file
        if all_chunks:
            output_file = self.output_dir / "policy_chunks.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                for chunk in all_chunks:
                    f.write(f"---CHUNK: {chunk['chunk_id']}---\n")
                    f.write(f"## {chunk['country']} - {chunk['visa_type']} Visa\n\n")
                    f.write(chunk['content'])
                    f.write("\n\n")
            
            print(f"\n💾 Saved {total_chunks} chunks to {output_file}")
        
        return total_chunks


def main():
    """Main entry point for chunking policy documents"""
    print("=" * 70)
    print("📄 SwiftVisa - Chunk Policy Documents")
    print("=" * 70)
    
    chunker = PolicyChunker(
        input_file="data/all_extracted_policies.json",
        output_dir="data/chunks",
        chunk_size=500,
        chunk_overlap=50
    )
    
    total_chunks = chunker.process_all_policies()
    
    print("\n" + "=" * 70)
    print(f"✅ CHUNKING COMPLETE: {total_chunks} chunks created")
    print("=" * 70)
    print("\n📋 Next Step:")
    print("   Run: python create_vectorstore.py")
    print("=" * 70)


if __name__ == "__main__":
    main()