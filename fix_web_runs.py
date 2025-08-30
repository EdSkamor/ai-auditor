from __future__ import annotations
import os, shutil

ROOT = "web_runs"
FILES = [
    "verdicts.jsonl",
    "verdicts_summary.json",
    "verdicts_top50_mismatches.csv",
    "populacja_enriched.xlsx",
    # jeśli kiedyś zapiszesz do CWD:
    "Audyt_koncowy.xlsx",
    "All_invoices.csv",
]

def latest_run_dir(root: str = ROOT) -> str | None:
    if not os.path.isdir(root):
        return None
    runs = [os.path.join(root, d) for d in os.listdir(root)
            if os.path.isdir(os.path.join(root, d))]
    return max(runs, key=os.path.getmtime) if runs else None

def main():
    run_dir = latest_run_dir()
    if not run_dir:
        print("Brak katalogu web_runs/* – odpal najpierw Krok A/B w panelu.")
        return
    moved = 0
    for fn in FILES:
        src = os.path.join(".", fn)
        dst = os.path.join(run_dir, fn)
        if os.path.exists(src):
            os.makedirs(run_dir, exist_ok=True)
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(src, dst)
            print(f"→ moved {src} -> {dst}")
            moved += 1
    print("OK: zsynchronizowano." if moved else "Nie było czego przenosić.")

if __name__ == "__main__":
    main()
