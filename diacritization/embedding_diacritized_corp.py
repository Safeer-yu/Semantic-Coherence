import pyarabic.araby as araby
import re
from gensim.models import Word2Vec
from pyarabic.araby import tokenize, is_arabicrange

def load_stopwords(file_path):
    """
    Load stopwords from a file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().split())
    return stopwords

def preprocess_text(text, stopwords):
    """
    Clean and tokenize the text, removing stopwords.
    """
    text = re.sub(' +', ' ', text)  # Remove extra spaces
    text = araby.strip_tatweel(text)  # Remove tatweel (elongation)
    punctuation = r'[\.,;:!??(){}\[\]<>"\'/\\@#$%^&*_+=~|]'
    # Remove defined punctuation
    text = re.sub(punctuation, '', text)
    tokens = tokenize(text, conditions=is_arabicrange)  # Tokenize and filter non-Arabic characters
    tokens = [token for token in tokens if token not in stopwords]  # Remove stopwords

    return tokens

def read_and_preprocess_corpus(file_path, stopwords, chunk_size=10000):
    """
    Generator to read and preprocess the corpus in chunks, ensuring words are not split between chunks.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        remainder = ''
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            # Combine remainder from previous chunk with the current chunk
            chunk = remainder + chunk
            
            # Find the last space or punctuation mark to avoid splitting a word
            last_space_index = max(chunk.rfind(' '), chunk.rfind('\n'), chunk.rfind('\t'))
            
            if last_space_index == -1:
                # If no space is found, process the entire chunk (unlikely scenario)
                tokens = preprocess_text(chunk, stopwords)
                remainder = ''
            else:
                # Process the part of the chunk up to the last space
                tokens = preprocess_text(chunk[:last_space_index], stopwords)
                
                # Store the remainder (unprocessed part of the chunk)
                remainder = chunk[last_space_index:]
            
            yield tokens
        
        # Process any remaining text after the last chunk
        if remainder:
            tokens = preprocess_text(remainder, stopwords)
            yield tokens

if __name__ == "__main__":
    corpus_file_path = 'full_diacritized_arabic_corpus.txt'
    stopwords_file_path = 'diacritized_arabic_stopwords_nltk.txt'

    # Load stopwords
    stopwords = load_stopwords(stopwords_file_path)

    # Read and preprocess the corpus
    tokenized_corpus = list(read_and_preprocess_corpus(corpus_file_path, stopwords))

    # Initialize and train the Word2Vec model
    model = Word2Vec(vector_size=100, window=5, min_count=5, sg=1, workers=4)
    model.build_vocab(tokenized_corpus)

    # Train the Word2Vec model
    model.train(tokenized_corpus, total_examples=model.corpus_count, epochs=5)

    # Save the model
    model.save("main_corpus_diacritized_word2vec_no_stopwords.model")
    print("Model saved as main_corpus_diacritized_word2vec_no_stopwords.model")
