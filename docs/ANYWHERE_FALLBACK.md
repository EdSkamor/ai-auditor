# ANYWHERE / ANCHOR – polityka
- `strict` — wynik bazowy, bez heurystyk.
- `ok_anchor1p` — dopasowanie liczby w liniach z kotwicą (NETTO/RAZEM/VAT/BRUTTO/DO ZAPŁATY), różnica ≤1%.
- `needs_review` — dopasowanie „gdziekolwiek” (fallback). To sugestia do ręcznego przeglądu, **nie** liczymy jako OK.
- `effective_conservative` — do OK zaliczamy tylko `ok_anchor1p`.

W UI „🧾 Walidacja” pokażemy rozbicie po statusach i listę flipów z numerem strony.
