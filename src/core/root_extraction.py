"""
Using Farasa, we built a stem-to-words dictionary.
Since stems do not always match roots, we first extracted roots using an existing 
lexical resource (Aralex: dictionary_with_stems_and_new_extracted_roots.xlsx).
For stems not covered by Aralex, we used the Claude API (claude-sonnet-4)
to extract the roots. The model was given morphological instructions specifying 
Arabic root conventions (connected letters, ء for all hamza forms, handling of 
loanwords, proper nouns, colloquial words, and fused tokens).
Results were spot-checked on sample batches and deemed satisfactory.
The output is a root-to-words dictionary to be used for computing semantic coherence.

"""


import pickle
from collections import defaultdict
import pandas as pd  

def load_word_to_root(file_path):
    """
    Load the word-to-root dictionary from an Excel file.
    Priority:
    1. Word
    2. Normalized Word
    3. Stem
    """
    word_to_root = {}
    
    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        word = row.get('Word')
        norm_word = row.get('Normalized_Word')  
        stem = row.get('Stem')
        root = row.get('Root')
        
        if pd.notna(root) and root != "ــ":
            
            # Highest priority: Word
            if pd.notna(word):
                word_to_root[word] = root

            # Only add if not already mapped
            if pd.notna(norm_word) and norm_word not in word_to_root:
                word_to_root[norm_word] = root

            if pd.notna(stem) and stem not in word_to_root:
                word_to_root[stem] = root
    
    return word_to_root

def update_stem_to_words_with_roots(stem_to_words, word_to_root):
    """
    Update the stem_to_words dictionary by replacing stems with roots from word_to_root.
    """
    root_to_words = defaultdict(set)
    
    for stem, words in stem_to_words.items():

        # if len(words) <= 1:   # uncomment to skip stems with only one word
        #     continue
        
        root = word_to_root.get(stem)  
        

        if not root:  # Skip stems with no root
            continue
        
        root_to_words[root].update(words)
    
    # Convert sets to lists for final dictionary
    root_to_words = {root: list(words) for root, words in root_to_words.items()}
    
    return root_to_words

def main():
    # Load the stem to words dictionary
    stem_to_words_path = "New-Corpus/parquet/output/stem_to_words_dict.pkl"
    with open(stem_to_words_path, "rb") as file:
        stem_to_words = pickle.load(file)

    # Load the word to root dictionary from the Excel file
    word_to_root_path = "dictionary_with_stems_and_new_extracted_roots.xlsx" 
    word_to_root = load_word_to_root(word_to_root_path)

    # Update the stem_to_words dictionary with roots
    root_to_words = update_stem_to_words_with_roots(stem_to_words, word_to_root)

    # Save the updated dictionary
    updated_dict_path = "src/output/root_to_words_dict.pkl"
    with open(updated_dict_path, "wb") as file:
        pickle.dump(root_to_words, file)

    print(f"Updated dictionary saved to {updated_dict_path}")

if __name__ == "__main__":
    main()