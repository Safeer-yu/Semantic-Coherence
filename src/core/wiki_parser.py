# wiki dump + Metadata


import requests
import os
import json
import hashlib
import mwparserfromhell
from gensim.corpora.wikicorpus import extract_pages
import bz2
from datetime import datetime, timezone

def sha256_of_file(path, chunk_size=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def download_arabic_wiki_dump():
    url = "https://dumps.wikimedia.org/arwiki/latest/arwiki-latest-pages-articles.xml.bz2"
    save_dir = "data_files/wiki_articles_2"
    local_filename = os.path.join(save_dir, "arwiki-latest-pages-articles.xml.bz2")

    os.makedirs(save_dir, exist_ok=True)

    if os.path.exists(local_filename):
        print(f"File already exists at {local_filename}, skipping download.")
        return local_filename, url

    print("Downloading Arabic Wikipedia dump...")
    with requests.get(url, stream=True, allow_redirects=True) as r:
        r.raise_for_status()
        final_url = r.url
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)

    return local_filename, final_url

def process_wikipedia_dump(dump_file_path, output_file_path):
    article_count = 0
    with bz2.open(dump_file_path, 'rb') as f:
        pages = extract_pages(f)

        with open(output_file_path, "w", encoding="utf-8") as output:
            for i, (title, content, pageid) in enumerate(pages):
                content_start = content.strip().lower()
                if content_start.startswith("#redirect") or content_start.startswith("#تحويل"):
                    continue

                try:
                    wikicode = mwparserfromhell.parse(content)
                    clean_text = wikicode.strip_code().strip()
                except Exception:
                    continue

                article = {
                    "id": i,
                    "Headline": title,
                    "Text": clean_text
                }

                output.write(json.dumps(article, ensure_ascii=False) + "\n")
                article_count += 1

                if i > 0 and i % 5000 == 0:
                    print(f"Processed {i} articles...")

    return article_count

if __name__ == "__main__":
    base_dir = os.getcwd()
    dump_path, resolved_url = download_arabic_wiki_dump()

    output_dir = os.path.join(base_dir, "data_files", "data")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "wiki_corpus_2.jsonl")
    metadata_path = os.path.join(output_dir, "wiki_corpus_metadata.json")

    article_count = process_wikipedia_dump(dump_path, output_path)

    metadata = {
        "source_name": "Arabic Wikipedia",
        "requested_url": "https://dumps.wikimedia.org/arwiki/latest/arwiki-latest-pages-articles.xml.bz2",
        "resolved_url": resolved_url,
        "download_utc": datetime.now(timezone.utc).isoformat(),
        "dump_filename": os.path.basename(dump_path),
        "dump_size_bytes": os.path.getsize(dump_path),
        "dump_sha256": sha256_of_file(dump_path),
        "output_file": output_path,
        "article_count": article_count,
        "parser_note": "mwparserfromhell used for Arabic-friendly raw wikitext parsing; redirects removed."
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Saved metadata to {metadata_path}")