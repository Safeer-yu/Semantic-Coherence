import os
import re
import json
import pickle
import glob
import pyarrow.parquet as pq  
from collections import defaultdict
from farasa.stemmer import FarasaStemmer
import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel


files_path = "data_files/wiki_and_parquet"
stopwords_file_path = 'arabic_stopwords_nltk.txt'
non_frequent_words_file_path= "data_files/data_stats/words_10_or_less_main.txt"
output_pickle_path = "parquet/output/stem_to_words_dict.pkl"

farasa_stemmer = FarasaStemmer(interactive=True)

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

class MyCorpus:
    def __init__(self, path, stopwords, non_frequent_words):
        self.jsonl_files = glob.glob(os.path.join(path, "*.jsonl"))
        self.parquet_files = glob.glob(os.path.join(path, "*.parquet"))
        self.stopwords = stopwords
        self.non_frequent_words= non_frequent_words


    def __iter__(self):
        for file_name in self.jsonl_files:
            with open(file_name, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        headline = data.get("Headline") or data.get("headline") or data.get("title") or ""
                        body = data.get("Text") or data.get("text") or data.get("body") or ""
                        full_text = f"{headline} {body}"

                        processed = preprocess_text(full_text, self.stopwords, self.non_frequent_words)
                        if processed:
                            yield processed
                    except:
                        continue

        for file_name in self.parquet_files:
            try:
                pq_file = pq.ParquetFile(file_name)

                for batch in pq_file.iter_batches(columns=["head_line", "text"], batch_size=5000):
                    data = batch.to_pydict()
                    headlines = data.get("head_line", [])
                    bodies = data.get("text", [])

                    for headline, body in zip(headlines, bodies):
                        headline = headline if isinstance(headline, str) else ""
                        body = body if isinstance(body, str) else ""
                        full_text = f"{headline} {body}"

                        processed = preprocess_text(full_text, self.stopwords, self.non_frequent_words)
                        if processed:
                            yield processed
            except:
                continue

def build_stems_dictionary():

    stopwords = load_stopwords(stopwords_file_path)
    non_frequent_words = load_non_frequent_words(non_frequent_words_file_path)
    
    sentences = MyCorpus(files_path, stopwords, non_frequent_words)
    stem_to_words = defaultdict(set)

    stem_cache = {} # Added cache to avoid repeated stemming of the same word
    

    
    count = 0
    for sentence in sentences:
        for word in sentence:
            try:
                # Farasa extracts the stem
                if word in stem_cache:
                    stem = stem_cache[word]
                else:
                    stem = farasa_stemmer.stem(word)
                    stem_cache[word] = stem

                stem_to_words[stem].add(word)
            except:
                continue
        
        count += 1
        if count % 1000 == 0:
            print(f"Processed {count} documents...")

  
    final_dict = {stem: list(words) for stem, words in stem_to_words.items()}
    os.makedirs(os.path.dirname(output_pickle_path), exist_ok=True)

    with open(output_pickle_path, "wb") as f:
        pickle.dump(final_dict, f)


if __name__ == "__main__":
    build_stems_dictionary()