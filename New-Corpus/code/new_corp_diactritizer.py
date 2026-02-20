# Farasa has memory issues when diacritizing long Wikipedia articles. 
# To avoid crashes or excessive memory usage, we need to divide long articles 
# into smaller chunks before diacritizing them.


import json
from farasa.diacratizer import FarasaDiacritizer
from pyarabic.araby import tokenize, is_arabicrange

def clean_arabic_only(text):
    ## Removes non-Arabic characters/words to clean the input
    tokens = tokenize(text)
    return ' '.join([t for t in tokens if is_arabicrange(t)])

def split_into_chunks(text, max_chars=12000):
    # Splits long text into smaller chunks so Farasa doesn't crash
    chunks = []
    while len(text) > max_chars:
        split_point = text[:max_chars].rfind(' ')
        if split_point == -1: split_point = max_chars
        chunks.append(text[:split_point])
        text = text[split_point:].lstrip()
    chunks.append(text)
    return chunks

def process_corpus(input_file, output_file):
    # Initialize the engine ONCE
    print("Initializing Farasa... please wait.")
    diacritizer = FarasaDiacritizer(interactive=True)

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for i, line in enumerate(infile, 1):
            try:
                data = json.loads(line)
                
                # 1. Merge Headline and Text fields
                h = data.get("Headline") or ""
                t = data.get("Text") or data.get("text") or ""
                combined = f"{h} {t}".strip()
                
                if not combined:
                    data['diacritized_text'] = ""
                else:
                    # 2. Clean non-Arabic
                    cleaned = clean_arabic_only(combined)
                    
                    # 3. Chunk and Diacritize
                    chunks = split_into_chunks(cleaned)
                    diacritized_parts = [diacritizer.diacritize(c) for c in chunks]
                    data['diacritized_text'] = " ".join(diacritized_parts)
                
                # 4. Save result
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                
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