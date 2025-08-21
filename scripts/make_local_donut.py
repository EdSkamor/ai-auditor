import os, json, random
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd

OUT_DIR = Path("data/local_donut")
IMG_DIR = OUT_DIR / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

def need_env(name: str) -> Path:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Brak zmiennej środowiskowej: {name}")
    p = Path(val)
    if not p.exists():
        raise SystemExit(f"Ścieżka z {name} nie istnieje: {p}")
    return p

KOSZTY_RES     = need_env("KOSZTY_RES")
PRZYCHODY_RES  = need_env("PRZYCHODY_RES")
KOSZTY_FACT    = need_env("KOSZTY_FACT")
PRZYCHODY_FACT = need_env("PRZYCHODY_FACT")

REQ_COLS = {
    "zalacznik": "zalacznik",
    "numer_dokumentu": "numer_dokumentu",
    "data_dokumentu": "data_dokumentu",
    "wartosc_netto_dokumentu": "wartosc_netto_dokumentu",
}

def load_rows(xlsx: Path, root: Path):
    df = pd.read_excel(xlsx)
    # normalizacja nagłówków
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    miss = [c for c in REQ_COLS if c not in df.columns]
    if miss:
        raise SystemExit(f"Brak kolumn w {xlsx}: {miss}")

    rows = []
    for _, r in df.iterrows():
        att = str(r.get("zalacznik") or "").strip()
        if not att:
            continue
        pdf = (root / att).resolve()
        if not pdf.is_file():
            continue
        numer = str(r.get("numer_dokumentu") or "").strip()
        data  = str(r.get("data_dokumentu") or "").split(" ")[0]
        try:
            netto = float(str(r.get("wartosc_netto_dokumentu") or "0").replace(",", "."))
        except Exception:
            netto = 0.0
        rows.append({"pdf": str(pdf), "numer": numer, "data": data, "netto": round(netto, 2)})
    return rows

def render_first_page(pdf_path: str, out_png: Path, dpi: int = 180):
    if out_png.exists():
        return
    with fitz.open(pdf_path) as doc:
        if len(doc) == 0:
            return
        page = doc.load_page(0)
        mat  = fitz.Matrix(dpi/72, dpi/72)
        pix  = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(str(out_png))

def main():
    rows = load_rows(KOSZTY_RES, KOSZTY_FACT) + load_rows(PRZYCHODY_RES, PRZYCHODY_FACT)
    if not rows:
        raise SystemExit("Brak rekordów do budowy datasetu (sprawdź XLS/PDF).")

    out = []
    for rec in rows:
        stem = Path(rec["pdf"]).stem
        png  = IMG_DIR / f"{stem}.png"
        try:
            render_first_page(rec["pdf"], png)
            out.append({"image_path": str(png), "labels": {"numer": rec["numer"], "data": rec["data"], "netto": rec["netto"]}})
        except Exception as e:
            print("! błąd renderu:", rec["pdf"], e)

    if not out:
        raise SystemExit("Po renderze brak przykładów.")

    random.seed(42)
    random.shuffle(out)
    n = len(out); n_val = max(1, int(0.1*n)); n_test = max(1, int(0.1*n))
    val = out[:n_val]; test = out[n_val:n_val+n_test]; train = out[n_val+n_test:]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        with open(OUT_DIR / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for ex in part:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"✅ Dataset zapisany w {OUT_DIR}: train={len(train)} val={len(val)} test={len(test)}")

if __name__ == "__main__":
    main()
