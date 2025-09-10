
 # FlowSense: Hệ thống giám sát mạng thụ động dựa trên thông tin điều khiển trong SDN


 ## 1. Giới thiệu đồ án 💡

 Đồ án này tập trung vào việc hiện thực và đánh giá **FlowSense** - một phương pháp giám sát mạng thụ động. Dự án giải quyết một thách thức quan trọng trong mạng lập trình phần mềm (SDN): làm thế nào để đo lường mức sử dụng băng thông một cách **chính xác** và **hiệu quả** mà không cần tốn thêm tài nguyên mạng.

 Thay vì dựa vào các phương pháp giám sát chủ động như **Polling**, FlowSense tận dụng các thông điệp có sẵn trong mạng như `PacketIn` và `FlowRemoved`. Điều này cho phép hệ thống thu thập thông tin lưu lượng mà **không tạo ra overhead** cho luồng điều khiển.

 Đồ án được xây dựng trên môi trường mô phỏng **Mininet** và sử dụng **Ryu Controller** để triển khai logic giám sát.


 ## 2. Công nghệ sử dụng 🛠️

 Dự án sử dụng các công nghệ chính sau:

 * **Mininet**: Một công cụ mô phỏng mạng ảo, cho phép tạo ra các topology mạng phức tạp trên một máy tính duy nhất.

 * **Ryu Controller**: Một framework SDN mã nguồn mở, hỗ trợ giao thức OpenFlow và được viết bằng Python.
 
 * **Python 3**: Ngôn ngữ lập trình chính.

 * **OpenFlow 1.3**: Giao thức giao tiếp chuẩn giữa Ryu Controller và các switch ảo.

 * **Matplotlib & Pandas**: Các thư viện Python dùng để xử lý, phân tích dữ liệu và trực quan hóa kết quả (vẽ biểu đồ).

 ## 3. Cấu trúc thư mục 📂

 Dự án được tổ chức gọn gàng để dễ dàng truy cập và thực thi. Dưới đây là mô tả chi tiết các file chính:

 * `TOPOLOGY.py`: Script mô hình mạng để đánh giá độ chính xác (Accuracy).

 * `GranularityTopo.py`: Script mô hình mạng để đánh giá độ chi tiết (Granularity).

 * `FlowSense_CollectLogs.py`: Code **Ryu Controller** hiện thực thuật toán FlowSense.

 * `Polling_CollectLogs.py`: Code **Ryu Controller** hiện thực phương pháp giám sát Polling.

 * `FLOWSENSE(Algorithm1).py`: Script phân tích dữ liệu từ FlowSense và vẽ biểu đồ.

 * `Draw_Polling_CollectLogs.py`: Script phân tích dữ liệu từ Polling và vẽ biểu đồ.

 * `Comparison.py`: Script so sánh kết quả của FlowSense và Polling trên cùng một biểu đồ.

 * `granularity_left.py` & `granularity_right.py`: Các script dùng để phân tích và vẽ biểu đồ đánh giá độ chi tiết.

 * `PostProcessed.py`: Script xử lý dữ liệu bổ sung cho FlowSense.

 ## 4. Hướng dẫn cài đặt và chạy mã nguồn

  Máy ảo **Ubuntu** phiên bản 22.04 LTS đã cài đặt Mininet và Ryu controller.

### Bước 1: Cài đặt các thư viện cần thiết

 Mở Terminal và chạy lệnh sau để cài đặt các thư viện Python:

 ```bash
 pip install ryu pandas matplotlib
 ```
 ### Bước 2: Chạy kịch bản đánh giá độ chính xác (Accuracy)

 Thực hiện theo các bước sau để chạy cả hai phương pháp và so sánh kết quả.

 1.  **Chạy Polling**:
     * Mở Terminal thứ nhất và chạy Ryu Controller ở chế độ Polling:
         ```bash
         ryu-manager Polling_CollectLogs.py
         ```
     * Mở Terminal thứ hai và chạy mô hình mạng với Mininet:
         ```bash
         sudo python TOPOLOGY.py
         ```
     * Sau khi mô phỏng hoàn tất, file `polling_raw.csv` sẽ được tạo. Chạy script phân tích để tạo file `polling_analyzed.csv`:
         ```bash
         python Draw_Polling_CollectLogs.py
         ```

 2.  **Chạy FlowSense**:
     * Đóng Mininet và Ryu ở bước trên.
     * Mở Terminal thứ nhất và chạy Ryu Controller ở chế độ FlowSense:
         ```bash
         ryu-manager FlowSense_CollectLogs.py
         ```
     * Mở Terminal thứ hai và chạy lại mô hình mạng:
         ```bash
         sudo python TOPOLOGY.py
         ```
     * Sau khi mô phỏng hoàn tất, file `flowsense_events.csv` sẽ được tạo. Chạy script phân tích để tạo file `a1_algorithm1_correct_final.csv`:
         ```bash
         python "FLOWSENSE(Algorithm1).py"
         ```

 3.  **So sánh kết quả**:
     * Chạy script so sánh để tạo biểu đồ tổng hợp:
         ```bash
         python Comparison.py
         ```
     * Một cửa sổ đồ thị sẽ hiển thị, so sánh mức sử dụng băng thông giữa hai phương pháp.

 ### Bước 3: Chạy kịch bản đánh giá độ chi tiết (Granularity)

 Kịch bản này được thiết kế để kiểm tra khả năng phản hồi của FlowSense với các luồng traffic phức tạp.

 1.  Mở Terminal thứ nhất và chạy Ryu Controller:

* **Lưu ý**: Trước khi chạy, hãy mở file `FlowSense_CollectLogs.py` và thay đổi tên file log thành `granularity_events.csv`.
     ```bash
     ryu-manager FlowSense_CollectLogs.py
     ```

 2.  Mở Terminal thứ hai và chạy mô hình mạng `GranularityTopo`:
     ```bash
     sudo python GranularityTopo.py
     ```

 3.  Sau khi mô phỏng hoàn tất, chạy các script phân tích sau để xem kết quả:
     * Để vẽ biểu đồ phân phối độ trễ:
         ```bash
         python granularity_left.py
         ```
     * Để vẽ biểu đồ tỷ lệ dữ liệu được báo cáo:
         ```bash
         python granularity_right.py
         ```



 ## 5. Kết quả và đánh giá 📈

 Dựa trên các kết quả mô phỏng, phương pháp **FlowSense** cho thấy hiệu quả vượt trội:

* **Độ chính xác cao**: Biểu đồ so sánh cho thấy FlowSense tái tạo lại mức sử dụng băng thông của mạng một cách rất gần với phương pháp Polling.

* **Không tạo overhead**: FlowSense không cần gửi thêm các yêu cầu Polling, giúp giảm thiểu đáng kể lưu lượng điều khiển.
* **Phản ứng nhanh**: Kết quả đánh giá granularity chứng minh FlowSense có thể cập nhật thông tin băng thông chỉ trong vài giây sau khi một luồng kết thúc, phù hợp cho các hệ thống giám sát gần thời gian thực.


