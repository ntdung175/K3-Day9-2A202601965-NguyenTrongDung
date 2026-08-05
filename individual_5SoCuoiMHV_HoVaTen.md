# Báo cáo cá nhân — K3 Day 09 Multi-Agent E-commerce Dispute Resolution

| Trường | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Trọng Dũng |
| MSSV | 2A202601965 |
| Vai trò | QA, Infrastructure & Verifier Engineer (thành viên 3) |
| Chính sách | `EC_POLICY_V1` |

## Phần việc phụ trách

| Deliverable | File | Kết quả |
| --- | --- | --- |
| Verifier Agent | `src/verifier_agent.py` | Hard gate schema, giới hạn mảng, BRL, confidence và grounding evidence theo facts CSV. |
| Trace logging | `src/logger.py` | Ghi trace JSONL cho từng bước Coordinator, Policy và Verifier. |
| Batch runner | `run_pipeline.py` | Sinh input, chạy 50 case, ghi output và trace. |
| QA & packaging | `validate_outputs.py`, `package_submission.py` | Kiểm tra 50 JSON trước khi tạo ZIP chỉ chứa `output/`. |

## Contract và kiểm chứng

Verifier nhận draft output cùng facts order từ `DataEngine`. Nó chặn evidence ID không thuộc order/item/payment/seller thực tế, kiểm tra format evidence, các giới hạn `5/10/3/3/5`, confidence trong `[0,1]`, BRL và tổng tiền khớp facts.

```powershell
python run_pipeline.py
python validate_outputs.py
python package_submission.py
```

Kết quả đã kiểm chứng: 50 input, 50 output, 150 dòng `logging/trace.jsonl`; QA pass và tạo `submission.zip`.

## Quyết định kỹ thuật

Chọn hard-gate verifier thay vì chỉ cắt ngắn danh sách: cắt có thể che evidence sai. Validator kiểm tra nguồn evidence từ facts đã nạp CSV để giảm false positive.

## Cam kết

Không commit API key, `.env`, `.venv` hoặc `submission.zip`. Model và kích thước model được khai báo trong `logging/metadata.json`.
