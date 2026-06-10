import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# ==========================
# INPUT FILE
# ==========================
PDF_FILE = "../data/raw/21_393_20260211152403.pdf"

records = []

# ==========================
# PARSE PDF
# ==========================
with pdfplumber.open(PDF_FILE) as pdf:

    # page 93 = index 92
    page = pdf.pages[92]

    text = page.extract_text()

    lines = text.split("\n")

    # Pattern: rank station rain basin
    pattern = re.compile(
        r"^(\d+)\s+(.+?)\s+(\d+\.\d+)\s+([A-Za-zÀ-ÿ]+)$"
    )

    for line in lines:
        line = line.strip()
        m = pattern.match(line)

        if m:
            records.append({
                "rank": int(m.group(1)),
                "station": m.group(2),
                "rain_mm": float(m.group(3)),
                "basin": m.group(4)
            })

# ==========================
# DATAFRAME
# ==========================
df = pd.DataFrame(records)

print(df)

# ==========================
# SAVE CSV
# ==========================
os.makedirs("../data/processed", exist_ok=True)

csv_path = "../data/processed/tabella12.csv"

df.to_csv(csv_path, index=False)

print(f"CSV saved: {csv_path}")

# ==========================
# SORT DATA
# ==========================
df = df.sort_values("rain_mm", ascending=False)

# ==========================
# COLOR MAP
# ==========================
colors = {
    "Flumendosa": "tab:blue",
    "Cedrino": "tab:orange",
    "Posada": "tab:green",
    "Pramaera": "tab:red",
    "Quirra": "tab:purple",
    "Picocca": "tab:brown"
}

# ==========================
# PLOT
# ==========================
plt.figure(figsize=(15,7))

plt.bar(
    df["station"],
    df["rain_mm"],
    color=[colors.get(b, "gray") for b in df["basin"]]
)

# ==========================
# LEGEND (BASIN)
# ==========================
handles = []
labels = []

for basin, color in colors.items():
    if basin in df["basin"].values:
        handles.append(plt.Rectangle((0, 0), 1, 1, color=color))
        labels.append(basin)

plt.legend(handles, labels, title="Basin")

# ==========================
# AXIS LABELS
# ==========================
plt.xticks(rotation=90, fontsize=8)
plt.ylabel("Cumulative rainfall (mm)")
plt.xlabel("Hydrometric station")
plt.title("Table 12 - Cumulative rainfall by station")

plt.tight_layout()

# ==========================
# SAVE FIGURE
# ==========================
os.makedirs("../figures", exist_ok=True)

figure_path = "../figures/cumulative_rainfall.png"

plt.savefig(
    figure_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Figure saved: {figure_path}")

# ==========================
# SHOW
# ==========================
plt.show()
