import re
from pathlib import Path
from datetime import datetime

def _safe_name(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name or "plik")

def save_uploads(files, dest_dir: str):
    dest = Path(dest_dir); dest.mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    saved = []
    for f in (files or []):
        out = dest / _safe_name(getattr(f, "name", "plik"))
        try:
            with open(out, "wb") as w:
                w.write(f.getbuffer())
            saved.append(out)
            with open("logs/upload.log", "a", encoding="utf-8") as _log:
                _log.write(f"{datetime.now().isoformat()}  SAVED  {out}  {out.stat().st_size}B\n")
        except Exception as e:
            with open("logs/upload.log", "a", encoding="utf-8") as _log:
                _log.write(f"{datetime.now().isoformat()}  ERROR  {out}  {e}\n")
    return saved
