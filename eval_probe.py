import csv, os, sys
import json
import numpy as np
import librosa
from sklearn.metrics import roc_auc_score, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import onnxruntime as ort

sys.path.insert(0, os.path.dirname(__file__))
from dsp import audio_to_mel

BASE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE, "Eheart_sound_by_Ahsan_Mandhar.onnx")
PROBE_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "probe.json")
DATA_BASE = r"C:\Users\Ahsan543\Desktop\heart sounds\heart-murmur-screen-cline-kit\heart-murmur-screen\data\the-circor-digiscope-phonocardiogram-dataset-1.0.3"
WAV_DIR = os.path.join(DATA_BASE, "training_data")
CSV_PATH = os.path.join(DATA_BASE, "training_data.csv")

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def classify(emb, probe):
    mean = np.asarray(probe["mean"], dtype=np.float64)
    std = np.asarray(probe["std"], dtype=np.float64)
    coef = np.asarray(probe["coef"], dtype=np.float64)
    z = (emb - mean) / std
    logit = float(probe["intercept"]) + float(np.dot(coef, z))
    p = float(sigmoid(logit))
    abstain = abs(p - 0.5) < float(probe.get("abstain", 0.05))
    label = "uncertain" if abstain else ("Present" if p >= 0.5 else "Absent")
    return label, p, abstain

def main():
    labels = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            labels[row["Patient ID"]] = row["Murmur"]

    present = [pid for pid, m in labels.items() if m == "Present"][:10]
    absent = [pid for pid, m in labels.items() if m == "Absent"][:10]
    samples = present + absent

    probe = json.load(open(PROBE_PATH, encoding="utf-8"))
    sess = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

    y_true, y_pred, y_prob = [], [], []
    uncertain = 0
    for pid in samples:
        truth = 1 if labels[pid] == "Present" else 0
        wav = os.path.join(WAV_DIR, f"{pid}_MV.wav")
        if not os.path.exists(wav):
            continue
        audio, sr = librosa.load(wav, sr=None, mono=True)
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        mel = audio_to_mel(audio)
        out = sess.run(None, {"input": mel})[0]
        emb = out[0].mean(axis=0) if out.ndim == 3 else out.flatten()
        pred, p, abst = classify(emb, probe)
        if abst:
            uncertain += 1
            continue
        y_true.append(truth)
        y_pred.append(1 if pred == "Present" else 0)
        y_prob.append(p)
        print(f"{pid}: truth={labels[pid]}, pred={pred}, p={p:.3f}, abstain={abst}")

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob) if len(set(y_true)) > 1 else 0

    print(f"\nTotal: {len(samples)}")
    print(f"Uncertain (excluded): {uncertain}")
    print(f"Evaluated: {len(y_true)}")
    print(f"TP={tp} TN={tn} FP={fp} FN={fn}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall/Sensitivity: {rec:.4f}")
    print(f"Specificity: {tn/(tn+fp):.4f}")
    print(f"F1: {f1:.4f}")
    print(f"AUC: {auc:.4f}")

if __name__ == "__main__":
    main()
