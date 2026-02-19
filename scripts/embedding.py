import pyarabic.araby as araby
import re
from gensim.models import Word2Vec
from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel



def load_stopwords(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().split())
    return stopwords


def preprocess_text(text, stopwords):
    """
    Clean and tokenize the text, removing stopwords.
    """
    text = re.sub(' +', ' ', text)  # Remove extra spaces
    text = araby.strip_tatweel(text)  # Remove tatweel (elongation)
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuations
    arabic_only_text = re.sub(r'[^\u0621-\u064A\s]', '', text)  # Arabic letters only (excluding Persian/Urdu chars)
    tokens = tokenize(arabic_only_text, conditions=is_arabicrange, morphs=strip_tashkeel)  # Tokenize and filter non-Arabic characters
    tokens = [token for token in tokens if token not in stopwords]  # Remove stopwords


    return tokens

def read_and_preprocess_corpus(file_path, stopwords, chunk_size=10000):
    """
    Generator to read and preprocess the corpus in chunks.
    """
    with open(file_path, 'r', encoding='cp1256') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            tokens = preprocess_text(chunk, stopwords)
            yield tokens

if __name__ == "__main__":
    corpus_file_path = 'arabic_corpus.txt'
    stopwords_file_path = 'arabic_stopwords_nltk.txt'

    stopwords = load_stopwords(stopwords_file_path)

    # Read and preprocess the corpus
    tokenized_corpus = list(read_and_preprocess_corpus(corpus_file_path, stopwords))

    # Initialize and train the Word2Vec model
    model = Word2Vec(vector_size=100, window=5, min_count=5, sg=1, workers=36)
    model.build_vocab(tokenized_corpus)

    # Train the Word2Vec model
    model.train(tokenized_corpus, total_examples=model.corpus_count, epochs=5)

    # Save the model
    model.save("main_corpus_word2vec.model")
    print("Model saved as main_corpus_word2vec.model")
