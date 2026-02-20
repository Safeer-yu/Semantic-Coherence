"""
Farasa has memory issues when diacritizing long Wikipedia articles. 
To avoid crashes or excessive memory usage, we need to divide long articles 
into smaller chunks before diacritizing them.

"""
# Since Farasa is relatively slow, we process one file at a time.

import json
import re
from farasa.diacratizer import FarasaDiacritizer
from pyarabic.araby import is_arabicrange

def smart_clean(text):
   
    # This regex keeps Arabic letters, numbers, and basic punctuation
    text = re.sub(r'[^\u0600-\u06FF0-9\s\.\/\-\,\:\!\?]', '', text)
    return ' '.join(text.split())

def split_into_chunks(text, max_chars=12000):
    chunks = []
    while len(text) > max_chars:
        split_point = text[:max_chars].rfind(' ')
        if split_point == -1: split_point = max_chars
        chunks.append(text[:split_point])
        text = text[split_point:].lstrip()
    chunks.append(text)
    return chunks

def process_corpus(input_file, output_file):
    diacritizer = FarasaDiacritizer(interactive=True)

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for i, line in enumerate(infile, 1):
            try:
                data = json.loads(line)
                
                h = data.get("Headline") or ""
                t = data.get("Text") or data.get("text") or ""
                combined = f"{h} {t}".strip()
                
                if not combined:
                    diacritized_out = ""
                else:
                   
                    cleaned = smart_clean(combined)
                    chunks = split_into_chunks(cleaned)
                    diacritized_parts = [diacritizer.diacritize(c) for c in chunks]
                    diacritized_out = " ".join(diacritized_parts)
                
                output_data = {
                    "ID": data.get("ID"),
                    "diacritized_text": diacritized_out
                }
                
                outfile.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                
                if i % 100 == 0:
                    print(f"Processed {i} lines...")
                    outfile.flush()

            except Exception as e:
                print(f"Error on line {i}: {e}")

if __name__ == "__main__":
    INPUT_FILE = '/home/safeer.alyubary/Semantic-Coherence/data_files/data/Sabanews.jsonl'
    OUTPUT_FILE = '/home/safeer.alyubary/Semantic-Coherence/New-Corpus/output/diacritized_Sabanews.jsonl'
    process_corpus(INPUT_FILE, OUTPUT_FILE)
    print("Done!")