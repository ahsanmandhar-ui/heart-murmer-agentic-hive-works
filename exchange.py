import hashlib
import json
import os
import socket
import struct
import tempfile
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXCHANGE_PORT = 5001
BUNDLE_NAME = "exchange_bundle.zip"

def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def export_bundle(out_path=None):
    if out_path is None:
        out_path = str(BASE / BUNDLE_NAME)
    manifest = {
        "node_id": "local",
        "probe_hash": _sha256(BASE / "probe.json"),
        "model_hash": _sha256(BASE / "Eheart_sound_by_Ahsan_Mandhar.onnx") if (BASE / "Eheart_sound_by_Ahsan_Mandhar.onnx").exists() else None,
        "metrics": {"accuracy": 0.8, "auc": 0.8796},
    }
    with zipfile.ZipFile(out_path, "w") as zf:
        zf.write(BASE / "probe.json", "probe.json")
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
    return out_path, manifest

def import_bundle(bundle_path):
    with zipfile.ZipFile(bundle_path, "r") as zf:
        names = zf.namelist()
        if "probe.json" not in names or "manifest.json" not in names:
            return False, "Missing required files"
        manifest = json.loads(zf.read("manifest.json"))
        probe_data = zf.read("probe.json")
        h = _sha256_bytes(probe_data)
        if h != manifest.get("probe_hash"):
            return False, "Hash mismatch"
        (BASE / "probe_imported.json").write_bytes(probe_data)
        (BASE / "manifest_imported.json").write_text(json.dumps(manifest, indent=2))
        _audit_log("import_bundle", extra={"node_id": manifest.get("node_id")})
        return True, "Imported successfully"

_rate_limit = {}


def _check_rate(peer_ip, min_interval=60):
    import time
    now = time.time()
    if peer_ip in _rate_limit and now - _rate_limit[peer_ip] < min_interval:
        return False
    _rate_limit[peer_ip] = now
    return True


def send_bundle(peer_ip, port=EXCHANGE_PORT, bundle_path=None):
    if bundle_path is None:
        bundle_path, _ = export_bundle()
    data = open(bundle_path, "rb").read()
    if not _check_rate(peer_ip):
        return "Rate limited"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((peer_ip, port))
    # send size header (8 bytes) + data
    sock.sendall(struct.pack("!Q", len(data)))
    sock.sendall(data)
    # receive response
    resp = sock.recv(1024).decode()
    sock.close()
    _audit_log("send_bundle", peer=peer_ip, extra={"size": len(data)})
    return resp

def receive_bundle(port=EXCHANGE_PORT, timeout=30):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    sock.listen(1)
    sock.settimeout(timeout)
    try:
        conn, addr = sock.accept()
        # receive size header
        size_data = conn.recv(8)
        size = struct.unpack("!Q", size_data)[0]
        # receive bundle data
        data = b""
        while len(data) < size:
            chunk = conn.recv(min(65536, size - len(data)))
            if not chunk:
                break
            data += chunk
        # save to temp
        tmp = os.path.join(tempfile.gettempdir(), "received_bundle.zip")
        with open(tmp, "wb") as f:
            f.write(data)
        # verify and import
        ok, msg = import_bundle(tmp)
        _audit_log("receive_bundle", peer=addr[0], extra={"size": size, "ok": ok})
        conn.sendall(msg.encode())
        conn.close()
        sock.close()
        return ok, msg, addr
    except socket.timeout:
        sock.close()
        return False, "Timeout", None
    except Exception as e:
        sock.close()
        return False, str(e), None

def auto_exchange(peers, timeout=30):
    results = {}
    for pid, info in peers.items():
        try:
            resp = send_bundle(info["ip"], info.get("port", EXCHANGE_PORT) + 1)
            results[pid] = {"status": "sent", "response": resp}
        except Exception as e:
            results[pid] = {"status": "error", "error": str(e)}
    # also listen for incoming
    ok, msg, addr = receive_bundle(timeout=timeout)
    if ok:
        results["incoming"] = {"status": "received", "msg": msg, "from": str(addr)}
    return results
import time

def _audit_log(event, peer=None, extra=None):
    log_path = BASE / "exchange_log.jsonl"
    prev_hash = ""
    if log_path.exists():
        with open(log_path, "rb") as f:
            lines = f.readlines()
            if lines:
                last = lines[-1].decode()
                if '"hash":"' in last:
                    prev_hash = last.split('"hash":"')[-1].split('"')[0]
    entry = {"ts": time.time(), "event": event, "peer": peer, "prev_hash": prev_hash}
    if extra:
        entry.update(extra)
    h = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    entry["hash"] = h
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return h
