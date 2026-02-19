"""
SwiftVisa - Chunk Clean Policy Text (FIXED VERSION)
Step 2: Take cleaned_policies.txt → split into chunks → save for embedding
"""

import re
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE = "data/cleaned_policies.txt"      # Output from extract_clean_txt.py
OUTPUT_DIR = "data/chunks"                     # Output directory
OUTPUT_FILE = "policy_chunks.txt"              # Output file name

# Chunking parameters
CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 50        # Overlap between chunks  
MIN_CHUNK_LENGTH = 100    # Skip chunks shorter than this


# ============================================================================
# CHUNKING FUNCTION (FIXED SYNTAX)
# ============================================================================

def smart_split(text: str, target_size: int, overlap: int) -> list:
    """
    Split text into chunks with overlap, preferring semantic boundaries.
    FIXED: Valid Python syntax only.
    """
    # If text is short enough, return as single chunk
    if len(text) <= target_size:
        if len(text) >= MIN_CHUNK_LENGTH:
            return [text]
        else:
            return []
    
    chunks = []
    start = 0
    
    # Preferred split points (in order of preference)
    separators = ['\n\n', '\n', '. ', '! ', '? ', ', ', ' ', '']
    
    while start < len(text):
        end = start + target_size
        
        # If at end of text, take remainder
        if end >= len(text):
            chunk = text[start:].strip()
            if len(chunk) >= MIN_CHUNK_LENGTH:
                chunks.append(chunk)
            break
        
        # Find best split point within overlap zone
        best_end = end
        for sep in separators:
            if not sep:
                continue
            # Search in overlap window
            search_start = max(start, end - overlap - len(sep))
            search_end = min(end + overlap, len(text))
            window = text[search_start:search_end]
            
            # Find last occurrence of separator
            pos = window.rfind(sep)
            if pos != -1:
                split_point = search_start + pos + len(sep)
                # Prefer splits near target_size but within overlap
                if start + target_size - overlap <= split_point <= end + overlap:
                    best_end = split_point
                    break
        
        # Extract and clean chunk
        chunk = text[start:best_end].strip()
        if len(chunk) >= MIN_CHUNK_LENGTH:
            chunks.append(chunk)
        
        # Move forward with overlap (FIXED SYNTAX)
        start = best_end - overlap
        if start < 0:
            start = overlap
    
    return chunks


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def chunk_cleaned_file():
    """Read cleaned file, chunk it, and save output"""
    input_path = Path(INPUT_FILE)
    output_dir = Path(OUTPUT_DIR)
    output_path = output_dir / OUTPUT_FILE
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check input file exists
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        print("   Please run extract_clean_txt.py first!")
        return None
    
    print(f"📖 Reading cleaned file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        cleaned_text = f.read()
    
    print(f"✂️  Chunking text (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = smart_split(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)
    
    if not chunks:
        print("❌ No chunks created. Check chunking parameters or input file.")
        return None
    
    print(f"✅ Created {len(chunks)} chunks")
    
    # Save to TXT file with clear delimiters
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# SwiftVisa - Chunked Policy Corpus\n")
        f.write(f"# Chunk size: {CHUNK_SIZE} | Overlap: {CHUNK_OVERLAP} | Min length: {MIN_CHUNK_LENGTH}\n")
        f.write(f"# Total chunks: {len(chunks)}\n")
        f.write(f"# Format: Chunks separated by '---CHUNK:{{id}}---'\n")
        f.write(f"# Ready for embedding → FAISS vector store\n")
        f.write("=" * 80 + "\n\n")
        
        # Write each chunk with delimiter
        for i, chunk in enumerate(chunks, 1):
            f.write(f"---CHUNK:{i}---\n")
            f.write(chunk)
            f.write("\n\n")
    
    print(f"💾 Saved chunked file: {output_path}")
    
    # Show file info
    file_size = output_path.stat().st_size
    print(f"📊 File stats: {file_size:,} bytes, {len(chunks)} chunks")
    print(f"👁️  File is now visible in your VS Code explorer at: {output_path}")
    
    # Show sample preview
    if chunks:
        print(f"\n📄 Sample chunk preview (first chunk):")
        sample = chunks[0]
        lines = sample.split('\n')[:10]
        for line in lines:
            if line.strip():
                preview = line[:70] + '...' if len(line) > 70 else line
                print(f"  {preview}")
    
    return output_path


def main():
    """Entry point"""
    print("✂️  SwiftVisa - Policy Text Chunker (FIXED)")
    print("=" * 70)
    print("Step 2: Chunk cleaned policies → Prepare for embedding")
    print("=" * 70)
    print(f"Input:  {INPUT_FILE}")
    print(f"Output: {OUTPUT_DIR}/{OUTPUT_FILE}")
    print(f"Params: chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}, min_length={MIN_CHUNK_LENGTH}")
    print("-" * 70)
    
    result = chunk_cleaned_file()
    
    if result:
        print(f"\n✨ Step 2 complete!")
        print(f"📁 Check your VS Code explorer: {OUTPUT_DIR}/{OUTPUT_FILE}")
        print(f"🎯 Next: Run create_vectorstore.py using this chunked file")
    else:
        print(f"\n❌ Chunking failed. Check errors above.")


if __name__ == "__main__":
    main()