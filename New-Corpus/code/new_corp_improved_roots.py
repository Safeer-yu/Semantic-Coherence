"""
Using Farasa, we built a stem-to-words dictionary and saved it as main_corpus_root_to_words_dict.pkl.
Since stems do not always match roots, we extracted roots using an existing dictionary (word_root_dictionary_Arabic.xlsx), 
and missing stems were completed with Araflex. All stem–root pairs were compiled in updated_main_corpus_root_to_words_dict.pkl 
and used to update the main dictionary by grouping words under their shared roots.

"""


import pickle
from collections import defaultdict
import pandas as pd  

def load_word_to_root(file_path):
    """
    Load the word-to-root dictionary from an Excel file.
    """
    word_to_root = {}
    
    # Read the Excel file
    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        word = row['Word']
        root = row['Root']
        if root != "ــ":  # Ignore entries where the root is missing
            word_to_root[word] = root
    
    return word_to_root

def update_stem_to_words_with_roots(stem_to_words, word_to_root):
    """
    Update the stem_to_words dictionary by replacing stems with roots from word_to_root.
    """
    root_to_words = defaultdict(set)
    
    for stem, words in stem_to_words.items():
        root = word_to_root.get(stem, stem)  # Use root if available and valid, otherwise keep the stem
        root_to_words[root].update(words)
    
    # Convert sets to lists for final dictionary
    root_to_words = {root: list(words) for root, words in root_to_words.items()}
    
    return root_to_words

def main():
    # Load the stem to words dictionary
    stem_to_words_path = "New-Corpus/output/new_corpus_root_to_words_dict.pkl"
    with open(stem_to_words_path, "rb") as file:
        stem_to_words = pickle.load(file)

    # Load the word to root dictionary from an Excel file
    word_to_root_path = "word_root_dictionary_Arabic.xlsx" 
    word_to_root = load_word_to_root(word_to_root_path)

    # Update the stem_to_words dictionary with roots
    root_to_words = update_stem_to_words_with_roots(stem_to_words, word_to_root)

    # Save the updated dictionary
    updated_dict_path = "New-Corpus/output/updated_new_corpus_root_to_words_dict.pkl"
    with open(updated_dict_path, "wb") as file:
        pickle.dump(root_to_words, file)

    print(f"Updated dictionary saved to {updated_dict_path}")

if __name__ == "__main__":
    main()