import base64
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

BASE = Path(__file__).resolve().parent
KEY_PATH = BASE / "node.key"
PUB_PATH = BASE / "node.pub"

def generate_keypair(path=None):
    if path is None:
        path = str(KEY_PATH)
    secret = os.urandom(32)
    private_key = Ed25519PrivateKey.from_private_bytes(secret)
    public_key = private_key.public_key()
    with open(path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    pub_path = path + ".pub" if not path.endswith(".key") else path.replace(".key", ".pub")
    with open(pub_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        ))
    print(f"Generated keypair: {path}, {pub_path}")
    print(f"public_key: {public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex()}")
    return path, pub_path

def ensure_keypair():
    if not KEY_PATH.exists() or not PUB_PATH.exists():
        generate_keypair()

def load_private_key():
    data = open(KEY_PATH, "rb").read()
    return Ed25519PrivateKey.from_private_bytes(data)

def load_public_key():
    data = open(PUB_PATH, "rb").read()
    return Ed25519PublicKey.from_public_bytes(data)

def sign_file(file_path, key_path=None):
    if key_path is None:
        key_path = str(KEY_PATH)
    private_key = load_private_key_from(key_path)
    data = open(file_path, "rb").read()
    signature = private_key.sign(data)
    sig_path = file_path + ".sig"
    with open(sig_path, "wb") as f:
        f.write(signature)
    print(f"Signed {file_path} -> {sig_path} (key={key_path})")
    return sig_path

def load_private_key_from(key_path):
    data = open(key_path, "rb").read()
    return Ed25519PrivateKey.from_private_bytes(data)

def verify_file(file_path, sig_path, pub_key_path=None):
    data = open(file_path, "rb").read()
    sig = open(sig_path, "rb").read()
    if pub_key_path:
        pub_data = open(pub_key_path, "rb").read()
        public_key = Ed25519PublicKey.from_public_bytes(pub_data)
    else:
        public_key = load_public_key()
    try:
        public_key.verify(sig, data)
        return True
    except InvalidSignature:
        return False

def get_public_key_hex():
    pub = load_public_key()
    return pub.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex()

def sign_bytes(data: bytes):
    private_key = load_private_key()
    signature = private_key.sign(data)
    sig_path = "manifest.json.sig"
    with open(sig_path, "wb") as f:
        f.write(signature)
    print(f"Signed manifest -> {sig_path}")

def verify_bytes(data: bytes, sig: bytes, pub_key_hex: str = None):
    if pub_key_hex is None:
        public_key = load_public_key()
    else:
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_key_hex))
    try:
        public_key.verify(sig, data)
        return True
    except InvalidSignature:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: identity.py [keygen|sign <file>|verify <file> <sig>|pubkey]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "keygen":
        generate_keypair()
    elif cmd == "sign" and len(sys.argv) >= 3:
        sign_file(sys.argv[2])
    elif cmd == "verify" and len(sys.argv) >= 4:
        ok = verify_file(sys.argv[2], sys.argv[3])
        print("verify:", ok)
    elif cmd == "pubkey":
        print(get_public_key_hex())
    else:
        print("Unknown command")