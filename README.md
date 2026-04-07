# Project: Smart Travel Assistant (TravelBuddy) - Lab 04

## 1. Mục tiêu cốt lõi

Xây dựng một AI Agent sử dụng **LangGraph** để giúp người dùng lập kế hoạch du lịch toàn diện. Agent phải có khả năng suy luận đa bước, kết hợp dữ liệu từ nhiều nguồn để đưa ra câu trả lời cuối cùng thay vì trả lời rời rạc.

## 2. Ràng buộc kỹ thuật (Tech Stack)

- **Framework:** LangGraph (yêu cầu quản lý state, nodes, và edges).
- **LLM:** Qwen 3.6 (gọi qua OpenRouter API bằng thư viện OpenAI).
- **API Base URL:** `https://openrouter.ai/api/v1`
- **Ngôn ngữ:** Python.

## 3. Chức năng chính (Tools)

Agent cần được cung cấp các công cụ (tools) giả lập sau:

- `search_flights`: Tra cứu vé máy bay dựa trên địa điểm và thời gian.
- `check_budget`: Quản lý và trừ dần ngân sách người dùng cung cấp.
- `Google Hotels`: Tìm khách sạn phù hợp với số tiền còn lại sau khi trừ tiền vé.

## 4. Logic luồng công việc (Graph Flow)

Agent phải tuân thủ quy trình tư duy:

1. Nhận yêu cầu (Ví dụ: "Đi Đà Nẵng, budget 5 triệu").
2. Tra cứu vé máy bay trước.
3. Tính toán chi phí còn lại (`Remaining = Total - Flight`).
4. Tìm khách sạn dựa trên `Remaining`.
5. Tổng hợp và phản hồi: "Với 5tr, vé máy bay hết X, còn lại Y nên tôi gợi ý khách sạn Z..."

## 5. Quy tắc phản hồi (Agent Rules)

- **Không trả lời rời rạc:** Phải thực hiện tất cả các bước tra cứu trước khi đưa ra kết quả cuối cùng cho người dùng.
- **Tính toán chính xác:** Luôn kiểm tra ngân sách trước khi gợi ý khách sạn.
- **Ngôn ngữ:** Tiếng Việt.
- **Định dạng code:** Tuân thủ Git Conventional Commits khi thực hiện commit.
