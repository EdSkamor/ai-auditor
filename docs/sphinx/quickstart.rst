Quickstart (3 min)
==================

Wymagania
---------
- Python 3.12 + venv
- (opcjonalnie) `streamlit` do UI

Instalacja
----------
.. code-block:: bash

   cd ~/ai-audytor 2>/dev/null || cd ~/ai-auditor
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   # minimal: pandas + excel
   pip install pandas openpyxl xlsxwriter

Minimalny run „demo”
--------------------
.. code-block:: bash

   demo
   # artefakty ostatniego runu:
   RUN=$(ls -td web_runs/demo_* | head -1); echo "$RUN"
   ls -1 "$RUN"

A/B tiebreak (kontrola etykiet)
-------------------------------
.. code-block:: bash

   bash scripts/smoke_tiebreak_ab.sh
   RUN=$(ls -td web_runs/tb_ab_* | head -1); echo "$RUN"
   head -n 2 "$RUN/v1.jsonl"  # oczekiwane: kryterium 'numer+seller'

Wariant preferencji fname (V2/V3)
---------------------------------
.. code-block:: bash

   bash scripts/smoke_tiebreak_v2.sh   # oczekiwane: 'numer+fname' dla pliku prefname
   RUN=$(ls -td web_runs/tb_smoke_v2_* tb_smoke_v3_* 2>/dev/null | head -1); echo "$RUN"
   head -n 2 "$RUN"/verdicts_tb_fname.jsonl 2>/dev/null || true

Perf 200 (pełny przebieg)
-------------------------
.. code-block:: bash

   bash scripts/smoke_perf_200.sh
   RUN=$(ls -td web_runs/perf200_* | head -1); echo "$RUN"
   sed -n '1,120p' "$RUN/verdicts_summary.json"

Paczka przekazania (ZIP)
------------------------
.. code-block:: bash

   # preferowany wrapper dopinający metadane:
   scripts/pack_run_plus.sh "$(ls -td web_runs/perf200_* | head -1)"
   ZIP=$(find "$(ls -td web_runs/perf200_* | head -1)" -maxdepth 1 -name '*.zip' -type f | head -1)
   unzip -l "$ZIP" | grep -E 'run_metadata\.json|Audyt_koncowy\.xlsx|verdicts\.jsonl'

UI (podgląd)
------------
.. code-block:: bash

   streamlit run streamlit_app.py 2>/dev/null || streamlit run app/streamlit_app.py


.. pages-bump: 2025-08-30T10:35:12Z

.. pages-bump: 2025-08-30T11:10:00Z

.. pages-bump-assert: 2025-08-30T11:15:28Z
