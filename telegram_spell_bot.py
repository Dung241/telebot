# ===== 1. Import thư viện =====
import telebot
import re
import os
from flask import Flask, request


# ===== 2. Cấu hình bot =====
TOKEN = '7922091397:AAHpyLRpiXr_IkDMFLPjy-IR048-RE_SZKI'  # Thay bằng token từ BotFather
bot = telebot.TeleBot(TOKEN)

# ===== 3. Hàm tách văn bản =====
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
        r'\bxd(\d+)': r'xcdao\1',
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


def tach_cum_so_lenh(input_van_ban):
    tokens = input_van_ban.split()
    groups = []
    temp_numbers = []
    temp_commands = []

    # Phân tách thành cụm số + cụm lệnh
    for token in tokens:
        if re.match(r'^\d+$', token):  # Nếu là số
            if temp_commands:
                groups.append((temp_numbers, temp_commands))
                temp_numbers, temp_commands = [], []
            temp_numbers.append(token)
        else:  # Nếu là lệnh
            temp_commands.append(token)

    # Thêm cụm cuối cùng nếu còn sót
    if temp_numbers or temp_commands:
        groups.append((temp_numbers, temp_commands))

    return groups


def xu_ly_cum_so_lenh(groups):
    result = []

    for item in groups:
        if not isinstance(item, tuple) or len(item) != 2:
            print(f"Lỗi dữ liệu: {item}")  # In ra lỗi để kiểm tra
            continue  # Bỏ qua phần tử lỗi

        numbers, commands = item  # Giờ đây chắc chắn có đủ 2 phần tử

        if not numbers:
            result.append(" ".join(commands))
            continue

        # Nhóm số 2 chữ số -> giữ nguyên
        if all(len(num) == 2 for num in numbers):
            result.append(" ".join(numbers + commands))

        # Nhóm số 3 chữ số
        elif all(len(num) == 3 for num in numbers):
            bldao_xcdao_cmds = [
                cmd for cmd in commands if "bldao" in cmd or "xcdao" in cmd
            ]
            dd_cmds = [cmd for cmd in commands if "dd" in cmd]
            other_cmds = [
                cmd for cmd in commands
                if cmd not in bldao_xcdao_cmds and cmd not in dd_cmds
            ]

            if len(numbers) == 1 and len(commands) == 1:
                result.append(f"{numbers[0]} {commands[0]}"
                              )  # Nếu chỉ có 1 số + 1 lệnh -> giữ nguyên
            elif len(dd_cmds) > 0 or len(bldao_xcdao_cmds) > 0:
                if other_cmds:
                    result.append(
                        " ".join(numbers + other_cmds)
                    )  # Nhóm số + lệnh không phải `dd` hoặc `bldao`
                for num in numbers:
                    short_num = num[1:]  # Bỏ hàng trăm (lấy 2 số cuối)
                    for cmd in dd_cmds:
                        result.append(f"{short_num} {cmd}"
                                      )  # Nhóm số (bỏ hàng trăm) + `dd`
                    for cmd in bldao_xcdao_cmds:
                        result.append(
                            f"{num} {cmd}")  # Nhóm số + `bldao/xcdao`
            else:
                result.append(" ".join(numbers + commands))

        # Nhóm số 4 chữ số
        elif all(len(num) == 4 for num in numbers):
            bldao_cmds = [cmd for cmd in commands if "bldao" in cmd]
            xcdao_cmds = [cmd for cmd in commands if "xcdao" in cmd]
            xc_cmds = [
                cmd for cmd in commands if "xc" in cmd and "xcdao" not in cmd
            ]
            other_cmds = [
                cmd for cmd in commands if cmd not in bldao_cmds
                and cmd not in xcdao_cmds and cmd not in xc_cmds
            ]

            if len(numbers) == 1 and len(commands) == 1:
                result.append(f"{numbers[0]} {commands[0]}"
                              )  # Nếu chỉ có 1 số + 1 lệnh -> giữ nguyên
            else:
                if other_cmds:
                    result.append(
                        " ".join(numbers + other_cmds)
                    )  # Nhóm số + lệnh không phải `bldao`, `xcdao`, `xc`
                for num in numbers:
                    for cmd in bldao_cmds:
                        result.append(f"{num} {cmd}")  # Nhóm số + `bldao`
                    short_num = num[1:]
                    for cmd in xcdao_cmds:
                        result.append(f"{short_num} {cmd}"
                                      )  # Nhóm số bỏ hàng ngàn + `xcdao`
                    for cmd in xc_cmds:
                        result.append(f"{short_num} {cmd}"
                                      )  # Nhóm số bỏ hàng ngàn + `xc`
        else:  # Trường hợp khác giữ nguyên
            result.append(" ".join(numbers + commands))

    return "; ".join(map(str.strip, result))



@bot.message_handler(func=lambda message: True)
def handle_message(message):
    van_ban_goc = message.text  # Lấy nội dung tin nhắn từ người dùng
    van_ban_da_xu_ly = preprocess_van_ban(van_ban_goc)
    groups = tach_cum_so_lenh(van_ban_da_xu_ly)
    ket_qua = xu_ly_cum_so_lenh(groups)
    bot.reply_to(message, ket_qua)  # Trả kết quả về cho người dùng


print('Bot is running...')


# ===== 3. Chạy Flask để giữ Web Service hoạt động =====
TOKEN = "7922091397:AAHpyLRpiXr_IkDMFLPjy-IR048-RE_SZKI"
WEBHOOK_URL="https://telebot-1-io0s.onrender.com/webhook")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def receive_update():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

if __name__ == "__main__":
    # Lấy PORT từ biến môi trường (Render cấp)
    port = int(os.environ.get("PORT", 10000))

    # Thiết lập webhook
    bot.remove_webhook()
    bot.set_webhook(url="https://telebot-1-io0s.onrender.com/webhook")

    # Chạy Flask server
    app.run(host="0.0.0.0", port=port)

