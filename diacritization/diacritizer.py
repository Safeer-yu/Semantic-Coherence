from farasa.diacratizer import FarasaDiacritizer
from pyarabic.araby import tokenize, is_arabicrange

# Initialize the diacritizer once outside the loop
DIACRITIZER = FarasaDiacritizer(interactive=True)

def clean_and_diacritize(chunk, diacritizer):
    """Clean non-Arabic text then diacritize the result."""
    # filter for Arabic-only tokens
    tokens = tokenize(chunk)
    arabic_tokens = [token for token in tokens if is_arabicrange(token)]
    
    # Re-join tokens into a clean string
    clean_text = ' '.join(arabic_tokens)
    
    # If the chunk was all non-Arabic, clean_text will be empty
    if not clean_text.strip():
        return ""
        
    # Diacritize the cleaned text
    return diacritizer.diacritize(clean_text)

def process_corpus(input_file, output_file, chunk_size=10000):
    """Main loop to process the file chunk by chunk."""
    with open(input_file, 'r', encoding='cp1256', errors='ignore') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        print("Processing started...")
        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break
            
            result = clean_and_diacritize(chunk, DIACRITIZER)
            
            if result:
                outfile.write(result + '\n') # Added newline for readability

if __name__ == "__main__":
    INPUT = 'arabic_corpus.txt'
    OUTPUT = 'cleaned_diacritized_corpus.txt'
    
    process_corpus(INPUT, OUTPUT)
    print("Task complete.")