# API

## `GET /healthz`
Zwraca: `{"status":"ok"}`

## `POST /analyze`
Body (JSON):
~~~
{"prompt":"...", "max_new_tokens":220, "do_sample":false, "temperature":0.7, "top_p":0.9}
~~~
Odpowiedź:
~~~
{"output":"..." }
~~~

## `POST /analyze-file`
Form-data:
- `file`: XLSX/CSV/TSV

Odpowiedź (skrót):
~~~
{
  "filename": "populacja.xlsx",
  "shape": [rows, cols],
  "columns": ["..."],
  "metrics": { "rows": 30, "cols": 7, "amount_sum": 2529594.52, "amount_mean": 84319.82 },
  "prompts": ["..."],
  "analysis": {
    "date_col": "data_dokumentu",
    "amount_col": "wartosc_netto_dokumentu",
    "monthly": [["2023-01", 12345.0], ...],
    "mom_abs": 111.0,
    "mom_pct": 3.2,
    "top_counterparties": [["ACME", 123456.0], ...]
  },
  "sample": [ { "kol1": "val", ... } ],
  "saved_to": null
}
~~~
