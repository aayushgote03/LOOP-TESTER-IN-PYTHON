import csv
import matplotlib.pyplot as plt
import os

csv_file = os.path.join("tiled_c_outputs", "timing_results_detailed.csv")

x_labels = []
y_values = []

with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        real_time = row["Real Time (s)"]
        # Skip rows with failed runs or missing data
        try:
            real_time = float(real_time)
        except ValueError:
            continue
        combo = f"{row['Loop Order']}_T{row['Tile Size']}"
        x_labels.append(combo)
        y_values.append(real_time)

plt.figure(figsize=(max(10, len(x_labels)//3), 6))
plt.plot(x_labels, y_values, marker='o')
plt.xlabel("Combination (LoopOrder_TileSize)")
plt.ylabel("Real Time (s)")
plt.title("Real Time for Each Loop Combination")
plt.xticks(rotation=90)
plt.tight_layout()
plt.grid(True)