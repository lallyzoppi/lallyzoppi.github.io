import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("../data/processed/tabella13.csv")

# Convert to datetime
df["datetime"] = pd.to_datetime(
    df["data"] + " " + df["orario"],
    dayfirst=True
)

# Pivot table: time vs stations
pivot = df.pivot_table(
    index="datetime",
    columns="stazione",
    values="portata_m3s"
)

# Plot heatmap
plt.figure(figsize=(12,6))

plt.imshow(pivot.T, aspect="auto")

# Axis labels
plt.yticks(range(len(pivot.columns)), pivot.columns)
plt.xticks([])

plt.title("Temporal evolution of discharge across stations")
plt.colorbar(label="Discharge (m³/s)")

plt.tight_layout()

# Save figure
plt.savefig(
    "../figures/discharge_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
