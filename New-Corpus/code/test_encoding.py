import json

test_file = "data_files/data/wiki_corpus.jsonl" # Pick one file

print("--- Testing UTF-8 ---")
try:
    with open(test_file, 'r', encoding='utf-8') as f:
        print(f.read(10000))
except Exception as e:
    print(f"UTF-8 Failed: {e}")

print("\n--- Testing CP-1256 ---")
try:
    with open(test_file, 'r', encoding='cp1256') as f:
        print(f.read(10000))
except Exception as e:
    print(f"CP-1256 Failed: {e}")


    #/home/safeer.alyubary/Semantic-Coherence/data_files/data/Alittihad.jsonl