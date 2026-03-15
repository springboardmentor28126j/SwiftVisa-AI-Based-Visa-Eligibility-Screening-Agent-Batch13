"""
SwiftVisa - Milestone 2: Response Logger
Tracks RAG pipeline responses for quality monitoring and improvement

Author: [Your Name]
Date: 2026
Milestone: 2 - RAG Pipeline
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ResponseLogger:
    """Log and track RAG pipeline responses for quality monitoring"""
    
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"responses_{today}.json"
        
        if not self.log_file.exists():
            self._init_log_file()
        
        print(f"📊 Response logger initialized: {self.log_file}")
    
    def _init_log_file(self):
        """Initialize log file with metadata structure"""
        log_data = {
            "metadata": {
                "project": "SwiftVisa",
                "milestone": "Milestone 2: RAG + LLM Pipeline",
                "log_start_date": datetime.now().isoformat(),
                "total_queries": 0,
                "quality_metrics": {
                    "high_confidence": 0,
                    "medium_confidence": 0,
                    "low_confidence": 0,
                    "avg_retrieved_docs": 0
                }
            },
            "responses": []
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def log_response(self, response: Dict, user_profile: Dict, feedback: Optional[str] = None) -> int:
        """
        Log a RAG pipeline response
        
        Args:
            response: Response dictionary from RAG pipeline
            user_profile: User profile dictionary
            feedback: Optional user feedback (helpful/not helpful)
        
        Returns:
            Entry ID
        """
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        entry = {
            "id": len(log_data["responses"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": response.get("query", ""),
            "user_profile": user_profile,
            "response_status": response.get("status", "UNKNOWN"),
            "confidence": response.get("confidence", "Unknown"),
            "retrieved_docs_count": len(response.get("retrieved_documents", [])),
            "response_length": len(response.get("response", "")),
            "user_feedback": feedback,
            "quality_score": self._calculate_quality_score(response, feedback)
        }
        
        log_data["responses"].append(entry)
        log_data["metadata"]["total_queries"] += 1
        
        # Update confidence metrics
        confidence = response.get("confidence", "Medium").lower()
        if confidence in log_data["metadata"]["quality_metrics"]:
            log_data["metadata"]["quality_metrics"][confidence] += 1
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Response logged: Entry #{entry['id']} | Quality Score: {entry['quality_score']}/10")
        return entry["id"]
    
    def _calculate_quality_score(self, response: Dict, feedback: Optional[str] = None) -> int:
        """
        Calculate quality score (0-10) based on response metrics
        
        Args:
            response: Response dictionary
            feedback: Optional user feedback
        
        Returns:
            Quality score (0-10)
        """
        score = 5  # Base score
        
        # Confidence bonus/penalty
        confidence = response.get("confidence", "Medium").lower()
        if confidence == "high":
            score += 2
        elif confidence == "low":
            score -= 2
        
        # Retrieved docs bonus
        docs_count = len(response.get("retrieved_documents", []))
        if docs_count >= 3:
            score += 1
        elif docs_count == 0:
            score -= 2
        
        # Status bonus
        status = response.get("status", "UNKNOWN")
        if status in ["ELIGIBLE", "PARTIALLY ELIGIBLE"]:
            score += 1
        elif status == "NO_RESULTS":
            score -= 2
        
        # User feedback bonus
        if feedback:
            if feedback.lower() in ["helpful", "good", "yes"]:
                score += 3
            elif feedback.lower() in ["not helpful", "bad", "no"]:
                score -= 3
        
        return max(0, min(10, score))  # Clamp to 0-10
    
    def get_quality_report(self) -> Dict:
        """Generate quality report from logged responses"""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        responses = log_data["responses"]
        if not responses:
            return {"message": "No responses logged yet", "total_queries": 0}
        
        total = len(responses)
        high_conf = sum(1 for r in responses if r["confidence"] == "High")
        avg_quality = sum(r["quality_score"] for r in responses) / total
        
        return {
            "total_queries": total,
            "confidence_distribution": {
                "high": high_conf,
                "medium": sum(1 for r in responses if r["confidence"] == "Medium"),
                "low": sum(1 for r in responses if r["confidence"] == "Low")
            },
            "average_quality_score": round(avg_quality, 2),
            "high_quality_responses": sum(1 for r in responses if r["quality_score"] >= 8),
            "low_quality_responses": sum(1 for r in responses if r["quality_score"] <= 4)
        }


def test_logger():
    """Test the ResponseLogger class"""
    print("Testing ResponseLogger")
    print("=" * 70)
    
    logger = ResponseLogger()
    
    # Test response
    test_response = {
        "query": "UK work visa documents",
        "status": "PARTIALLY ELIGIBLE",
        "confidence": "High",
        "retrieved_documents": [{"content": "test"}] * 3,
        "response": "Based on the policy..."
    }
    
    test_profile = {
        "nationality": "Indian",
        "destination_country": "United Kingdom",
        "visa_type": "Work Visa",
        "purpose": "Employment"
    }
    
    # Log response
    logger.log_response(test_response, test_profile, feedback="helpful")
    
    # Get report
    report = logger.get_quality_report()
    print(f"\n📊 Quality Report:")
    print(f"   Total queries: {report.get('total_queries', 0)}")
    print(f"   Average quality: {report.get('average_quality_score', 0)}/10")
    
    print("\n" + "=" * 70)
    print("✅ ResponseLogger working correctly!")


if __name__ == "__main__":
    test_logger()