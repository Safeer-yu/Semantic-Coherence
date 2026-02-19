import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel
from gensim.models import Word2Vec
import re
import json
import os


files_path = "data_files/data"
stopwords_file_path = 'arabic_stopwords_nltk.txt'
model_save_path = "New-Corpus/models/new_corp_word2vec.model"

# Ensure the model directory exists
os.makedirs(os.path.dirname(model_save_path), exist_ok=True)

def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().split())

    return stopwords

def preprocess_text(text, stopwords):
    """Clean and tokenize the text, removing stopwords."""
    text = araby.strip_tatweel(text)
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    # Filter for Arabic alphabet range
    arabic_only_text = re.sub(r'[^\u0621-\u064A\s]', '', text)
    
    # Tokenize and strip tashkeel simultaneously
    tokens = tokenize(arabic_only_text, conditions=is_arabicrange, morphs=strip_tashkeel)
    tokens = [token for token in tokens if token not in stopwords and len(token)>1]  # Remove stopwords
  
    return tokens


class MyCorpus:
    """Iterable generator to keep memory usage low."""
    def __init__(self, path, stopwords):
        self.files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jsonl')]
        self.stopwords = stopwords

    def __iter__(self):
        for file_name in self.files:
            with open(file_name, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        # Check multiple possible keys for text
                        headline = data.get("Headline", "")
                        body = data.get("Text") or data.get("text") or ""
                        full_text = f"{headline} {body}"
                        
                        processed = preprocess_text(full_text, self.stopwords)
                        if processed:
                            yield processed
                    except Exception as e:
                        continue


print("Loading stopwords and preparing corpus...")
stop_words = load_stopwords(stopwords_file_path)
sentences = MyCorpus(files_path, stop_words)

print("Training Word2Vec model (Skip-gram)...")
model = Word2Vec(
    vector_size=100, 
    window=5, 
    min_count=5, 
    sg=1, 
    workers=36
)

# Build vocabulary from the generator
model.build_vocab(sentences)

# Train the model
model.train(
    sentences, 
    total_examples=model.corpus_count, 
    epochs=5
)

model.save(model_save_path)
print(f"Success! Model saved to {model_save_path}")