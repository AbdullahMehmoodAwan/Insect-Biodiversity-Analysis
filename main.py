import pandas as pd
import matplotlib.pyplot as plt

# Load sample insect biodiversity data (assumes a CSV file)
# Example format: Date, Species, Count
df = pd.read_csv("insect_data.csv")

# Convert 'Date' to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Data Cleaning: Remove any missing values
df.dropna(inplace=True)

# Group data by species and date to get population trends
species_trends = df.groupby(["Date", "Species"])["Count"].sum().unstack()

# Plot the insect biodiversity trends over time
plt.figure(figsize=(10, 6))
species_trends.plot(marker="o", linestyle="-", colormap="viridis", alpha=0.8)

plt.title("Insect Biodiversity Trends Over Time")
plt.xlabel("Date")
plt.ylabel("Population Count")
plt.legend(title="Species", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True)
plt.show()
