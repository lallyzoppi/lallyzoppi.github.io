# =====================================================
# 05_AI_Forecast_Analysis.py
#
# AI Fire Forecast Analysis
# Sardinia Wildfire Risk Model
#
# PART 1/4
# =====================================================


import os
import pandas as pd
import numpy as np


# =============================
# CONFIG
# =============================

FORECAST = "SARDINIA_FIRE_FORECAST_14D.csv"

OUTDIR = "analysis"

os.makedirs(
    OUTDIR,
    exist_ok=True
)


# =============================
# LOAD DATA
# =============================


print("\nLoading forecast...")


df = pd.read_csv(
    FORECAST
)


df["date"] = pd.to_datetime(
    df["date"]
)


print(
    "Records:",
    len(df)
)


# =============================
# BASIC INFO
# =============================


start_date = df.date.min()
end_date   = df.date.max()


print(
    "Period:",
    start_date.date(),
    "->",
    end_date.date()
)


# =============================
# DAILY SUMMARY
# =============================


daily = (
    df.groupby("date")
    .agg(
        mean_risk=(
            "risk_probability",
            "mean"
        ),

        min_risk=(
            "risk_probability",
            "min"
        ),

        max_risk=(
            "risk_probability",
            "max"
        ),

        std_risk=(
            "risk_probability",
            "std"
        )
    )
    .reset_index()
)



# add classes if present

if "risk_class" in df.columns:


    classes = (
        df.groupby(
            [
                "date",
                "risk_class"
            ]
        )
        .size()
        .unstack(
            fill_value=0
        )
        .reset_index()
    )


    daily = daily.merge(
        classes,
        on="date",
        how="left"
    )



daily.to_csv(
    os.path.join(
        OUTDIR,
        "daily_summary.csv"
    ),
    index=False
)


print(
    "Daily summary saved"
)


# =============================
# GLOBAL STATISTICS
# =============================


overall_mean = (
    df.risk_probability.mean()
)


overall_max = (
    df.risk_probability.max()
)


overall_min = (
    df.risk_probability.min()
)



highest = daily.loc[
    daily.mean_risk.idxmax()
]


lowest = daily.loc[
    daily.mean_risk.idxmin()
]



# =============================
# TREND ANALYSIS
# =============================


first = daily.mean_risk.iloc[0]
last  = daily.mean_risk.iloc[-1]


difference = last - first



if difference > 0.10:

    trend = "INCREASING"


elif difference < -0.10:

    trend = "DECREASING"


else:

    trend = "STABLE"



# =============================
# SUMMARY TEXT
# =============================


summary_file = os.path.join(
    OUTDIR,
    "summary.txt"
)



with open(
    summary_file,
    "w",
    encoding="utf-8"
) as f:


    f.write(
        "=====================================\n"
    )

    f.write(
        "SARDINIA FIRE FORECAST ANALYSIS\n"
    )

    f.write(
        "=====================================\n\n"
    )


    f.write(
        f"Forecast period:\n"
    )

    f.write(
        f"{start_date.date()} - {end_date.date()}\n\n"
    )


    f.write(
        f"Total cells: {len(df)}\n\n"
    )


    f.write(
        "GLOBAL RISK\n"
    )

    f.write(
        f"Mean: {overall_mean:.3f}\n"
    )

    f.write(
        f"Maximum: {overall_max:.3f}\n"
    )

    f.write(
        f"Minimum: {overall_min:.3f}\n\n"
    )


    f.write(
        "TREND\n"
    )

    f.write(
        trend
    )

    f.write(
        "\n\n"
    )


    f.write(
        "MOST CRITICAL DAY\n"
    )

    f.write(
        f"{highest.date.date()} "
    )

    f.write(
        f" mean={highest.mean_risk:.3f}\n\n"
    )


    f.write(
        "LOWEST RISK DAY\n"
    )

    f.write(
        f"{lowest.date.date()} "
    )

    f.write(
        f" mean={lowest.mean_risk:.3f}\n"
    )



print("\n==============================")
print("PART 1 COMPLETED")
print("==============================")

print(
    "Trend:",
    trend
)

print(
    "Highest:",
    highest.date.date(),
    highest.mean_risk
)

print(
    "Lowest:",
    lowest.date.date(),
    lowest.mean_risk
)

# =====================================================
# PART 2/4
#
# Graphs + Meteorological Correlations
# =====================================================


import matplotlib.pyplot as plt



# =============================
# DAILY RISK TREND
# =============================


print(
    "\nCreating risk trend plot..."
)


plt.figure(
    figsize=(11,5)
)


plt.plot(
    daily["date"],
    daily["mean_risk"],
    marker="o"
)


plt.title(
    "Daily Mean Fire Risk Forecast"
)


plt.xlabel(
    "Date"
)


plt.ylabel(
    "Mean Risk Probability"
)


plt.grid(
    True
)


plt.xticks(
    rotation=45
)


plt.tight_layout()


plt.savefig(
    os.path.join(
        OUTDIR,
        "risk_trend.png"
    ),
    dpi=200
)


plt.close()



# =============================
# RISK DISTRIBUTION
# =============================


print(
    "Creating probability distribution..."
)



plt.figure(
    figsize=(8,5)
)


plt.hist(
    df["risk_probability"],
    bins=30
)


plt.xlabel(
    "Risk Probability"
)


plt.ylabel(
    "Number of Cells"
)


plt.title(
    "Risk Probability Distribution"
)


plt.grid(
    True
)


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
# METEO CORRELATION
# =============================


print(
    "Analysing meteorological correlations..."
)



# possible names from ERA5


meteorological_columns = [

    "risk_probability",

    "temperature",
    "temperature_2m",
    "t2m",

    "humidity",
    "relative_humidity",

    "wind",
    "wind_speed",
    "wind_speed_10m",

    "u10",
    "v10",

    "tp",
    "precipitation"

]



available = [

    c for c in meteorological_columns
    if c in df.columns

]



if len(available) > 1:


    corr = (
        df[available]
        .corr(
            numeric_only=True
        )
    )


    corr.to_csv(
        os.path.join(
            OUTDIR,
            "correlation_matrix.csv"
        )
    )


    # =============================
    # DRAW CORRELATION MATRIX
    # =============================


    fig,ax = plt.subplots(
        figsize=(8,6)
    )


    img = ax.imshow(
        corr
    )


    ax.set_xticks(
        range(len(corr.columns))
    )

    ax.set_xticklabels(
        corr.columns,
        rotation=45,
        ha="right"
    )


    ax.set_yticks(
        range(len(corr.columns))
    )

    ax.set_yticklabels(
        corr.columns
    )


    plt.colorbar(
        img
    )


    plt.title(
        "Meteorological Correlations"
    )


    plt.tight_layout()


    plt.savefig(
        os.path.join(
            OUTDIR,
            "correlation_matrix.png"
        ),
        dpi=200
    )


    plt.close()



else:

    print(
        "No meteorological variables found"
    )





# =============================
# RISK vs TEMPERATURE
# =============================



temp_columns = [

    "temperature",
    "temperature_2m",
    "t2m"

]


temp = None



for c in temp_columns:

    if c in df.columns:

        temp=c
        break




if temp is not None:


    plt.figure(
        figsize=(7,5)
    )


    plt.scatter(
        df[temp],
        df.risk_probability,
        alpha=0.5
    )


    plt.xlabel(
        temp
    )


    plt.ylabel(
        "Risk Probability"
    )


    plt.title(
        "Risk vs Temperature"
    )


    plt.grid(
        True
    )


    plt.tight_layout()


    plt.savefig(
        os.path.join(
            OUTDIR,
            "risk_vs_temperature.png"
        ),
        dpi=200
    )


    plt.close()




# =============================
# SAVE AUTOMATIC DIAGNOSTIC
# =============================


with open(
    os.path.join(
        OUTDIR,
        "diagnostics.txt"
    ),
    "w",
    encoding="utf-8"
) as f:


    f.write(
        "FIRE FORECAST DIAGNOSTICS\n"
    )

    f.write(
        "=========================\n\n"
    )


    if "corr" in locals():

        risk_corr = (
            corr["risk_probability"]
            .sort_values(
                ascending=False
            )
        )


        f.write(
            "Correlation with risk:\n\n"
        )


        f.write(
            str(risk_corr)
        )


    else:

        f.write(
            "Correlation not available\n"
        )



print(
    "\n=============================="
)

print(
    "PART 2 COMPLETED"
)

print(
    "=============================="
)

# =====================================================
# PART 3/4
#
# Geographic Analysis
# Hotspots + Risk Maps
# =====================================================


import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point


GEOJSON = "Sardegna.geojson"


print("\nCreating geographic analysis...")


# =============================
# CREATE GEO DATAFRAME
# =============================


geometry = gpd.points_from_xy(
    df.longitude,
    df.latitude
)


gdf = gpd.GeoDataFrame(
    df,
    geometry=geometry,
    crs="EPSG:4326"
)



# =============================
# HOTSPOTS TOP 20
# =============================


hotspots = (
    gdf.sort_values(
        "risk_probability",
        ascending=False
    )
    .head(20)
)



hotspots_out = hotspots[
    [
        "date",
        "latitude",
        "longitude",
        "risk_probability",
        "risk_class"
    ]
]


hotspots_out.to_csv(
    os.path.join(
        OUTDIR,
        "top20_hotspots.csv"
    ),
    index=False
)


print(
    "Hotspots saved"
)



# =============================
# LOAD SARDINIA
# =============================


sardinia = gpd.read_file(
    GEOJSON
)


sardinia = sardinia.to_crs(
    "EPSG:4326"
)



# =============================
# MEAN RISK MAP
# =============================


mean_points = (
    gdf.groupby(
        [
            "latitude",
            "longitude"
        ]
    )
    .risk_probability
    .mean()
    .reset_index()
)



mean_geometry = gpd.points_from_xy(
    mean_points.longitude,
    mean_points.latitude
)


mean_gdf = gpd.GeoDataFrame(
    mean_points,
    geometry=mean_geometry,
    crs="EPSG:4326"
)



fig,ax = plt.subplots(
    figsize=(10,10)
)



sardinia.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)



mean_gdf.plot(
    ax=ax,
    column="risk_probability",
    cmap="RdYlGn_r",
    markersize=25,
    alpha=0.8,
    legend=True
)



ax.set_title(
    "Average Fire Risk Forecast - Sardinia"
)


ax.axis(
    "off"
)


plt.tight_layout()



plt.savefig(
    os.path.join(
        OUTDIR,
        "mean_risk_map.png"
    ),
    dpi=200
)


plt.close()



print(
    "Mean risk map saved"
)


# =============================
# HOTSPOT SUMMARY TEXT
# =============================


with open(
    os.path.join(
        OUTDIR,
        "hotspot_report.txt"
    ),
    "w",
    encoding="utf-8"
) as f:


    f.write(
        "SARDINIA FIRE RISK HOTSPOTS\n"
    )

    f.write(
        "===========================\n\n"
    )


    for i,row in hotspots.iterrows():

        f.write(
            f"{row['date'].date()} "
            f"LAT={row.latitude:.3f} "
            f"LON={row.longitude:.3f} "
            f"RISK={row.risk_probability:.3f}\n"
        )



print("\n==============================")
print("PART 3 COMPLETED")
print("==============================")

# =====================================================
# PART 4/4
#
# Automatic Fire Forecast Commentary
# Final Report
# =====================================================


print("\nGenerating automatic forecast analysis...")


# =============================
# CLASS ANALYSIS
# =============================


class_counts = (
    df["risk_class"]
    .value_counts()
    if "risk_class" in df.columns
    else None
)



# percentuali

total = len(df)


if class_counts is not None:

    high_pct = (
        class_counts.get("HIGH",0)
        / total * 100
    )

    medium_pct = (
        class_counts.get("MEDIUM",0)
        / total * 100
    )

    low_pct = (
        class_counts.get("LOW",0)
        / total * 100
    )

else:

    high_pct = 0
    medium_pct = 0
    low_pct = 0




# =============================
# RISK LEVEL
# =============================


if overall_mean >= 0.70:

    general_level = "ALTO"

elif overall_mean >= 0.40:

    general_level = "MODERATO"

else:

    general_level = "BASSO"



# =============================
# AUTOMATIC COMMENT
# =============================


comment = f"""

BOLLETTINO AUTOMATICO RISCHIO INCENDI
SARDEGNA

Periodo previsione:
{start_date.date()} - {end_date.date()}


VALUTAZIONE GENERALE:

Il modello prevede un livello di rischio
complessivo:

{general_level}


La probabilità media stimata è:

{overall_mean:.3f}


Il giorno più critico risulta:

{highest.date.date()}

con rischio medio:

{highest.mean_risk:.3f}


Il giorno con rischio minimo risulta:

{lowest.date.date()}

con rischio medio:

{lowest.mean_risk:.3f}



DISTRIBUZIONE DEL RISCHIO:

HIGH:
{high_pct:.1f} %

MEDIUM:
{medium_pct:.1f} %

LOW:
{low_pct:.1f} %



EVOLUZIONE TEMPORALE:

Il trend generale del rischio è:

{trend}



INTERPRETAZIONE:

La previsione mostra una variazione
spazio-temporale del rischio incendio.

Le aree classificate HIGH rappresentano
le zone dove le condizioni ambientali
risultano più favorevoli alla possibile
propagazione del fuoco.


Nota:

Il modello rappresenta una probabilità
di rischio e non una previsione certa
di incendio.


"""



with open(
    os.path.join(
        OUTDIR,
        "ai_commentary.txt"
    ),
    "w",
    encoding="utf-8"
) as f:

    f.write(comment)




# =============================
# FINAL TECHNICAL REPORT
# =============================


with open(
    os.path.join(
        OUTDIR,
        "final_report.txt"
    ),
    "w",
    encoding="utf-8"
) as f:


    f.write(
        "====================================\n"
    )

    f.write(
        "FIRE FORECAST ASSESSMENT REPORT\n"
    )

    f.write(
        "====================================\n\n"
    )


    f.write(
        comment
    )


    f.write(
        "\n\nOUTPUT FILES:\n\n"
    )


    f.write(
        "- daily_summary.csv\n"
    )

    f.write(
        "- risk_trend.png\n"
    )

    f.write(
        "- risk_distribution.png\n"
    )

    f.write(
        "- mean_risk_map.png\n"
    )

    f.write(
        "- top20_hotspots.csv\n"
    )



print(
    "\n================================="
)

print(
    "ALL ANALYSIS COMPLETED"
)

print(
    "================================="
)

print(
    "Check folder:",
    OUTDIR
)
