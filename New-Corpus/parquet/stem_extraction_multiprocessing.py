# multiprocessing 

# This script uses multiprocessing to speed up processing of multiple files in parallel

import os
import re
import json
import pickle
import glob
import pyarrow.parquet as pq  
from collections import defaultdict
from multiprocessing import Pool
from farasa.stemmer import FarasaStemmer
import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel
from tqdm import tqdm


files_path = "data_files/wiki_and_parquet"
stopwords_file_path = 'arabic_stopwords_nltk.txt'
non_frequent_words_file_path= "data_files/data_stats/words_10_or_less_main.txt"
output_pickle_path = "parquet/output/multiprocessing_stem_to_words_dict.pkl"

def preprocess_text(text, stopwords, non_frequent_words):
  
    text = araby.strip_tatweel(text)
    # Switched to these cleaning steps to avoid word breaking or words concatenating
    # Remove defined punctuation
    punctuation = r'[\.،,؛;:!?؟?(){}\[\]<>"\'/\\@#$%^&*_+=~|]'
    text = re.sub(punctuation, ' ', text)
    # Remove Mashriki numerals (Arabic-Indic digits)
    text = re.sub(r'[٠-٩]', ' ', text)
    # Tokenize and strip tashkeel
    tokens = tokenize(text, conditions=is_arabicrange, morphs=strip_tashkeel)
    tokens = [t for t in tokens if t not in stopwords and t not in non_frequent_words and len(t) > 1]
    return tokens



def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(f.read().split())
    
def load_non_frequent_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(f.read().split())

def process_single_file(file_name):
    """Worker function that detects file type and processes text"""
    stemmer = FarasaStemmer(interactive=True)
    stop_words = load_stopwords(stopwords_file_path)
    non_frequent_words = load_non_frequent_words(non_frequent_words_file_path)
    local_dict = defaultdict(set)

    try:
        # JSONL Files 
        if file_name.endswith('.jsonl'):
            with open(file_name, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    h = data.get("Headline") or data.get("headline") or data.get("title") or ""
                    b = data.get("Text") or data.get("text") or data.get("body") or ""
                    processed = preprocess_text(f"{h} {b}", stop_words, non_frequent_words)
                    for word in processed:
                        local_dict[stemmer.stem(word)].add(word)

        # Parquet Files
        elif file_name.endswith('.parquet'):
            pf = pq.ParquetFile(file_name)
            # Using batches to keep memory usage low
            for batch in pf.iter_batches(columns=["head_line", "text"], batch_size=5000):
                data = batch.to_pydict()
                headlines = data["head_line"]
                bodies = data["text"]
                
                for h, b in zip(headlines, bodies):
                    h = h if isinstance(h, str) else ""
                    b = b if isinstance(b, str) else ""
                    processed = preprocess_text(f"{h} {b}", stop_words, non_frequent_words)
                    for word in processed:
                        local_dict[stemmer.stem(word)].add(word)
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

    return local_dict

def build_stems_dictionary():
    # Detect both types of files
    all_files = glob.glob(os.path.join(files_path, "*.jsonl")) + \
                glob.glob(os.path.join(files_path, "*.parquet"))
    
    num_files = len(all_files)
    final_stem_to_words = defaultdict(set)
    
    # Using Pool(processes=num_files) is okay for 6 files
    with Pool(processes=num_files) as pool:
        for local_dict in tqdm(pool.imap_unordered(process_single_file, all_files), total=num_files):
            for stem, words in local_dict.items():
                final_stem_to_words[stem].update(words)
            print(f"Merged a file. Total stems: {len(final_stem_to_words)}")

    # Convert sets to lists and save
    final_dict_as_list = {stem: list(words) for stem, words in final_stem_to_words.items()}
    os.makedirs(os.path.dirname(output_pickle_path), exist_ok=True)
    with open(output_pickle_path, "wb") as f:
        pickle.dump(final_dict_as_list, f)
    
    print(f"Saved to {output_pickle_path} ")

if __name__ == "__main__":
    build_stems_dictionary()