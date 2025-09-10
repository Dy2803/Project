
**FlowSense: Hệ thống giám sát mạng thụ động dựa trên thông tin điều khiển trong SDN**

**1.1 Giới thiệu đồ án** 

Đồ án tốt nghiệp này trình bày việc triển khai **FlowSense** - một phương pháp giám sát băng thông **thụ động** và hiệu quả trong môi trường mạng lập trình phần mềm (SDN). Thay vì sử dụng phương pháp giám sát chủ động tốn kém tài nguyên (như **Polling**), **FlowSense** tận dụng các thông điệp có sẵn trong mạng như **PacketIn** và **FlowRemoved** để tính toán mức sử dụng băng thông một cách chính xác.

Dự án này sử dụng công cụ mô phỏng mạng **Mininet** và nền tảng **Ryu Controller (viết bằng Python)** để hiện thực hóa và đánh giá thuật toán.

**1.2 Các công nghệ được sử dụng** 

**Mininet**: Công cụ mô phỏng mạng ảo.

**Ryu Controller**: Framework SDN mã nguồn mở bằng Python.

**Python**: Ngôn ngữ lập trình chính.

**OpenFlow**: Giao thức giao tiếp giữa Ryu Controller và các switch ảo.

**Matplotlib, Pandas**: Thư viện Python để xử lý dữ liệu và vẽ biểu đồ.

**1.3 Tổ chức các script như sau**

.
├── FlowSense_CollectLogs.py   # Code Ryu Controller cho FlowSense

├── Polling_CollectLogs.py     # Code Ryu Controller cho Polling

├── TOPOLOGY.py                # Mô hình mạng để đánh giá độ chính xác

├── GranularityTopo.py         # Mô hình mạng để đánh giá độ chi tiết (granularity)

├── FLOWSENSE(Algorithm1).py   # Script phân tích log và vẽ biểu đồ FlowSense

├── Draw_Polling_CollectLogs.py # Script phân tích log và vẽ biểu đồ Polling

├── Comparison.py              # Script so sánh kết quả FlowSense và Polling

├── PostProcessed.py           # Script xử lý sau cho FlowSense

├── granularity_left.py        # Script vẽ biểu đồ Granularity (Độ trễ checkpoint)

└── granularity_right.py       # Script vẽ biểu đồ Granularity (Tỷ lệ dữ liệu được ghi nhận theo thời gian kể từ checkpoint)
