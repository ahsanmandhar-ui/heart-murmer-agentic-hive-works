import json
import os
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

BASE = Path(__file__).resolve().parent
PROBE_PATH = BASE / "probe.json"
FEEDBACK_PATH = BASE / "feedback.jsonl"
OUT_PATH = BASE / "probe_retrained.json"

LABEL_MAP = {"Absent": 0, "Present": 1}

def main():
    if not FEEDBACK_PATH.exists():
        print("No feedback.jsonl found. Collect corrections first.")
        return

    records = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("corrected") in LABEL_MAP:
                records.append(rec)

    if len(records) < 5:
        print(f"Only {len(records)} usable corrections (need >= 5).")
        return

    probe = json.load(open(PROBE_PATH, encoding="utf-8"))
    mean = np.asarray(probe["mean"], dtype=np.float64)
    std = np.asarray(probe["std"], dtype=np.float64)

    X = np.asarray([r["embedding"] for r in records], dtype=np.float64)
    y = np.asarray([LABEL_MAP[r["corrected"]] for r in records], dtype=np.int64)

    # Standardize using original mean/std
    Xz = (X - mean) / std

    clf = LogisticRegression(max_iter=1000, C=1.0)
    clf.fit(Xz, y)

    new_probe = dict(probe)
    new_probe["coef"] = clf.coef_[0].tolist()
    new_probe["intercept"] = float(clf.intercept_[0])
    new_probe["abstain"] = probe.get("abstain", 0.05)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(new_probe, f)

    acc = clf.score(Xz, y)
    print(f"Retrained on {len(records)} corrections.")
    print(f"Training accuracy: {acc:.4f}")
    print(f"Saved to {OUT_PATH}")

if __name__ == "__main__":
    main()
