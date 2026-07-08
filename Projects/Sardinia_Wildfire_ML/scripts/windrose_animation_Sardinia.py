import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import subprocess

from windrose import WindroseAxes


# ==========================
# FILE
# ==========================

nc_file = (
    "/Users/lauz/Desktop/VENTO/wind_sardinia/output/"
    "wind_analysis_2026.nc"
)

sardegna_file = (
    "/Users/lauz/Desktop/Sardegna.Geojson"
)

out_dir = (
    "/Users/lauz/Desktop/VENTO/"
    "wind_sardinia/output/windrose_frames"
)

os.makedirs(out_dir, exist_ok=True)


mp4_file = os.path.join(
    out_dir,
    "sardinia_windrose_2026.mp4"
)



# ==========================
# DIREZIONE
# ==========================

def nome_vento(deg):

    deg = deg % 360

    if deg >= 337.5 or deg < 22.5:
        return "Tramontana"

    elif deg < 67.5:
        return "Grecale"

    elif deg < 112.5:
        return "Levante"

    elif deg < 157.5:
        return "Scirocco"

    elif deg < 202.5:
        return "Ostro"

    elif deg < 247.5:
        return "Libeccio"

    elif deg < 292.5:
        return "Ponente"

    else:
        return "Maestrale"



# ==========================
# LOAD
# ==========================

print("Apro NetCDF...")

ds = xr.open_dataset(nc_file)

speed = ds["wind_speed"]
direction = ds["wind_direction"]



# ==========================
# SARDEGNA
# ==========================

sardegna = gpd.read_file(
    sardegna_file
)

sardegna = sardegna.to_crs(
    "EPSG:4326"
)



# ==========================
# CITTA'
# ==========================

locations = {

"Alghero": (40.58,8.55),
"Sassari": (40.75,8.62),
"Olbia": (40.82,9.32),
"Nuoro": (40.32,9.33),
"Oristano": (39.90,8.60),
"Arbatax": (39.92,9.55),
"Iglesias": (39.31,8.54),
"Cagliari": (39.22,9.12),
"Villasimius": (39.14,9.42)

}



# spostamento grafico
offsets = {

"Alghero":(-0.10,-0.05),
"Sassari":(0.12,0.10),

"Olbia":(0.05,0.04),
"Nuoro":(0,0),

"Oristano":(-0.05,0),
"Arbatax":(0.04,0),

"Iglesias":(-0.04,-0.04),
"Cagliari":(0,-0.05),
"Villasimius":(0.05,-0.03)

}


rose_size = 0.115



months = [
"2026-01",
"2026-02",
"2026-03",
"2026-04",
"2026-05",
"2026-06"
]



# ==========================
# FRAME
# ==========================

for i,month in enumerate(months):

    print("Creo",month)


    sp_month = speed.sel(
        valid_time=month
    )


    dr_month = direction.sel(
        valid_time=month
    )


    mean_speed = sp_month.mean(
        dim="valid_time"
    )


    fig,ax = plt.subplots(
        figsize=(10,12)
    )



    mean_speed.plot(
        ax=ax,
        cmap="turbo",
        cbar_kwargs={
            "label":"Mean wind speed (m/s)"
        }
    )


    sardegna.boundary.plot(
        ax=ax,
        color="black",
        linewidth=1.5
    )


    ax.set_xlim(
        7.9,
        10.15
    )

    ax.set_ylim(
        38.6,
        41.45
    )



    ax.set_title(
        "Sardinia Wind Roses + Mean Wind Speed\n"
        + month,

        fontsize=20,
        pad=20,
        fontweight="bold"
    )



    bbox = ax.get_position()



    # ==========================
    # WIND ROSE
    # ==========================

    for name,(lat,lon) in locations.items():


        sp = sp_month.sel(
            latitude=lat,
            longitude=lon,
            method="nearest"
        ).values.flatten()


        dr = dr_month.sel(
            latitude=lat,
            longitude=lon,
            method="nearest"
        ).values.flatten()



        mask = (
            np.isfinite(sp)
            &
            np.isfinite(dr)
        )

        sp = sp[mask]
        dr = dr[mask]



        dx,dy = offsets[name]


        x = bbox.x0 + (
            lon + dx - 7.9
        )/(10.15-7.9) * bbox.width


        y = bbox.y0 + (
            lat + dy - 38.6
        )/(41.45-38.6) * bbox.height



        rose_ax = fig.add_axes(
            [
                x-rose_size/2,
                y-rose_size/2,
                rose_size,
                rose_size
            ],
            projection="windrose"
        )



        rose_ax.bar(
            dr,
            sp,
            normed=True,
            opening=0.8,
            edgecolor="white",
            bins=[0,2,4,6,8,10,15]
        )


        rose_ax.set_xticks([])
        rose_ax.set_yticks([])



        vento = nome_vento(
            np.mean(dr)
        )

        vel = np.mean(sp)



        rose_ax.set_title(
            f"{name}\n"
            f"{vento}\n"
            f"{vel:.1f} m/s",

            fontsize=9,
            pad=3,
            fontweight="bold"
        )



    # ==========================
    # LEGENDA
    # ==========================

    fig.text(

        0.78,
        0.78,

        "WIND ROSE\n\n"
        "N  Tramontana\n"
        "NE Grecale\n"
        "E  Levante\n"
        "SE Scirocco\n"
        "S  Ostro\n"
        "SW Libeccio\n"
        "W  Ponente\n"
        "NW Maestrale\n\n"
        "Length = frequency\n"
        "Color = speed",

        fontsize=10,

        bbox=dict(
            facecolor="white",
            alpha=0.85
        )
    )



    outfile = os.path.join(
        out_dir,
        f"month_{i+1:02d}.png"
    )


    plt.savefig(
        outfile,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.2
    )


    plt.close()



# ==========================
# MP4
# ==========================

print("Creo MP4...")


subprocess.run(
[
"ffmpeg",
"-y",
"-framerate",
"1",
"-i",
os.path.join(out_dir,"month_%02d.png"),

"-vf",
"scale=trunc(iw/2)*2:trunc(ih/2)*2",

"-c:v",
"libx264",
"-pix_fmt",
"yuv420p",

mp4_file
]
)


print("===================")
print("FINITO")
print(mp4_file)
print("===================")
