import pdfplumber
import pandas as pd
import re
import os

PDF_FILE = "../data/raw/21_393_20260211152403.pdf"

os.makedirs("../data/processed", exist_ok=True)

records = []

with pdfplumber.open(PDF_FILE) as pdf:

    text = ""
    for i in [93, 94]:
        text += "\n" + (pdf.pages[i].extract_text() or "")

pattern = re.compile(
    r"(\d+)\s+F\d+\s+(.+?)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+([\d\.]+)\s+([\d\.]+)"
)

for line in text.split("\n"):
    m = pattern.match(line.strip())
    if m:
        records.append({
            "id": int(m.group(1)),
            "station": m.group(2),
            "date": m.group(3),
            "time": m.group(4),
            "level_m": float(m.group(5)),
            "flow": float(m.group(6))
        })

df = pd.DataFrame(records)

# datetime
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], dayfirst=True)

# FILTER POSADA (puoi cambiarlo)
df_posada = df[df["station"].str.contains("Posada", na=False)]

df_posada = df_posada.sort_values("datetime")

# EXPORT FOR WEB
df_posada.to_csv("../data/processed/posada_timeseries.csv", index=False)

print("Export completed:", len(df_posada))
