"""SwiftVisa - Create Document Index"""
import json, re
from pathlib import Path
from datetime import datetime

chunk_file = Path("data/chunks/policy_chunks.txt")
if not chunk_file.exists():
    print("Chunk file not found")
    exit()

with open(chunk_file, 'r', encoding='utf-8') as f:
    content = f.read()

raw_chunks = re.split(r'---CHUNK:\d+---\n', content)
index = {"metadata": {"project": "SwiftVisa", "milestone": "Milestone 1", "total_chunks": 0, "total_countries": 0, "total_visa_types": 0}, "countries": {}, "visa_categories": {"Tourist": {"count": 0, "countries": []}, "Work": {"count": 0, "countries": []}, "Student": {"count": 0, "countries": []}, "Family": {"count": 0, "countries": []}}}

chunk_id = 0
countries_set = set()
visa_types_set = set()

for chunk in raw_chunks:
    chunk = chunk.strip()
    if not chunk or chunk.startswith('#'):
        continue
    chunk_id += 1
    country = visa_type = None
    for line in chunk.split('\n')[:5]:
        if line.startswith('## ') and '-' in line:
            parts = line.replace('##', '').strip().split('-')
            if len(parts) >= 2:
                country = parts[0].strip()
                visa_type = parts[1].replace('Visa', '').strip()
    if country and visa_type:
        if country not in index["countries"]:
            index["countries"][country] = {"visa_types": [], "chunk_count": 0}
        if visa_type not in index["countries"][country]["visa_types"]:
            index["countries"][country]["visa_types"].append(visa_type)
        index["countries"][country]["chunk_count"] += 1
        if visa_type in index["visa_categories"]:
            index["visa_categories"][visa_type]["count"] += 1
            if country not in index["visa_categories"][visa_type]["countries"]:
                index["visa_categories"][visa_type]["countries"].append(country)
        countries_set.add(country)
        visa_types_set.add(visa_type)

index["metadata"]["total_chunks"] = chunk_id
index["metadata"]["total_countries"] = len(countries_set)
index["metadata"]["total_visa_types"] = len(visa_types_set)
index["countries"] = dict(sorted(index["countries"].items()))

output_path = Path("data/document_index.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"Document index created: {output_path}")
print(f"Countries: {index['metadata']['total_countries']}, Visa types: {index['metadata']['total_visa_types']}, Chunks: {index['metadata']['total_chunks']}")
