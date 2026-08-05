# K3 Day 09 — Multi-Agent E-commerce Dispute Resolution

## 1. Bài toán

- Xử lý 50 yêu cầu hỗ trợ từ dữ liệu Olist.
- Kết luận phải dựa trên CSV, không suy diễn sự kiện không tồn tại.
- Đầu ra: issue, trách nhiệm, evidence, refund và action.

---

## 2. Thách thức

- Một claim “giao trễ” có thể là lỗi seller, logistics hoặc không hợp lệ.
- Dữ liệu tách trong orders, items, payments và sellers.
- Cần evidence ID hợp lệ và tính tiền chính xác đến 2 chữ số BRL.

---

## 3. Kiến trúc 6 agent

```text
Input → Coordinator → Order/Seller ┐
                    → Delivery     ├→ Policy → Verifier → Output
                    → Payment      ┘
```

- Coordinator tổng hợp handoff.
- Domain agents truy xuất facts có thể kiểm chứng từ CSV.
- Policy áp dụng `EC_POLICY_V1`; Verifier là hard gate trước khi ghi file.

---

## 4. Policy Engine

| Điều kiện | Kết quả |
| --- | --- |
| canceled/unavailable + đã thanh toán | Full refund, platform |
| giao trễ + seller handoff trễ | Refund freight, seller |
| giao trễ + seller handoff đúng hạn | Refund freight, logistics |
| ≥2 payment rows + đối soát khớp | Giải thích split payment |
| giao đúng hạn + payment khớp | Bác claim giao trễ |

---

## 5. Grounding và Verifier

- Chỉ dùng evidence: `order`, `item`, `payment`, `seller`, `policy`.
- Kiểm tra schema, confidence, giới hạn ID và số tiền.
- Evidence không liên quan đến root cause bị loại khỏi kết quả cuối.
- Mọi financial total được đối chiếu với facts từ CSV.

---

## 6. Demo UI

Mở `demo.html` để chọn từng case.

- Hiển thị customer request, assessment, root cause, responsible party.
- Hiển thị entity IDs, evidence đã verifier và BRL refund.
- Chuyển nhanh giữa 50 case để minh họa pipeline end-to-end.

---

## 7. Kết quả kiểm chứng

```powershell
python run_pipeline.py
python validate_outputs.py
python package_submission.py
```

- 50 input → 50 output.
- 150 trace events cho lần chạy mới nhất.
- ZIP chỉ chứa 50 JSON trong `output/`.
- Leaderboard: **100 điểm**.

---

## 8. Kết luận

- Tách domain agents giúp quyết định grounded và dễ kiểm tra.
- Verifier không chỉ kiểm tra format: nó bảo vệ evidence precision.
- Pipeline tái lập được từ CSV, input và policy version.
