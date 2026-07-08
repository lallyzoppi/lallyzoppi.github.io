import os
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import rioxarray
import numpy as np
import pandas as pd



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

output_mp4 = (
    "/Users/lauz/Desktop/VENTO/"
    "wind_direction_animation_2026.mp4"
)



# ==========================
# APERTURA NETCDF
# ==========================

print("Apro NetCDF...")


ds = xr.open_dataset(nc_file)


wind = ds["mean_wind"]

direction = ds["wind_direction"]



# ==========================
# SISTEMA LATITUDINE
# ==========================

print("Ordino latitudine...")


wind = wind.sortby("latitude")

direction = direction.sortby("latitude")



# ==========================
# CRS
# ==========================

wind = wind.rio.set_spatial_dims(
    x_dim="longitude",
    y_dim="latitude"
)

wind = wind.rio.write_crs(
    "EPSG:4326"
)



direction = direction.rio.set_spatial_dims(
    x_dim="longitude",
    y_dim="latitude"
)

direction = direction.rio.write_crs(
    "EPSG:4326"
)



# ==========================
# SARDEGNA
# ==========================

print("Carico Sardegna...")


sardegna = gpd.read_file(
    sardegna_file
)


sardegna = sardegna.to_crs(
    "EPSG:4326"
)



# ==========================
# CLIP
# ==========================

print("Ritaglio Sardegna...")


wind = wind.rio.clip(
    sardegna.geometry,
    sardegna.crs,
    drop=True
)


direction = direction.rio.clip(
    sardegna.geometry,
    sardegna.crs,
    drop=True
)



# ==========================
# FIGURA
# ==========================

fig, ax = plt.subplots(
    figsize=(10,10)
)



# ==========================
# COLORBAR
# ==========================

cax = fig.add_axes(
    [0.88,0.2,0.03,0.6]
)


sm = plt.cm.ScalarMappable(
    cmap="turbo",
    norm=plt.Normalize(0,20)
)


fig.colorbar(
    sm,
    cax=cax,
    label="Mean wind speed (m/s)"
)



# ==========================
# ANIMAZIONE
# ==========================

def update(frame):

    ax.clear()


    print(
        f"Frame {frame+1}/{len(direction.valid_time)}"
    )


    # vento medio fisso
    w = wind


    # direzione variabile
    d = direction.isel(
        valid_time=frame
    )


    # elimina eventuali NaN
    d = d.fillna(0)



    # ======================
    # SFONDO
    # ======================

    w.plot(
        ax=ax,
        cmap="turbo",
        vmin=0,
        vmax=20,
        add_colorbar=False
    )



    # ======================
    # BORDO SARDEGNA
    # ======================

    sardegna.boundary.plot(
        ax=ax,
        color="black",
        linewidth=1.3
    )



    # ======================
    # DIREZIONE VENTO
    # ======================

    rad = np.deg2rad(
        d.values
    )


    u_arrow = np.sin(rad)

    v_arrow = np.cos(rad)



    step = 2



    ax.quiver(
        d.longitude.values[::step],
        d.latitude.values[::step],
        u_arrow[::step,::step],
        v_arrow[::step,::step],
        scale=35,
        width=0.004
    )



    # ======================
    # STREAMLINES
    # ======================

    ax.streamplot(
        d.longitude.values,
        d.latitude.values,
        u_arrow,
        v_arrow,
        density=1,
        linewidth=0.6
    )



    # ======================
    # TITOLO
    # ======================

    t = pd.to_datetime(
        d.valid_time.values
    )


    ax.set_title(
        t.strftime(
            "%d/%m/%Y %H:%M UTC\n"
            "Mean wind speed + direction"
        ),
        fontsize=14,
        weight="bold"
    )


    ax.set_xlabel(
        "Longitude"
    )

    ax.set_ylabel(
        "Latitude"
    )


    return ax



# ==========================
# CREA ANIMAZIONE
# ==========================

print("Creo animazione...")


ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(direction.valid_time),
    interval=200
)



# ==========================
# SALVATAGGIO MP4
# ==========================

print("Salvo MP4...")


writer = animation.FFMpegWriter(
    fps=15,
    bitrate=5000
)


ani.save(
    output_mp4,
    writer=writer,
    dpi=300
)



# ==========================
# CONTROLLO
# ==========================

print("")
print("========================")
print("CONTROLLO FILE")
print(output_mp4)


if os.path.exists(output_mp4):

    size = os.path.getsize(output_mp4)

    print("VIDEO CREATO!")
    print(
        "Dimensione MB:",
        round(size/1024/1024,2)
    )

else:

    print("ERRORE: MP4 NON CREATO")


print("========================")
