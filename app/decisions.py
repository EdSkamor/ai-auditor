from __future__ import annotations
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

# Pliki decyzji: data/decisions/decisions_YYYYMMDD.csv
# Kolumny: id,decision,reason,ts,user
# Decyzje: "approved" | "rejected"

DECISIONS_DIR = Path("data/decisions")
DECISIONS_DIR.mkdir(parents=True, exist_ok=True)

VALID_DECISIONS = {"approved", "rejected"}

@dataclass
class Decision:
    id: str
    decision: str
    reason: str = ""
    ts: Optional[str] = None  # ISO8601
    user: str = "local"

    def normalize(self) -> "Decision":
        d = self.decision.strip().lower()
        if d in {"ok","accept","accepted","zatwierdz","zatwierdź","approve","approved"}:
            d = "approved"
        elif d in {"reject","rejected","odrzuc","odrzuć","odrzucone"}:
            d = "rejected"
        if d not in VALID_DECISIONS:
            raise ValueError(f"Unsupported decision: {self.decision!r}")
        if not self.ts:
            self.ts = datetime.now().astimezone().isoformat(timespec="seconds")
        self.decision = d
        self.id = str(self.id).strip()
        self.reason = (self.reason or "").strip()
        self.user = (self.user or "local").strip()
        return self

def decisions_csv_path(for_date: Optional[str] = None) -> Path:
    if not for_date:
        for_date = datetime.now().strftime("%Y%m%d")
    return DECISIONS_DIR / f"decisions_{for_date}.csv"

def _ensure_csv_header(p: Path) -> None:
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(["id","decision","reason","ts","user"])

def save_decisions(ids: Iterable[str], decision: str, reason: str = "", user: str = "local", for_date: Optional[str] = None) -> Path:
    p = decisions_csv_path(for_date)
    _ensure_csv_header(p)
    norm: List[Decision] = []
    for _id in ids:
        norm.append(Decision(id=str(_id), decision=decision, reason=reason, user=user).normalize())
    with p.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for d in norm:
            w.writerow([d.id, d.decision, d.reason, d.ts, d.user])
    return p

def load_decisions(for_date: Optional[str] = None) -> List[Decision]:
    p = decisions_csv_path(for_date)
    if not p.exists():
        return []
    out: List[Decision] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(Decision(
                id=str(row.get("id","")),
                decision=str(row.get("decision","")),
                reason=row.get("reason","") or "",
                ts=row.get("ts","") or None,
                user=row.get("user","") or "local",
            ).normalize())
    return out

def merge_decisions_into_csv(input_csv: Path, output_csv: Path, for_date: Optional[str] = None) -> Path:
    decs = load_decisions(for_date)
    by_id = {d.id: d for d in decs}
    with input_csv.open("r", encoding="utf-8", newline="") as f_in, \
         output_csv.open("w", encoding="utf-8", newline="") as f_out:
        r = csv.DictReader(f_in)
        fieldnames = list(r.fieldnames or [])
        for extra in ("decision","decision_ts","decision_user"):
            if extra not in fieldnames:
                fieldnames.append(extra)
        w = csv.DictWriter(f_out, fieldnames=fieldnames)
        w.writeheader()
        for row in r:
            _id = str(row.get("id","")).strip()
            d = by_id.get(_id)
            row["decision"] = d.decision if d else ""
            row["decision_ts"] = d.ts if d else ""
            row["decision_user"] = d.user if d else ""
            w.writerow(row)
    return output_csv

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="AI-Audytor decisions helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s_save = sub.add_parser("save", help="Zapisz decyzje dla listy ID")
    s_save.add_argument("--ids", required=True, help="Lista ID po przecinku, np. 101,102,103")
    s_save.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    s_save.add_argument("--reason", default="")
    s_save.add_argument("--user", default=os.environ.get("USER","local"))
    s_save.add_argument("--date", default=None, help="YYYYMMDD (opcjonalnie)")

    s_merge = sub.add_parser("merge", help="Zmerguj decyzje do CSV")
    s_merge.add_argument("--in", dest="in_csv", required=True)
    s_merge.add_argument("--out", dest="out_csv", required=True)
    s_merge.add_argument("--date", default=None, help="YYYYMMDD (opcjonalnie)")

    args = ap.parse_args()
    if args.cmd == "save":
        p = save_decisions(
            ids=[s.strip() for s in args.ids.split(",") if s.strip()],
            decision=args.decision,
            reason=args.reason,
            user=args.user,
            for_date=args.date,
        )
        print(p)
    elif args.cmd == "merge":
        out = merge_decisions_into_csv(Path(args.in_csv), Path(args.out_csv), for_date=args.date)
        print(out)
