# Pakowanie runu

## Preferowany: scripts/pack_run.sh (z dopinaniem metadanych)
`scripts/pack_run.sh` po spakowaniu dopina automatycznie:
- `run_metadata.json` (jeśli jest w katalogu runu),
- `ExecutiveSummary.pdf` (jeśli jest).

### Użycie
```bash
RUN=$(ls -td web_runs/perf200_* | head -1)
bash scripts/pack_run.sh "$RUN"
ZIP=$(find "$RUN" -maxdepth 1 -name '*.zip' -type f | sort | tail -1)
unzip -l "$ZIP" | grep -E 'run_metadata\.json|ExecutiveSummary\.pdf'
```

## Alternatywa: scripts/pack_run_plus.sh
Wrapper pozostaje dostępny wstecznie kompatybilnie (wywołuje `pack_run.sh` i dopina te same pliki).
