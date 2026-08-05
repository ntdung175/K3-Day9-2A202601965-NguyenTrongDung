# Báo cáo cá nhân — K3 Day 09 Multi-Agent E-commerce Dispute Resolution

| Trường | Nội dung |
| --- | --- |
| **Họ và tên** | **Nguyễn Trọng Dũng** |
| **MSSV** | **2A202601965** |
| **Khóa / Lớp** | K3 |
| **Vai trò chính** | **Leader, Coordinator & Policy Architect (Thành viên 1)** |
| **Chính sách áp dụng** | `EC_POLICY_V1` |
| **Mô hình AI** | `gemma-2-9b-it` (9B parameters — $\le 10\text{B}$) |

---

## 1. Phần việc phụ trách & Ownership

| Deliverable / Module | File / Artifact | Nội dung công việc & Kết quả bàn giao |
| --- | --- | --- |
| **Kiến trúc Hệ thống** | [architecture.md] | Xây dựng sơ đồ Mermaid Multi-Agent, định nghĩa vai trò 6 Agent, phân quyền truy cập dữ liệu CSV, ma trận `EC_POLICY_V1` và giao thức A2A Handoff Protocol. |
| **Sổ tay Hướng dẫn** | [LAB_GUIDE_K3.md] | Xây dựng sổ tay lộ trình 240 phút (Phase 1-4) phân công vai trò cho từng thành viên trong nhóm. |
| **Cấu hình Hệ thống** | `src/config.py` | Cấu hình đường dẫn, nạp an toàn API Key từ `.env`, thiết lập Cohort K3, Policy `EC_POLICY_V1` và Model `gemma-2-9b-it`. |
| **Policy Agent Engine** | `src/policy_agent.py` | Thực thi ma trận quy tắc `EC_POLICY_V1` cho 6 primary issues (`canceled_order_paid`, `unavailable_order_paid`, `late_delivery_seller`, `late_delivery_logistics`, `valid_split_payment`, `unsupported_late_claim`), tính tiền refund và chuẩn hóa Evidence IDs. |
| **Coordinator Agent** | `src/coordinator.py` | Tiếp nhận ticket khiếu nại `input/EC_xxx.json`, trích xuất `claimed_order_id`, khởi tạo gói Handoff A2A, điều phối luồng làm việc giữa các Domain Agents và hợp nhất output. |
| **Metadata Audit** | `logging/metadata.json` | Khai báo minh bạch thông số model `gemma-2-9b-it` (9B), framework và runtime. |

---

## 2. Giao thức Contract & Luồng Kiểm chứng

### 🔄 Luồng điều phối Handoff A2A:
1. **Coordinator Agent** tiếp nhận ticket khiếu nại (`input/EC_xxx.json`), khởi tạo gói tin Handoff Packet chứa `case_id` và `claimed_order_id`.
2. Chuyển giao nhiệm vụ tra cứu cho các Domain Agents (`OrderSellerAgent`, `DeliveryAgent`, `PaymentAgent`) để trích xuất dữ liệu thực tế từ 9 file CSV Olist.
3. Hợp nhất aggregated facts và chuyển sang **Policy Agent** để đối chiếu với ma trận `EC_POLICY_V1`:
   - Phân loại chính xác 1 trong 6 `primary_issue`.
   - Xác định `case_status` (`action_required` nếu refund > 0, `no_action` nếu refund = 0).
   - Thiết lập `confidence: 1.0` khi grounding dữ liệu khớp quy tắc.
   - Xác định bên chịu trách nhiệm (`OLIST_PLATFORM`, `seller`, `LOGISTICS_PROVIDER` hoặc không có).
   - Tính toán chính xác số tiền hoàn lại (`recommended_refund_brl`).
   - Chuẩn hóa thứ tự Evidence IDs (`order` $\rightarrow$ `item` $\rightarrow$ `payment` $\rightarrow$ `seller` $\rightarrow$ `policy`).
4. Kết quả được chuyển qua **Verifier Agent** để kiểm tra hard-gate schema trước khi xuất file vào `output/EC_xxx.json`.

### 🧪 Lệnh xác minh đã thực thi thành công:
```bash
python run_pipeline.py
python validate_outputs.py
python package_submission.py
```
- **Kết quả kiểm chứng**: 50 file input được xử lý thành 50 file output hợp lệ trong `output/`, ghi vết đầy đủ 150 dòng trong `logging/trace.jsonl`, QA Contract đạt **PASS 100%** và tạo file ZIP `submission.zip` đúng cấu trúc.

---

## 3. Quyết định Kỹ thuật Quan trọng

- **Thứ tự Ưu tiên trong Ma trận `EC_POLICY_V1`**: Thiết lập thứ tự đánh giá nghiêm ngặt theo bảng chính sách (Canceled / Unavailable Order $\rightarrow$ Late Delivery $\rightarrow$ Split Payment $\rightarrow$ Unsupported Late) để đảm bảo không bao giờ bỏ sót nghĩa vụ hoàn tiền của nền tảng khi đơn hàng bị hủy/không có sẵn.
- **Chuẩn hóa Thứ tự Evidence IDs**: Đơn giản hóa và sắp xếp Evidence IDs theo đúng trình tự chuẩn (`order` $\rightarrow$ `item` $\rightarrow$ `payment` $\rightarrow$ `seller` $\rightarrow$ `policy`) với mã `policy` ở vị trí cuối cùng, loại bỏ hoàn toàn lặp ID để đạt điểm tối đa trên hệ thống chấm tự động.

---

## 4. Cam kết tuân thủ quy định bài lab

- [x] Đã kiểm tra mô hình `gemma-2-9b-it` có tham số **9B** ($\le 10\text{B}$ parameters).
- [x] Đã đặt API Key trong file `.env` và cấu hình `.gitignore` chặn commit secret.
- [x] Tên mô hình và thông số được khai báo rõ ràng trong mã nguồn và file `logging/metadata.json`.
- [x] Mã nguồn và báo cáo cá nhân được commit đầy đủ trên Git Repository nhóm trước khi đóng gói nộp bài.
- [x] File `submission.zip` chỉ chứa đúng 50 file JSON output chuẩn trong thư mục `output/`.

---
**Người báo cáo**: Nguyễn Trọng Dũng  
**MSSV**: 2A202601965  
**Vai trò**: Leader, Coordinator & Policy Architect (Thành viên 1)
