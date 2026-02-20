import re
from farasa.diacratizer import FarasaDiacritizer


def smart_clean(text):
    # Keep Arabic letters, numbers, and basic punctuation
    text = re.sub(r'[^\u0600-\u06FF0-9\s\.\/\-\:\,\!\?]', '', text)
    return ' '.join(text.split())


def process_chunk(chunk, diacritizer):
    """Clean then diacritize a chunk."""
    chunk = smart_clean(chunk)
    return diacritizer.diacritize(chunk)


def diacritize_corpus(input_file, output_file, chunk_size=10000):
    """Diacritize full corpus safely without cutting words."""
    
    diacritizer = FarasaDiacritizer(interactive=True)

    with open(input_file, 'r', encoding='cp1256') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        remainder = ""

        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break

            # Add leftover from previous iteration
            chunk = remainder + chunk

            # Prevent cutting a word
            last_space = chunk.rfind(" ")
            if last_space == -1:
                remainder = chunk
                continue

            safe_chunk = chunk[:last_space]
            remainder = chunk[last_space:]

            diacritized_chunk = process_chunk(safe_chunk, diacritizer)
            outfile.write(diacritized_chunk + " ")

        # Process any remaining text
        if remainder.strip():
            diacritized_chunk = process_chunk(remainder, diacritizer)
            outfile.write(diacritized_chunk)


if __name__ == "__main__":
    input_file = 'arabic_corpus.txt'
    output_file = 'diacritized_arabic_corpus_3.txt'

    diacritize_corpus(input_file, output_file)