# granularity_utilization_reported_cdf.py – Vẽ CDF tỷ lệ utilization được report sau 1s, 5s, 10s

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Đọc log FlowRemoved
path = "granularity_events.csv"
df = pd.read_csv(path)
df = df[(df['event'] == 'FlowRemoved') & (df['byte_count'] > 0) & (df['duration'] > 0)].copy()
df['timestamp'] -= df['timestamp'].min()

# Khôi phục flows
flows = []
for _, row in df.iterrows():
    duration = row['duration']
    raw_end = row['timestamp']
    idle_timeout = row.get('idle_timeout', 5)
    if abs(duration - idle_timeout) < 0.5:
        end = raw_end - idle_timeout
    else:
        end = raw_end
    start = end - duration
    if end <= start or (end - start) < 0.2:
        continue
    flows.append({'start': start, 'end': end, 'bytes': row['byte_count']})

# Tạo checkpoint tại flow end
checkpoints = sorted(set(f['end'] for f in flows))

# Tính % utilization report sau 1s, 5s, 10s
percentages_1s, percentages_5s, percentages_10s = [], [], []
for t in checkpoints:
    active = [f for f in flows if f['start'] <= t <= f['end']]
    if not active:
        continue
    total_bytes = sum(f['bytes'] for f in active)

    def pct(after):
        reported = sum(f['bytes'] for f in active if f['end'] <= t + after)
        return reported / total_bytes if total_bytes > 0 else 0

    percentages_1s.append(pct(1))
    percentages_5s.append(pct(5))
    percentages_10s.append(pct(10))

# Vẽ CDF
plt.figure(figsize=(8, 5))
def plot_cdf(data, label, color):
    data = np.sort(data)
    y = np.arange(1, len(data)+1) / len(data)
    plt.step(data, y, where='post', label=label, color=color)

plot_cdf(percentages_1s, "After 1s", "red")
plot_cdf(percentages_5s, "After 5s", "green")
plot_cdf(percentages_10s, "After 10s", "blue")

plt.xlabel("Fraction of utilization reported")
plt.ylabel("Fraction of checkpoints")
plt.title("Granularity – % Utilization Reported Over Time")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("granularity_utilization_reported_cdf.png")
plt.show()
