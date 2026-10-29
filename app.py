import json
from pathlib import Path

import librosa
import streamlit as st

from agents.orchestrator import run_pipeline

BASE = Path(__file__).resolve().parent

# Ensure cryptographic identity exists
try:
    import identity
    identity.ensure_keypair()
except Exception:
    pass

# Secure sensitive files on startup
try:
    import secure_storage
    secure_storage.secure_all()
except Exception:
    pass

st.set_page_config(page_title="Multi-Agent Heart Sound Detector", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  :root { --bg:#0b1020; --card:rgba(255,255,255,0.06); --border:rgba(255,255,255,0.12); --text:#e5e7eb; --muted:#9ca3af; --primary:#6366f1; --primary-2:#06b6d4; }
  .stApp { background: radial-gradient(1200px 600px at 20% -10%, #1e293b, var(--bg)); }
  .block-container { padding: 2rem 1rem; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; backdrop-filter: blur(8px); margin-bottom: 16px; }
  .title { font-size: 1.1rem; font-weight: 600; margin: 0 0 8px; }
  .muted { color: var(--muted); font-size: 0.9rem; }
  .metric { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; text-align: center; }
  .metric .k { font-size: 0.75rem; color: var(--muted); }
  .metric .v { font-size: 1.2rem; font-weight: 600; }
  .result { font-size: 1.2rem; font-weight: 600; margin: 8px 0; }
  .safety { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 12px; margin-top: 16px; }
  @media (max-width: 768px) { .block-container { padding: 1rem 0.5rem; } }
</style>
""", unsafe_allow_html=True)

st.title("Multi-Agent Heart Sound Detector")
st.caption("Local ONNX inference + linear probe. Decision support only.")

with st.sidebar:
    st.subheader("Model")
    st.write("**Name:** Eheart_sound_by_Ahsan_Mandhar.onnx")
    st.write("**Type:** AST (Audio Spectrogram Transformer)")
    st.write("**Size:** ~83 MB")
    st.write("**Runtime:** ONNX Runtime (CPU)")
    st.divider()
    st.subheader("Network")
    import network
    network.start_listener()
    peers = network.discover_peers(1.0)
    if peers:
        st.success(f"🟢 {len(peers)} peer(s) found on LAN")
        for pid, info in peers.items():
            st.write(f"**{pid}** — {info['ip']}:{info['port']}")
    else:
        st.warning("🟡 No peer detected (scanning...)")
    st.caption("Auto-exchange requires peer on same LAN.")

    st.divider()
    st.subheader("Resources")
    import resource_guard
    r = resource_guard.get_resources()
    st.write(f"CPU: {r['cpu_percent']:.0f}%")
    st.write(f"RAM available: {r['ram_available_mb']:.0f} MB")
    st.write(f"Disk free: {r['disk_free_mb']:.0f} MB")
    ok, msg = resource_guard.can_proceed()
    if ok:
        st.success("Resources OK")
    else:
        st.warning(msg)

    st.divider()
    st.subheader("Exchange")
    if st.button("Export bundle"):
        import exchange
        path, manifest = exchange.export_bundle()
        st.success(f"Bundle exported: {path}")
        st.json(manifest)
    uploaded_bundle = st.file_uploader("Import bundle", type=["zip"], key="bundle")
    if uploaded_bundle is not None:
        import exchange, tempfile, os
        tmp = os.path.join(tempfile.gettempdir(), "import_bundle.zip")
        with open(tmp, "wb") as f:
            f.write(uploaded_bundle.read())
        ok, msg = exchange.import_bundle(tmp)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

uploaded = st.file_uploader("Upload a heart-sound audio file", type=["wav", "mp3", "flac", "ogg", "m4a"])

if uploaded is not None:
    st.audio(uploaded)
    if st.button("Analyze", use_container_width=True):
        with st.spinner("Running multi-agent pipeline..."):
            audio, sr = librosa.load(uploaded, sr=None, mono=True)
            state = run_pipeline(audio, sr)

        if state.errors:
            st.error("Pipeline errors: " + "; ".join(state.errors))

        res = state.result
        label = res.get("label", "unknown")
        color = {"Present": "red", "Absent": "green", "uncertain": "orange"}.get(label, "gray")
        st.markdown(f"<div class='result' style='color:{color}'>Result: {label} (p={res.get('p',0):.3f})</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric'><div class='k'>Probability</div><div class='v'>{res.get('p',0):.3f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric'><div class='k'>Logit</div><div class='v'>{res.get('logit',0):.3f}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric'><div class='k'>Abstain</div><div class='v'>{'Yes' if res.get('abstain') else 'No'}</div></div>", unsafe_allow_html=True)

        st.write("Safety note:", res.get("safety_note"))
        st.write("Disclaimer:", res.get("disclaimer"))

        rep = state.report
        st.write("Mel shape:", rep.get("mel_shape"))
        st.write("Embedding length/mean/std:", rep.get("embedding_len"), round(rep.get("embedding_mean",0),4), round(rep.get("embedding_std",0),4))

        with st.expander("Agent event log"):
            for e in state.events:
                st.write("-", e)

        st.session_state["last_embedding"] = out.embedding.tolist()
        st.session_state["last_pred"] = out.label
        st.session_state["last_p"] = out.p

        with st.expander("Report correction (human-in-the-loop)"):
            corrected = st.selectbox("Correct label", ["Absent", "Present", "Unknown"], key="corrected_label")
            if st.button("Save correction"):
                import json, os, datetime
                rec = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "filename": uploaded.name,
                    "predicted": st.session_state.get("last_pred"),
                    "probability": st.session_state.get("last_p"),
                    "corrected": corrected,
                    "embedding": st.session_state.get("last_embedding"),
                }
                path = BASE / "feedback.jsonl"
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
                st.success(f"Saved correction: {corrected}")