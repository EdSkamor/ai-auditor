# Pakowanie runu

## scripts/pack_run_plus.sh
Wrapper na `scripts/pack_run.sh`, który po spakowaniu dopina:
- `run_metadata.json` (jeśli jest w katalogu runu),
- `ExecutiveSummary.pdf` (jeśli jest).

### Użycie
```bash
scripts/pack_run_plus.sh web_runs/<RUN_DIR>
```

ZIP wynikowy pozostaje w katalogu danego runu.
