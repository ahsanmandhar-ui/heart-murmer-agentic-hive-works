import os
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SENSITIVE_FILES = ["node.key", "feedback.jsonl", "probe.json", "hive_queue.db"]

def secure_file(path):
    """Restrict file access to current user only (Windows icacls)."""
    if not os.path.exists(path):
        return False
    try:
        # Remove inherited permissions, grant only current user
        subprocess.run(["icacls", path, "/inheritance:r"], check=True, capture_output=True)
        user = os.environ.get("USERNAME", "")
        if user:
            subprocess.run(["icacls", path, "/grant:r", f"{user}:F"], check=True, capture_output=True)
        return True
    except Exception:
        return False

def secure_all():
    results = {}
    for name in SENSITIVE_FILES:
        path = BASE / name
        if path.exists():
            results[name] = secure_file(str(path))
    return results

if __name__ == "__main__":
    import json
    print(json.dumps(secure_all(), indent=2))
