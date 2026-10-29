import json
from pathlib import Path

import numpy as np

from .state import AgentState

BASE = Path(__file__).resolve().parent.parent
PCA_PATH = BASE / "pca.json"

def _load_pca():
    if PCA_PATH.exists():
        with open(PCA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def run(state: AgentState) -> AgentState:
    state.events.append("VisualizationAgent: start")
    try:
        emb = np.asarray(state.embedding, dtype=np.float64)
        pca = _load_pca()
        state.report = {
            "embedding_len": int(emb.shape[0]),
            "embedding_mean": float(np.mean(emb)),
            "embedding_std": float(np.std(emb)),
            "mel_shape": tuple(state.mel.shape) if state.mel is not None else None,
            "pca_loaded": pca is not None,
        }
        if pca is not None:
            mean = np.asarray(pca["mean"], dtype=np.float64)
            comps = np.asarray(pca["components"], dtype=np.float64)
            v = emb - mean
            xy = [float((comps[0] * v).sum()), float((comps[1] * v).sum())]
            state.report["pca_xy"] = xy
        state.events.append("VisualizationAgent: done")
    except Exception as e:
        state.errors.append(f"VisualizationAgent: {e}")
        state.safe = False
    return state
