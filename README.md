# Rulebase Chatbot

## Giới thiệu
`rulebase_chatbot` là một chatbot đơn giản được xây dựng theo kiểu **rule-based**, chạy với Python và giao diện Web. Chatbot này sử dụng các quy tắc định sẵn (patterns / rules) để nhận diện `intent` từ người dùng và trả lời các câu hỏi phổ biến như về giá, giờ mở cửa, địa chỉ, menu, wifi, v.v.

---

## Tính năng

- Nhận diện intent dựa vào rule (pattern matching) thay vì machine learning.  
- Hỗ trợ các intent chính như:
  - Hỏi giá món (`ask_price`)  
  - Hỏi menu (`ask_menu`)  
  - Hỏi giờ mở cửa hoặc thời gian hoạt động (`ask_hours`)  
  - Hỏi địa chỉ quán (`ask_address`)  
  - Hỏi wifi / mạng internet (`ask_wifi`)  
- Giao diện web đơn giản để nhập câu hỏi và nhận phản hồi.  

---

## Cấu trúc project

```
rulebase_chatbot/
│── main.py             # Backend server (FastAPI) xử lý logic rule-based
│── templates/
│    └── index.html     # Giao diện web chatbot
│── static/
│    └── style.css      # Style cho frontend
│── requirements.txt    # Thư viện cần cài
│── README.md           # Tệp mô tả project này
```

---

## Yêu cầu

- Python 3.x  
- Các thư viện trong `requirements.txt` (ví dụ: fastapi, uvicorn, jinja2, v.v.)

---

## Cài đặt

```bash
# Clone repository
git clone https://github.com/nguyenduongtrong/rulebase_chatbot.git
cd rulebase_chatbot

# Cài thư viện phụ thuộc
pip install -r requirements.txt
```

---

## Cách chạy

```bash
uvicorn main:app --reload
```

- Sau khi server chạy, mở trình duyệt và truy cập địa chỉ `http://127.0.0.1:8000`  
- Nhập câu hỏi vào giao diện web, bot sẽ trả lời dựa vào rule đã thiết lập  

---

## Ví dụ câu hỏi

- `Giá cà phê sữa bao nhiêu?`  
- `Mấy giờ quán mở cửa?`  
- `Quán nằm ở đâu?`  
- `Có wifi không?`  
- `Menu quán gồm những gì?`

---

## Hạn chế & Có thể cải thiện

- Bot dựa vào rule (pattern) cố định, sẽ **khó hiểu đúng** nếu người dùng nói cách khác hoặc có lỗi chính tả  
- Không có khả năng học từ dữ liệu mới  
- Giao diện đơn giản, chưa tối ưu UX  
- Có thể mở rộng:

  - Thêm nhiều rule với cấu trúc câu phong phú hơn  
  - Sử dụng phân tích cú pháp (parser) hoặc NLP để hiểu câu hỏi linh hoạt hơn  
  - Hỗ trợ từ đồng nghĩa, xử lý lỗi chính tả  
  - Logging để ghi lại các câu bot chưa hiểu để cải thiện rule

---