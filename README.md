# Semantic Coherence

This project investigates:

- The semantic coherence of Arabic morphological root families
- The effect of diacritization on embedding performance

The work began with an existing large Arabic corpus (~1.9B words).
During experimentation, a better-structured corpus was identified and adopted after it demonstrated superior embedding performance.

## Installation
```bash
pip install -r requirements.txt
```

## Activate environment
```bash 
conda activate my_hpc_env
```
## Computational Resources

All large-scale experiments were conducted on the UAEU High Performance Computing (HPC) cluster.


## Data
- **Original Corpus (Initial Experiments)**
The project uses an [Arabic text corpus](https://github.com/tarekeldeeb/arabic_corpus?tab=readme-ov-file) which consists of 1.9 billion words

- **New Corpus (Recommended)**  
  More structured Arabic corpus totaling approximately 1.9 billion words.  
  This dataset combines:
  - A [1.5 B-word structured Arabic corpus](https://opendatalab.com/OpenDataLab/arabic_billion_words/cli/main)  
  - The complete Arabic Wikipedia dump (~0.4 billion words)
  
After training embeddings on this corpus, similarity evaluations showed significantly improved performance.
As a result, this corpus is recommended for embedding-based experiments.

## Pipeline
The following pipeline was applied to the Original Corpus, and partially repeated on the New Corpus.

### Step 1 — Train Word Embeddings
- Train a Word2Vec model on the corpus.
- Evaluate embedding quality using similarity tests.

The New Corpus embeddings outperformed the Original Corpus embeddings in similarity evaluations.

### Step 2 — Root Extraction
#### 2.1 Initial Extraction (Farasa Stemmer)
- Preprocess corpus text.
- Extract stems using Farasa.
- Build a dictionary:
stem → words

#### 2.2 Improved Root Mapping
Because stems do not always correspond to true linguistic roots:
- Use an external word–root dictionary (word_root_dictionary_Arabic.xlsx).
- Complete missing mappings using Araflex
- Merge stems sharing the same root.
- Produce: root → words
Saved as:
updated_main_corpus_root_to_words_dict.pkl

### Step 3 — Semantic Coherence Analysis
For each root family:
- Retrieve all words belonging to the root.
- Compute pairwise distances between word embeddings.
- Calculate the average pairwise distance.
- Exclude roots with fewer than 10 words to reduce noise.

### Step 4 — Diacritization
- Apply Farasa diacritizer to the corpus.
- Train embeddings on the diacritized corpus.
- Evaluate performance differences.

Farasa performs well on standard structures but is not perfectly accurate, especially in ambiguous constructions