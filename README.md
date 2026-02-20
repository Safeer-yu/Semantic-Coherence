# Semantic Coherence

## Installation
```bash
pip install -r requirements.txt
```

## Activate environment
```bash 
conda activate my_hpc_env
```
## Computational Resources

This work was performed using the UAEU High Performance Computing (HPC) cluster. 


## Data
- **Original Corpus**
The project uses an [Arabic text corpus](https://github.com/tarekeldeeb/arabic_corpus?tab=readme-ov-file) which consists of 1.9 billion words

- **New Corpus (Recommended)**  
  A larger and more structured Arabic corpus totaling approximately 1.9 billion words.  
  This dataset combines:
  - A [1.5 B-word structured Arabic corpus](https://opendatalab.com/OpenDataLab/arabic_billion_words/cli/main)  
  - The complete Arabic Wikipedia dump - aronund 0.4 billion words
   

## Building an Arabic Dictionary of Words and Their Roots

Using Farasa, we initially built a stem-to-words dictionary.
Since stems do not always correspond to roots, we extracted roots using an existing dictionary (word_root_dictionary_Arabic.xlsx), and missing stems were completed with Araflex.
All stem–root pairs were compiled and used to produce updated_main_corpus_root_to_words_dict.pkl, where words are grouped under their shared roots.

## Semantic Coherence

After building a dictionary of roots and their associated words, we compute the pairwise distances between all words within each root family using a word embedding model.
For each root, we calculate the average distance across all word pairs.
To reduce noise, roots with fewer than 10 associated words are excluded from this analysis.

## Diacrtization
We used Farasa as the initial diacritization tool. It performs well on standard sentence structures; however, some limitations were observed in complex or ambiguous constructions. As expected, the output is not 100% accurate.