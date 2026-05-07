import pickle

# Path to your pickle file
input_pkl = "parquet/output/root_to_words_dict_one_word_collection_excluded.pkl"

# Path to output text file
output_txt = "parquet/output/root_to_words_dict_one_word_collection_excluded.txt"
# Load pickle file
with open(input_pkl, "rb") as f:
    data = pickle.load(f)

with open(output_txt, "w", encoding="utf-8") as f:
    f.write("{\n")
    
    for i, (stem, words) in enumerate(data.items()):
        comma = "," if i < len(data) - 1 else ""
        f.write(f"{stem}: {words}{comma}\n")
    
    f.write("}")

print("Conversion complete!")

