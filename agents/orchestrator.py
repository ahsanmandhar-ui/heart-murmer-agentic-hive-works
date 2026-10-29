from .state import AgentState
from .preprocess_agent import run as preprocess_run
from .inference_agent import run as inference_run
from .decision_agent import run as decision_run
from .safety_agent import run as safety_run
from .visualization_agent import run as visualization_run

def run_pipeline(audio, sr) -> AgentState:
    state = AgentState(audio=audio, sr=sr)
    state.events.append("Orchestrator: pipeline start")
    state = preprocess_run(state)
    if state.safe:
        state = inference_run(state)
    if state.safe:
        state = decision_run(state)
    state = safety_run(state)
    state = visualization_run(state)
    state.events.append("Orchestrator: pipeline done")
    return state
