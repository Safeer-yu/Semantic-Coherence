import os
import re
import json
import pickle
from collections import defaultdict
from farasa.stemmer import FarasaStemmer
import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel

# Initialize Farasa
farasa_stemmer = FarasaStemmer(interactive=True)

files_path = "data_files/data"
stopwords_file_path = 'arabic_stopwords_nltk.txt'
output_pickle_path = "New-Corpus/output/new_corpus_root_to_words_dict.pkl"

def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(f.read().split())

def preprocess_text(text, stopwords):
    """Clean and tokenize text specifically for Arabic root extraction."""
    text = araby.strip_tatweel(text)
    text = re.sub(r'[^\w\s]', '', text)
    # Filter for Arabic range
    arabic_only_text = re.sub(r'[^\u0621-\u064A\s]', '', text)
    
    # Tokenize and strip tashkeel
    tokens = tokenize(arabic_only_text, conditions=is_arabicrange, morphs=strip_tashkeel)
    # Remove stopwords and very short noise
    return [t for t in tokens if t not in stopwords and len(t) > 1]

class MyCorpus:
  
    def __init__(self, path, stopwords):
        self.files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jsonl')]
        self.stopwords = stopwords

    def __iter__(self):
        for file_name in self.files:
            with open(file_name, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        headline = data.get("Headline") or ""
                        body = data.get("Text") or data.get("text") or ""
                        full_text = f"{headline} {body}"
                        
                        processed = preprocess_text(full_text, self.stopwords)
                        if processed:
                            yield processed
                    except Exception:
                        continue

def build_root_dictionary():

    stop_words = load_stopwords(stopwords_file_path)
    
    sentences = MyCorpus(files_path, stop_words)
    root_to_words = defaultdict(set)
    

    
    count = 0
    for sentence in sentences:
        for word in sentence:
            try:
                # Farasa extracts the stem/root
                root = farasa_stemmer.stem(word)
                root_to_words[root].add(word)
            except:
                continue
        
        count += 1
        if count % 1000 == 0:
            print(f"Processed {count} documents...")

  
    final_dict = {root: list(words) for root, words in root_to_words.items()}
    

    with open(output_pickle_path, "wb") as f:
        pickle.dump(final_dict, f)


if __name__ == "__main__":
    build_root_dictionary()