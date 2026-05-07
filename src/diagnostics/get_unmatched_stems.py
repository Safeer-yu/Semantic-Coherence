import pickle
import pandas as pd


def load_word_to_root(file_path):
    """
    Load lookup dictionary from Excel using Word, Normalized_Word, and Stem columns.

    Priority:
    1. Word
    2. Normalized_Word
    3. Stem
    """
    word_to_root = {}

    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        word = row.get("Word")
        norm_word = row.get("Normalized_Word")
        stem = row.get("Stem")
        root = row.get("Root")

        if pd.notna(root) and root != "ــ":
            if pd.notna(word):
                word_to_root[word] = root

            if pd.notna(norm_word) and norm_word not in word_to_root:
                word_to_root[norm_word] = root

            if pd.notna(stem) and stem not in word_to_root:
                word_to_root[stem] = root

    return word_to_root


def export_unmatched_to_excel(stem_to_words_path, word_to_root_path, excel_output_path):
    with open(stem_to_words_path, "rb") as f:
        stem_to_words = pickle.load(f)

    word_to_root = load_word_to_root(word_to_root_path)

    unmatched_data = []

    for stem, words in stem_to_words.items():
        if stem not in word_to_root:
            unmatched_data.append({
                "Word": stem,
                "Collection_Size": len(words)
            })

    df = pd.DataFrame(unmatched_data)
    df = df.sort_values(by="Collection_Size", ascending=False)

    df.to_excel(excel_output_path, index=False)
    print(f"Saved unmatched words to: {excel_output_path}")


if __name__ == "__main__":
    stem_to_words_path = "New-Corpus/parquet/output/stem_to_words_dict.pkl"
    word_to_root_path = "dictionary_with_stems.xlsx"
    excel_output_path = "New-Corpus/test/unmatched_words.xlsx"

    export_unmatched_to_excel(stem_to_words_path, word_to_root_path, excel_output_path)