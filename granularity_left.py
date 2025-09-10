# granularity_time_until_all_flows_end.py – Vẽ biểu đồ Granularity (trái Figure 3)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Đọc file log
df = pd.read_csv("granularity_events.csv")
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
    flows.append({'start': start, 'end': end})

# Tính thời gian chờ từ mỗi checkpoint đến khi flow cuối kết thúc
checkpoints = [f['end'] for f in flows]
delays = []
for t in checkpoints:
    active_flows = [f for f in flows if f['start'] <= t <= f['end']]
    if not active_flows:
        continue
    latest_end = max(f['end'] for f in active_flows)
    delays.append(latest_end - t)

# Vẽ CDF log scale
delays_sorted = np.sort(delays)
cdf = np.arange(1, len(delays_sorted) + 1) / len(delays_sorted)

plt.figure(figsize=(8, 5))
plt.semilogx(delays_sorted, cdf, color='red')
plt.xlabel("Time until last active flow ends (s)")
plt.ylabel("Fraction of checkpoints")
plt.title("Granularity – Time Until Last Active Flow Ends")
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("granularity_time_until_all_flows_end.png")
plt.show()
