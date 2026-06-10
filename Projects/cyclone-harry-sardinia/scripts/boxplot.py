import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("../data/processed/tabella13.csv")

# Boxplot of discharge distribution per station
plt.figure(figsize=(12,6))

df.boxplot(column="portata_m3s", by="stazione", rot=90)

# Formatting
plt.title("Discharge distribution per station")
plt.suptitle("")  # remove automatic title
plt.ylabel("Discharge (m³/s)")

plt.tight_layout()
plt.show()
