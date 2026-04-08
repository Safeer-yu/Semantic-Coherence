import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel
import re
import json
import os
import glob
from collections import Counter
import pyarrow.parquet as pq


files_path = "data_files/wiki_and_parquet"
stopwords_file_path = "arabic_stopwords_nltk.txt"
output_file_path = "data_files/data_stats/word_frequencies_main.txt"
stats_file_path = "data_files/data_stats/word_stats_main.txt"
low_freq_words_file_path = "data_files/data_stats/words_10_or_less_main.txt"

def load_stopwords(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return set(f.read().split())


def preprocess_text(text, stopwords):
  
    text = araby.strip_tatweel(text)
    # Switched to these cleaning steps to avoid word breaking or words concatenating
    # Remove defined punctuation
    punctuation = r'[\.،,؛;:!?؟?(){}\[\]<>"\'/\\@#$%^&*_+=~|]'
    text = re.sub(punctuation, ' ', text)
    # Remove Mashriki numerals (Arabic-Indic digits)
    text = re.sub(r'[٠-٩]', ' ', text)
    # Tokenize and strip tashkeel
    tokens = tokenize(text, conditions=is_arabicrange, morphs=strip_tashkeel)
    tokens = [token for token in tokens if token not in stopwords and len(token) > 1]
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

words_more_than_10 = 0
tokens_more_than_10 = 0

words_10_or_less = 0
tokens_10_or_less = 0

words_5_or_less = 0
tokens_5_or_less = 0

words_2_or_less = 0
tokens_2_or_less = 0

words_10_or_less_list = []

for word, freq in counter.items():
    if freq > 10:
        words_more_than_10 += 1
        tokens_more_than_10 += freq

    if freq <= 10:
        words_10_or_less += 1
        tokens_10_or_less += freq
        words_10_or_less_list.append(word)

    if freq <= 5:
        words_5_or_less += 1
        tokens_5_or_less += freq

    if freq <= 2:
        words_2_or_less += 1
        tokens_2_or_less += freq

with open(stats_file_path, "w", encoding="utf-8") as f:
    f.write(f"Total tokens: {total_tokens}\n")
    f.write(f"Unique words: {unique_words}\n\n")

    f.write(f"Words occurring more than 10 times: {words_more_than_10}\n")
    f.write(f"Percentage of unique words: {(words_more_than_10 / unique_words) * 100:.2f}%\n")
    f.write(f"Percentage of total tokens: {(tokens_more_than_10 / total_tokens) * 100:.2f}%\n\n")

    f.write(f"Words occurring 10 times or less: {words_10_or_less}\n")
    f.write(f"Percentage of unique words: {(words_10_or_less / unique_words) * 100:.2f}%\n")
    f.write(f"Percentage of total tokens: {(tokens_10_or_less / total_tokens) * 100:.2f}%\n\n")

    f.write(f"Words occurring 5 times or less: {words_5_or_less}\n")
    f.write(f"Percentage of unique words: {(words_5_or_less / unique_words) * 100:.2f}%\n")
    f.write(f"Percentage of total tokens: {(tokens_5_or_less / total_tokens) * 100:.2f}%\n\n")

    f.write(f"Words occurring 2 times or less: {words_2_or_less}\n")
    f.write(f"Percentage of unique words: {(words_2_or_less / unique_words) * 100:.2f}%\n")
    f.write(f"Percentage of total tokens: {(tokens_2_or_less / total_tokens) * 100:.2f}%\n")

with open(low_freq_words_file_path, "w", encoding="utf-8") as f:
    for word in words_10_or_less_list:
        f.write(word + "\n")

with open(output_file_path, "w", encoding="utf-8") as f:
    for word, freq in counter.most_common():
        f.write(f"{word}\t{freq}\n")

print(f"Saved word frequencies to {output_file_path}")
print(f"Saved stats to {stats_file_path}")
print(f"Saved words occurring 10 times or less to {low_freq_words_file_path}")