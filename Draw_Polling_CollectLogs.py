
import pandas as pd
import matplotlib.pyplot as plt

# Đọc dữ liệu từ polling_raw.csv
df = pd.read_csv("polling_raw.csv")

# Ép kiểu dữ liệu đảm bảo đúng định dạng
df['real_time'] = pd.to_numeric(df['real_time'], errors='coerce')
df['elapsed'] = pd.to_numeric(df['elapsed'], errors='coerce')
df['byte_count'] = pd.to_numeric(df['byte_count'], errors='coerce')
df['duration_sec'] = pd.to_numeric(df['duration_sec'], errors='coerce')
df['dpid'] = pd.to_numeric(df['dpid'], errors='coerce')
df['eth_src'] = df['eth_src'].astype(str)
df['eth_dst'] = df['eth_dst'].astype(str)

# Lọc flow hợp lệ
df = df[(df['byte_count'] > 0) & (df['duration_sec'] > 0)]

# Gộp theo flow key = (dpid, eth_src, eth_dst), rồi tính delta giữa 2 lần polling
records = []
last_stats = {}  # (dpid, eth_src, eth_dst) -> (last_bytes, last_time)

for _, row in df.sort_values("real_time").iterrows():
    key = (row['dpid'], row['eth_src'], row['eth_dst'])
    now_bytes = row['byte_count']
    now_time = row['real_time']

    if key in last_stats:
        last_bytes, last_time = last_stats[key]
        delta_bytes = now_bytes - last_bytes
        delta_time = now_time - last_time

        if delta_bytes > 0 and delta_time > 0:
            bw = (delta_bytes * 8) / (delta_time * 1e6)  # Mbps
            records.append({
                'time': row['elapsed'],
                'util_mbps': bw
            })

    last_stats[key] = (now_bytes, now_time)

# Gộp lại theo thời gian ( làm tròn giây ) để vẽ biểu đồ
records_df = pd.DataFrame(records)
records_df['time'] = records_df['time'].round().astype(int)
grouped = records_df.groupby('time')['util_mbps'].sum().reset_index()

# Vẽ biểu đồ step
plt.figure(figsize=(10, 5))
plt.step(grouped['time'].to_numpy(), grouped['util_mbps'].to_numpy(), where='post', color='red', label='Polling (analyzed delta)')
plt.xlabel("Time (s)")
plt.ylabel("Utilization (Mbps)")
plt.title("Polling")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("polling_analyzed_plot.png")
plt.show()

# Lưu CSV kết quả
grouped.to_csv("polling_analyzed.csv", index=False)
