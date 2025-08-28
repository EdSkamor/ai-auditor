from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

def one(path, *, invoice_id, date, seller, buyer, currency, net, vat, gross, po=None):
    c = canvas.Canvas(path, pagesize=A4)
    x,y = 20*mm, 270*mm
    c.setFont("Helvetica-Bold", 14); c.drawString(x,y, f"FAKTURA / INVOICE {invoice_id}"); y-=12*mm
    c.setFont("Helvetica", 10)
    c.drawString(x,y, f"Data wystawienia: {date}"); y-=8*mm
    c.drawString(x,y, f"Sprzedawca: {seller}"); y-=8*mm
    c.drawString(x,y, f"Nabywca: {buyer}"); y-=8*mm
    if po:
        c.drawString(x,y, f"PO: {po}"); y-=8*mm
    y-=4*mm
    c.drawString(x,y, f"Suma netto: {net} {currency}"); y-=8*mm
    c.drawString(x,y, f"VAT: {vat} {currency}"); y-=8*mm
    c.drawString(x,y, f"Suma brutto: {gross} {currency}"); y-=8*mm
    c.showPage(); c.save()

if __name__=="__main__":
    outdir = "demo_invoices"
    os.makedirs(outdir, exist_ok=True)
    one(os.path.join(outdir,"f1_pln.pdf"), invoice_id="FV/001/12/2024", date="2024-12-05",
        seller="ACME Sp. z o.o.", buyer="Klient Alfa", currency="PLN", net="1000,00", vat="230,00", gross="1230,00", po="PO-12345")
    one(os.path.join(outdir,"f2_eur.pdf"), invoice_id="INV-2024-12-020", date="05.12.2024",
        seller="EU Services GmbH", buyer="Klient Beta", currency="EUR", net="200.00", vat="46.00", gross="246.00")
    one(os.path.join(outdir,"f3_usd.pdf"), invoice_id="2024/12/AC-77", date="2024-12-20",
        seller="US Cloud LLC", buyer="Klient Gamma", currency="$", net="300.00", vat="0.00", gross="300.00")
    # duplikat po nr+sprzedawcy+dacie
    one(os.path.join(outdir,"f4_dup_pln.pdf"), invoice_id="FV/001/12/2024", date="2024-12-05",
        seller="ACME Sp. z o.o.", buyer="Klient Alfa", currency="PLN", net="1000.00", vat="230.00", gross="1230.00")
    print("OK -> demo_invoices/*.pdf")
