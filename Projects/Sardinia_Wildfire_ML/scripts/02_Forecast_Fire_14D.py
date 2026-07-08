# =====================================================
# 02_forecast_fire_14days.py
#
# Forecast rischio incendio Sardegna 14 giorni
# =====================================================

import pandas as pd
import numpy as np
import requests
import joblib
import time


# =============================
# FILE
# =============================

GRID_FILE = "SARDINIA_GRID.csv"
MODEL_FILE = "SARDINIA_FIRE_NEXT14_MODEL_FINAL.pkl"
OUTPUT = "SARDINIA_FIRE_FORECAST_14D.csv"


# =============================
# LOAD MODELLO
# =============================

bundle = joblib.load(MODEL_FILE)

model = bundle["model"]
FEATURES = bundle["features"]
THRESHOLD = bundle["threshold"]

print("MODELLO CARICATO")
print("Threshold:", THRESHOLD)


# =============================
# GRIGLIA
# =============================

grid = pd.read_csv(GRID_FILE)

rows = []

print("Punti griglia:", len(grid))


# =============================
# DOWNLOAD METEO
# =============================

for i, r in grid.iterrows():

    lat = r["latitude"]
    lon = r["longitude"]

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}"
        f"&longitude={lon}"
        "&forecast_days=14"
        "&daily="
        "temperature_2m_mean,"
        "wind_speed_10m_mean,"
        "precipitation_sum"
    )

    try:

        data = requests.get(
            url,
            timeout=20
        ).json()


        for j, d in enumerate(data["daily"]["time"]):

            rows.append(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "date": d,
                    "t2m": data["daily"]["temperature_2m_mean"][j],
                    "wind_speed": data["daily"]["wind_speed_10m_mean"][j],
                    "tp": data["daily"]["precipitation_sum"][j]
                }
            )


    except Exception as e:

        print(
            "Errore:",
            lat,
            lon,
            e
        )


    if i % 50 == 0:
        print("processati:", i)

    time.sleep(0.2)



df = pd.DataFrame(rows)


print(
    "Forecast scaricato:",
    df.shape
)


# =============================
# FEATURE ENGINEERING
# =============================


df["date"] = pd.to_datetime(df["date"])


df["month"] = df["date"].dt.month


df["month_sin"] = np.sin(
    2*np.pi*df["month"]/12
)

df["month_cos"] = np.cos(
    2*np.pi*df["month"]/12
)



# =============================
# SECCHEZZA
# =============================

df["vpd"] = df["t2m"] / 10


df["dryness"] = (
    df["vpd"] *
    (df["wind_speed"] + 1)
)



# vento

df["u10"] = 0

df["v10"] = -df["wind_speed"]



# =============================
# ORDINA
# =============================

df = df.sort_values(
    [
        "latitude",
        "longitude",
        "date"
    ]
)



# =============================
# LAG
# =============================

for lag in [1,3,7]:

    df[f"wind_lag_{lag}"] = (
        df.groupby(
            [
                "latitude",
                "longitude"
            ]
        )["wind_speed"]
        .shift(lag)
    )


    df[f"temp_lag_{lag}"] = (
        df.groupby(
            [
                "latitude",
                "longitude"
            ]
        )["t2m"]
        .shift(lag)
    )



# =============================
# PIOGGIA
# =============================

df["rain_7d"] = 0
df["rain_14d"] = 0
df["rain_30d"] = 0



# =============================
# DRY DAYS (FIX)
# =============================

df["dry_days"] = (
    df["tp"]
    .fillna(0)
    .eq(0)
    .astype(int)
    .groupby(
        df["tp"]
        .fillna(0)
        .ne(0)
        .cumsum()
    )
    .cumsum()
)



df = df.fillna(0)



# =============================
# CHECK
# =============================

missing = set(FEATURES) - set(df.columns)

if missing:

    raise Exception(
        f"Feature mancanti: {missing}"
    )



print("FEATURE OK")



# =============================
# PREDIZIONE
# =============================

df["risk_probability"] = (
    model.predict_proba(
        df[FEATURES]
    )[:,1]
)



df["risk_class"] = np.where(
    df["risk_probability"] >= 0.85,
    "HIGH",
    np.where(
        df["risk_probability"] >= 0.60,
        "MEDIUM",
        "LOW"
    )
)



# =============================
# OUTPUT
# =============================

df = df.sort_values(
    [
        "date",
        "latitude",
        "longitude"
    ]
)



df.to_csv(
    OUTPUT,
    index=False
)



print("==============================")
print("CREATO:")
print(OUTPUT)
print("==============================")


print(
    df["risk_class"]
    .value_counts()
)


print("FINE FORECAST")
