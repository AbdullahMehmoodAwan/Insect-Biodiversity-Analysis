# Insect Biodiversity Analysis

Tracks population counts for six indicator insect species across a full observation season (September 2024 to April 2025) at Namadgi National Park, ACT. The goal is to understand seasonal dynamics, detect environmental drivers, and flag conservation concerns for threatened species.

---

## Species Studied

| Species | Conservation Status | Notes |
|---|---|---|
| Bogong Moth | **Endangered** (EPBC Act 2021) | Migratory; aestivates in alpine zones during summer |
| Mountain Grasshopper | Near Threatened | Sensitive to alpine habitat degradation |
| Alpine Jewel Beetle | Data Deficient | Limited survey data; baseline tracking needed |
| Blue Ant Wasp | Least Concern | Velvet ant; active in warmer months |
| Golden Stag Beetle | Least Concern | Summer active; found in eucalypt woodland |
| Crimson Cicada | Least Concern | Seasonal abundance tied closely to temperature |

The Bogong Moth (*Agrotis infusa*) is of particular interest. It is listed as Endangered under the Environment Protection and Biodiversity Conservation (EPBC) Act following steep population declines attributed to drought, climate-driven disruption of migratory cues, and reduced alpine food availability.

---

## Data

### File: `insect_data.csv`

300 records across 50 observation dates. Sampling is weekly from September through January and April, and daily during the February 2025 intensive window.

| Column | Description |
|---|---|
| `Date` | Observation date (YYYY-MM-DD) |
| `Location` | Survey site (Namadgi NP ACT) |
| `Species` | Common species name |
| `Count` | Number of individuals recorded on a standardised transect |
| `Temp_C` | Air temperature at time of observation (degrees Celsius) |
| `Rainfall_7day_mm` | Cumulative rainfall in the 7 days prior to observation (mm) |

---

## Analysis Pipeline (`main.py`)

### 1. Load and reshape

The CSV is loaded into a long-format DataFrame, then pivoted to a wide matrix where each row is an observation date and each column is a species. Environmental variables are averaged per date. Missing values are dropped before any calculation.

### 2. Shannon Diversity Index

Computed for every observation date using:

```
H' = -sum( p_i * ln(p_i) )
```

where `p_i` is the proportion of total count contributed by species `i`. Higher H' means counts are more evenly spread across species. A drop in H' can indicate dominance by one or two species, which is often a sign of ecosystem stress.

### 3. Linear trend analysis

A simple linear regression (`scipy.stats.linregress`) is fitted per species across all 50 observation dates. Slope, R-squared, and p-value are printed to the console. Because sampling covers a full seasonal arc (rising spring counts then declining autumn counts), a positive slope indicates the dataset is weighted toward the ascending phase.

### 4. Environmental correlations

Pearson correlation coefficients are calculated between total daily count and (a) temperature and (b) 7-day prior rainfall. Since these are ectotherms, a strong positive correlation with temperature is expected. Rainfall correlation is typically negative in this dataset because the wet autumn months correspond with low insect activity.

### 5. Visualisations

The script saves a 3-row, 2-column figure (`biodiversity_analysis.png`) with the following panels:

- **Row 1 (full width):** Population counts over the full season. The February daily observation window is shaded. One line per species.
- **Row 2 left:** Shannon diversity index over time, filled area below curve.
- **Row 2 right:** Scatter plot of temperature vs total count, with a linear regression line and Pearson r shown.
- **Row 3 left:** Grouped bar chart of monthly average counts per species.
- **Row 3 right:** Proportional abundance lines showing how each species' share of total count changes through the season.

---

## Setup

```bash
pip install pandas numpy matplotlib scipy seaborn
```

## Run

```bash
python main.py
```

Console output includes the trend table and correlation results. The plot is displayed interactively and also saved to `biodiversity_analysis.png`.

---

## Interactive Demo

Open `index.html` in any modern browser (no server required). It plays through the full observation season in real time, updating charts, diversity stats, and species cards as each data point is "received." Designed as a quick visual overview of what the project tracks.

---

## Data Sources and References

- Field observation protocol adapted from standard transect survey guidelines used in ACT Parks and Conservation surveys.
- Conservation status from the EPBC Act species list and IUCN Red List.
- Bogong Moth population decline documented in: Warrant et al. (2016), *Current Biology*; DCCEEW EPBC listing documentation (2021).
- Climate reference data: Bureau of Meteorology station records for the Namadgi/Tidbinbilla region.
- Atlas of Living Australia (ala.org.au): species occurrence records used for distribution context.
