import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("../data/processed/wind.csv")
df["Stazione"] = df["Stazione"].str.strip()

coords = {
    "San Teodoro RU": (40.77, 9.67),
    "Cagliari Molentargius": (39.22, 9.12),
    "Santa Teresa Di Gallura RU": (41.24, 9.19),
    "Narcao Monte Rosas": (39.17, 8.68),
    "Arbus Ingurtosu": (39.53, 8.46),
    "Luras RU": (40.93, 9.18),
    "Stintino RU": (40.94, 8.22),
    "Bosa RU": (40.29, 8.50),
    "Pattada": (40.58, 9.11),
    "Sadali": (39.82, 9.28),
    "Fonni": (40.12, 9.25),
    "Perdasdefogu RU": (39.68, 9.44),
    "Macomer RU": (40.26, 8.78),
    "Bitti RU": (40.48, 9.38),
    "Masainas RU": (39.53, 8.62),
    "Meana Sardo": (39.94, 9.07),
    "Domus De Maria": (38.94, 8.83),
    "Seui RU": (39.85, 9.32),
    "Orgosolo Monte Novo": (40.20, 9.35),
    "Santu Lussurgiu Badde Urbara": (40.14, 8.66),
    "Tempio Limbara": (40.90, 9.10),
    "Desulo Perdu Abes": (40.02, 9.22),
    "Santadi Punta Sebera": (39.09, 8.64),
    "Iglesias San Michele": (39.31, 8.54)
}

df["lat"] = df["Stazione"].map(lambda x: coords[x][0])
df["lon"] = df["Stazione"].map(lambda x: coords[x][1])

# =========================
# DATA
# =========================
lon = df["lon"].values
lat = df["lat"].values
wind = df["Vento_medio_ms"].values

lon_grid = np.linspace(8.0, 10.5, 300)
lat_grid = np.linspace(38.5, 41.5, 300)

lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

grid = griddata((lon, lat), wind, (lon_mesh, lat_mesh), method="linear")

# =========================
# MAP
# =========================
fig = plt.figure(figsize=(10, 12))
ax = plt.axes(projection=ccrs.PlateCarree())

ax.set_extent([8.0, 10.5, 38.5, 41.5])

ax.add_feature(cfeature.COASTLINE, linewidth=1)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.LAND, alpha=0.3)
ax.add_feature(cfeature.OCEAN, alpha=0.2)

c = ax.contourf(
    lon_mesh,
    lat_mesh,
    grid,
    levels=25,
    cmap="turbo",
    alpha=0.85,
    transform=ccrs.PlateCarree()
)

plt.colorbar(c, label="Mean Wind Speed (m/s)", shrink=0.7)

# =========================
# STATIONS
# =========================
ax.scatter(
    lon,
    lat,
    color="black",
    s=40,
    edgecolors="white",
    linewidth=0.5,
    transform=ccrs.PlateCarree(),
    zorder=10
)

# =========================
# LABELS (FORZATI + VISIBILI)
# =========================
highlight = {
    "Iglesias San Michele",
    "Santadi Punta Sebera"
}

for _, r in df.iterrows():

    is_highlight = r["Stazione"] in highlight

    ax.text(
        r["lon"],
        r["lat"],
        r["Stazione"],
        fontsize=10 if is_highlight else 7,
        fontweight="bold" if is_highlight else "normal",
        color="red" if is_highlight else "black",
        bbox=dict(
            facecolor="white",
            alpha=0.8,
            edgecolor="none",
            pad=1
        ),
        transform=ccrs.PlateCarree(),
        zorder=20
    )

# =========================
# TITLE
# =========================
plt.title("Cyclone Harry – Wind Field over Sardinia")

# =========================
# SAVE
# =========================
plt.savefig(
    "../figures/wind_field_sardinia.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
