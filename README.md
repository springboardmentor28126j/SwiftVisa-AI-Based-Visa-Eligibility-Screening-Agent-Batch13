# SwiftVisa AI – Milestone 1
## Visa Policy Search System

---

# Project Goal

The goal of Milestone 1 is to prepare visa policy data and build a smart search system using AI.
This milestone creates the base system for the Visa Eligibility Screening Agent.

---

#  What Was Done (Step-by-Step)

Below is the complete process in simple steps.

## Step 1 – Collect Visa Data

Visa information was collected for different countries.

File used:

data/all_countries.json

This file contains:
- Country name
- Visa type
- Policy summary
- Required documents
- Official source

This is the main visa policy database.

---

## Step 2 – Convert Data into Chunks

Large files are hard to search.

Each visa policy was converted into a small text block called a “chunk”.

New file created:

data/visa_policy_chunks.json

Each chunk contains:
- Chunk ID
- Country
- Visa Type
- Full searchable text

This makes the data ready for AI processing.

---

## Step 3 – Create AI Embeddings

Model used:

SentenceTransformer (all-MiniLM-L6-v2)

Purpose:

- Converts text into numerical vectors
- Helps the system understand meaning

Embeddings were created for every chunk.

New file created:

data/visa_policy_embeddings.json

Each visa policy now contains:

- Text
- AI embedding (vector format)

---

## Step 4 – Store in FAISS Database

FAISS was used to store embeddings.

FAISS:

- Stores embeddings efficiently
- Performs fast similarity search

New file created:

data/visa_faiss.index

Data is now searchable using vector similarity.

---

## Step 5 – Build Smart Search System

File created:

search.py

User can type a question like:

"What documents are required for UK Student Visa?"

System Process:

1. Convert the question into embedding
2. Compare with stored visa embeddings
3. Retrieve most similar visa policy
4. Display best matching result

Output includes:

- Country
- Visa Type
- Policy Details

---

#  Complete Workflow

all_countries.json  
        ↓  
Create chunks  
        ↓  
visa_policy_chunks.json  
        ↓  
Create embeddings  
        ↓  
visa_policy_embeddings.json  
        ↓  
Store in FAISS  
        ↓  
Smart Search (search.py)  
        ↓  
Best matching visa policy shown  

---

#  Project Structure

SWIFTVISA_AI/

data/
- all_countries.json
- visa_policy_chunks.json
- visa_policy_embeddings.json
- visa_faiss.index

embed.py  
search.py  
requirements.txt  
README.md  

---

#  Tools Used

- Python 3
- SentenceTransformer
- FAISS
- NumPy

---

#  How To Run

Step 1 – Install Dependencies

pip install -r requirements.txt

Step 2 – Create Embeddings and FAISS Index

python embed.py

Step 3 – Start Search System

python search.py

---

#  Milestone 1 Status
Completed:
✔ Visa data organized  
✔ Data converted into chunks  
✔ AI embeddings generated  
✔ FAISS vector index created  
✔ Smart semantic search implemented  

Milestone 1 successfully completed.
