import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort

from .state import AgentState

BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / "Eheart_sound_by_Ahsan_Mandhar.onnx"

@lru_cache(maxsize=1)
def _session():
    opts = ort.SessionOptions()
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return ort.InferenceSession(str(MODEL_PATH), sess_options=opts, providers=["CPUExecutionProvider"])

def run(state: AgentState) -> AgentState:
    state.events.append("InferenceAgent: start")
    try:
        sess = _session()
        out = sess.run(None, {"input": state.mel})
        emb_arr = out[0]
        if emb_arr.ndim == 3:
            state.embedding = emb_arr[0].mean(axis=0)
        else:
            state.embedding = emb_arr.flatten()
        state.events.append(f"InferenceAgent: embedding len {len(state.embedding)}")
    except Exception as e:
        state.errors.append(f"InferenceAgent: {e}")
        state.safe = False
    return state
