# SwiftVisa-AI-Based-Visa-Eligibility-Screening-Agent-Batch13

Task 1: Visa Policy Knowledge Base Construction

Description:
In this task, we build the knowledge base for the SwiftVisa project.
The knowledge base is the core data layer that stores all visa-related information in a format that can be understood and used by an AI system.
The main goal of Task 1 is to collect visa rules from official government websites and transform this raw information into a structured and searchable vector database. This allows the AI system to later retrieve accurate visa information and answer user queries.

Why This Task Is Important:
An AI system cannot work with raw website content directly.
It needs:
- Clean and structured data
- Smaller meaningful text pieces
- Numerical representations (embeddings)

This task prepares all visa data in the correct format so that future AI components (RAG, chatbot, query engine) can work efficiently.

Steps Involved
1. Data Collection:  
Visa information is manually collected from official government portals of different countries.  
For each country, the following visa types are considered:

   - Student
   - Tourist
   - Work
   - Permanent Residence
   - Family

2. Identify Required Documents:  
For every country and visa type, the list of required documents is extracted, such as:

   - Passport
   - Application forms
   - Financial proof
   - Invitation letters


3. Structured Storage(JSON):   
 All collected information is stored in a structured file: visa_policy.json

    This file contains:

   - Country name (e.g., USA, India, Canada, Australia)
   - Visa type (Student, Tourist, Work, PR, Family)
   - Visa code (e.g., F-1, M-1, Employment Visa)
   - Required documents


4. Text Conversion

   The structured JSON data is converted into readable text format so that it can be processed by NLP models.

   Example:

   Country: USA  
   Visa Type: Student  
   Visa Code: F-1

   Eligibility Criteria:
   - Acceptance to SEVP-approved school,
   - Valid SEVIS I-20,
   - Sufficient funds for tuition/living,
   - Intent to return home,
   - English proficiency
     
   Required Documents:
   - Passport  
   - I-20  
   - Financial proof  

6. Chunking :   

    Large text is split into smaller pieces called chunks.
    
    This is done because:
    - AI models have context limits
    - Smaller chunks improve search accuracy
    - Retrieval becomes faster and more precise

    Example:

    Chunk size: 500 characters

    Overlap: 50 characters

7. Embedding Generation :

    Each chunk is converted into a numerical vector using a sentence transformer model.

    These numbers capture the meaning of the text.
    This process is called embedding.

8. Vector Database (FAISS)

   All embeddings are stored in a FAISS vector database.

   This allows:

   - Fast similarity search
   - Semantic retrieval
   - Efficient AI querying

Final Outcome:
At the end of Task 1, we obtain:
A clean and structured visa dataset
A fully built vector knowledge base
Stored in FAISS for fast retrieval

This knowledge base will be used in Milestone 2 to:
-Search visa rules and Answer user questions using AI (RAG system)

