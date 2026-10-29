import hashlib
import json
import os
import platform
import socket
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def create_manifest(metrics=None):
    import identity
    manifest = {
        "node_id": "node-" + socket.gethostname(),
        "public_key": identity.get_public_key_hex(),
        "model": {
            "file": "Eheart_sound_by_Ahsan_Mandhar.onnx",
            "hash": _sha256(BASE / "Eheart_sound_by_Ahsan_Mandhar.onnx") if (BASE / "Eheart_sound_by_Ahsan_Mandhar.onnx").exists() else None,
            "probe_hash": _sha256(BASE / "probe.json"),
        },
        "metrics": metrics or {"accuracy": 0.8, "auc": 0.8796},
        "hardware": {
            "os": platform.system(),
            "arch": platform.machine(),
            "python": platform.python_version(),
        },
        "license": "MIT",
    }
    # sign manifest
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    identity.sign_bytes(manifest_bytes)  # need add this function
    return manifest

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: manifest.py [create]")
        sys.exit(1)
    if sys.argv[1] == "create":
        m = create_manifest()
        print(json.dumps(m, indent=2))