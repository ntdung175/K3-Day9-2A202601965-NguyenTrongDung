# Báo cáo cá nhân — K3 Day 09 Multi-Agent E-commerce Dispute Resolution

| Trường | Nội dung |
| --- | --- |
| Họ và tên | Chu Thị Yến Khanh |
| MSSV | 01739 |
| Vai trò | Thành viên 3 — QA, Infrastructure & Verifier Engineer |
| Chính sách | `EC_POLICY_V1` |

## Phần việc phụ trách

| Deliverable | File | Kết quả |
| --- | --- | --- |
| Verifier Agent | `src/verifier_agent.py` | Kiểm tra schema, giới hạn danh sách, định dạng evidence, BRL, confidence và đối chiếu evidence với facts từ CSV. |
| Trace logging | `src/logger.py` | Ghi trace JSONL cho các bước Coordinator, Policy và Verifier của từng case. |
| Batch runner | `run_pipeline.py` | Chạy batch 50 ticket, tạo output JSON và trace. |
| QA | `validate_outputs.py` | Đọc lại input/output, tái tạo facts từ Olist CSV và kiểm tra từng output trước khi nộp. |
| Packaging | `package_submission.py` | Chỉ đóng gói 50 file `output/EC_001.json` đến `output/EC_050.json` vào `submission.zip`. |

## Contract và kiểm chứng

`VerifierAgent` nhận kết quả draft cùng facts đơn hàng từ `DataEngine`. Verifier kiểm tra evidence ID thuộc đúng order/item/payment/seller thực tế, format evidence, giới hạn `affected_entities`/`evidence_ids`/root cause/action, confidence trong `[0,1]`, giá trị BRL và tính nhất quán với dữ liệu gốc.

Lệnh kiểm tra và đóng gói:

```powershell
python run_pipeline.py
python validate_outputs.py
python package_submission.py
```

Kết quả cần đạt: đủ 50 input, đủ 50 output, trace cho toàn bộ case, QA pass và `submission.zip` chỉ chứa thư mục `output/`.

## Quyết định kỹ thuật

Chọn hard-gate verifier thay vì chỉ cắt ngắn danh sách khi vượt giới hạn. Cắt ngắn có thể che giấu evidence sai; verifier đối chiếu evidence với facts đã nạp từ CSV để ngăn output dùng ID không tồn tại hoặc không thuộc đơn hàng đang xử lý.

## Cam kết

Không đưa API key, `.env`, `.venv` hoặc `submission.zip` vào commit. Model và metadata runtime được khai báo riêng trong `logging/metadata.json`.
