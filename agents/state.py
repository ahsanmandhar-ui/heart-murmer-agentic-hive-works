from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class AgentState:
    audio: Any = None
    sr: int = 16000
    mel: Any = None
    embedding: Any = None
    result: Dict[str, Any] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    safe: bool = True
    report: Dict[str, Any] = field(default_factory=dict)
