from .state import AgentState

def run(state: AgentState) -> AgentState:
    state.events.append("SafetyAgent: start")
    try:
        if state.errors:
            state.safe = False
            state.result.setdefault("label", "uncertain")
            state.result["safety_note"] = "Errors occurred; treat as uncertain."
        else:
            p = state.result.get("p", 0.5)
            if state.result.get("abstain"):
                state.result["safety_note"] = "Low confidence; recommend human review."
            elif p > 0.8 or p < 0.2:
                state.result["safety_note"] = "High confidence; still decision support only."
            else:
                state.result["safety_note"] = "Moderate confidence; recommend review."
        state.result["disclaimer"] = "Decision support only. Not a medical diagnosis."
        state.events.append("SafetyAgent: done")
    except Exception as e:
        state.errors.append(f"SafetyAgent: {e}")
        state.safe = False
    return state
