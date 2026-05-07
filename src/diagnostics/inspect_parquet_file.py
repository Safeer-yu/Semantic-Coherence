import os
import glob
import pyarrow.parquet as pq

DATA_DIR = "data_files/parquet"
OUTPUT_FILE = "test/sample_output.txt"

parquet_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.parquet")))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(f"Total files: {len(parquet_files)}\n\n")

    for file in parquet_files:
        f.write("\n" + "="*80 + "\n")
        f.write(f"FILE: {file}\n")
        
        pq_file = pq.ParquetFile(file)
        
        # read first 5 rows only
        batch_iter = pq_file.iter_batches(batch_size=5)
        batch = next(batch_iter)
        
        data = batch.to_pydict()
        num_rows = len(next(iter(data.values())))
        
        for i in range(num_rows):
            f.write(f"\n--- Document {i+1} ---\n")
            
            for col, values in data.items():
                value = values[i]
                
                # shorten long text
                if isinstance(value, str) and len(value) > 300:
                    value = value[:300] + " ..."
                
                f.write(f"{col}: {value}\n")

print(f"Done. Output saved to: {OUTPUT_FILE}")