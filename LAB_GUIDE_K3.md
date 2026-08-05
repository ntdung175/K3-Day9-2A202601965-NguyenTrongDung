# SỔ TAY HƯỚNG DẪN BUỔI LAB — K3 MULTI-AGENT E-COMMERCE DISPUTE RESOLUTION

---

## 📌 1. Thông tin chung & Quy định quan trọng

- **Cohort**: **K3**
- **Repository**: `K3-Day9-Multi-Agent-A2A` (`K3-Day9-2A202601965-NguyenTrongDung`)
- **Chính sách áp dụng**: **`EC_POLICY_V1`**
- **Mô hình chọn chính thức**: **`gemma-2-9b-it`** (9B parameters - Đạt chuẩn $\le 10\text{B}$)
- **Thời lượng lab**: **240 phút** (04 Checkpoints / Phases)

### ⚠️ CẢNH BÁO QUY ĐỊNH BẮT BUỘC (Vi phạm = 0 điểm)
1. **Mô hình AI**: Chỉ sử dụng các model dưới hoặc bằng **10B parameters** ($\le 10\text{B}$). Chạy local (Ollama/vLLM) hoặc qua Provider tùy ý.
2. **Khai báo Model**: Tên model phải khai báo rõ trong mã nguồn Python và file `logging/metadata.json`. **Không đặt tên model trong file `.env`**.
3. **Bảo mật Secret**: Toàn bộ API Key, token, secret phải đặt trong file `.env`. File `.env` **tuyệt đối không được commit** lên Git (đã được cấu hình trong `.gitignore`).
4. **Quy trình Git**: Phải commit toàn bộ source code lên Git Repository nhóm **trước khi nộp file ZIP**.
5. **Nộp bài qua ZIP**: **CHỈ NÉN DUY NHẤT thư mục `output/`** thành file ZIP (chứa đúng 50 file JSON: `EC_001.json` đến `EC_050.json`). **Không đưa source code, `.env`, hay bất kỳ file rác nào vào file ZIP này**.

---

## 🧠 2. Thuật ngữ & Nguyên tắc cốt lõi

| Thuật ngữ gốc | Bản chất khái niệm | Minh họa trong Lab K3 |
| :--- | :--- | :--- |
| **Multi-agent** | Nhiều agent chuyên trách phối hợp thay vì một agent tự làm mọi việc. | **Coordinator** giao ticket cho các Agent đơn hàng, thanh toán, giao hàng, policy và verifier. |
| **Handoff** | Gói thông tin có cấu trúc một agent chuyển cho agent tiếp theo. | Chuyển `ticket_id`, `facts_found`, `evidence_ids`, `missing_facts` và `next_recommendation`. |
| **Grounding** | Quyết định chỉ dựa trên dữ liệu có thể kiểm chứng được từ CSV. | Refund phải dẫn về `payment_id`, `order_id` hoặc mã policy có thật; không tự nghĩ ra sự kiện. |
| **Verifier** | Agent kiểm tra kết quả cuối trước khi ghi ra file output JSON. | Đối chiếu Evidence IDs, kiểm tra định dạng JSON schema và các ràng buộc về số lượng phần tử. |

---

## ⏱️ 3. Lộ trình triển khai (240 Phút - 4 Phases)

| Phase | Thời gian | Vai trò | Nội dung chi tiết |
| :--- | :---: | :--- | :--- |
| **Phase 1** | **0:00–0:20** | Cả nhóm | **Xác nhận Cohort K3**: Clone repo K3, đọc chính sách `EC_POLICY_V1` và kiểm tra 9 CSV dữ liệu Olist. |
| **Phase 2** | **0:20–1:10** | Leader + Cả nhóm | **Thiết kế Agent & Handoff**: Chốt 6 vai trò agent, định nghĩa input/output và sơ đồ handoff. Cập nhật `architecture.md`. |
| **Phase 3** | **1:10–3:10** | Nhóm phát triển | **Code & Chạy 50 tickets**: Triển khai DataLoader, Domain Agents, Policy K3 và Verifier. **Test 1 ticket mẫu thành công trước khi chạy cả batch**. Sửa nguyên nhân lỗi ở agent/prompt chứ không sửa tay JSON. |
| **Phase 4** | **3:10–4:00** | Cả nhóm | **Kiểm chứng & Đóng gói**: Validate 50 file JSON trong `output/`, kiểm tra `logging/trace.jsonl`, `logging/metadata.json` và nén ZIP thư mục `output/`. |

---

## 👥 4. Phân chia công việc theo vai trò thành viên

### 🔵 Phương án 1: Nhóm 3 người

- **Thành viên 1 (Leader - Coordinator & Policy Architect)**:
  - Xây dựng **Coordinator Agent** (nhận ticket, giao task, hợp nhất handoff).
  - Xây dựng **Policy Agent** (thực thi ma trận `EC_POLICY_V1`, tính refund BRL, đề xuất action).
  - Soạn thảo và hoàn thiện file `architecture.md`.
- **Thành viên 2 (Data Engine & Domain Agents Specialist)**:
  - Xây dựng Data Engine nạp & tra cứu dữ liệu từ 9 file CSV (`data/`).
  - Xây dựng **Order & Seller Agent** (`order_delivered_carrier_date` vs `shipping_limit_date`).
  - Xây dựng **Delivery Agent** (`order_delivered_customer_date` vs `order_estimated_delivery_date`).
  - Xây dựng **Payment Agent** (đối soát tổng payment rows vs items + freight).
- **Thành viên 3 (QA, Infrastructure & Verifier Engineer)**:
  - Xây dựng **Verifier Agent** (chặn lỗi schema, kiểm tra giới hạn $\le 5$ IDs/entity, $\le 10$ evidence, confidence $\in [0, 1]$).
  - Xây dựng hệ thống ghi log `logging/trace.jsonl` và file `logging/metadata.json`.
  - Chạy batch 50 ticket, xuất 50 file JSON vào `output/` và nén ZIP nộp bài.

---

### 🟢 Phương án 2: Nhóm 4 người

- **Thành viên 1 (Leader - Multi-Agent Orchestrator)**:
  - Xây dựng **Coordinator Agent** tiếp nhận 50 case input.
  - Thiết kế Handoff Protocol và luồng giao tiếp A2A.
  - Viết tài liệu sơ đồ kiến trúc `architecture.md`.
- **Thành viên 2 (Operations & Shipping Specialist)**:
  - Tra cứu dữ liệu `olist_orders`, `olist_order_items`, `sellers`.
  - Xây dựng **Order & Seller Agent** và **Delivery Agent**.
- **Thành viên 3 (Financial & Policy Engineer)**:
  - Tra cứu dữ liệu `olist_order_payments`.
  - Xây dựng **Payment Agent** và **Policy Agent** (`EC_POLICY_V1`).
  - Chuẩn hóa định dạng Evidence IDs (`order:...`, `item:...`, `payment:...`, `seller:...`, `policy:...`).
- **Thành viên 4 (QA, Verification & Pipeline Engineer)**:
  - Xây dựng **Verifier Agent** kiểm soát chất lượng JSON output.
  - Tạo module ghi log `logging/trace.jsonl` và `logging/metadata.json`.
  - Chạy kiểm thử end-to-end 50 tickets, nén ZIP `output/` và hỗ trợ nhóm viết báo cáo cá nhân.

---

## ⚖️ 5. Ma trận quy tắc nghiệp vụ `EC_POLICY_V1` (K3 Policy)

| Primary issue | Điều kiện kích hoạt trong CSV | Bên chịu trách nhiệm | Refund đề xuất | Action xử lý |
| :--- | :--- | :--- | :---: | :--- |
| `canceled_order_paid` | `order_status = canceled` & Tổng payment > 0 | `platform` / `OLIST_PLATFORM` | Tổng payment | `issue_full_refund` |
| `unavailable_order_paid` | `order_status = unavailable` & Tổng payment > 0 | `platform` / `OLIST_PLATFORM` | Tổng payment | `issue_full_refund` |
| `late_delivery_seller` | Giao sau `estimated_date` **VÀ** carrier nhận hàng SAU `shipping_limit_date` | `seller` / Seller ID vi phạm | Tổng freight | `refund_freight` |
| `late_delivery_logistics` | Giao sau `estimated_date` **VÀ** carrier nhận hàng KHÔNG muộn hơn `shipping_limit_date` | `logistics_provider` / `LOGISTICS_PROVIDER` | Tổng freight | `refund_freight` |
| `valid_split_payment` | Có $\ge 2$ payment rows; Tổng payment = Tổng items + freight (sai số $\le 0.10$ BRL) | Không có | 0 | `explain_valid_split_payment` |
| `unsupported_late_claim` | Đơn giao không muộn hơn `estimated_date` và payment khớp | Không có | 0 | `reject_late_refund` |

### 🔍 Quy ước Evidence IDs chuẩn hóa K3
- `order:<order_id>`
- `item:<order_id>:<order_item_id>`
- `payment:<order_id>:<payment_sequential>`
- `seller:<seller_id>`
- `policy:<root_cause_code>` (VD: `policy:SELLER_HANDOFF_AFTER_LIMIT`, `policy:DELIVERY_WITHIN_ESTIMATE`...)

---

## 📦 6. Cấu trúc bài nộp & Checklist kiểm tra cuối cùng

### 📁 1. Cấu trúc bài nộp Git Repository
```text
K3-Day9-2A202601965-NguyenTrongDung/
├── data/                                 # 9 CSV Olist
├── input/                                # 50 JSON input (EC_001.json -> EC_050.json)
├── output/                               # 50 JSON output
├── logging/
│   ├── metadata.json                     # Thông số model, framework, policy version
│   └── trace.jsonl                       # Trace log chạy 50 cases
├── .gitignore                            # Đã chặn .env, __pycache__, *.zip
├── .env                                  # API keys (KHÔNG COMMIT)
├── architecture.md                       # Sơ đồ & mô tả vai trò agent, handoff
├── individual_<MSSV>_<HoTen>.md          # Báo cáo cá nhân từng thành viên
└── LAB_GUIDE_K3.md                       # Sổ tay hướng dẫn bài lab
```

### 📁 2. Cấu trúc file ZIP nộp bài
```text
submission.zip
└── output/
    ├── EC_001.json
    ├── EC_002.json
    ├── ...
    └── EC_050.json
```

### ✅ Checklist Tự kiểm tra (Self-Checklist)
- [ ] Tên model $\le 10\text{B}$ đã khai báo trong code & `logging/metadata.json`.
- [ ] API Key nằm trong `.env` và đã kiểm tra `.env` không xuất hiện trên Git.
- [ ] 1 ticket mẫu đã pass thành công Verifier Agent trước khi chạy full batch 50 ticket.
- [ ] Thư mục `output/` có chính xác **50 file JSON** (`EC_001.json` đến `EC_050.json`).
- [ ] File ZIP **chỉ nén duy nhất** thư mục `output/`.
- [ ] Đã commit toàn bộ source code lên Git repo nhóm trước khi nộp.
