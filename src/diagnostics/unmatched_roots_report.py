import pickle
import pandas as pd


def load_word_to_root(file_path):
    """
    Load lookup dictionary from Excel using Word, Normalized_Word, and Stem columns.

    Priority:
    1. Word
    2. Normalized_Word
    3. Stem
    """
    word_to_root = {}

    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        word = row.get("Word")
        norm_word = row.get("Normalized_Word")
        stem = row.get("Stem")
        root = row.get("Root")

        if pd.notna(root) and root != "ــ":
            # Highest priority: exact word
            if pd.notna(word):
                word_to_root[word] = root

            # Add normalized word only if not already mapped by Word
            if pd.notna(norm_word) and norm_word not in word_to_root:
                word_to_root[norm_word] = root

            # Add stem only if not already mapped by Word or Normalized_Word
            if pd.notna(stem) and stem not in word_to_root:
                word_to_root[stem] = root

    return word_to_root


def collect_unmatched(stem_to_words, word_to_root):
    """
    Collect unmatched stems and compute statistics.
    """
    unmatched = []

    total_entries = 0
    matched_entries = 0
    unmatched_entries = 0

    total_words_in_collections = 0
    unmatched_words_in_collections = 0

    for stem, words in stem_to_words.items():
        total_entries += 1
        collection_size = len(words)
        total_words_in_collections += collection_size

        if stem in word_to_root:
            matched_entries += 1
        else:
            unmatched_entries += 1
            unmatched_words_in_collections += collection_size
            unmatched.append({
                "stem": stem,
                "collection_size": collection_size,
                "words": sorted(list(words))
            })

    stats = {
        "total_entries": total_entries,
        "matched_entries": matched_entries,
        "unmatched_entries": unmatched_entries,
        "total_words_in_collections": total_words_in_collections,
        "unmatched_words_in_collections": unmatched_words_in_collections
    }

    return unmatched, stats


def write_unmatched_report_txt(output_path, unmatched, stats):
    """
    Write unmatched items and statistics to a TXT file.
    """
    total_entries = stats["total_entries"]
    unmatched_entries = stats["unmatched_entries"]
    total_words_in_collections = stats["total_words_in_collections"]
    unmatched_words_in_collections = stats["unmatched_words_in_collections"]

    def pct(part, whole):
        return (part / whole * 100) if whole else 0

    size_eq_1 = sum(1 for item in unmatched if item["collection_size"] == 1)
    size_gt_3 = sum(1 for item in unmatched if item["collection_size"] > 3)
    size_gt_5 = sum(1 for item in unmatched if item["collection_size"] > 5)
    size_gt_10 = sum(1 for item in unmatched if item["collection_size"] > 10)

    unmatched_sorted = sorted(unmatched, key=lambda x: x["collection_size"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("UNMATCHED ROOT LOOKUP REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total entries checked: {total_entries}\n")
        f.write(f"Matched entries: {stats['matched_entries']}\n")
        f.write(f"Unmatched entries: {unmatched_entries}\n")
        f.write(f"Unmatched entries percentage: {pct(unmatched_entries, total_entries):.2f}%\n\n")

        f.write(f"Total words across all collections: {total_words_in_collections}\n")
        f.write(f"Total words in unmatched collections: {unmatched_words_in_collections}\n")
        f.write(
            f"Percentage of words that didn't get matched: "
            f"{pct(unmatched_words_in_collections, total_words_in_collections):.2f}%\n\n"
        )

        f.write("UNMATCHED COLLECTION SIZE DISTRIBUTION\n")
        f.write("-" * 60 + "\n")
        f.write(
            f"Percentage of unmatched entries with collection size = 1: "
            f"{pct(size_eq_1, unmatched_entries):.2f}%\n"
        )
        f.write(
            f"Percentage of unmatched entries with collection size > 3: "
            f"{pct(size_gt_3, unmatched_entries):.2f}%\n"
        )
        f.write(
            f"Percentage of unmatched entries with collection size > 5: "
            f"{pct(size_gt_5, unmatched_entries):.2f}%\n"
        )
        f.write(
            f"Percentage of unmatched entries with collection size > 10: "
            f"{pct(size_gt_10, unmatched_entries):.2f}%\n\n"
        )

        f.write("UNMATCHED ENTRIES DETAILS\n")
        f.write("-" * 60 + "\n")
        for i, item in enumerate(unmatched_sorted, start=1):
            f.write(f"{i}. Stem: {item['stem']}\n")
            f.write(f"   Collection size: {item['collection_size']}\n")
            f.write(f"   Words: {', '.join(item['words'])}\n\n")


def main():
    stem_to_words_path = "src/output/stem_to_words_dict.pkl"
    word_to_root_path = "dictionary_with_stems.xlsx"
    report_txt_path = "src/test/unmatched_report_2.txt"

    with open(stem_to_words_path, "rb") as file:
        stem_to_words = pickle.load(file)

    word_to_root = load_word_to_root(word_to_root_path)

    unmatched, stats = collect_unmatched(stem_to_words, word_to_root)

    write_unmatched_report_txt(report_txt_path, unmatched, stats)

    print(f"Unmatched report saved to {report_txt_path}")


if __name__ == "__main__":
    main()