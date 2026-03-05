"""
LLM Prompt Template for Visa Eligibility Screening
This module provides structured prompts for visa eligibility assessment.
"""

from typing import Dict, List, Optional

class VisaEligibilityPrompt:
    """
    A class to generate structured prompts for visa eligibility screening.
    """
    
    SYSTEM_PROMPT = """You are a professional visa eligibility assistant. Your role is to analyze user information and determine their eligibility for visa applications based on official government requirements.

Core Responsibilities:
1. Assess user eligibility for specific visa types
2. Identify missing documents or requirements
3. Provide clear, actionable recommendations
4. Maintain accuracy based on official visa policies

Guidelines:
- Base all assessments strictly on provided official visa policies
- Be clear and specific about requirements
- Highlight any critical issues or deal-breakers
- Provide constructive guidance
- If information is insufficient, clearly state what additional details are needed
- Never make assumptions about eligibility - use only provided facts"""
    
    @staticmethod
    def format_retrieved_documents(documents: List[Dict]) -> str:
        """Format retrieved policy documents for prompt"""
        formatted = []
        for i, doc in enumerate(documents, 1):
            formatted.append(f"""
Document {i}:
Country: {doc.get('country_code', 'N/A')}
Visa Type: {doc.get('visa_name', 'N/A')} ({doc.get('visa_id', 'N/A')})
Section: {doc.get('section', 'N/A')}

Content:
{doc.get('text', 'No content available')}
---
""")
        return '\n'.join(formatted)
    
    @staticmethod
    def format_user_profile(profile: Dict) -> str:
        """Format user profile information for prompt"""
        formatted = []
        for key, value in profile.items():
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        return '\n'.join(formatted)
    
    @classmethod
    def generate_eligibility_prompt(
        cls,
        user_query: str,
        retrieved_documents: List[Dict],
        user_profile: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate a complete prompt for visa eligibility screening.
        
        Args:
            user_query: The user's visa application question
            retrieved_documents: List of relevant visa policy documents
            user_profile: Optional user information
            
        Returns:
            Dictionary with 'system' and 'user' prompts
        """
        
        # Format documents
        docs_text = cls.format_retrieved_documents(retrieved_documents)
        
        # Format profile
        profile_text = cls.format_user_profile(user_profile) if user_profile else "No profile information provided"
        
        user_prompt = f"""# CONTEXT
You are analyzing visa eligibility for the following request.

## User Query
{user_query}

## Retrieved Visa Policies
{docs_text}

## User Profile
{profile_text}

# TASK
Based on the official visa requirements provided above, evaluate the user's eligibility and provide:

1. **Eligibility Assessment**: Clear YES/NO/PARTIAL determination
2. **Requirements Met**: List all requirements the user currently satisfies
3. **Missing Requirements**: Identify gaps in documentation or eligibility criteria
4. **Required Documents**: List all documents needed for this visa application
5. **Recommendations**: Specific steps the user should take
6. **Important Notes**: Any critical information or warnings

# RESPONSE FORMAT
Provide your response in the following structured format:

## Eligibility Status
[YES/NO/PARTIAL] - [Brief explanation]

## Requirements Met ✓
- [List all satisfied requirements]

## Missing Requirements ⚠️
- [List all unsatisfied requirements with explanations]

## Required Documents 📄
1. [Document name] - [Purpose/description]
2. [Document name] - [Purpose/description]

## Next Steps 🎯
1. [Specific action item]
2. [Specific action item]

## Important Information ⚡
- [Critical notes, deadlines, or warnings]

## Official Source
[Link to official government visa information]
"""
        
        return {
            'system': cls.SYSTEM_PROMPT,
            'user': user_prompt
        }
    
    @classmethod
    def generate_simple_query_prompt(
        cls,
        user_query: str,
        retrieved_documents: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate a simpler prompt for basic visa information queries.
        
        Args:
            user_query: The user's question
            retrieved_documents: Relevant visa policy documents
            
        Returns:
            Dictionary with 'system' and 'user' prompts
        """
        
        docs_text = cls.format_retrieved_documents(retrieved_documents)
        
        user_prompt = f"""Based on the following official visa policy documents, answer the user's question clearly and concisely.

## User Question
{user_query}

## Relevant Visa Policies
{docs_text}

## Task
Provide a clear, accurate answer based solely on the provided visa policy information. Include:
- Direct answer to the question
- Relevant requirements or procedures
- Link to official source if available

If the provided documents don't contain sufficient information, clearly state that."""
        
        return {
            'system': cls.SYSTEM_PROMPT,
            'user': user_prompt
        }


# Example usage
if __name__ == "__main__":
    # Example: Generate prompt for eligibility screening
    
    sample_query = "I want to apply for a US F1 student visa"
    
    sample_documents = [
        {
            'country_code': 'USA',
            'visa_id': 'F1',
            'visa_name': 'Student Visa',
            'section': 'ELIGIBILITY REQUIREMENTS',
            'text': 'Valid Passport, Form I-20, SEVIS Payment, Proof of Funds'
        }
    ]
    
    sample_profile = {
        'nationality': 'Indian',
        'purpose': 'Master\'s degree in Computer Science',
        'current_documents': 'Valid passport, University admission letter',
        'financial_status': '$50,000 in savings'
    }
    
    prompt_generator = VisaEligibilityPrompt()
    prompts = prompt_generator.generate_eligibility_prompt(
        user_query=sample_query,
        retrieved_documents=sample_documents,
        user_profile=sample_profile
    )
    
    print("="*60)
    print("SYSTEM PROMPT")
    print("="*60)
    print(prompts['system'])
    print("\n" + "="*60)
    print("USER PROMPT")
    print("="*60)
    print(prompts['user'])
