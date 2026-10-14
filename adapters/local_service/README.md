# Local Service

`adapters/local_service` hiện là placeholder adapter cho local service path trong ATP.

Phạm vi:

- giữ architectural slot cho service-backed local integration
- không triển khai service runtime thật trong baseline hiện hành

Cập nhật 14/10/2026 (KD-ATP-009):

- chưa có use case cụ thể nào được gán cho slot này; không có mã, bài kiểm hay registry nào dùng nó
- tên `local_service` mơ hồ (bản kiểm toán thiết kế 2/4/2026, mục N-4): khác `adapters/subprocess` (thực thi mức tiến trình). Giữ nguyên tên vì đổi tên là đổi hình dạng adapter đã đóng băng
- gợi ý ví dụ "ollama HTTP endpoint" trong bản kiểm toán đó **không còn hợp lệ**: máy macOS không chạy Ollama hay model local (`00_AUTHORITY/Global_Mac_No_Ollama_Rule.md`, hiệu lực 3/6/2026). Slot này không được dùng để đưa LLM local trở lại
