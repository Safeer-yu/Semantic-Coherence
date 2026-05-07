import os
import glob
import pyarrow.parquet as pq

# Folder
DATA_DIR = "data_files/parquet"



def count_words(text):
    if isinstance(text, str):
        return len(text.split())
    return 0

total_words = 0
file_count = 0

parquet_files = glob.glob(os.path.join(DATA_DIR, "*.parquet"))

for file in parquet_files:
    print(f"\nProcessing: {file}")
    
    pq_file = pq.ParquetFile(file)
    file_words = 0  # words in this file only
    
    for batch in pq_file.iter_batches(columns=["head_line", "text"]):
        headlines = batch.column(0).to_pylist()
        bodies = batch.column(1).to_pylist()
        
        for h, b in zip(headlines, bodies):
            file_words += count_words(h)
            file_words += count_words(b)
    
    print(f"Words in this file: {file_words:,}")
    
    total_words += file_words
    file_count += 1

print("\n======================")
print(f"Files processed: {file_count}")
print(f"Total words (headline + body): {total_words:,}")