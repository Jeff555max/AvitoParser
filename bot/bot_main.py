
import telebot
from telebot import types
import subprocess
import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PAGE_SIZE = int(os.getenv("PAGE_SIZE", 5))

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

DB_PATH = os.environ.get("DB_PATH", "/db/results.db") if os.environ.get("DOCKER") else "results.db"

# --- Меню ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("▶️ Запустить парсер"))
    markup.add(types.KeyboardButton("📋 Журнал"), types.KeyboardButton("⚙️ Настройки"))
    return markup

def journal_menu(page=0, total=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    if page > 0:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"journal:{page-1}"))
    if (page+1)*PAGE_SIZE < total:
        buttons.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data=f"journal:{page+1}"))
    if buttons:
        markup.row(*buttons)
    return markup

# --- Команды ---
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "▶️ Запустить парсер")
def run_parser(message):
    bot.send_message(message.chat.id, "Парсер запущен! Ожидайте завершения...")
    # Запуск main.py как отдельного процесса
    try:
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            bot.send_message(message.chat.id, "Парсинг завершён успешно!")
        else:
            bot.send_message(message.chat.id, f"Ошибка при парсинге:\n{result.stderr}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка запуска парсера: {e}")

@bot.message_handler(func=lambda m: m.text == "📋 Журнал")
def show_journal(message):
    page = 0
    posts, total = get_posts_page(page)
    text = render_posts(posts, page, total)
    bot.send_message(message.chat.id, text, reply_markup=journal_menu(page, total), parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith("journal:"))
def paginate_journal(call):
    page = int(call.data.split(":")[1])
    posts, total = get_posts_page(page)
    text = render_posts(posts, page, total)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=journal_menu(page, total), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def settings_menu(message):
    bot.send_message(message.chat.id, "Настройки пока не реализованы.")

# --- Журнал ---
def get_posts_page(page):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, price, address, link FROM objects ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE_SIZE, page*PAGE_SIZE))
    rows = c.fetchall()
    c.execute("SELECT COUNT(*) FROM objects")
    total = c.fetchone()[0]
    conn.close()
    return rows, total

def render_posts(posts, page, total):
    if not posts:
        return "Нет объектов в базе."
    text = f"<b>Журнал объектов (стр. {page+1})</b>\n\n"
    for idx, (title, price, address, link) in enumerate(posts, 1):
        text += f"<b>{title}</b>\nЦена: {price}\nАдрес: {address}\n<a href=\"{link}\">Ссылка</a>\n\n"
    text += f"Показано {min((page+1)*PAGE_SIZE, total)} из {total} объектов."
    return text

if __name__ == "__main__":
    bot.polling(none_stop=True)
