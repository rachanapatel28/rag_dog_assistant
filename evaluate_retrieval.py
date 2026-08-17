import json

from search import search

TEST_SET_FILE = "eval/test_set.json"
K_VALUES = [1, 3, 5]
MAX_K = max(K_VALUES)


def load_test_set(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieved_sources(query, top_k):
    # search returns [(distance, chunk), ...] nearest-first
    results = search(query, top_k=top_k)
    return [chunk["source"] for distance, chunk in results]


def evaluate():
    test_set = load_test_set(TEST_SET_FILE)
    in_scope = [q for q in test_set if not q["out_of_scope"]]
    skipped = len(test_set) - len(in_scope)

    print(f"Evaluating retrieval on {len(in_scope)} in-scope questions "
          f"({skipped} out-of-scope questions skipped)\n")

    hits_at_k = {k: 0 for k in K_VALUES}

    for q in in_scope:
        sources = retrieved_sources(q["question"], MAX_K)
        acceptable = set(q["acceptable_sources"])

        per_k = {}
        for k in K_VALUES:
            hit = any(s in acceptable for s in sources[:k])
            per_k[k] = hit
            if hit:
                hits_at_k[k] += 1

        mark = "HIT " if per_k[3] else "MISS"
        print(f"[{mark}] Q{q['id']}: {q['question']}")
        if not per_k[3]:
            print(f"        expected one of: {sorted(acceptable)}")
            print(f"        retrieved (top 3): {sources[:3]}")

    print("\n--- Hit rate (an acceptable source appears in the top-k) ---")
    n = len(in_scope)
    for k in K_VALUES:
        print(f"  top-{k}: {hits_at_k[k]}/{n} = {hits_at_k[k] / n:.0%}")


if __name__ == "__main__":
    evaluate()