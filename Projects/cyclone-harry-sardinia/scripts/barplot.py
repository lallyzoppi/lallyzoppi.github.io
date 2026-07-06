import pandas as pd
import matplotlib.pyplot as plt

# Load hydrometric data
df = pd.read_csv("../data/processed/tabella13.csv")

# Compute maximum discharge per station
df_max = df.groupby("stazione")["portata_m3s"].max().sort_values(ascending=False)

# Plot bar chart
plt.figure(figsize=(12,6))
plt.bar(df_max.index, df_max.values)

# Formatting
plt.xticks(rotation=90)
plt.ylabel("Maximum discharge (m³/s)")
plt.title("Maximum discharge comparison between stations")

plt.tight_layout()
plt.show()
