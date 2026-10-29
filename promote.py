import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent

def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def should_promote(local_manifest, peer_manifest, threshold=0.01):
    local_auc = local_manifest.get("metrics", {}).get("auc", 0)
    peer_auc = peer_manifest.get("metrics", {}).get("auc", 0)
    if peer_auc > local_auc + threshold:
        return True, f"Peer AUC {peer_auc:.4} > local {local_auc:.4} + {threshold}"
    return False, f"Peer AUC {peer_auc:.4} not better than local {local_auc:.4}"

def promote(peer_manifest_path, peer_probe_path):
    # verify hash
    import hashlib
    peer_manifest = load_manifest(peer_manifest_path)
    probe_data = open(peer_probe_path, "rb").read()
    h = hashlib.sha256(probe_data).hexdigest()
    if h != peer_manifest.get("probe_hash"):
        return False, "Hash mismatch"
    # promote
    (BASE / "probe_backup.json").write_bytes((BASE / "probe.json").read_bytes())
    (BASE / "probe.json").write_bytes(probe_data)
    # log
    log = {"timestamp": __import__("datetime").datetime.now().isoformat(), "action": "promote", "peer_auc": peer_manifest.get("metrics", {}).get("auc")}
    with open(BASE / "exchange_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")
    return True, "Promoted successfully"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: promote.py <peer_manifest.json> <peer_probe.json>")
        sys.exit(1)
    ok, msg = promote(sys.argv[1], sys.argv[2])
    print(msg)
    sys.exit(0 if ok else 1)
