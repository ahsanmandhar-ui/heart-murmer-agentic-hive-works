import librosa
import numpy as np

from .state import AgentState
from dsp import audio_to_mel, SR

def run(state: AgentState) -> AgentState:
    state.events.append("PreprocessAgent: start")
    try:
        if state.sr != SR:
            state.audio = librosa.resample(state.audio, orig_sr=state.sr, target_sr=SR)
            state.sr = SR
        state.mel = audio_to_mel(state.audio)
        state.events.append(f"PreprocessAgent: mel shape {tuple(state.mel.shape)}")
    except Exception as e:
        state.errors.append(f"PreprocessAgent: {e}")
        state.safe = False
    return state
