import pandas as pd
import matplotlib.pyplot as plt

# Đọc dữ liệu từ file
df = pd.read_csv("flowsense_events.csv")

# Lọc FlowRemoved từ switch s2 (DPID=2) và hợp lệ
flowrm_df = df[
    (df['event'] == 'FlowRemoved') &
    (df['dpid'] == 2) &
    (df['byte_count'] > 0) &
    (df['duration'] > 0)
].copy()

# Chuẩn hóa thời gian
flowrm_df['timestamp'] -= flowrm_df['timestamp'].min()

# Khôi phục flows: start, end, utilization
flows = []
for _, row in flowrm_df.iterrows():
    duration = row['duration']
    raw_end = row['timestamp']
    idle_timeout = row.get('idle_timeout', 5)

    # Điều chỉnh thời gian nếu timeout là do idle
    if abs(duration - idle_timeout) < 0.5:
        end = raw_end - idle_timeout
    else:
        end = raw_end

    start = end - duration
    if end <= start or (end - start) < 0.2:
        continue

    util = (row['byte_count'] * 8) / ((end - start) * 1e6)  # Mbps
    flows.append({'start': start, 'end': end, 'util': util})

# Dựng lại timeline từ các mốc start/end
timeline = sorted(set([f['start'] for f in flows] + [f['end'] for f in flows]))

# Tính tổng utilization tại mỗi khoảng thời gian
time_points = []
utils = []
for i in range(len(timeline) - 1):
    t1 = timeline[i]
    t2 = timeline[i + 1]
    active_flows = [f for f in flows if not (f['end'] <= t1 or f['start'] >= t2)]
    total_util = sum(f['util'] for f in active_flows)
    time_points.append(t1)
    utils.append(total_util)

# Thêm điểm cuối để biểu đồ step
time_points.append(timeline[-1])
utils.append(utils[-1])

# Vẽ biểu đồ
plt.figure(figsize=(10, 5))
plt.step(time_points, utils, where='post',linestyle='--',  color='blue', label='FlowSense Post Proccesed')
plt.xlabel("Time (s)")
plt.ylabel("Utilization (Mbps)")
plt.title("FlowSense – Reconstructed Link Utilization")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("flowsense_post_processed_filtered.png")
plt.show()

# Xuất CSV để dùng trong biểu đồ so sánh
export_df = pd.DataFrame({'time': time_points, 'util_mbps': utils})
export_df.to_csv("flowsense_post_processed.csv", index=False)
