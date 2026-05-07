import pickle
import random
import statistics
from collections import Counter

pkl_path = "src/output/root_to_words_dict.pkl"
output_txt_path = "src/output/root_dict_stats.txt"


def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def main():
    root_to_words = load_pkl(pkl_path)

    with open(output_txt_path, "w", encoding="utf-8") as out:

        def write(line=""):
            out.write(line + "\n")

        total_roots = len(root_to_words)
        words_per_root = {root: len(words) for root, words in root_to_words.items()}
        total_unique_words = sum(words_per_root.values())
        counts = list(words_per_root.values())

        more_than_3 = sum(1 for c in counts if c > 3)
        more_than_5 = sum(1 for c in counts if c > 5)
        more_than_10 = sum(1 for c in counts if c > 10)

        write("===== BASIC STATS =====")
        write(f"Total roots: {total_roots}")
        write(f"Total unique words across all roots: {total_unique_words}")
        write(f"Average words per root: {statistics.mean(counts):.4f}")
        write(f"Median words per root: {statistics.median(counts)}")
        write(f"Min words in a root: {min(counts)}")
        write(f"Max words in a root: {max(counts)}")

        write("\n===== THRESHOLD STATS =====")
        write(f"Roots with > 3 words:  {more_than_3} ({more_than_3 / total_roots * 100:.2f}%)")
        write(f"Roots with > 5 words:  {more_than_5} ({more_than_5 / total_roots * 100:.2f}%)")
        write(f"Roots with > 10 words: {more_than_10} ({more_than_10 / total_roots * 100:.2f}%)")

        write("\n===== DISTRIBUTION (words per root) =====")
        distribution = Counter(counts)
        for k in sorted(distribution):
            write(f"{k} word(s): {distribution[k]} roots ({distribution[k] / total_roots * 100:.2f}%)")

        write("\n===== BUCKETED DISTRIBUTION =====")
        buckets = {
            "1": 0,
            "2-3": 0,
            "4-5": 0,
            "6-10": 0,
            "11-20": 0,
            "21+": 0,
        }

        for c in counts:
            if c == 1:
                buckets["1"] += 1
            elif 2 <= c <= 3:
                buckets["2-3"] += 1
            elif 4 <= c <= 5:
                buckets["4-5"] += 1
            elif 6 <= c <= 10:
                buckets["6-10"] += 1
            elif 11 <= c <= 20:
                buckets["11-20"] += 1
            else:
                buckets["21+"] += 1

        for bucket, n in buckets.items():
            write(f"{bucket}: {n} roots ({n / total_roots * 100:.2f}%)")

        write("\n===== TOP 50 LARGEST ROOTS =====")
        top_50 = sorted(root_to_words.items(), key=lambda x: len(x[1]), reverse=True)[:50]
        for root, words in top_50:
            words_sorted = sorted(words)
            write(f"\nRoot: {root}")
            write(f"Number of words: {len(words_sorted)}")
            write(f"Words (first 100): {words_sorted[:100]}")

        write("\n===== RANDOM SAMPLE OF 50 ROOTS =====")
        sample_items = random.sample(list(root_to_words.items()), min(50, total_roots))
        for root, words in sample_items:
            words_sorted = sorted(words)
            write(f"\nRoot: {root}")
            write(f"Number of words: {len(words_sorted)}")
            write(f"Words (first 50): {words_sorted[:50]}")

        write("\n===== EXTRA STATS =====")
        singleton_roots = sum(1 for c in counts if c == 1)
        write(f"Singleton roots: {singleton_roots} ({singleton_roots / total_roots * 100:.2f}%)")

        roots_ge_2 = sum(1 for c in counts if c >= 2)
        roots_ge_3 = sum(1 for c in counts if c >= 3)
        roots_ge_5 = sum(1 for c in counts if c >= 5)
        roots_ge_10 = sum(1 for c in counts if c >= 10)

        write(f"Roots >= 2 words:  {roots_ge_2} ({roots_ge_2 / total_roots * 100:.2f}%)")
        write(f"Roots >= 3 words:  {roots_ge_3} ({roots_ge_3 / total_roots * 100:.2f}%)")
        write(f"Roots >= 5 words:  {roots_ge_5} ({roots_ge_5 / total_roots * 100:.2f}%)")
        write(f"Roots >= 10 words: {roots_ge_10} ({roots_ge_10 / total_roots * 100:.2f}%)")

    print(f"Stats saved to {output_txt_path}")


if __name__ == "__main__":
    main()