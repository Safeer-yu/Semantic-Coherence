import re
import pickle
from collections import defaultdict
from farasa.stemmer import FarasaStemmer
import pyarabic.araby as araby
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel

# Initialize Farasa stemmer
farasa_stemmer = FarasaStemmer(interactive=True)

def preprocess_text(text, stopwords, root_to_words):
    """
    Clean, tokenize, and update the root_to_words dictionary.
    """
    text = re.sub(' +', ' ', text)  # Remove extra spaces
    text = araby.strip_tatweel(text)  # Remove tatweel (elongation)
    # Remove punctuations
    text = re.sub(r'[^\w\s]', '', text)
    arabic_only_text = re.sub(r'[^\u0621-\u064A\s]', '', text)  # Arabic letters only (excluding Persian/Urdu chars)
    tokens = tokenize(arabic_only_text, conditions=is_arabicrange, morphs=strip_tashkeel)
    
    for word in tokens:
        if word not in stopwords:
            root = farasa_stemmer.stem(word)
            root_to_words[root].add(word)  # Add word to the set for that root

def read_and_process_corpus(file_path, stopwords, root_to_words, chunk_size=200000):

    with open(file_path, 'r', encoding='cp1256') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            preprocess_text(chunk, stopwords, root_to_words)

def main():
    # Paths
    corpus_path = '/home/safeer.alyubary/embedding_4/arabic_corpus.txt'
    stopwords_path = "arabic_stopwords_nltk.txt"
    output_path = "data_files/main_corpus_root_to_words_dict.pkl"

    # Load stopwords
    with open(stopwords_path, "r", encoding="utf-8") as file:
        stopwords = set(file.read().split())

    # Use a set to avoid duplicates during processing
    root_to_words = defaultdict(set)

    # Process the corpus in chunks
    print("Processing the corpus in chunks...")
    read_and_process_corpus(corpus_path, stopwords, root_to_words)

    # Convert sets to lists for final storage

    root_to_words_final = {root: list(words) for root, words in root_to_words.items()}


    with open(output_path, "wb") as file:
        pickle.dump(root_to_words_final, file, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Dictionary saved to {output_path}")

if __name__ == "__main__":
    main()
    

