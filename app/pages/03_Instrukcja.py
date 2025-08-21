import os, streamlit as st
from pathlib import Path

st.set_page_config(page_title="AI-Audytor – Instrukcja", layout="wide")
st.title("📘 Instrukcja (dla użytkownika)")


from app.ui_nav import back as _back
_back()
st.markdown("""
### Co to jest?
**AI-Audytor** pomaga w dwóch rzeczach:
- **Chat – Audytor**: rozmawiasz z asystentem o danych finansowych, możesz dodać pliki (PDF/XLSX/CSV), poprosić o tabelę lub wykres.
- **Walidacja**: porównujesz liczby z arkusza z tym, co jest na fakturach PDF (np. kwoty netto/brutto).

Działa **lokalnie** – pliki **nie są wysyłane** do chmury.
""")

with st.expander("Jak zacząć w 30 sekund?", expanded=True):
    st.markdown("""
1. Wejdź na **Home**. Jeśli jest komunikat „Model lokalny OK”, wszystko gra.
   Jeśli nie – ustaw zmienną środowiskową `LLM_GGUF` na ścieżkę do pliku `.gguf` i odśwież stronę.
2. Przejdź do **Chat – Audytor** → wpisz pytanie. Możesz dodać pliki (PDF/XLSX/CSV).
3. Do porównań arkusz ↔ faktury użyj zakładki **Walidacja**.
4. Sporne przypadki przejrzysz i oznaczysz w **Przeglądzie**.
""")

st.subheader("💬 Chat – Audytor")
st.markdown("""
- Przykład pytania: *„Policz sumaryczny VAT i pokaż top-3 kontrahentów wg brutto.”*
- Po dodaniu pliku XLSX/CSV/ PDF, system streści zawartość i odpowie na pytanie.
- Możesz poprosić o **wykres** (np. kolumnowy brutto wg kontrahenta) albo **tabelę**.
""")
st.page_link("pages/00_Chat_Audytor.py", label="➡️ Przejdź do: Chat – Audytor", icon="💬")

st.divider()
st.subheader("🧾 Walidacja (arkusz ↔ faktury PDF)")
st.markdown("""
**Po co?** Sprawdzamy, czy wartości z arkusza (np. netto/brutto) zgadzają się z tym, co jest na fakturach PDF.

**Przygotowanie (.env.local):**
- `KOSZTY_RES` – ścieżka do arkusza kosztów (xlsx)
- `KOSZTY_FACT` – folder z fakturami kosztów (PDF)
- `PRZYCHODY_RES` / `PRZYCHODY_FACT` – analogicznie dla przychodów

**Użycie:**
1. Wejdź w **Walidacja** i kliknij **Start walidacji** (po kolei dla kosztów/przychodów).
2. Poczekaj na statusy: `ok`, `mismatch`, `missing_pdf`, `needs_review`.
3. Przejdź do **Przeglądu** – tam zaakceptujesz/odrzucisz sporne pozycje.

**Co oznacza `needs_review`?**
- System znalazł taką samą kwotę, ale **poza miejscem kotwicy** (np. liczba 150 000 pojawia się w innym miejscu dokumentu).
- To sygnał do **manualnej decyzji** audytora.
""")
st.page_link("pages/01_Walidacja.py", label="➡️ Przejdź do: Walidacja", icon="🧾")

st.caption("""
Tryby dopasowania (w tle):
- **ANCHOR (ostrożny)** – szuka w typowych sekcjach faktury (SUMA/NETTO/BRUTTO/VAT/DO ZAPŁATY).
- **ANYWHERE (awaryjny)** – potrafi znaleźć kwotę w dowolnym miejscu dokumentu.
Gdy ANCHOR nie znajdzie, a ANYWHERE trafi idealnie, oznaczamy to jako `needs_review`.
""")

st.divider()
st.subheader("🧐 Przegląd (ręczne decyzje)")
st.markdown("""
- Widzisz **sporne pozycje** (`needs_review`) wraz z kontekstem z PDF.
- Klikasz **akceptuję (ok)** albo **odrzucam (mismatch)**.
- Tworzony jest wynik **effective_override** – to finalny raport po Twoich decyzjach.
""")
st.page_link("pages/02_Przeglad.py", label="➡️ Przejdź do: Przegląd", icon="🧐")

st.divider()
st.subheader("Bezpieczeństwo i prywatność")
st.markdown("""
- Pliki trzymamy **lokalnie** w `data/`. Repozytorium **ignoruje** dane (jest w `.gitignore`).
- Modele są lokalne (`models/`).
- Tokeny/ścieżki w `.env.local` (lokalnie, poza Gitem).
""")

st.divider()
st.subheader("Szybkie podpowiedzi (FAQ)")
with st.expander("Model nie wykryty (`LLM_GGUF`)"):
    st.code('export LLM_GGUF="/pełna/ścieżka/do/modelu.gguf"', language="bash")
with st.expander("Brak dostępu do modelu HF (prywatny)"):
    st.markdown("Zaloguj się w terminalu: `hf auth login` (token z uprawnieniem *Model: Read*).")
with st.expander("Port zajęty (8501)"):
    st.code('fuser -k 8501/tcp  # albo: pkill -f "streamlit run"', language="bash")
with st.expander("Walidacja nic nie zwraca"):
    st.markdown("Sprawdź ścieżki w `.env.local` (RES/FACT) i uruchom **Walidację** ponownie.")
