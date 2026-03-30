import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel
import re
import json
import os
import glob
from collections import Counter
import pyarrow.parquet as pq


files_path = "data_files/parquet"
stopwords_file_path = "arabic_stopwords_nltk.txt"
output_file_path = "data_files/word_frequencies_2.txt"
stats_file_path = "data_files/word_stats_2.txt"

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
    tokens = [token for token in tokens if token not in stopwords]
    return tokens

counter = Counter()
stop_words = load_stopwords(stopwords_file_path)

jsonl_files = glob.glob(os.path.join(files_path, "*.jsonl"))
parquet_files = glob.glob(os.path.join(files_path, "*.parquet"))

for file_name in jsonl_files:
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                headline = data.get("Headline") or data.get("headline") or data.get("title") or ""
                body = data.get("Text") or data.get("text") or data.get("body") or ""
                full_text = f"{headline} {body}"

                tokens = preprocess_text(full_text, stop_words)
                counter.update(tokens)
            except:
                continue

for file_name in parquet_files:
    try:
        pq_file = pq.ParquetFile(file_name)

        for batch in pq_file.iter_batches(columns=["head_line", "text"], batch_size=5000):
            headlines = batch.column(0).to_pylist()
            bodies = batch.column(1).to_pylist()

            for headline, body in zip(headlines, bodies):
                headline = headline if isinstance(headline, str) else ""
                body = body if isinstance(body, str) else ""
                full_text = f"{headline} {body}"

                tokens = preprocess_text(full_text, stop_words)
                counter.update(tokens)
    except:
        continue



# Stats

total_tokens = sum(counter.values())
unique_words = len(counter)

with open(stats_file_path, "w", encoding="utf-8") as f:
    f.write(f"Total tokens: {total_tokens}\n")
    f.write(f"Unique words: {unique_words}\n")



with open(output_file_path, "w", encoding="utf-8") as f:
    for word, freq in counter.most_common():
        f.write(f"{word}\t{freq}\n")

print(f"Saved word frequencies to {output_file_path}")