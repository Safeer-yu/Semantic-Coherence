import os
from openxlab.dataset import download
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")
# get json files from open data lab

files = [
    "Alittihad.jsonl",
    "Almasryalyoum.jsonl",
    "Almustaqbal.jsonl",
    "Alqabas.jsonl",
    "Echoroukonline.jsonl",
    "Riyadh.jsonl",
    "Sabanews.jsonl",
    "SaudiYoum.jsonl",
    "Techreen.jsonl"
]

OPENXLAB_AK = os.getenv("OPENXLAB_AK")
OPENXLAB_SK = os.getenv("OPENXLAB_SK")


path = 'data_files/1.5_Billion_words'

for file in files:
    print(f"Downloading {file}...")
    download(
    dataset_repo='OpenDataLab/arabic_billion_words', 
    source_path=f'/raw/json/{file}', 
    target_path=path
)
print("Download complete!")