import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats

# -------------------------------------------
# Load data
# -------------------------------------------
df = pd.read_csv("insect_data.csv")
df["Date"] = pd.to_datetime(df["Date"])
df.dropna(inplace=True)
df = df.sort_values(["Date", "Species"]).reset_index(drop=True)

# Pivot to wide format: rows = observation dates, columns = species
species_counts = df.groupby(["Date", "Species"])["Count"].sum().unstack()

# Environmental variables averaged per date
env = df.groupby("Date")[["Temp_C", "Rainfall_7day_mm"]].mean()

# -------------------------------------------
# Shannon diversity index per observation date
# H' = -sum(p_i * ln(p_i))
# Higher values = more even distribution across species
# -------------------------------------------
def shannon_index(row):
    counts = row.dropna()
    total = counts.sum()
    if total == 0:
        return np.nan
    p = counts / total
    p = p[p > 0]
    return -(p * np.log(p)).sum()

diversity = species_counts.apply(shannon_index, axis=1)

# -------------------------------------------
# Conservation status for each species
# Sources: EPBC Act 1999, IUCN Red List
# -------------------------------------------
conservation_status = {
    "Alpine Jewel Beetle":   "Data Deficient",
    "Blue Ant Wasp":         "Least Concern",
    "Bogong Moth":           "Endangered",      # EPBC Act listed 2021
    "Crimson Cicada":        "Least Concern",
    "Golden Stag Beetle":    "Least Concern",
    "Mountain Grasshopper":  "Near Threatened",
}

# -------------------------------------------
# Summary header
# -------------------------------------------
print(f"\n{'='*65}")
print("Insect Biodiversity Analysis  |  Namadgi NP, ACT")
print(f"{'='*65}")
print(f"Period:    {df['Date'].min().strftime('%d %b %Y')} to {df['Date'].max().strftime('%d %b %Y')}")
print(f"Dates:     {df['Date'].nunique()}  |  Species: {df['Species'].nunique()}  |  Records: {len(df)}")

# -------------------------------------------
# Species trend analysis using linear regression
# Note: data covers a full seasonal arc (spring through autumn),
# so a positive slope means the ascending phase dominates the dataset.
# -------------------------------------------
print(f"\nSpecies Trend Analysis (linear regression, full season):")
print(f"{'-'*65}")

x = np.arange(len(species_counts))
for species in species_counts.columns:
    y = species_counts[species].values
    mask = ~np.isnan(y)
    slope, intercept, r, p_val, se = stats.linregress(x[mask], y[mask])
    status = conservation_status.get(species, "Unknown")
    direction = "rising" if slope > 0 else "declining"
    print(
        f"  {species:<25} slope={slope:+.2f}  R2={r**2:.3f}  p={p_val:.4f}  "
        f"[{status}]  ({direction})"
    )

# -------------------------------------------
# Environmental correlations
# -------------------------------------------
total_by_date = species_counts.sum(axis=1)
common_idx = env.index.intersection(total_by_date.index)
env_sub = env.loc[common_idx]
cnt_sub = total_by_date.loc[common_idx]

r_temp, p_temp = stats.pearsonr(env_sub["Temp_C"], cnt_sub)
r_rain, p_rain = stats.pearsonr(env_sub["Rainfall_7day_mm"], cnt_sub)

print(f"\nEnvironmental Correlations (Pearson r, total count vs.):")
print(f"  Temperature (C):       r = {r_temp:+.3f}   (p = {p_temp:.4f})")
print(f"  7-day Rainfall (mm):   r = {r_rain:+.3f}   (p = {p_rain:.4f})")

# -------------------------------------------
# Shannon diversity summary
# -------------------------------------------
print(f"\nShannon Diversity Index (H'):")
print(f"  Season mean:  {diversity.mean():.3f} nats")
print(f"  Minimum:      {diversity.min():.3f}  on {diversity.idxmin().strftime('%d %b %Y')}")
print(f"  Maximum:      {diversity.max():.3f}  on {diversity.idxmax().strftime('%d %b %Y')}")
print(f"{'='*65}\n")

# -------------------------------------------
# Color palette (one per species, consistent throughout)
# -------------------------------------------
color_map = {
    "Alpine Jewel Beetle":   "#9B6FD6",
    "Blue Ant Wasp":         "#4A8FD4",
    "Bogong Moth":           "#E05C5C",
    "Crimson Cicada":        "#E88C3A",
    "Golden Stag Beetle":    "#E8C63A",
    "Mountain Grasshopper":  "#5AB572",
}
species_order = list(species_counts.columns)

# -------------------------------------------
# Visualizations
# -------------------------------------------
fig = plt.figure(figsize=(16, 14), facecolor="white")
fig.suptitle(
    "Insect Biodiversity Analysis  |  Namadgi NP, ACT  |  Sep 2024 to Apr 2025",
    fontsize=13,
    fontweight="bold",
    y=0.99,
)

gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.38)

# --- Plot 1: Full season population trends ---
ax1 = fig.add_subplot(gs[0, :])
for sp in species_order:
    ax1.plot(
        species_counts.index,
        species_counts[sp],
        marker=".",
        markersize=4,
        linewidth=1.6,
        color=color_map[sp],
        alpha=0.85,
        label=sp,
    )
# Shade the Feb 2025 daily observation window
ax1.axvspan(
    pd.Timestamp("2025-02-01"),
    pd.Timestamp("2025-02-19"),
    alpha=0.07,
    color="steelblue",
)
ax1.text(
    pd.Timestamp("2025-02-10"),
    ax1.get_ylim()[1] * 0.96,
    "daily obs.",
    ha="center",
    fontsize=7.5,
    color="steelblue",
    va="top",
)
ax1.set_title("Population Counts Over Observation Season", fontsize=11)
ax1.set_xlabel("Date")
ax1.set_ylabel("Count per survey transect")
ax1.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8.5, framealpha=0.9)
ax1.grid(True, alpha=0.25)
ax1.tick_params(axis="x", rotation=30)

# --- Plot 2: Shannon diversity index over time ---
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(diversity.index, diversity.values, color="#2E86AB", linewidth=2, marker=".")
ax2.fill_between(diversity.index, diversity.values, alpha=0.12, color="#2E86AB")
ax2.set_title("Shannon Diversity Index Over Time", fontsize=10)
ax2.set_xlabel("Date")
ax2.set_ylabel("H' (nats)")
ax2.grid(True, alpha=0.25)
ax2.tick_params(axis="x", rotation=30)

# --- Plot 3: Temperature vs total count scatter ---
ax3 = fig.add_subplot(gs[1, 1])
ax3.scatter(env_sub["Temp_C"], cnt_sub, color="#E05C5C", alpha=0.6, s=28, zorder=3)
# Regression line
m, b = np.polyfit(env_sub["Temp_C"].values, cnt_sub.values, 1)
x_line = np.linspace(env_sub["Temp_C"].min(), env_sub["Temp_C"].max(), 100)
ax3.plot(
    x_line,
    m * x_line + b,
    color="#333333",
    linewidth=1.5,
    linestyle="--",
    label=f"r = {r_temp:.3f}",
)
ax3.set_title("Temperature vs Total Count", fontsize=10)
ax3.set_xlabel("Temperature (C)")
ax3.set_ylabel("Total count per survey")
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.25)

# --- Plot 4: Monthly average count per species ---
ax4 = fig.add_subplot(gs[2, 0])
df["Month"] = df["Date"].dt.to_period("M")
monthly_avg = df.groupby(["Month", "Species"])["Count"].mean().unstack()
monthly_avg.index = monthly_avg.index.astype(str)
x_pos = np.arange(len(monthly_avg))
bar_width = 0.12
for i, sp in enumerate(species_order):
    if sp in monthly_avg.columns:
        ax4.bar(
            x_pos + i * bar_width,
            monthly_avg[sp].fillna(0),
            width=bar_width,
            label=sp,
            color=color_map[sp],
            alpha=0.85,
        )
ax4.set_xticks(x_pos + bar_width * 2.5)
ax4.set_xticklabels(monthly_avg.index, rotation=35, fontsize=7.5)
ax4.set_title("Monthly Average Count per Species", fontsize=10)
ax4.set_xlabel("Month")
ax4.set_ylabel("Average count")
ax4.legend(fontsize=7, ncol=2)
ax4.grid(True, alpha=0.25, axis="y")

# --- Plot 5: Proportional abundance over time ---
ax5 = fig.add_subplot(gs[2, 1])
row_totals = species_counts.sum(axis=1)
for sp in species_order:
    proportion = species_counts[sp] / row_totals
    ax5.plot(
        species_counts.index,
        proportion,
        linewidth=1.6,
        color=color_map[sp],
        alpha=0.85,
        label=sp,
    )
ax5.set_title("Proportional Abundance by Species", fontsize=10)
ax5.set_xlabel("Date")
ax5.set_ylabel("Proportion of total count")
ax5.legend(fontsize=7, bbox_to_anchor=(1.01, 1), loc="upper left")
ax5.grid(True, alpha=0.25)
ax5.tick_params(axis="x", rotation=30)

plt.savefig("biodiversity_analysis.png", bbox_inches="tight", dpi=150)
print("Saved figure: biodiversity_analysis.png")
plt.show()
