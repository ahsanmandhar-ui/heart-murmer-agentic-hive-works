import os, sys, json, tempfile, shutil, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import identity, exchange, promote, resource_guard

def test():
    tmp = tempfile.mkdtemp()
    node_a = os.path.join(tmp, "node_a")
    node_b = os.path.join(tmp, "node_b")
    os.makedirs(node_a)
    os.makedirs(node_b)

    shutil.copy("probe.json", os.path.join(node_a, "probe.json"))
    shutil.copy("probe.json", os.path.join(node_b, "probe.json"))

    results = []

    # 1. Generate identities
    key_a, pub_a = identity.generate_keypair(os.path.join(node_a, "node.key"))
    key_b, pub_b = identity.generate_keypair(os.path.join(node_b, "node.key"))
    results.append(("Node A keygen", True))
    results.append(("Node B keygen", True))

    # 2. Sign probe on both
    identity.sign_file(os.path.join(node_a, "probe.json"), key_a)
    identity.sign_file(os.path.join(node_b, "probe.json"), key_b)
    results.append(("Node A sign", True))
    results.append(("Node B sign", True))

    # 3. Cross-verify signatures
    ok_a = identity.verify_file(os.path.join(node_b, "probe.json"), os.path.join(node_b, "probe.json.sig"), pub_b)
    ok_b = identity.verify_file(os.path.join(node_a, "probe.json"), os.path.join(node_a, "probe.json.sig"), pub_a)
    results.append(("A verifies B signature", ok_a))
    results.append(("B verifies A signature", ok_b))

    # 4. Hash verification
    h_a = hashlib.sha256(open(os.path.join(node_a, "probe.json"), "rb").read()).hexdigest()
    h_b = hashlib.sha256(open(os.path.join(node_b, "probe.json"), "rb").read()).hexdigest()
    results.append(("Hashes match (same probe)", h_a == h_b))

    # 5. Resource guard
    ok_a, _ = resource_guard.can_proceed()
    ok_b, _ = resource_guard.can_proceed()
    results.append(("Resource guard (Node A)", ok_a))
    results.append(("Resource guard (Node B)", ok_b))

    # 6. Exchange bundle (Node A -> Node B)
    os.chdir(node_a)
    bundle_path, manifest_a = exchange.export_bundle(os.path.join(node_a, "bundle_a.zip"))
    os.chdir(node_b)
    ok, msg = exchange.import_bundle(os.path.join(node_a, "bundle_a.zip"))
    results.append(("Node B import bundle from A", ok))

    # 7. Promotion gate
    peer_manifest = {"metrics": {"auc": 0.90, "accuracy": 0.85}}
    local_manifest = {"metrics": {"auc": 0.8796, "accuracy": 0.80}}
    should, reason = promote.should_promote(local_manifest, peer_manifest)
    results.append(("Promotion gate (peer better)", should))

    # Summary
    print("\n=== Two-Node Integration Test ===")
    all_pass = True
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {name}")
        if not ok:
            all_pass = False
    print(f"\nOverall: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    print(f"Temp dir: {tmp}")

if __name__ == "__main__":
    test()
