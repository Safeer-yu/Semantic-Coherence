# Semantic Coherence

This project investigates:

- The semantic coherence of Arabic morphological root families
- The effect of diacritization on embedding performance and semantic coherence


## Installation
### Install required packages

```bash
pip install -r requirements.txt
```
### Copy the template file to create your own .env file

```bash
cp .env.example .env
```

## Activate environment
```bash 
conda activate my_hpc_env
```
## Computational Resources

All large-scale experiments were conducted on the UAEU High Performance Computing (HPC) cluster.

## Data
- **Corpus**  
   - A [1.5 B-word structured Arabic corpus](https://huggingface.co/datasets/MohamedRashad/arabic-billion-words/tree/main/data).
  - The complete Arabic Wikipedia dump (~0.4 billion words)
  


# Pipeline

### Step 1 — Preprocessing
- Clean the corpus 
- Calculate token frequencies in order to exclude tokens that appear fewer than 10 times, since they are mostly typos, foreign words, or incorrectly connected words caused by scraping issues.
- Use these frequencies later when calculating frequency-weighted semantic coherence.


### Step 2 — Train Word Embeddings
- Train a Word2Vec model on the corpus.
- Evaluate embedding quality using similarity and analogy tests.
- Run the model several times to test different parameters. The best-performing parameters were selected for the final model.


### Step 3 — Root Extraction
We first stem the corpus and then extract roots from the stems.

#### 3.1 Stem Extraction (Farasa Stemmer)
- Preprocess corpus text.
- Extract stems using Farasa.
- Build a dictionary:
stem → words

#### 3.2 Root Extraction

Because stems do not always correspond to true linguistic roots, we first extracted roots using an existing lexical resource: Aralex: dictionary_with_stems_and_new_extracted_roots.xlsx.

For stems not covered by Aralex, we used the Claude API (claude-sonnet-4) to extract the roots. The model was given morphological instructions specifying Arabic root conventions, including connected letters, the use of ء for all hamza forms, and the handling of loanwords, proper nouns, colloquial words, and fused tokens.

Results were spot-checked on sample batches and deemed satisfactory.

The output is a root-to-words dictionary used for computing semantic coherence.

### Step 4 — Semantic Coherence Analysis

For each root family:

- Retrieve all words belonging to the root.
- Compute pairwise cosine similarity between word embeddings.
- Calculate semantic coherence in two versions:

  1. **Unweighted semantic coherence**  
     The average pairwise cosine similarity across all word pairs in a root family.

  2. **Frequency-weighted semantic coherence**  
     A weighted average of pairwise cosine similarities, where each word pair is weighted according to the frequencies of the two words. This gives more influence to pairs involving more frequent words.

In both versions, higher scores indicate greater semantic coherence within the root family.

### Step 5 — Diacritization
