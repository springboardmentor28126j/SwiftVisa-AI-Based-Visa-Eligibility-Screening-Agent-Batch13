"""
Demo script to test the complete Milestone 1 deliverables.
This demonstrates loading embeddings, searching the index, and generating prompts.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

try:
    import faiss  # type: ignore
except Exception:
    faiss = None

# Add prompts directory to path robustly
import sys
from pathlib import Path as _Path
# Resolve prompts directory relative to this script's parent directory
_prompts_path = _Path(__file__).resolve().parents[1] / 'prompts'
sys.path.append(str(_prompts_path))
from eligibility_prompt import VisaEligibilityPrompt

class VisaSearchDemo:
    """Demo class to showcase Milestone 1 capabilities"""
    
    def __init__(self):
        """Initialize all components"""
        print("🚀 Initializing Visa Search System...")
        
        # Resolve milestone1 root and data paths
        self.project_root = _Path(__file__).resolve().parents[1]
        embeddings_dir = self.project_root / 'data' / 'embeddings'

        # Load FAISS index
        index_path = embeddings_dir / 'visa_faiss.index'
        self.search_backend = 'faiss'
        if faiss is not None and index_path.exists():
            self.index = faiss.read_index(str(index_path))
            print(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
        else:
            embeddings_path = embeddings_dir / 'embeddings.npy'
            if not embeddings_path.exists():
                raise FileNotFoundError(f"Embeddings file not found for fallback search: {embeddings_path}")
            self.embeddings = np.load(embeddings_path)
            self.index = None
            self.search_backend = 'numpy'
            print(f"✅ Loaded NumPy embeddings fallback with {self.embeddings.shape[0]} vectors")

        # Load metadata
        metadata_path = embeddings_dir / 'metadata.json'
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"✅ Loaded metadata for {len(self.metadata)} chunks")

        # Load indexes
        index_dir = self.project_root / 'data' / 'index'
        with open(index_dir / 'document_index.json', 'r', encoding='utf-8') as f:
            self.doc_index = json.load(f)

        with open(index_dir / 'eligibility_index.json', 'r', encoding='utf-8') as f:
            self.eligibility_index = json.load(f)

        print(f"✅ Loaded indexes for {self.doc_index['summary']['total_countries']} countries")
        
        # Load embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Loaded embedding model")
        
        # Initialize prompt generator
        self.prompt_gen = VisaEligibilityPrompt()
        print("✅ Initialized prompt generator\n")
    
    def search(self, query: str, top_k: int = 3):
        """Search for relevant visa documents"""
        print(f"🔍 Searching for: '{query}'\n")
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        if self.search_backend == 'faiss':
            distances, indices = self.index.search(query_embedding, top_k)
            ranked_pairs = list(zip(indices[0].tolist(), distances[0].tolist()))
        else:
            query_vec = query_embedding[0]
            query_norm = np.linalg.norm(query_vec)
            doc_norms = np.linalg.norm(self.embeddings, axis=1)
            denom = np.clip(query_norm * doc_norms, 1e-12, None)
            cosine = np.dot(self.embeddings, query_vec) / denom
            ranked_idx = np.argsort(-cosine)[:top_k]
            ranked_pairs = [(int(idx), float(max(0.0, 1.0 - cosine[idx]))) for idx in ranked_idx]
        
        # Get results
        results = []
        for idx, dist in ranked_pairs:
            if idx < len(self.metadata):
                results.append({
                    'metadata': self.metadata[idx],
                    'distance': float(dist),
                    'similarity_score': 1 / (1 + dist)  # Convert distance to similarity
                })
        
        return results
    
    def display_results(self, results):
        """Display search results"""
        print("📊 Search Results:\n")
        
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            print(f"Result {i}:")
            print(f"  Country: {meta['country_code']}")
            print(f"  Visa: {meta['visa_name']} ({meta['visa_id']})")
            print(f"  Section: {meta['section']}")
            print(f"  Similarity: {result['similarity_score']:.3f}")
            print(f"  Preview: {meta['text'][:100]}...")
            print()
    
    def generate_prompt(self, query: str, results, user_profile: dict = None):
        """Generate LLM prompt from results"""
        print("📝 Generating LLM Prompt...\n")
        
        # Format documents for prompt
        documents = [r['metadata'] for r in results]
        
        # Generate prompt
        prompts = self.prompt_gen.generate_eligibility_prompt(
            user_query=query,
            retrieved_documents=documents,
            user_profile=user_profile
        )
        
        return prompts
    
    def demo_search_and_prompt(self):
        """Run a complete demo"""
        print("="*70)
        print("MILESTONE 1 DEMO: Complete System Test")
        print("="*70 + "\n")
        
        # Example query
        query = "I want to apply for a student visa in the Australia"
        
        # User profile
        user_profile = {
            'nationality': 'Indian',
            'purpose': 'Master\'s degree',
            'documents': 'Valid passport, Admission letter',
            'financial_status': '$50,000 available'
        }
        
        # Step 1: Search
        results = self.search(query, top_k=3)
        self.display_results(results)
        
        # Step 2: Generate prompt
        prompts = self.generate_prompt(query, results, user_profile)
        
        print("="*70)
        print("GENERATED SYSTEM PROMPT")
        print("="*70)
        print(prompts['system'][:300] + "...\n")
        
        print("="*70)
        print("GENERATED USER PROMPT (First 500 chars)")
        print("="*70)
        print(prompts['user'][:500] + "...\n")
        
        print("✅ Demo Complete!")
        print("\nThis demonstrates:")
        print("  1. ✅ Loading FAISS embeddings")
        print("  2. ✅ Semantic search across visa documents")
        print("  3. ✅ Retrieving relevant policies")
        print("  4. ✅ Generating structured LLM prompts")
        print("  5. ✅ Complete RAG pipeline foundation")

def main():
    """Main demo function"""
    try:
        demo = VisaSearchDemo()
        demo.demo_search_and_prompt()
        
        print("\n" + "="*70)
        print("MILESTONE 1: ALL SYSTEMS OPERATIONAL ✅")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
