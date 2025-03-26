# ===== 1. Import thư viện =====
import telebot
import re

# ===== 2. Cấu hình bot =====
TOKEN = '7922091397:AAHpyLRpiXr_IkDMFLPjy-IR048-RE_SZKI'  # Thay bằng token từ BotFather
bot = telebot.TeleBot(TOKEN)

# ===== 3. Hàm tách văn bản =====
import re

def tach_van_ban(van_ban):
    # Thay 2d, 2đ thành 2dai
    van_ban = re.sub(r'(?<!\S)2[đd](?!\S)', '2dai', van_ban)
    # Thay 3d, 3đ thành 3dai
    van_ban = re.sub(r'(?<!\S)3[đd](?!\S)', '3dai', van_ban)
    # Thay 4d, 4đ thành 4dai
    van_ban = re.sub(r'(?<!\S)4[đd](?!\S)', '4dai', van_ban)

    # Chuẩn hóa khoảng trắng trước các cụm từ đặc biệt
    van_ban = re.sub(r'(?<!\s)(bl|xc|bldao|xcdao|xien|dd|da|dau|dui|xdao|bdao)', r' \1', van_ban)
    # Xóa khoảng trắng sau các cụm từ đặc biệt
    van_ban = re.sub(r'\b(bl|xc|bldao|xcdao|dd|da|x|b|d|dau|dui)\s+', r'\1', van_ban)

    # Thêm khoảng trắng giữa số và chữ (trừ 'd', 'n'), bỏ qua các cụm đặc biệt
    van_ban = re.sub(r'(\d)([a-ce-m-oA-CE-M-Oq-zQ-Z])', r'\1 \2', van_ban)

    # Bỏ khoảng trắng trước 'n'
    van_ban = re.sub(r'\s+n', 'n', van_ban)

    # Thay dấu chấm, dấu phẩy thành khoảng trắng
    van_ban = re.sub(r'[.,]', ' ', van_ban)

    # Thay thế các cụm đặc biệt
    replacements = {
        r'\bb\đ(?=\d*)': 'bldao',  # Sửa bđ thành bldao kể cả khi có số phía sau
        r'\bx\đ(?=\d*)': 'xcdao',  # Sửa xđ thành xcdao kể cả khi có số phía sau
        r'dxc': 'xcdao',
        r'\bđđ\b': 'dd',
        r'\bx(\d+)': r'xc\1',
        r'\bb(\d+)': r'bl\1',
        r'\bxdao': 'xcdao',  # Thay xdao bằng xcdao
        r'\bdx': 'xcdao'     # Thay dx bằng xcdao
    }
    for pattern, replacement in replacements.items():
        van_ban = re.sub(pattern, replacement, van_ban)

    # Chuyển '05' thành '0.5'
    van_ban = re.sub(r'(?<!\d)05(?!\d)', '0.5', van_ban) 

    # Bỏ khoảng trắng trước 'dai'
    van_ban = re.sub(r'\s+(dai)', r'\1', van_ban)

    return van_ban

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    van_ban_goc = message.text
    ket_qua = tach_van_ban(van_ban_goc)
    bot.reply_to(message, ket_qua)

print('Bot is running...')
bot.polling()
