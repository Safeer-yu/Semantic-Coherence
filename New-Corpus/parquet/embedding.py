import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel
from gensim.models import Word2Vec
import re
import json
import os
import glob
import pyarrow.parquet as pq


files_path = "/data_files/parquet"

stopwords_file_path = "arabic_stopwords_nltk.txt"
model_save_path = "New-Corpus/parquet/output/word2vec.model"


def load_stopwords(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return set(f.read().split())


def preprocess_text(text, stopwords):
    """Clean and tokenize text specifically for Arabic root extraction."""
    text = araby.strip_tatweel(text)
    # Switched to these cleaning steps to avoid word breaking or words concatenating
    punctuation = r'[\.،,؛;:!?؟?(){}\[\]<>"\'/\\@#$%^&*_+=~|]'
    # Remove defined punctuation
    text = re.sub(punctuation, ' ', text)
    # Tokenize and strip tashkeel
    tokens = tokenize(text, conditions=is_arabicrange, morphs=strip_tashkeel)
    tokens = [token for token in tokens if token not in stopwords and len(token) > 1]
    return tokens


class MyCorpus:
    def __init__(self, path, stopwords):
        self.jsonl_files = glob.glob(os.path.join(path, "*.jsonl"))
        self.parquet_files = glob.glob(os.path.join(path, "*.parquet"))
        self.stopwords = stopwords

    def __iter__(self):
        for file_name in self.jsonl_files:
            with open(file_name, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        headline = data.get("Headline") or data.get("headline") or data.get("title") or ""
                        body = data.get("Text") or data.get("text") or data.get("body") or ""
                        full_text = f"{headline} {body}"

                        processed = preprocess_text(full_text, self.stopwords)
                        if processed:
                            yield processed
                    except:
                        continue

        for file_name in self.parquet_files:
            try:
                pq_file = pq.ParquetFile(file_name)

                for batch in pq_file.iter_batches(columns=["head_line", "text"], batch_size=1000):
                    headlines = batch.column(0).to_pylist()
                    bodies = batch.column(1).to_pylist()

                    for headline, body in zip(headlines, bodies):
                        headline = headline if isinstance(headline, str) else ""
                        body = body if isinstance(body, str) else ""
                        full_text = f"{headline} {body}"

                        processed = preprocess_text(full_text, self.stopwords)
                        if processed:
                            yield processed
            except:
                continue


stop_words = load_stopwords(stopwords_file_path)
sentences = MyCorpus(files_path, stop_words)

model = Word2Vec(
    sentences=sentences,
    vector_size=100,
    window=5,
    min_count=5,
    sg=1,
    workers=36
)

model.save(model_save_path)
print(f"Success! Model saved to {model_save_path}")