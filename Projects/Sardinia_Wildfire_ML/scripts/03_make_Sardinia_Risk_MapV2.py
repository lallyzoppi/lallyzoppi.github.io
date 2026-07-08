# =====================================================
# 03_make_Sardinia_Risk_MapV2_3.py
#
# Sardinia Wildfire Risk Animation
#
# Color scheme:
# BLUE -> GREEN -> YELLOW -> ORANGE -> RED
# =====================================================


import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from scipy.spatial import cKDTree
from shapely.vectorized import contains
import imageio.v2 as imageio



# =============================
# FILES
# =============================

FORECAST = "SARDINIA_FIRE_FORECAST_14D.csv"

GEOJSON = "Sardegna.geojson"

OUTDIR = "maps"

MP4FILE = "SARDINIA_FIRE_RISK_14D.mp4"



os.makedirs(
    OUTDIR,
    exist_ok=True
)



# =============================
# LOAD DATA
# =============================


df = pd.read_csv(
    FORECAST
)


df["date"] = pd.to_datetime(
    df["date"]
)



sardinia = gpd.read_file(
    GEOJSON
)


sardinia = sardinia.to_crs(
    "EPSG:4326"
)



print(
    "Forecast:",
    df.shape
)





# =============================
# GRID
# =============================


minx,miny,maxx,maxy = sardinia.total_bounds


RES = 0.008



lon = np.arange(
    minx,
    maxx,
    RES
)


lat = np.arange(
    miny,
    maxy,
    RES
)



GX,GY = np.meshgrid(
    lon,
    lat
)






# =============================
# MASK
# =============================


island_shape = sardinia.geometry.unary_union


mask = contains(
    island_shape,
    GX,
    GY
)






# =============================
# INIT
# =============================


rng = np.random.default_rng(123)


frames = []


previous_grid = None


dates = sorted(
    df["date"].unique()
)








# =============================
# CREATE MAPS
# =============================


for i,day in enumerate(dates):


    print(
        "Creating day:",
        day
    )



    daily = df[
        df.date == day
    ]



    points = np.column_stack(
        (
            daily.longitude,
            daily.latitude
        )
    )


    values = daily.risk_probability.values






    # =============================
    # LOCAL HOTSPOT INTERPOLATION
    # =============================


    tree = cKDTree(
        points
    )


    query = np.column_stack(
        (
            GX.ravel(),
            GY.ravel()
        )
    )


    dist,idx = tree.query(
        query,
        k=3
    )



    weights = 1/(dist**2 + 0.001)



    grid = (
        values[idx] * weights
    ).sum(axis=1) / weights.sum(axis=1)



    grid = grid.reshape(
        GX.shape
    )






    # =============================
    # TEMPORAL CONTINUITY
    # =============================


    grid += rng.normal(
        0,
        0.008,
        grid.shape
    )



    if previous_grid is not None:

        grid = (
            0.75 * grid
            +
            0.25 * previous_grid
        )



    previous_grid = grid.copy()



    grid = np.clip(
        grid,
        0,
        1
    )


    grid[~mask] = np.nan







    # =============================
    # PLOT
    # =============================


    fig,ax = plt.subplots(
        figsize=(8,10),
        dpi=200
    )



    img = ax.imshow(

        grid,

        extent=[
            minx,
            maxx,
            miny,
            maxy
        ],

        origin="lower",

        # BLUE-GREEN-YELLOW-ORANGE-RED
        cmap="turbo",

        vmin=np.nanpercentile(
            grid,
            5
        ),

        vmax=np.nanpercentile(
            grid,
            95
        )
    )





    sardinia.boundary.plot(
        ax=ax,
        color="black",
        linewidth=1
    )





    ax.set_title(
        f"Sardinia Wildfire Risk\n{pd.to_datetime(day).date()}",
        fontsize=15
    )



    ax.axis("off")






    plt.colorbar(
        img,
        ax=ax,
        label="Fire Risk Probability"
    )






    outfile = (
        f"{OUTDIR}/risk_day_{i+1:02d}.png"
    )



    plt.savefig(
        outfile,
        dpi=200
    )


    plt.close()





    frames.append(
        imageio.imread(
            outfile
        )
    )








# =============================
# CREATE MP4
# =============================


print(
    "Creating video..."
)



writer = imageio.get_writer(

    MP4FILE,

    fps=2,

    codec="libx264",

    macro_block_size=16

)



for frame in frames:

    writer.append_data(
        frame
    )



writer.close()



print("===================")

print("DONE")

print(
    "Maps:",
    OUTDIR
)

print(
    "Video:",
    MP4FILE
)
