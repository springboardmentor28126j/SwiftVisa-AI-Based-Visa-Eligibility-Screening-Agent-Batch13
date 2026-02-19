# SwiftVisa AI – Milestone 1
## Visa Policy Search System

---

# 🎯 Project Goal

The goal of Milestone 1 is to prepare visa policy data and build a smart search system using AI.

This milestone creates the base system for the Visa Eligibility Screening Agent.

---

# 🧭 What We Did (Step-by-Step)

Below is the complete process in simple steps.

---

# Step 1 – Collect Visa Data

We collected visa information for different countries.

The file used:

data/all_countries.json

This file contains:

- Country name
- Visa type
- Policy summary
- Required documents
- Official source

This is our main visa policy database.

---

# Step 2 – Convert Data into Chunks

Large files are hard to search.

So we converted each visa policy into a small text block called a “chunk”.

New file created:

data/visa_policy_chunks.json

Each chunk contains:

- Chunk ID
- Country
- Visa Type
- Full searchable text

This makes the data ready for AI processing.

---

# Step 3 – Create AI Embeddings

We used a free AI model:

SentenceTransformer (all-MiniLM-L6-v2)

What it does:

- Converts text into numbers (vectors)
- These numbers help the system understand meaning

We created embeddings for every chunk.

New file created:

data/visa_policy_embeddings.json

Now each visa policy has:

- Text
- AI embedding (number format)

---

# Step 4 – Store in FAISS Database

We used FAISS.

FAISS is a tool that:

- Stores embeddings
- Finds similar information very fast

New file created:

data/visa_faiss.index

Now our data is searchable.

---

# Step 5 – Build Smart Search

We created:

search.py

User can type a question like:

"What documents are required for UK Student Visa?"

System process:

1. Convert question into embedding
2. Compare with stored visa embeddings
3. Find most similar visa policy
4. Show result

Output shows:

- Country
- Visa Type
- Details

---

# 🔄 Complete Workflow

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

# 📁 Project Structure

SWIFTVISA_AI/

- data/
    - all_countries.json
    - visa_policy_chunks.json
    - visa_policy_embeddings.json
    - visa_faiss.index

- embed.py
- search.py
- requirements.txt
- README.md

---

# 🛠 Tools Used

- Python 3
- SentenceTransformer
- FAISS
- NumPy

---

# 🚀 How To Run

Step 1:

Install libraries

pip install -r requirements.txt

Step 2:

Create embeddings

python embed.py

Step 3:

Start search system

python search.py

---

# ✅ Milestone 1 Completed

We successfully:

✔ Organized visa data  
✔ Converted it into searchable format  
✔ Created AI embeddings  
✔ Stored data in FAISS  
✔ Built smart semantic search  

This completes Milestone 1.

---

