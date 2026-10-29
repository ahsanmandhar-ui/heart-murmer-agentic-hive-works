import json
import math
from pathlib import Path

import numpy as np

from .state import AgentState

BASE = Path(__file__).resolve().parent.parent
PROBE_PATH = BASE / "probe.json"

def _load_probe():
    with open(PROBE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def run(state: AgentState) -> AgentState:
    state.events.append("DecisionAgent: start")
    try:
        probe = _load_probe()
        emb = np.asarray(state.embedding, dtype=np.float64)
        mean = np.asarray(probe["mean"], dtype=np.float64)
        std = np.asarray(probe["std"], dtype=np.float64)
        coef = np.asarray(probe["coef"], dtype=np.float64)
        z = (emb - mean) / std
        logit = float(probe["intercept"]) + float(np.dot(coef, z))
        p = float(_sigmoid(logit))
        abstain = abs(p - 0.5) < float(probe.get("abstain", 0.05))
        label = "uncertain" if abstain else ("Present" if p >= 0.5 else "Absent")
        state.result = {"p": p, "logit": logit, "label": label, "abstain": abstain}
        state.events.append(f"DecisionAgent: {label} (p={p:.3f})")
    except Exception as e:
        state.errors.append(f"DecisionAgent: {e}")
        state.safe = False
    return state
