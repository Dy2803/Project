# sosanh.py – So sánh FlowSense và Polling trên cùng biểu đồ
import pandas as pd
import matplotlib.pyplot as plt

# Đọc dữ liệu FlowSense
flowsense_df = pd.read_csv("a1_algorithm1_correct_final.csv")
flowsense_df['time'] = pd.to_numeric(flowsense_df['time'], errors='coerce')
flowsense_df['util_mbps'] = pd.to_numeric(flowsense_df['util_mbps'], errors='coerce')
flowsense_df = flowsense_df.dropna()

# Đọc dữ liệu Polling đã phân tích
df = pd.read_csv("polling_analyzed.csv")
df['time'] = pd.to_numeric(df['time'], errors='coerce') 
df['util_mbps'] = pd.to_numeric(df['util_mbps'], errors='coerce')
df = df.dropna()

#  Chuẩn hóa timestamp Polling về mốc 0
df['time'] = df['time'] - df['time'].min()

# Vẽ biểu đồ kết hợp
plt.figure(figsize=(10, 5))

# FlowSense
plt.step(flowsense_df['time'].to_numpy(), flowsense_df['util_mbps'].to_numpy(), where='post', linestyle='--', color='blue', label='FlowSense')

# Polling
plt.step(df['time'].to_numpy(), df['util_mbps'].to_numpy(), where='post', linestyle='-', color='red', label='Polling')

plt.xlabel("Time (s)")
plt.ylabel("Utilization (Mbps)")
plt.title("FlowSense vs Polling – Link Utilization Over Time")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("flowsense_vs_polling.png")
plt.show()
