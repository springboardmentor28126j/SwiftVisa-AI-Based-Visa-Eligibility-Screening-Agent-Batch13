"""
SwiftVisa - Milestone 2: Eligibility Screener
Interactive command-line interface for visa eligibility screening

Author: [Your Name]
Date: 2026
Milestone: 2 - RAG Pipeline
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from rag_pipeline import RAGPipeline
from response_logger import ResponseLogger

# ============================================================================
# GROQ API KEY - HARDCODED FOR DEMO PURPOSES
# ============================================================================
GROQ_API_KEY_HARDCODED = "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"
# ============================================================================


class EligibilityScreener:
    """Main eligibility screening interface for Milestone 2"""
    
    def __init__(self, groq_model: str = "llama-3.1-8b-instant"):
        print("🚀 Initializing SwiftVisa Eligibility Screener (Groq LLM)")
        print("=" * 70)
        
        if not Path("vectorstore").exists():
            print("❌ Vector store not found. Please run Milestone 1 first!")
            print("   1. python extract_raw_data.py  OR  python create_document_index.py")
            print("   2. python chunk_policies.py")
            print("   3. python create_vectorstore.py")
            return
        
        self.pipeline = RAGPipeline(
            groq_model=groq_model,
            groq_api_key=GROQ_API_KEY_HARDCODED,
            top_k=3
        )
        
        self.logger = ResponseLogger()
        
        print("=" * 70)
        print("✅ Eligibility Screener ready!")
        print("   LLM: Groq (llama-3.1-8b-instant)")
        print("   Type your visa question or 'quit' to exit")
        print("=" * 70)
    
    def screen_eligibility(self, query: str, user_profile: dict) -> dict:
        """Screen visa eligibility"""
        response = self.pipeline.generate_response(query, user_profile)
        
        if response.get("status") != "ERROR":
            self.logger.log_response(response, user_profile)
        
        return response
    
    def interactive_mode(self):
        """Run interactive eligibility screening session"""
        print("\n💬 Interactive Eligibility Screening")
        print("-" * 70)
        print("Example queries:")
        print("  • What documents do I need for a UK work visa?")
        print("  • Am I eligible for Canada student visa?")
        print("  • Processing time for Australia tourist visa?")
        print("-" * 70)
        
        while True:
            query = input("\n🗣️  Your visa question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using SwiftVisa!")
                
                report = self.logger.get_quality_report()
                if report.get("total_queries", 0) > 0:
                    print(f"\n📊 Session Summary:")
                    print(f"   Total queries: {report['total_queries']}")
                    print(f"   Average quality: {report['average_quality_score']}/10")
                
                break
            
            if not query:
                continue
            
            print("\n📋 Quick Profile (press Enter to skip):")
            nationality = input("   Nationality: ").strip() or "Indian"
            destination = input("   Destination Country: ").strip() or "United Kingdom"
            visa_type = input("   Visa Type: ").strip() or "Work Visa"
            purpose = input("   Purpose: ").strip() or "Employment"
            
            user_profile = {
                "nationality": nationality,
                "destination_country": destination,
                "visa_type": visa_type,
                "purpose": purpose
            }
            
            print("\n🤖 Analyzing eligibility with Groq LLM...")
            response = self.screen_eligibility(query, user_profile)
            
            print("\n" + "=" * 70)
            print(response.get("response", "No response generated"))
            print("=" * 70)
            
            feedback = input("\n💬 Was this helpful? (yes/no/skip): ").strip().lower()
            if feedback in ['yes', 'y']:
                self.logger.log_response(response, user_profile, feedback="helpful")
            elif feedback in ['no', 'n']:
                self.logger.log_response(response, user_profile, feedback="not helpful")


def main():
    screener = EligibilityScreener(groq_model="llama-3.1-8b-instant")
    screener.interactive_mode()


if __name__ == "__main__":
    main()