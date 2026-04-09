"""
Script to create embeddings using SentenceTransformer and store in FAISS.
This creates a searchable vector store for visa documents.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_CHUNKS_PATH = PROJECT_ROOT / 'data' / 'processed_chunks.json'
EMBEDDINGS_DIR = PROJECT_ROOT / 'data' / 'embeddings'

def load_chunks() -> List[Dict]:
    """Load processed document chunks"""
    with open(PROCESSED_CHUNKS_PATH, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    return chunks

def create_embeddings(chunks: List[Dict], model_name: str = 'all-MiniLM-L6-v2'):
    """
    Create embeddings for all chunks using SentenceTransformer.
    Using 'all-MiniLM-L6-v2' - a fast and efficient model.
    """
    
    print(f"📥 Loading SentenceTransformer model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print(f"🔄 Creating embeddings for {len(chunks)} chunks...")
    
    # Extract texts from chunks
    texts = [chunk['text'] for chunk in chunks]
    
    # Create embeddings with progress bar
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    print(f"✅ Created embeddings with shape: {embeddings.shape}")
    
    return embeddings, model

def create_faiss_index(embeddings: np.ndarray):
    """
    Create and populate FAISS index for fast similarity search.
    Using IndexFlatL2 for exact search (good for smaller datasets).
    """
    
    print(f"\n🔨 Building FAISS index...")
    
    # Get embedding dimension
    dimension = embeddings.shape[1]
    
    # Create FAISS index (using L2 distance for similarity)
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to index
    index.add(embeddings)
    
    print(f"✅ FAISS index created with {index.ntotal} vectors")
    
    return index

def save_artifacts(index, chunks: List[Dict], embeddings: np.ndarray):
    """Save FAISS index, metadata, and embeddings"""
    
    embeddings_dir = EMBEDDINGS_DIR
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    index_path = embeddings_dir / 'visa_faiss.index'
    faiss.write_index(index, str(index_path))
    print(f"💾 Saved FAISS index to: {index_path}")
    
    # Save metadata (chunks without text for smaller size)
    metadata = []
    for i, chunk in enumerate(chunks):
        meta = {
            'id': i,
            'country_code': chunk['country_code'],
            'visa_id': chunk['visa_id'],
            'visa_name': chunk['visa_name'],
            'section': chunk['section'],
            'doc_path': chunk['doc_path'],
            'text': chunk['text']  # Keep text for retrieval
        }
        metadata.append(meta)
    
    metadata_path = embeddings_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved metadata to: {metadata_path}")
    
    # Save embeddings as numpy array
    embeddings_path = embeddings_dir / 'embeddings.npy'
    np.save(embeddings_path, embeddings)
    print(f"💾 Saved embeddings to: {embeddings_path}")
    
    # Save summary statistics
    summary = {
        'total_chunks': len(chunks),
        'embedding_dimension': embeddings.shape[1],
        'model_name': 'all-MiniLM-L6-v2',
        'index_type': 'IndexFlatL2',
        'countries': len(set(c['country_code'] for c in chunks)),
        'unique_visas': len(set(f"{c['country_code']}_{c['visa_id']}" for c in chunks))
    }
    
    summary_path = embeddings_dir / 'summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"💾 Saved summary to: {summary_path}")
    
    return summary

def main():
    """Main function to create embeddings and FAISS index"""
    
    print("🚀 Starting embedding generation and FAISS indexing...\n")
    
    # Step 1: Load chunks
    chunks = load_chunks()
    print(f"📚 Loaded {len(chunks)} document chunks\n")
    
    # Step 2: Create embeddings
    embeddings, model = create_embeddings(chunks)
    
    # Step 3: Create FAISS index
    index = create_faiss_index(embeddings)
    
    # Step 4: Save everything
    print(f"\n💾 Saving artifacts...")
    summary = save_artifacts(index, chunks, embeddings)
    
    # Print summary
    print(f"\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print("="*50)
    
    print("\n✅ Embedding generation and indexing complete!")

if __name__ == "__main__":
    main()
