from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import re
import unicodedata
import difflib

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class UserMessage(BaseModel):
    message: str

# Danh sách sản phẩm và giá (dùng để rule extract)
PRODUCTS = {
    "latte": "45.000 VND",
    "cappuccino": "50.000 VND",
    "americano": "40.000 VND",
    "espresso": "35.000 VND",
    "trà sữa": "42.000 VND",
    "bánh": "25.000 VND (tùy loại)",
    "croissant": "28.000 VND"
}

# Ta sẽ có 10 rules (intent) với các mẫu biểu thức chính quy (những rule này là "grammar-ish" - matching patterns)
RULES = [
    {
        "name": "hours",
        "patterns": [r"giờ", r"mở cửa", r"mấy giờ", r"khi nào"],
        "response": lambda m: "Quán mở cửa từ 7:00 sáng đến 22:00 tối."
    },
    {
        "name": "price_query",
        "patterns": [r"bao nhiêu", r"giá", r"bao nhiêu tiền", r"cost|price"],
        "response": "price_handler"  # tên hàm sẽ được gọi
    },
    {
        "name": "menu",
        "patterns": [r"menu", r"danh sách", r"gì có", r"món nào"],
        "response": lambda m: "Menu gồm: " + ", ".join(PRODUCTS.keys()) + "."
    },
    {
        "name": "address",
        "patterns": [r"địa chỉ", r"ở đâu", r"nằm tại", r"chỗ nào"],
        "response": lambda m: "Quán nằm tại 123 Đường Nguyễn Huệ, Quận 1, TP.HCM."
    },
    {
        "name": "wifi",
        "patterns": [r"wifi", r"mật khẩu", r"password", r"pass"],
        "response": lambda m: "WiFi miễn phí. Mật khẩu: Coffee2025."
    },
    {
        "name": "open_now",
        "patterns": [r"đang mở", r"mở không", r"open\?", r"có mở"],
        "response": lambda m: "Hiện tại quán mở cửa (7:00 - 22:00)."
    },
    {
        "name": "takeaway",
        "patterns": [r"mang về", r"takeaway", r"mua mang về", r"giao hàng"],
        "response": lambda m: "Chúng tôi hỗ trợ mang về và giao hàng (phụ phí tùy khu vực)."
    },
    {
        "name": "payment",
        "patterns": [r"thanh toán", r"pay", r"ví điện tử", r"card"],
        "response": lambda m: "Chấp nhận tiền mặt, thẻ và các ví điện tử phổ biến."
    },
    {
        "name": "promotion",
        "patterns": [r"khuyến mãi", r"giảm giá", r"promo", r"deal"],
        "response": lambda m: "Hiện tại có chương trình mua 2 tặng 1 cho bánh vào thứ 3 hàng tuần."
    },
    {
        "name": "ingredient",
        "patterns": [r"thành phần", r"có gì", r"chứa", r"contains"],
        "response": lambda m: "Bạn muốn biết thành phần của món nào? Ví dụ: latte, cappuccino, trà sữa..."
    }
]

# Helper: chuẩn hóa text (lower, remove diacritics optionally)
def normalize_text(text):
    text = text.lower().strip()
    # keep accents for matching Vietnamese, but also create a version without accents for fuzzy
    no_accents = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    return text, no_accents

# Helper: cố gắng tìm sản phẩm trong câu
def find_product(text):
    text_lower, text_no_accent = normalize_text(text)
    # direct name match
    for prod in PRODUCTS:
        if prod in text_lower:
            return prod
    # try no-accent match
    for prod in PRODUCTS:
        prod_no_accent = ''.join(c for c in unicodedata.normalize('NFKD', prod) if not unicodedata.combining(c))
        if prod_no_accent in text_no_accent:
            return prod
    # fuzzy match on words
    words = re.findall(r"[\w\u00C0-\u017F]+", text_no_accent)
    prod_names_no_accent = {prod: ''.join(c for c in unicodedata.normalize('NFKD', prod) if not unicodedata.combining(c)) for prod in PRODUCTS}
    for w in words:
        matches = difflib.get_close_matches(w, prod_names_no_accent.values(), n=1, cutoff=0.8)
        if matches:
            # find the prod key for the matched value
            for prod, na in prod_names_no_accent.items():
                if na == matches[0]:
                    return prod
    return None

# Price handler - trả lời câu hỏi giá dựa trên parsing (grammar-ish)
def price_handler(message):
    prod: str | None = find_product(message)
    if prod:
        return f"{prod.title()} có giá {PRODUCTS[prod]}."
    # nếu không tìm thấy sản phẩm cụ thể, đề xuất
    # kiểm tra nếu câu hỏi dạng "giá bao nhiêu" nhưng không rõ món
    return "Bạn hỏi về giá món nào? Ví dụ: 'Giá latte bao nhiêu?' hoặc 'Bao nhiêu tiền một cappuccino?'."

# Hàm chính trả lời theo RULES
def chatbot_response(user_input: str) -> str:
    text, text_no_acc = normalize_text(user_input)
    # kiểm tra từng rule theo thứ tự (tương tự grammar rules)
    for rule in RULES:
        for patt in rule["patterns"]:
            # dùng regex search để cho phép biểu thức nhỏ
            if re.search(patt, text, flags=re.IGNORECASE):
                handler = rule["response"]
                if isinstance(handler, str) and handler == "price_handler":
                    return price_handler(user_input)
                elif callable(handler):
                    return handler(user_input)
                else:
                    return str(handler)
    # Nếu không match rule nào, thử dò sản phẩm trực tiếp (câu ngắn như "latte?")
    prod = find_product(user_input)
    if prod:
        return f"{prod.title()} có giá {PRODUCTS[prod]}."
    # fallback
    return "Xin lỗi, tôi chưa hiểu. Bạn có thể hỏi về menu, giá, giờ mở cửa, địa chỉ, wifi, khuyến mãi..."

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat(user_message: UserMessage):
    response = chatbot_response(user_message.message)
    return {"reply": response}
