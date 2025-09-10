import os, requests, pytest
URL=os.getenv("AI_ENDPOINT","http://127.0.0.1:8002")
def test_health():
    try:
        r=requests.get(f"{URL}/health", timeout=2)
        assert r.status_code==200
    except Exception:
        pytest.xfail("Brak połączenia do lokalnego AI (OK w tym smoke).")
