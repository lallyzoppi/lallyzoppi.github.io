import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# LOAD DATA FROM FILE
# =========================
file_path = "../data/processed/wind.csv"
df = pd.read_csv(file_path)

# clean station names
df["Stazione"] = df["Stazione"].str.strip()

# sort
df = df.sort_values("Vento_medio_ms")
df2 = df.sort_values("Raffica_ms")

# =========================
# STYLE
# =========================
sns.set_theme(style="darkgrid", context="talk")

# =========================
# FIGURE
# =========================
fig, axes = plt.subplots(3, 1, figsize=(14, 18))

# =========================
# 1) WIND SPEED
# =========================
sns.barplot(
    data=df,
    y="Stazione",
    x="Vento_medio_ms",
    hue="Stazione",
    dodge=False,
    palette="viridis",
    legend=False,
    ax=axes[0]
)

axes[0].set_title("Wind Speed (m/s) by Station")
axes[0].set_xlabel("Wind Speed (m/s)")
axes[0].set_ylabel("")

# =========================
# 2) GUST SPEED
# =========================
sns.barplot(
    data=df2,
    y="Stazione",
    x="Raffica_ms",
    hue="Stazione",
    dodge=False,
    palette="magma",
    legend=False,
    ax=axes[1]
)

axes[1].set_title("Maximum Gusts (m/s) by Station")
axes[1].set_xlabel("Gust Speed (m/s)")
axes[1].set_ylabel("")

# =========================
# 3) SCATTER + TREND
# =========================
sns.scatterplot(
    data=df,
    x="Vento_medio_ms",
    y="Raffica_ms",
    s=120,
    color="deepskyblue",
    edgecolor="black",
    ax=axes[2]
)

sns.regplot(
    data=df,
    x="Vento_medio_ms",
    y="Raffica_ms",
    scatter=False,
    color="red",
    ax=axes[2]
)

axes[2].set_title("Wind Speed vs Gusts")
axes[2].set_xlabel("Wind Speed (m/s)")
axes[2].set_ylabel("Gust Speed (m/s)")

# =========================
# SAVE FIGURE
# =========================
output_file = "../figures/wind_plots.png"
plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches="tight")

plt.show()

print(f"Plot salvato in: {output_file}")
