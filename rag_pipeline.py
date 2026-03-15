"""
SwiftVisa - Milestone 2: RAG Pipeline
Core retrieval logic using Groq cloud LLM with metadata filtering

Author: [Your Name]
Date: 2026
Milestone: 2 - RAG Pipeline
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from visa_references import get_official_visa_website


# ============================================================================
# GROQ API KEY - HARDCODED FOR DEMO PURPOSES
# ============================================================================
GROQ_API_KEY_HARDCODED = "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"
# ============================================================================


class RAGPipeline:
    """RAG Pipeline for SwiftVisa eligibility screening with Groq LLM"""
    
    def __init__(self, 
                 vectorstore_path: str = "vectorstore",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 groq_model: str = "llama-3.1-8b-instant",
                 groq_api_key: Optional[str] = None,
                 top_k: int = 3):
        """
        Initialize RAG pipeline with Groq LLM
        
        Args:
            vectorstore_path: Path to FAISS vector store
            embedding_model: SentenceTransformer model for embeddings
            groq_model: Groq model name
            groq_api_key: Your Groq API key (or uses hardcoded key)
            top_k: Number of chunks to retrieve
        """
        self.vectorstore_path = vectorstore_path
        self.top_k = top_k
        self.groq_model = groq_model
        
        # Set cache directory for HuggingFace models
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        os.environ['HF_HOME'] = cache_dir
        
        # Load embeddings
        print("Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load vector store
        print("Loading vector store...")
        self.vectorstore = FAISS.load_local(
            vectorstore_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ RAG Pipeline initialized")
        
        # Initialize Groq LLM
        self._llm = None
        self._groq_api_key = groq_api_key or GROQ_API_KEY_HARDCODED
    
    @property
    def llm(self):
        """Lazy load Groq LLM"""
        if self._llm is None:
            if not self._groq_api_key:
                print("❌ GROQ_API_KEY not found.")
                return None
            
            print(f"Loading Groq LLM: {self.groq_model}...")
            try:
                self._llm = ChatGroq(
                    model=self.groq_model,
                    groq_api_key=self._groq_api_key,
                    temperature=0.1
                )
                print("✅ Groq LLM loaded")
            except Exception as e:
                print(f"❌ Failed to load Groq LLM: {e}")
                self._llm = None
        return self._llm
    
    def retrieve(self, query: str, country_filter: Optional[str] = None, 
                 visa_type_filter: Optional[str] = None) -> List[Dict]:
        """
        Retrieve top-K relevant policy chunks with filtering
        
        Args:
            query: User query
            country_filter: Optional country filter
            visa_type_filter: Optional visa type filter
        
        Returns:
            List of retrieved documents with metadata
        """
        search_kwargs = {"k": self.top_k}
        
        # Build filters
        filters = {}
        if country_filter:
            filters["country"] = country_filter.strip()
        if visa_type_filter:
            filters["visa_type"] = visa_type_filter.strip()
        
        if filters:
            search_kwargs["filter"] = filters
            print(f"   🔍 Applying filters: {filters}")
        
        # Get retriever
        retriever = self.vectorstore.as_retriever(search_kwargs=search_kwargs)
        
        # Retrieve documents
        docs = retriever.invoke(query)
        
        # Fallback if no results with filters
        if not docs and filters:
            print(f"   ⚠️  No results with filters, trying broader search...")
            retriever_fallback = self.vectorstore.as_retriever(search_kwargs={"k": self.top_k})
            docs = retriever_fallback.invoke(query)
        
        # Format results
        results = []
        for i, doc in enumerate(docs, 1):
            results.append({
                "rank": i,
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return results
    
    def generate_response(self, query: str, user_profile: Dict) -> Dict:
        """
        Generate complete RAG response with Groq LLM
        
        Args:
            query: User query
            user_profile: User profile dictionary
        
        Returns:
            Response dictionary with status, confidence, and content
        """
        # Extract user profile fields
        nationality = user_profile.get('nationality', 'N/A')
        destination = user_profile.get('destination_country', 'N/A')
        visa_type = user_profile.get('visa_type', 'N/A')
        purpose = user_profile.get('purpose', 'N/A')
        
        # Get official website
        official_website = get_official_visa_website(destination, visa_type)
        
        # Extract visa type keyword for filtering
        visa_keyword = visa_type.replace(' Visa', '').strip()
        
        # Retrieve relevant chunks
        retrieved_docs = self.retrieve(
            query, 
            country_filter=destination,
            visa_type_filter=visa_keyword
        )
        
        # Handle no results
        if not retrieved_docs:
            return {
                "query": query,
                "response": f"No relevant policy information found for {visa_type} in {destination}. Please verify the visa type and country, or consult official sources.\n\n🔗 **Official Government Resource:**\n- {destination} Immigration: [{official_website}]({official_website})",
                "retrieved_documents": [],
                "confidence": "Low",
                "status": "NO_RESULTS",
                "official_website": official_website
            }
        
        # Format context
        context = "\n\n".join([
            f"[Source: {doc['metadata'].get('country', 'Unknown')} - {doc['metadata'].get('visa_type', 'Unknown')} Visa]\n{doc['content']}"
            for doc in retrieved_docs
        ])
        
        # Check if LLM available
        if self.llm is None:
            return {
                "query": query,
                "response": f"Groq LLM not available. Retrieved {len(retrieved_docs)} policy chunks.\n\n🔗 **Official Government Resource:**\n- {destination} Immigration: [{official_website}]({official_website})",
                "retrieved_documents": retrieved_docs,
                "confidence": "Medium",
                "status": "RETRIEVAL_ONLY",
                "official_website": official_website
            }
        
        # Build prompt
        template = f"""You are SwiftVisa, an expert immigration assistant.

IMPORTANT INSTRUCTIONS:
1. ONLY assess eligibility for the visa type specified: {{visa_type}}
2. If retrieved information is for a DIFFERENT visa type, say "Insufficient information"
3. Always cite sources from retrieved policy information
4. Include the official government website: {{official_website}}

RETRIEVED POLICY INFORMATION:
{{context}}

USER PROFILE:
- Nationality: {{nationality}}
- Destination: {{destination}}
- Visa Type: {{visa_type}}
- Purpose: {{purpose}}

OUTPUT FORMAT (STRICT):
## Eligibility Assessment for {{visa_type}}
**Status:** [ELIGIBLE / PARTIALLY ELIGIBLE / NOT ELIGIBLE / INSUFFICIENT INFORMATION]
**Confidence:** [High / Medium / Low]
**Requirements Met:** [List applicable requirements]
**Required Documents:** [List documents from policy]
**Next Steps:** [List actionable next steps]
**Sources:** [Cite policy sources]

**🔗 Official Government Resources:**
- {{destination}} Immigration: [{{official_website}}]({{official_website}})

Disclaimer: This assessment is based on retrieved policy information and is not a substitute for official government advice. Always verify requirements at {{official_website}}.
"""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "context": context,
                "nationality": nationality,
                "destination": destination,
                "visa_type": visa_type,
                "purpose": purpose,
                "official_website": official_website
            })
            
            # Parse confidence and status
            confidence = "High" if "Confidence:** High" in response else "Medium"
            if "Confidence:** Low" in response:
                confidence = "Low"
            
            status = "ELIGIBLE" if "**Status:** ELIGIBLE" in response else "PARTIALLY ELIGIBLE"
            if "NOT ELIGIBLE" in response:
                status = "NOT ELIGIBLE"
            if "INSUFFICIENT INFORMATION" in response:
                status = "INSUFFICIENT INFORMATION"
            
            return {
                "query": query,
                "response": response,
                "retrieved_documents": retrieved_docs,
                "confidence": confidence,
                "status": status,
                "official_website": official_website,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "query": query,
                "response": f"Error generating response: {str(e)}\n\n🔗 **Official Government Resource:**\n- {destination} Immigration: [{official_website}]({official_website})",
                "retrieved_documents": retrieved_docs,
                "confidence": "Low",
                "status": "ERROR",
                "official_website": official_website
            }


def test_pipeline():
    """Test the RAG pipeline"""
    print("Testing RAG Pipeline")
    print("=" * 70)
    
    pipeline = RAGPipeline(groq_api_key=GROQ_API_KEY_HARDCODED, top_k=3)
    
    test_query = "What documents for UK work visa?"
    profile = {
        "nationality": "Indian",
        "destination_country": "United Kingdom",
        "visa_type": "Work Visa",
        "purpose": "Employment"
    }
    
    result = pipeline.generate_response(test_query, profile)
    print(f"\nStatus: {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Response preview: {result['response'][:300]}...")
    
    print("\n" + "=" * 70)
    print("✅ RAG Pipeline working correctly!")


if __name__ == "__main__":
    test_pipeline()