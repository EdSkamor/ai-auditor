from __future__ import annotations
import argparse, json, os, datetime as dt
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def load_json(p):
    return json.load(open(p,encoding="utf-8")) if p and os.path.isfile(p) else {}

def parse_top_mismatches(verdicts_jsonl:str, limit:int=10):
    rows=[]
    if verdicts_jsonl and os.path.isfile(verdicts_jsonl):
        with open(verdicts_jsonl, encoding="utf-8") as f:
            for line in f:
                try:
                    j=json.loads(line)
                except: 
                    continue
                if j.get("zgodnosc")=="NIE":
                    rows.append([
                        j.get("sekcja",""),
                        j.get("pozycja_id",""),
                        j.get("numer_pop",""),
                        j.get("data_pop",""),
                        j.get("wyciagniete",{}).get("numer_pdf",""),
                        j.get("wyciagniete",{}).get("data_pdf",""),
                        j.get("porownanie",{}).get("numer",""),
                        j.get("porownanie",{}).get("data",""),
                        j.get("porownanie",{}).get("netto",""),
                    ])
                if len(rows)>=limit: break
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--verdicts", default=None, help="verdicts.jsonl do sekcji TopN")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Asystent Audytora – Executive Summary")
    ap.add_argument("--topn", type=int, default=10)
    args = ap.parse_args()

    S = load_json(args.summary)
    met = S.get("metryki", {})
    uw  = S.get("uwagi_globalne", [])

    doc = SimpleDocTemplate(args.out, pagesize=A4, title=args.title)
    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]; h1.textColor = colors.HexColor("#111111")
    h2 = styles["Heading2"]; h2.textColor = colors.HexColor("#333333")
    p  = styles["BodyText"]

    story=[]
    story += [Paragraph(args.title, h1), Spacer(1,8)]
    story += [Paragraph(f"Data raportu: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", p), Spacer(1,6)]

    # Metryki
    story += [Paragraph("Podsumowanie metryk", h2)]
    data = [
        ["Liczba pozycji (Koszty)", met.get("liczba_pozycji_koszty","")],
        ["Liczba PDF (Koszty)", met.get("liczba_pdf_koszty","")],
        ["Liczba pozycji (Przychody)", met.get("liczba_pozycji_przychody","")],
        ["Liczba PDF (Przychody)", met.get("liczba_pdf_przychody","")],
        ["Braki PDF – Koszty", met.get("braki_pdf",{}).get("Koszty","")],
        ["Braki PDF – Przychody", met.get("braki_pdf",{}).get("Przychody","")],
        ["Niezgodności – numer/data/netto", str(met.get("niezgodnosci",{}))],
    ]
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.whitesmoke),
    ]))
    story += [t, Spacer(1,12)]

    # Uwagi
    if uw:
        story += [Paragraph("Uwagi globalne", h2)]
        for u in uw:
            story += [Paragraph(f"• {u}", p)]
        story += [Spacer(1,12)]

    # Top N niezgodności
    rows = parse_top_mismatches(args.verdicts, args.topn)
    story += [Paragraph(f"Top {args.topn} niezgodności", h2)]
    if rows:
        head = ["Sekcja","ID","Numer POP","Data POP","Numer PDF","Data PDF","=Numer","=Data","=Netto"]
        t2 = Table([head] + rows, hAlign="LEFT", colWidths=[60,30,90,70,90,70,50,50,50])
        t2.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.25,colors.grey),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#F1F5F9")),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')
        ]))
        story += [t2]
    else:
        story += [Paragraph("Brak niezgodności do pokazania.", p)]

    doc.build(story)
    print(f"OK -> {args.out}")
if __name__=="__main__":
    main()
