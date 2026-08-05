# Báo cáo cá nhân — K3 Day 09 Multi-Agent E-commerce Dispute Resolution

| Trường | Nội dung |
| --- | --- |
| Họ và tên | Diêm Công Thành |
| MSSV | 2A202601689 |
| Vai trò | Data Engine & Domain Agents Specialist (thành viên 2) |
| Chính sách | `EC_POLICY_V1` |

## Phần việc phụ trách

| Deliverable | File | Kết quả |
| --- | --- | --- |
| Data Engine | `src/data_engine.py` | Nạp 9 file CSV Olist, tạo index tra cứu nhanh theo `order_id`, `customer_id`, `seller_id`, `product_id` và gom facts cho từng case. |
| Order & Seller Agent | `src/order_seller_agent.py` | Kiểm tra trạng thái đơn hàng, danh sách item, seller liên quan và xác định seller bàn giao muộn theo `shipping_limit_date`. |
| Delivery Agent | `src/delivery_agent.py` | So sánh `order_delivered_customer_date` với `order_estimated_delivery_date`, tính trạng thái giao trễ và số ngày trễ. |
| Payment Agent | `src/payment_agent.py` | Đối soát payment rows với tổng item + freight, phát hiện split payment và tính các tổng tiền BRL. |

## Contract và kiểm chứng

Role 2 cung cấp contract dữ liệu cho toàn bộ pipeline thông qua `DataEngine.get_order_facts(order_id)`. Hàm này hợp nhất kết quả từ ba domain agent thành một gói facts đã grounding, gồm trạng thái đơn, item/seller IDs, mốc giao carrier, mốc giao khách hàng, payment IDs, tổng item, freight, payment và evidence IDs hợp lệ.

Các helper dùng chung như `to_float`, `to_int`, `round_brl`, `parse_timestamp`, `is_after`, `elapsed_days`, `item_entity_id` và `payment_entity_id` giúp domain agent xử lý dữ liệu CSV nhất quán, tránh lệch format ID và sai số khi tính BRL.

```powershell
python run_pipeline.py
python validate_outputs.py
```

Kết quả đã kiểm chứng: 50 input được xử lý thành 50 output JSON; dữ liệu domain được chuyển tiếp sang Coordinator, Policy và Verifier mà không cần sửa tay output.

## Quyết định kỹ thuật

Chọn cơ chế lazy-load và index cache cho CSV để mỗi bảng chỉ đọc một lần, sau đó tra cứu nhiều case bằng index một-nhiều hoặc một-một. Cách này giữ code đơn giản nhưng vẫn đủ nhanh cho batch 50 ticket.

Tách riêng Order/Seller, Delivery và Payment thành domain agent độc lập để đúng tinh thần multi-agent: mỗi agent chỉ chịu trách nhiệm một vùng dữ liệu, trả về facts và evidence riêng, sau đó `DataEngine` hợp nhất và loại trùng evidence trước khi bàn giao cho Coordinator.

## Cam kết

Không commit API key, `.env`, `.venv` hoặc dữ liệu nộp không cần thiết. Các output của role 2 chỉ sử dụng dữ liệu có thật trong CSV Olist và tuân thủ chính sách `EC_POLICY_V1`.
