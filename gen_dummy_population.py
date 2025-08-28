import pandas as pd, os

# Koszty
koszty = pd.DataFrame([
    {"DATA DOKUMENTU":"2024-12-05","NUMER DOKUMENTU":"FV_001_12_2024","WARTOŚĆ NETTO DOKUMENTU":"1000,00","ZAŁĄCZNIK":"611"},
    {"DATA DOKUMENTU":"05.12.2024","NUMER DOKUMENTU":"INV-2024-12-020","WARTOŚĆ NETTO DOKUMENTU":"200.00","ZAŁĄCZNIK":"612"},
    {"DATA DOKUMENTU":"2024/12/20","NUMER DOKUMENTU":"2024-12-AC-77","WARTOŚĆ NETTO DOKUMENTU":"300,00","ZAŁĄCZNIK":"613"},
    # rozbieżność netto (powinno dać NIE na netto)
    {"DATA DOKUMENTU":"2024-12-05","NUMER DOKUMENTU":"FV/001/12/2024","WARTOŚĆ NETTO DOKUMENTU":"999,99","ZAŁĄCZNIK":"614"},
])

# Przychody – pusta dla demo
przychody = pd.DataFrame(columns=["DATA DOKUMENTU","NUMER DOKUMENTU","WARTOŚĆ NETTO DOKUMENTU","ZAŁĄCZNIK"])

with pd.ExcelWriter("populacja.xlsx", engine="openpyxl") as xl:
    koszty.to_excel(xl, sheet_name="Koszty", index=False)
    przychody.to_excel(xl, sheet_name="Przychody", index=False)
print("OK -> populacja.xlsx")
