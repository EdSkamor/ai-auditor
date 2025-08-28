import pandas as pd, sys
xls = sys.argv[1] if len(sys.argv)>1 else "invoices_report.xlsx"
xf = pd.ExcelFile(xls)
for sh in xf.sheet_names:
    if sh.startswith("Summary_") or sh in ("Summary_ALL","Monthly_PLN"):
        print("\n===", sh, "===")
        df = xf.parse(sh)
        print(df.head(20).to_string(index=False))
