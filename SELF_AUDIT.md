# AI-Auditor – Self Audit

Branch: main  |  Commit: 44e3600

## Checklist
- Menu gate (st.stop): [x]
- Unification BACKEND_URL (no AI_SERVER_URL): [ ]
- BasicAuth on all API calls: [x] (6/6)
- Upload limit 100MB in backend: [x]

## Smoke-test results
- /healthz HTTP 200
- /ready   HTTP 200
- /analyze HTTP 503

## Key findings
BACKEND_URL in src/config.py:
```
9:BACKEND_URL = (
10:    st.secrets.get("BACKEND_URL")
11:    if hasattr(st, 'secrets') and st.secrets and st.secrets.get("BACKEND_URL")
12:    else os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
39:    return BACKEND_URL
```
Occurrences of AI_SERVER_URL (should be 0):
```
./start_streamlit_with_ai.sh:37:export AI_SERVER_URL="http://localhost:8000"
./start_streamlit_with_ai.sh:43:echo "   - Serwer AI: $AI_SERVER_URL"
./streamlit_app_old.py:41:AI_SERVER_URL = "https://ai-auditor-romaks-8002.loca.lt"
./streamlit_app_old.py:50:        health_response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
./streamlit_app_old.py:55:        ready_response = requests.get(f"{AI_SERVER_URL}/ready", timeout=5)
./streamlit_app_old.py:73:            f"{AI_SERVER_URL}/analyze", json=payload, timeout=AI_TIMEOUT
./streamlit_app_old.py:215:                response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
./streamlit_app_old.py:277:            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
./streamlit_app_old.py:1412:            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
./AI_CONNECTION_GUIDE.md:151:   - Zmień `AI_SERVER_URL` w Streamlit
./AUDIT_FIXES_SUMMARY.md:13:- **Problem**: Niespójność między `BACKEND_URL` i `AI_SERVER_URL`
./STATUS_AI_CONNECTION.md:65:AI_SERVER_URL=https://ai-auditor-romaks.loca.lt streamlit run streamlit_app.py --server.port 8502
./start_ai_server.sh:24:export AI_SERVER_URL="http://localhost:8000"
./start_ai_server.sh:27:echo "   - Serwer AI: $AI_SERVER_URL"
./web/legacy/modern_ui.py:36:        self.AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8000")
./web/legacy/modern_ui.py:863:            health_response = requests.get(f"{self.AI_SERVER_URL}/healthz", timeout=5)
./web/legacy/modern_ui.py:870:            ready_response = requests.get(f"{self.AI_SERVER_URL}/ready", timeout=5)
./web/legacy/modern_ui.py:886:                f"{self.AI_SERVER_URL}/analyze", json=payload, timeout=self.AI_TIMEOUT
./web/legacy/modern_ui.py:905:            health_response = requests.get(f"{self.AI_SERVER_URL}/healthz", timeout=5)
./web/legacy/modern_ui.py:906:            ready_response = requests.get(f"{self.AI_SERVER_URL}/ready", timeout=5)
./web/legacy/modern_ui.py:912:                "server_url": self.AI_SERVER_URL,
./web/legacy/modern_ui.py:918:                "server_url": self.AI_SERVER_URL,
./web/modern_ui.py:36:        self.AI_SERVER_URL = "http://localhost:8000"
./web/modern_ui.py:849:            health_response = requests.get(f"{self.AI_SERVER_URL}/healthz", timeout=5)
./web/modern_ui.py:854:            ready_response = requests.get(f"{self.AI_SERVER_URL}/ready", timeout=5)
./web/modern_ui.py:870:                f"{self.AI_SERVER_URL}/analyze",
./web/modern_ui.py:891:            health_response = requests.get(f"{self.AI_SERVER_URL}/healthz", timeout=5)
./web/modern_ui.py:892:            ready_response = requests.get(f"{self.AI_SERVER_URL}/ready", timeout=5)
./web/modern_ui.py:897:                "server_url": self.AI_SERVER_URL
./web/modern_ui.py:903:                "server_url": self.AI_SERVER_URL
./scripts/anti_hang_self_audit.sh:45:AI_SERVER_HITS=$(grep -R --line-number "AI_SERVER_URL" . || true)
./scripts/anti_hang_self_audit.sh:119:  echo "- Unification BACKEND_URL (no AI_SERVER_URL): $([ -z "$AI_SERVER_HITS" ] && echo '[x]' || echo '[ ]')"
./scripts/anti_hang_self_audit.sh:138:    echo "Occurrences of AI_SERVER_URL (should be 0):"
./streamlit_app_enhanced.py:36:AI_SERVER_URL = "https://ai-auditor-romaks-8002.loca.lt"
./streamlit_app_enhanced.py:43:        health_response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
./streamlit_app_enhanced.py:48:        ready_response = requests.get(f"{AI_SERVER_URL}/ready", timeout=5)
./streamlit_app_enhanced.py:67:            f"{AI_SERVER_URL}/analyze",
./streamlit_app_enhanced.py:198:            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
./streamlit_app_enhanced.py:901:        ai_server = st.text_input("Serwer AI", AI_SERVER_URL)
./streamlit_app_complete.py:36:AI_SERVER_URL = "https://ai-auditor-romaks-8002.loca.lt"
./streamlit_app_complete.py:43:        health_response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=5)
./streamlit_app_complete.py:48:        ready_response = requests.get(f"{AI_SERVER_URL}/ready", timeout=5)
./streamlit_app_complete.py:67:            f"{AI_SERVER_URL}/analyze",
./streamlit_app_complete.py:198:            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
./streamlit_app_complete.py:219:            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
./streamlit_app_complete.py:475:            response = requests.get(f"{AI_SERVER_URL}/healthz", timeout=2)
```

## Logs (tails)
### backend.log (last 80 lines)
```
INFO:aiauditor:Warming up model in background…
ERROR:aiauditor:Warm-up failed: [MODEL_LOAD_ERROR] PyTorch and transformers not available. Install with: pip install torch transformers
Traceback (most recent call last):
  File "/workspaces/ai-auditor/local_test/server.py", line 73, in _warmup
    _ = call_model(
        ^^^^^^^^^^^
  File "/workspaces/ai-auditor/local_test/core/model_interface.py", line 362, in call_model
    return get_model_interface().call_model(prompt, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspaces/ai-auditor/local_test/core/model_interface.py", line 186, in call_model
    self._load_model()
  File "/workspaces/ai-auditor/local_test/core/model_interface.py", line 121, in _load_model
    raise ModelLoadError(
local_test.core.exceptions.ModelLoadError: [MODEL_LOAD_ERROR] PyTorch and transformers not available. Install with: pip install torch transformers
```
### streamlit.log (last 80 lines)
```

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://172.17.0.2:8501
  External URL: http://79.191.157.103:8501

  Stopping...
```
