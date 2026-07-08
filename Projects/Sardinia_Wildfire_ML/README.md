# Sardinia Wildfire Risk Assessment Using Machine Learning

## Overview

This project investigates the relationship between environmental conditions and wildfire occurrence in Sardinia using machine learning techniques.

The analysis combines meteorological data from the ERA5 reanalysis dataset, satellite-based fire observations from NASA MODIS FIRMS, and geospatial information to identify patterns associated with wildfire risk.

The primary objective is to develop machine learning models capable of characterizing the environmental conditions associated with wildfire events and generating wildfire risk indicators.

---

## Data Sources

The study integrates three primary data sources.

### Meteorological Data

#### ERA5 Reanalysis Dataset

**Source:**

https://cds.climate.copernicus.eu/

ERA5 provides atmospheric variables describing weather conditions, including:

* air temperature (`t2m`)
* total precipitation (`tp`)
* eastward wind component at 10 m (`u10`)
* northward wind component at 10 m (`v10`)

The original ERA5 data are processed and transformed into analysis-ready variables suitable for machine learning applications.

---

### Satellite Fire Observations

#### NASA FIRMS – Fire Information for Resource Management System

**Source:**

https://firms.modaps.eosdis.nasa.gov/

NASA MODIS FIRMS provides satellite-derived thermal anomaly (hotspot) detections, which are used as indicators of potential wildfire activity.

A thermal anomaly does not necessarily correspond to a confirmed wildfire and should always be interpreted together with meteorological and environmental conditions.

---

### Geospatial Data

A GeoJSON boundary layer representing the island of Sardinia is used for:

* spatial visualization;
* geographic filtering;
* wildfire risk mapping.

---

## Data Processing Workflow

The original datasets are not directly used for model training.

The processing workflow includes:

1. Extraction of the original datasets;
2. Selection of the Sardinia study area;
3. Data cleaning and quality control;
4. Spatial and temporal integration of the datasets;
5. Construction of the final machine learning dataset.

The resulting dataset,

`SARDINIA_FIRE_ML.csv`

contains the integrated meteorological, satellite-derived, and spatial variables used for model development.

---

## Machine Learning Workflow

The project includes the following stages:

* exploratory data analysis;
* feature engineering;
* model training;
* model evaluation;
* wildfire risk prediction;
* spatial visualization of wildfire risk.

The analysis is implemented in Python using:

* pandas
* numpy
* xarray
* geopandas
* shapely
* scikit-learn
* LightGBM
* matplotlib

---

## Analysis Pipeline

```
ERA5 meteorological data
            │
            ▼
Data preprocessing
            │
            ▼
MODIS FIRMS fire observations
            │
            ▼
Spatial and temporal integration
            │
            ▼
SARDINIA_FIRE_ML.csv
            │
            ▼
Machine Learning models
            │
            ▼
Wildfire risk prediction
            │
            ▼
Wildfire risk maps
            │
            ▼
Validation reports
```

---

## Repository Structure

```text
Sardinia-Wildfire-ML/

├── README.md
├── index.html
├── requirements.txt
│
├── data/
│   ├── SARDINIA_FIRE_ML.csv
│   ├── Sardegna.geojson
│   └── README.md
│
├── scripts/
│   ├── 01_train_fire_model_v5.py
│   ├── 02_Forecast_Fire_14D.py
│   ├── 03_make_Sardinia_Risk_MapV2.py
│   ├── 04_validation_report.py
│   └── 05_AI_Forecast_Analysis.py
│
├── results/
│   ├── figures/
│   
│
---

## Reproducibility

The repository contains the complete analysis workflow, machine learning scripts, and project documentation.

The original ERA5 and MODIS datasets are not redistributed and must be downloaded from their respective official providers.

To install the required Python packages:

```bash
conda create -n windmap python=3.12
pip install -r requirements.txt
```

---

## License

This project is intended exclusively for research and educational purposes.

