import sys, pandas as pd, re
from pathlib import Path

# kanon projektu (minimum do walidacji)
CANON = {
    "data_dokumentu": ["data dokumentu","data_dokumentu","data","invoice date","data wystawienia","data dok","dokument data"],
    "numer_dokumentu": ["numer dokumentu","numer_dokumentu","nr dokumentu","nr_dokumentu","nr","invoice no","invoice number","numer faktury","nr faktury"],
    "wartosc_netto_dokumentu": ["wartość netto dokumentu","wartosc_netto_dokumentu","netto","net amount","kwota netto","wartosc netto","net_total","net amount"],
    "zalacznik": ["zalacznik","załącznik","plik","nazwa pliku","attachment","filename","file"]
}
# (opcjonalne – jeśli masz duplikaty z sufiksem _1 w niektórych arkuszach)
OPTIONAL = {
    "data_dokumentu_1": ["data_dokumentu_1","data dokumentu 1"],
    "numer_dokumentu_1": ["numer_dokumentu_1","nr dokumentu 1"],
    "wartosc_netto_dokumentu_1": ["wartosc_netto_dokumentu_1","wartosc netto 1"],
}

def norm(s:str)->str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace(".", " ").replace("-", " ").replace("/", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("ą","a").replace("ć","c").replace("ę","e").replace("ł","l").replace("ń","n").replace("ó","o").replace("ś","s").replace("ż","z").replace("ź","z")
    s = s.replace(" ", "_")
    return s

def pick_header(df):
    # szukamy wiersza, gdzie po normalizacji trafi co najmniej 2 nazwy z naszego słownika
    for i in range(min(10, len(df))):
        row = [norm(str(x)) for x in df.iloc[i].tolist()]
        score = 0
        for v in CANON.values():
            for cand in v:
                if norm(cand) in row:
                    score += 1; break
        if score >= 2:
            return i
    return 0  # fallback

def build_map(cols):
    inv = {}
    # mapuj kanon + opcjonalne
    for k, vals in {**CANON, **OPTIONAL}.items():
        for c in cols:
            nc = norm(c)
            if any(norm(v)==nc for v in vals):
                inv[k] = c
                break
    return inv

def run(path):
    x = Path(path)
    df0 = pd.read_excel(x, header=None)
    hdr_row = pick_header(df0)
    df = pd.read_excel(x, header=hdr_row)
    # oryginalne nagłówki
    orig_cols = list(df.columns)
    colmap = build_map(orig_cols)

    # zbuduj docelowe kolumny
    out = pd.DataFrame()
    for canon in ["data_dokumentu","numer_dokumentu","wartosc_netto_dokumentu","zalacznik",
                  "data_dokumentu_1","numer_dokumentu_1","wartosc_netto_dokumentu_1"]:
        src = colmap.get(canon)
        if src in df.columns:
            out[canon] = df[src]
        else:
            out[canon] = None

    # trim i normalizacja typów bazowych
    for c in out.columns:
        if "data" in c:
            out[c] = pd.to_datetime(out[c], errors="coerce", dayfirst=True).dt.date
        elif "wartosc" in c:
            out[c] = pd.to_numeric(out[c], errors="coerce", downcast="float")
        else:
            out[c] = out[c].astype(str).str.strip()

    out_path = x.with_name(x.stem + "_normalized.xlsx")
    out.to_excel(out_path, index=False)
    # echo podsumowania
    print(f"INPUT : {x}")
    print(f"HEADER: row={hdr_row}  matched={colmap}")
    print(f"OUTPUT: {out_path}")
    print(f"COLUMNS: {list(out.columns)}")

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Użycie: python scripts/normalize_populacja.py <plik.xlsx> [<plik2.xlsx> ...]")
        sys.exit(2)
    for p in sys.argv[1:]:
        run(p)
