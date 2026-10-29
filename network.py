import json
import socket
import threading
import time
from pathlib import Path

DISCOVER_PORT = 5000
BROADCAST_ADDR = "255.255.255.255"
NODE_ID = "node-" + socket.gethostname()

_peers = {}
_lock = threading.Lock()
_listener_started = False

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

def _listener():
    global _peers
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", DISCOVER_PORT))
    sock.settimeout(1.0)
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            if msg.get("type") == "discover" and msg.get("node_id") != NODE_ID:
                # respond
                resp = json.dumps({"type": "announce", "node_id": NODE_ID, "ip": get_local_ip(), "port": 8501})
                sock.sendto(resp.encode(), addr)
            elif msg.get("type") == "announce" and msg.get("node_id") != NODE_ID:
                with _lock:
                    _peers[msg["node_id"]] = {"ip": msg["ip"], "port": msg.get("port", 8501), "last_seen": time.time()}
        except socket.timeout:
            # prune stale peers (>30s)
            with _lock:
                now = time.time()
                stale = [k for k, v in _peers.items() if now - v["last_seen"] > 30]
                for k in stale:
                    del _peers[k]
        except Exception:
            pass

def start_listener():
    global _listener_started
    if _listener_started:
        return
    _listener_started = True
    t = threading.Thread(target=_listener, daemon=True)
    t.start()

def discover_peers(timeout=2.0):
    start_listener()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.5)
    msg = json.dumps({"type": "discover", "node_id": NODE_ID})
    try:
        sock.sendto(msg.encode(), (BROADCAST_ADDR, DISCOVER_PORT))
    except Exception:
        pass
    time.sleep(timeout)
    with _lock:
        return dict(_peers)

def get_peers():
    with _lock:
        return dict(_peers)
