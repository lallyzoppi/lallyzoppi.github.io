import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

PDF_FILE = "../data/raw/21_393_20260211152403.pdf"

records = []

with pdfplumber.open(PDF_FILE) as pdf:

    # Tabella 13: pagine 94-95 => indici 93 e 94
    text = ""

    for page_idx in [93, 94]:
        text += "\n" + (pdf.pages[page_idx].extract_text() or "")

# Pattern della tabella
pattern = re.compile(
    r"(\d+)\s+"                     # numero progressivo
    r"(F\d+)\s+"                    # codice stazione
    r"(.+?)\s+"                     # nome stazione
    r"(\d{2}/\d{2}/\d{4})\s+"       # data
    r"(\d{2}:\d{2})\s+"             # orario
    r"([\d\.]+)\s+"                 # livello
    r"([\d\.]+)"                    # portata
)

for line in text.split("\n"):

    line = line.strip()

    match = pattern.match(line)

    if match:

        records.append({
            "id": int(match.group(1)),
            "codice": match.group(2),
            "stazione": match.group(3),
            "data": match.group(4),
            "orario": match.group(5),
            "livello_m": float(match.group(6)),
            "portata_m3s": float(match.group(7))
        })

df = pd.DataFrame(records)

# ==========================
# CSV
# ==========================

os.makedirs("../data/processed", exist_ok=True)

csv_file = "../data/processed/tabella13.csv"

df.to_csv(csv_file, index=False)

print(f"Salvato: {csv_file}")
print(df.head())

# ==========================
# PORTATA MASSIMA PER STAZIONE
# ==========================

df_max = (
    df.groupby("stazione", as_index=False)["portata_m3s"]
      .max()
      .sort_values("portata_m3s", ascending=False)
)

# ==========================
# GRAFICO
# ==========================

plt.figure(figsize=(14, 7))

plt.bar(
    df_max["stazione"],
    df_max["portata_m3s"]
)

plt.xticks(
    rotation=90,
    fontsize=8,
    ha="right"
)

plt.ylabel("Discharge (m³/s)")
plt.xlabel("Hydrometric station")

plt.title(
    "Tabella 13 - Maximum measured discharge by station"
)

plt.tight_layout()

os.makedirs("../figures", exist_ok=True)

figure_file = "../figures/MaximumDischarge.png"

plt.savefig(
    figure_file,
    dpi=300,
    bbox_inches="tight"
)

print(f"Grafico salvato: {figure_file}")

plt.show()
