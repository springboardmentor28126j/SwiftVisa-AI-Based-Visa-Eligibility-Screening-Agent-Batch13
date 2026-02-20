import os
import json


# -------- Recursive Cleaner + Flattener --------
def flatten_and_clean(d, parent_key=""):
    lines = []

    for key, value in d.items():

        if key == "signal_type":
            continue

        full_key = f"{parent_key} {key}".strip()
        formatted_key = full_key.replace("_", " ").title()

        if isinstance(value, dict):
            lines.extend(flatten_and_clean(value, full_key))

        elif isinstance(value, list):
            lines.append(f"{formatted_key}: {', '.join(map(str, value))}")

        else:
            lines.append(f"{formatted_key}: {value}")

    return lines


# -------- Main Chunking Function --------
def chunk_visa_dataset(folder_path):
    all_chunks = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        country = data.get("country", "Unknown")
        official_sources = data.get("official_policy_sources", [])

        sources_text = "Official Policy Sources:\n" + "\n".join(official_sources)

        for visa_entry in data.get("visa_dataset_reference", []):
            visa_type = visa_entry.get("target_visa_type", "Unknown")

            screening_tool = visa_entry.get("visa_screening_tool", {})

            for section_name, section_data in screening_tool.items():

                if not section_data:
                    continue

                readable_lines = flatten_and_clean(section_data)
                details = "\n".join(readable_lines)

                text_chunk = f"""
Country: {country}
Visa Type: {visa_type}
Section: {section_name.replace("_", " ").title()}

{details}

{sources_text}
""".strip()

                all_chunks.append({
                    "text": text_chunk,
                    "metadata": {
                        "country": country,
                        "visa_type": visa_type,
                        "section": section_name,
                        "official_sources": official_sources
                    }
                })

    return all_chunks


# -------- Save Output --------
def save_chunks(chunks, json_path="chunked_output.json", txt_path="chunked_output.txt"):

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"\n{'='*80}\n")
            f.write(f"CHUNK {i+1}\n")
            f.write(f"{'='*80}\n\n")
            f.write(chunk["text"])
            f.write("\n\n")


# -------- Run Pipeline --------
if __name__ == "__main__":
    folder_path = "../data/clean"
    chunks = chunk_visa_dataset(folder_path)

    print(f"Total chunks created: {len(chunks)}")

    save_chunks(chunks)

    print("Chunked data saved successfully with official sources included.")


#######################################################
#----  Total Chunks :175                         ######
#----                                            ######
#######################################################