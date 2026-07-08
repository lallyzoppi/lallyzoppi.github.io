# =====================================================
# 04_validation_report.py
#
# Validation Report
# Sardinia Fire Forecast
# =====================================================

import os
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# FILES
# =============================

FORECAST = "SARDINIA_FIRE_FORECAST_14D.csv"

OUTDIR = "validation"

os.makedirs(OUTDIR, exist_ok=True)

# =============================
# LOAD
# =============================

df = pd.read_csv(FORECAST)

df["date"] = pd.to_datetime(df["date"])

print("Forecast loaded:", df.shape)

# =============================
# DAILY STATISTICS
# =============================

daily = (
    df.groupby("date")["risk_probability"]
    .agg(["mean", "min", "max", "std"])
    .reset_index()
)

daily.columns = [
    "date",
    "mean_risk",
    "min_risk",
    "max_risk",
    "std_risk"
]

# =============================
# CLASS COUNTS
# =============================

classes = (
    df.groupby(["date", "risk_class"])
      .size()
      .unstack(fill_value=0)
)

daily = daily.merge(
    classes,
    on="date",
    how="left"
)

daily.to_csv(
    os.path.join(
        OUTDIR,
        "daily_statistics.csv"
    ),
    index=False
)

print("Daily statistics saved.")

# =============================
# HISTOGRAM
# =============================

plt.figure(figsize=(8,5))

plt.hist(
    df["risk_probability"],
    bins=25
)

plt.xlabel("Risk Probability")
plt.ylabel("Cells")
plt.title("Distribution of Fire Risk Probability")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTDIR,
        "risk_distribution.png"
    ),
    dpi=200
)

plt.close()

# =============================
# DAILY MEAN
# =============================

plt.figure(figsize=(10,5))

plt.plot(
    daily["date"],
    daily["mean_risk"],
    marker="o"
)

plt.grid(True)

plt.ylabel("Mean Risk")

plt.title("Daily Mean Fire Risk")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTDIR,
        "daily_mean_risk.png"
    ),
    dpi=200
)

plt.close()

# =============================
# CLASS DISTRIBUTION
# =============================

risk_classes = df["risk_class"].value_counts()

plt.figure(figsize=(6,5))

risk_classes.plot(kind="bar")

plt.ylabel("Number of Cells")

plt.title("Risk Classes")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTDIR,
        "class_distribution.png"
    ),
    dpi=200
)

plt.close()

# =============================
# CORRELATION
# =============================

possible = [
    "risk_probability",
    "temperature",
    "t2m",
    "wind_speed",
    "wind",
    "u10",
    "v10",
    "humidity",
    "relative_humidity",
    "tp"
]

cols = [c for c in possible if c in df.columns]

if len(cols) > 1:

    corr = df[cols].corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(8,6))

    im = ax.imshow(corr)

    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right")

    ax.set_yticks(range(len(cols)))
    ax.set_yticklabels(cols)

    plt.colorbar(im)

    plt.title("Correlation Matrix")

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTDIR,
            "correlation_matrix.png"
        ),
        dpi=200
    )

    plt.close()

# =============================
# HOTSPOTS
# =============================

top = df.sort_values(
    "risk_probability",
    ascending=False
).head(20)

top.to_csv(
    os.path.join(
        OUTDIR,
        "top20_hotspots.csv"
    ),
    index=False
)

# =============================
# REPORT
# =============================

highest = daily.loc[
    daily["mean_risk"].idxmax()
]

lowest = daily.loc[
    daily["mean_risk"].idxmin()
]

with open(
    os.path.join(
        OUTDIR,
        "validation_report.txt"
    ),
    "w"
) as f:

    f.write("=====================================\n")
    f.write("SARDINIA FIRE FORECAST VALIDATION\n")
    f.write("=====================================\n\n")

    f.write(
        f"Forecast Days : {len(daily)}\n"
    )

    f.write(
        f"Overall Mean Risk : {df['risk_probability'].mean():.3f}\n"
    )

    f.write(
        f"Overall Maximum : {df['risk_probability'].max():.3f}\n"
    )

    f.write(
        f"Overall Minimum : {df['risk_probability'].min():.3f}\n\n"
    )

    f.write(
        "Highest Risk Day\n"
    )

    f.write(
        f"{highest['date'].date()}  Mean={highest['mean_risk']:.3f}\n\n"
    )

    f.write(
        "Lowest Risk Day\n"
    )

    f.write(
        f"{lowest['date'].date()}  Mean={lowest['mean_risk']:.3f}\n\n"
    )

    f.write(
        "Risk Classes\n"
    )

    f.write(
        str(df["risk_class"].value_counts())
    )

    f.write("\n\n")

    f.write("Top 20 Hotspots saved in top20_hotspots.csv\n")

print("\n===================================")
print("VALIDATION COMPLETED")
print("===================================")
print("Output folder:", OUTDIR)
