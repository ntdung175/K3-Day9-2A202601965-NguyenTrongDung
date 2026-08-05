# KỊCH BẢN THUYẾT TRÌNH DEMO GIAO DIỆN STREAMLIT UI
## K3 Multi-Agent E-commerce Dispute Resolution (`EC_POLICY_V1`)

---

### 🎬 1. Lời Mở Đầu (30 giây)
> *"Kính chào thầy/cô và các bạn. Hôm nay đại diện cho nhóm K3, em xin thuyết trình sản phẩm **Hệ thống Multi-Agent Giải quyết Khiếu nại Thương mại Điện tử Olist (Cohort K3 / EC_POLICY_V1)**. Đây là Dashboard tương tác trực tiếp giúp trực quan hóa toàn bộ luồng xử lý tự động 50 ticket khiếu nại của khách hàng."*

---

### 📊 2. Màn hình 1: Tổng quan Dashboard & Metrics (1 phút)
- **Hành động trên UI**: Bấm chọn Tab **`📊 1. Tổng quan Dashboard & Metrics`**.
- **Lời thoại**:
  > *"Tại màn hình **Dashboard Tổng quan**, hệ thống hiển thị 4 chỉ số KPI chính:*
  > - *Đã xử lý thành công **50/50 tickets**.*
  > - *Tỷ lệ QA Validation đạt **PASS 100%**.*
  > - *Sử dụng mô hình AI **`gemma-2-9b-it` (9B parameters)** tuân thủ quy định bài lab.*
  > - *Biểu đồ phân bố thể hiện rõ 6 nhóm Primary Issues theo ma trận chính sách `EC_POLICY_V1`. Tổng số tiền hoàn lại (Refund) đề xuất được tính toán tự động đạt **2,735.65 BRL** từ 9 file CSV Olist."*

---

### 🤖 3. Màn hình 2: Kiến trúc 6 Agents & Handoff (1.5 phút)
- **Hành động trên UI**: Bấm chọn Tab **`🤖 2. Thiết kế Kiến trúc 6 Agents & Handoff`**.
- **Lời thoại**:
  > *"Về mặt kiến trúc, hệ thống áp dụng mô hình **Centralized Multi-Agent Orchestration**. Trung tâm là **Coordinator Agent** đóng vai trò hạt nhân điều phối gói tin Handoff Protocol A2A tới 3 Domain Agents chuyên trách:*
  > 1. ***Order & Seller Agent***: Tra cứu trạng thái đơn và hạn bàn giao seller.
  > 2. ***Delivery Agent***: So sánh ngày giao thực tế với hạn ước tính.
  > 3. ***Payment Agent***: Đối soát các dòng thanh toán split payment.
  >
  > *Sau khi thu thập chứng cứ, **Policy Agent** sẽ áp dụng ma trận quy tắc `EC_POLICY_V1`, và cuối cùng **Verifier Agent** đứng ở cổng Hard Gate để đảm bảo 100% bằng chứng Evidence IDs là có thật từ CSV trước khi xuất JSON final."*

---

### 🔍 4. Màn hình 3: Điều tra Chi tiết từng Ticket (2 phút)
- **Hành động trên UI**: Bấm chọn Tab **`🔍 3. Điều tra Chi tiết 50 Tickets`**. Chọn thử ticket `EC_001` hoặc `EC_005` trên ô Dropdown.
- **Lời thoại**:
  > *"Điểm nổi bật của giao diện là tính năng **Case Investigator** cho phép soi chi tiết từng ticket từ `EC_001` đến `EC_050`:*
  > - *Cột bên trái là yêu cầu khiếu nại của khách hàng cùng các **Facts thực tế trích xuất từ dữ liệu CSV Olist**.*
  > - *Cột bên phải là **Output JSON chính thức** đã qua Verifier Agent: thể hiện rõ `primary_issue`, trạng thái `action_required`, số tiền refund, cùng danh sách **Evidence IDs grounding chuẩn mực** theo đúng thứ tự (`order` $\rightarrow$ `item` $\rightarrow$ `payment` $\rightarrow$ `seller` $\rightarrow$ `policy`)."*

---

### ⚡ 5. Màn hình 4: Cải tiến Kỹ thuật (1 phút)
- **Hành động trên UI**: Bấm chọn Tab **`⚡ 4. Giải thích Cải tiến từ 93 -> 100 Điểm`**.
- **Lời thoại**:
  > *"Về mặt tối ưu kỹ thuật, nhóm đã thực hiện 4 cải tiến quan trọng giúp hệ thống đạt **100/100 điểm tuyệt đối**:*
  > 1. ***Chuẩn hóa thứ tự Evidence IDs***: Đặt mã `policy` ở vị trí cuối cùng để khớp 100% quy tắc kiểm định.
  > 2. ***Chính xác hóa Confidence = 1.0***: Đưa độ tin cậy lên 1.0 cho các quyết định suy luận dựa trên dữ liệu thật.
  > 3. ***Cấu trúc `case_id` ở đầu JSON object***.
  > 4. ***Xử lý triệt để các đơn 0-item*** (gán `item_ids: []`, `seller_ids: []`, `item_total_brl: 0.0`)."*

---

### 📜 6. Màn hình 5: Trace Logs & Kết Thúc (30 giây)
- **Hành động trên UI**: Bấm chọn Tab **`📜 5. Lịch vết Thực thi (Trace Logs)`**.
- **Lời thoại**:
  > *"Cuối cùng, hệ thống lưu trữ minh bạch toàn bộ 150 dòng nhật ký tương tác A2A trong file `logging/trace.jsonl` và đóng gói file `submission.zip` chỉ chứa đúng 50 file JSON output chuẩn.*
  > *Em xin kết thúc phần trình bày và sẵn sàng nhận câu hỏi từ thầy/cô!"*
