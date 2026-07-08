# =====================================================
# ERA5 SARDEGNA - DOWNLOAD ANNO PER ANNO
# 2002–2025
# VENTO + TEMPERATURA + PRECIPITAZIONE
# =====================================================

import cdsapi
import os

# =====================================================
# CARTELLA OUTPUT
# =====================================================

cartella = "/Users/lauz/Desktop/VENTO/wind_sardinia/data"
os.makedirs(cartella, exist_ok=True)

client = cdsapi.Client()

# =====================================================
# LOOP ANNI
# =====================================================

for anno in range(2002, 2026):

    print("==============================")
    print("SCARICO ANNO:", anno)
    print("==============================")

    output_file = os.path.join(
        cartella,
        f"ERA5_Sardegna_{anno}.nc"
    )

    client.retrieve(

        "reanalysis-era5-single-levels",

        {

            "product_type": "reanalysis",

            "variable": [

                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "2m_temperature",
                "total_precipitation"

            ],

            "year": str(anno),

            "month": [
                "01","02","03","04","05","06",
                "07","08","09","10","11","12"
            ],

            "day": [
                "01","02","03","04","05",
                "06","07","08","09","10",
                "11","12","13","14","15",
                "16","17","18","19","20",
                "21","22","23","24","25",
                "26","27","28","29","30","31"
            ],

            "time": [
                "00:00",
                "06:00",
                "12:00",
                "18:00"
            ],

            "area": [
                41.5,
                8.0,
                38.8,
                10.0
            ],

            "data_format": "netcdf"

        },

        output_file

    )

    print("COMPLETATO ANNO:", anno)

print("==============================")
print("DOWNLOAD COMPLETO 2002–2025")
print("==============================")
