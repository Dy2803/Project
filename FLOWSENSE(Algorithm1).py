
import pandas as pd
import matplotlib.pyplot as plt

# Đọc log từ file CSV
df = pd.read_csv("flowsense_events.csv")

# Tách riêng PacketIn và FlowRemoved
pktin_df = df[df['event'] == 'PacketIn']
flowrm_df = df[(df['event'] == 'FlowRemoved') & (df['dpid'] == 2)]
flowrm_df = flowrm_df[(flowrm_df['byte_count'] > 0) & (flowrm_df['duration'] > 0)]

# Tạo flow_id → timestamp mapping cho PacketIn
flow_starts = {
    row['flow_id']: row['timestamp']
    for _, row in pktin_df.iterrows()
    if pd.notna(row['flow_id'])
}

# Duyệt FlowRemoved, khôi phục flow và tính utilization
flows = []
for _, row in flowrm_df.iterrows():
    flow_id = row['flow_id']
    end = row['timestamp']
    duration = row['duration']
    soft_timeout = row['idle_timeout'] if not pd.isna(row['idle_timeout']) else 5

    # Nếu timeout là do idle_timeout thì lùi thời gian kết thúc
    if abs(duration - soft_timeout) < 0.5:
        end -= soft_timeout

    start = flow_starts.get(flow_id, end - duration)

    if end <= start or (end - start) < 0.2:
        continue

    util = (row['byte_count'] * 8) / ((end - start) * 1e6)  # Mbps
    flows.append({'flow_id': flow_id, 'start': start, 'end': end, 'util': util})

# Khởi tạo Active List và danh sách checkpoint
checkpoints = []
active_list = []

# Xử lý tuần tự theo thời gian flow kết thúc
for flow in sorted(flows, key=lambda f: f['end']):
    chkpt_time = flow['end']
    chkpt_util = flow['util']

    # Cập nhật các checkpoint trước nếu flow còn active trong khoảng đó
    for c in checkpoints:
        if flow['start'] <= c['time'] <= flow['end']:
            c['util'] += flow['util']
            c['active'] -= 1

    # Tính số flow đang active tại thời điểm này
    active_now = sum(1 for f in active_list if f['start'] <= chkpt_time <= f['end'])

    # Tạo checkpoint mới
    checkpoints.append({'time': chkpt_time, 'util': chkpt_util, 'active': active_now})

    # Cập nhật Active List
    active_list = [f for f in active_list if f['flow_id'] != flow['flow_id']]
    active_list.append(flow)

# Chuẩn bị dữ liệu vẽ
checkpoints.sort(key=lambda x: x['time'])
times = [c['time'] for c in checkpoints]
utils = [c['util'] for c in checkpoints]

# Vẽ biểu đồ step-wise
plt.figure(figsize=(10, 5))
plt.step(times, utils, where='post', linestyle='--', label='FlowSense (Algorithm 1)', color='blue')
plt.xlabel("Time (s)")
plt.ylabel("Utilization (Mbps)")
plt.title("FlowSense – Link Utilization (with PacketIn ActiveList)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("flowsense_algorithm1_correct_final.png")
plt.show()

# Xuất CSV
pd.DataFrame({'time': times, 'util_mbps': utils}).to_csv("a1_algorithm1_correct_final.csv", index=False)
