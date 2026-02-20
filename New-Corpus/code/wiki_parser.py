import requests
import os
import json
import mwparserfromhell
from gensim.corpora.wikicorpus import extract_pages
import bz2

def download_arabic_wiki_dump():
    url = "https://dumps.wikimedia.org/arwiki/latest/arwiki-latest-pages-articles.xml.bz2"
    save_dir = "data_files/wiki_articles"
    local_filename = os.path.join(save_dir, "arwiki-latest-pages-articles.xml.bz2")
    
    os.makedirs(save_dir, exist_ok=True)

    if os.path.exists(local_filename):
        print(f"File already exists at {local_filename}, skipping download.")
        return local_filename

    print("Downloading Arabic Wikipedia dump...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
    return local_filename

def process_wikipedia_dump(dump_file_path, output_file_path):
    with bz2.open(dump_file_path, 'rb') as f:
        pages = extract_pages(f)

        with open(output_file_path, "w", encoding="utf-8") as output:
            for i, (title, content, pageid) in enumerate(pages):
                
                # Filter out Redirects (English and Arabic)
    
                content_start = content.strip().lower()
                if content_start.startswith("#redirect") or content_start.startswith("#تحويل"):
                    continue
                try:
                    wikicode = mwparserfromhell.parse(content)
                    clean_text = wikicode.strip_code().strip()
                except Exception:
                    # cases where the parser might fail on very weird formatting
                    continue

                article = {
                    "id": i,
                    "Headline": title,
                    "Text": clean_text
                }

                # Write to file immediately
                output.write(json.dumps(article, ensure_ascii=False) + "\n")

                if i > 0 and i % 5000 == 0:
                    print(f"Processed {i} articles...")

    print("Processing complete!")

if __name__ == "__main__":
    base_dir = os.getcwd() 
    dump_path = download_arabic_wiki_dump()
    os.makedirs("data_files/wiki_articles", exist_ok=True)
    output_path = os.path.join(base_dir, "data_files/wiki_articles/wiki_corpus.jsonl")
    
    process_wikipedia_dump(dump_path, output_path)