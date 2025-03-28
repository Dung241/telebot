# ===== 1. Import thư viện =====
import telebot
import re
import os
from flask import Flask

# ===== 2. Cấu hình bot =====
TOKEN = '7922091397:AAHpyLRpiXr_IkDMFLPjy-IR048-RE_SZKI'  # Thay bằng token từ BotFather
bot = telebot.TeleBot(TOKEN)

# ===== 3. Hàm tách văn bản =====
import re

def preprocess_van_ban(van_ban):
    """ Tiền xử lý văn bản theo quy tắc chuẩn hóa """
    # Thay dấu chấm, dấu phẩy thành khoảng trắng
    van_ban = re.sub(r'[.,]', ' ', van_ban)

    # Thay các trường hợp 2d, 2đ, 2d. thành 2dai
    van_ban = re.sub(r'(?<!\S)2[đd]\.?', '2dai', van_ban)

    # Thay các trường hợp 3d, 3đ, 3d. thành 3dai
    van_ban = re.sub(r'(?<!\S)3[đd]\.?', '3dai', van_ban)

    # Thay các trường hợp 4d, 4đ, 4d. thành 4dai
    van_ban = re.sub(r'(?<!\S)4[đd]\.?', '4dai', van_ban)

    # Chuẩn hóa khoảng trắng trước các cụm từ đặc biệt
    van_ban = re.sub(
        r'(?<!\s)(bl|xc|bldao|xcdao|xien|dd|da|dau|dui|xdao|bdao)', r' \1',
        van_ban)
    # Xóa khoảng trắng sau các cụm từ đặc biệt
    van_ban = re.sub(r'\b(bl|xc|bldao|xcdao|dd|da|x|b|d|dau|dui)\s+', r'\1',
                     van_ban)

    # Thêm khoảng trắng giữa số và chữ (trừ 'd', 'n'), bỏ qua các cụm đặc biệt
    van_ban = re.sub(r'(\d)([a-ce-m-oA-CE-M-Oq-zQ-Z])', r'\1 \2', van_ban)

    # Chuyển '05' thành '0.5'
    van_ban = re.sub(r'(?<!\d)05(?!\d)', '0.5', van_ban)

    # Thay thế các cụm đặc biệt
    replacements = {
        r'\bb\đ(?=\d*)': 'bldao',
        r'\bx\đ(?=\d*)': 'xcdao',
        r'dxc': 'xcdao',
        r'\bđđ\b': 'dd',
        r'\bx(\d+)': r'xc\1',
        r'\bb(\d+)': r'bl\1',
        r'\bxdao': 'xcdao',
        r'\bdx': 'xcdao'
    }
    for pattern, replacement in replacements.items():
        van_ban = re.sub(pattern, replacement, van_ban)

    # Bỏ khoảng trắng trước 'n' và số kèm 'n'
    van_ban = re.sub(r'\s+(n\d*)', r'\1', van_ban)

    # Bỏ khoảng trắng trước 'dai'
    van_ban = re.sub(r'\s+(dai)', r'\1', van_ban)

    # Xóa khoảng trắng sau tất cả các cụm đặc biệt
    van_ban = re.sub(
        r'\b(bl|b|xc|bldao|xcdao|xien|dd|da|dau|dui|xdao|bdao)\s+', r'\1',
        van_ban)

    return van_ban

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    van_ban_goc = message.text
    ket_qua = preprocess_van_ban(van_ban_goc)
    bot.reply_to(message, ket_qua)

print('Bot is running...')
bot.polling()


# ===== 3. Chạy Flask để giữ Web Service hoạt động =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ===== 4. Chạy bot và server Flask =====
if __name__ == '__main__':
    from threading import Thread
    
    # Chạy bot trên một luồng riêng
    def run_bot():
        bot.polling()

    Thread(target=run_bot).start()

    # Chạy Flask trên cổng Render yêu cầu
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
