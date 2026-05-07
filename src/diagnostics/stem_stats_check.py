import pickle
import random
import statistics
from collections import Counter

pkl_path = "src/output/stem_to_words_dict.pkl"
output_txt_path = "src/output/stem_dict_stats.txt"


def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def main():
    stem_to_words = load_pkl(pkl_path)

    with open(output_txt_path, "w", encoding="utf-8") as out:

        def write(line=""):
            out.write(line + "\n")

        total_stems = len(stem_to_words)
        words_per_stem = {stem: len(words) for stem, words in stem_to_words.items()}
        total_unique_words = sum(words_per_stem.values())
        counts = list(words_per_stem.values())

        more_than_3 = sum(1 for c in counts if c > 3)
        more_than_5 = sum(1 for c in counts if c > 5)
        more_than_10 = sum(1 for c in counts if c > 10)

        write("===== BASIC STATS =====")
        write(f"Total stems: {total_stems}")
        write(f"Total unique words across all stems: {total_unique_words}")
        write(f"Average words per stem: {statistics.mean(counts):.4f}")
        write(f"Median words per stem: {statistics.median(counts)}")
        write(f"Min words in a stem: {min(counts)}")
        write(f"Max words in a stem: {max(counts)}")

        write("\n===== THRESHOLD STATS =====")
        write(f"Stems with > 3 words:  {more_than_3} ({more_than_3 / total_stems * 100:.2f}%)")
        write(f"Stems with > 5 words:  {more_than_5} ({more_than_5 / total_stems * 100:.2f}%)")
        write(f"Stems with > 10 words: {more_than_10} ({more_than_10 / total_stems * 100:.2f}%)")

        write("\n===== DISTRIBUTION (words per stem) =====")
        distribution = Counter(counts)
        for k in sorted(distribution):
            write(f"{k} word(s): {distribution[k]} stems ({distribution[k] / total_stems * 100:.2f}%)")

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
            write(f"{bucket}: {n} stems ({n / total_stems * 100:.2f}%)")

        write("\n===== TOP 50 LARGEST STEMS =====")
        top_50 = sorted(stem_to_words.items(), key=lambda x: len(x[1]), reverse=True)[:50]
        for stem, words in top_50:
            words_sorted = sorted(words)
            write(f"\nStem: {stem}")
            write(f"Number of words: {len(words_sorted)}")
            write(f"Words (first 100): {words_sorted[:100]}")

        write("\n===== RANDOM SAMPLE OF 50 STEMS =====")
        sample_items = random.sample(list(stem_to_words.items()), min(50, total_stems))
        for stem, words in sample_items:
            words_sorted = sorted(words)
            write(f"\nStem: {stem}")
            write(f"Number of words: {len(words_sorted)}")
            write(f"Words (first 50): {words_sorted[:50]}")

        write("\n===== EXTRA STATS =====")
        singleton_stems = sum(1 for c in counts if c == 1)
        write(f"Singleton stems: {singleton_stems} ({singleton_stems / total_stems * 100:.2f}%)")

        stems_ge_2 = sum(1 for c in counts if c >= 2)
        stems_ge_3 = sum(1 for c in counts if c >= 3)
        stems_ge_5 = sum(1 for c in counts if c >= 5)
        stems_ge_10 = sum(1 for c in counts if c >= 10)

        write(f"Stems >= 2 words:  {stems_ge_2} ({stems_ge_2 / total_stems * 100:.2f}%)")
        write(f"Stems >= 3 words:  {stems_ge_3} ({stems_ge_3 / total_stems * 100:.2f}%)")
        write(f"Stems >= 5 words:  {stems_ge_5} ({stems_ge_5 / total_stems * 100:.2f}%)")
        write(f"Stems >= 10 words: {stems_ge_10} ({stems_ge_10 / total_stems * 100:.2f}%)")

    print(f"Stats saved to {output_txt_path}")


if __name__ == "__main__":
    main()