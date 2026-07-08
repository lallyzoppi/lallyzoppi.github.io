import os
import glob
import zipfile

extract_root = "ERA5_extracted"
os.makedirs(extract_root, exist_ok=True)

files = sorted(glob.glob("ERA5_Sardegna_*.nc"))

for f in files:

    year = f.split("_")[-1].replace(".nc", "")

    out_dir = os.path.join(extract_root, year)

    os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(f, "r") as z:
        z.extractall(out_dir)

    print("OK:", year)
