import logging
import requests
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 🎯 Токен Telegram бота
TELEGRAM_TOKEN = "8574235178:AAHPhLYm0g4adMH0-evcj4Tsxp3hqyJax5Y"

# 🌐 Настройки API
API_URL = "https://litellm.tokengate.ru/v1/chat/completions"
API_KEY = "sk-q9e9WNdWoZra6XgZfMKiOw"

# 📚 Словарь моделей
MODELS = {
    "alice": {
        "id": "yandex/aliceai-llm/latest",
        "label": "🔵 Alice",
        "category": "🔵 Общего назначения"
    },
    "gigachat": {
        "id": "cloudru/GigaChat/GigaChat-2-Max",
        "label": "🟣 GigaChat",
        "category": "🟣 Продвинутая"
    },
    "yandexgpt-lite": {
        "id": "yandex/yandexgpt-lite/rc",
        "label": "🟢 YandexGPT‑Lite",
        "category": "🟢 Компактная"
    }
}

# 🔄 Текущая модель (по умолчанию)
current_model = "alice"

# 📂 Файл для хранения истории
HISTORY_FILE = "historys.txt"

logging.basicConfig(level=logging.INFO)


# 🧠 Функции работы с памятью
def load_history():
    """Загружает историю из файла в словарь"""
    if not os.path.exists(HISTORY_FILE):
        return {}
    histories = {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if " - " in line:
                chat_id, msgs = line.strip().split(" - ", 1)
                parts = msgs.split("|")
                history = []
                for p in parts:
                    p = p.strip()
                    if p.startswith("user:"):
                        history.append({"role": "user", "content": p.replace("user:", "").strip()})
                    elif p.startswith("assistant:"):
                        history.append({"role": "assistant", "content": p.replace("assistant:", "").strip()})
                histories[int(chat_id)] = history
    return histories


def save_history(histories):
    """Сохраняет историю в файл"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for chat_id, msgs in histories.items():
            msg_texts = " | ".join([f"{m['role']}: {m['content']}" for m in msgs])
            f.write(f"{chat_id} - {msg_texts}\n")


# 🧠 Загружаем историю при старте
user_histories = load_history()


# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Теперь я сохраняю в `historys.txt` и твои сообщения, и свои ответы.\n\n"
        "⚙️ Управление:\n"
        "• /model — сменить модель\n"
        "• /models — категории моделей\n"
        "• /current — активная модель\n"
        "• /clear — очистить историю"
    )


# 🔄 Команда /model
async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(MODELS["alice"]["label"], callback_data="alice")],
        [InlineKeyboardButton(MODELS["gigachat"]["label"], callback_data="gigachat")],
        [InlineKeyboardButton(MODELS["yandexgpt-lite"]["label"], callback_data="yandexgpt-lite")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔄 Выберите модель:\n"
        "🔵 Alice — универсальная\n"
        "🟣 GigaChat — продвинутая\n"
        "🟢 YandexGPT‑Lite — компактная",
        reply_markup=reply_markup
    )


# 🔄 Обработка inline‑кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_model
    query = update.callback_query
    await query.answer()

    choice = query.data
    if choice in MODELS:
        current_model = choice
        label = MODELS[choice]["label"]
        category = MODELS[choice]["category"]
        await query.edit_message_text(
            text=f"✅ Модель переключена на: *{label}*\nКатегория: {category}",
            parse_mode="Markdown"
        )


# 📋 Команда /models
async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = [
        "🟢 Компактная — лёгкая и быстрая",
        "🟡 Мультимодальная — работает с текстом и изображениями",
        "🔵 Общего назначения — универсальная",
        "🟠 Программирование — справляется с кодом",
        "🟣 Продвинутая — для сложных задач",
        "⚪️ Рассуждения — строит логические цепочки"
    ]
    await update.message.reply_text("📚 Категории моделей:\n" + "\n".join(categories))


# 🔎 Команда /current
async def current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    label = MODELS[current_model]["label"]
    category = MODELS[current_model]["category"]
    await update.message.reply_text(
        f"🔄 Текущая модель: *{label}*\nКатегория: {category}",
        parse_mode="Markdown"
    )


# 🧹 Команда /clear — очистка истории пользователя
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in user_histories:
        user_histories[chat_id] = []
        save_history(user_histories)
        await update.message.reply_text("🧹 История очищена!")
    else:
        await update.message.reply_text("ℹ️ У тебя пока нет сохранённой истории.")


# 💬 Основной чат с памятью
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_histories
    user_text = update.message.text
    chat_id = update.effective_chat.id

    if user_text.startswith("/"):
        return

    # Инициализация истории для пользователя
    if chat_id not in user_histories:
        user_histories[chat_id] = []

    # Добавляем сообщение пользователя
    user_histories[chat_id].append({"role": "user", "content": user_text})
    user_histories[chat_id] = user_histories[chat_id][-10:]

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": MODELS[current_model]["id"],
        "messages": user_histories[chat_id]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        result = response.json()
        bot_reply = result["choices"][0]["message"]["content"]

        # Добавляем ответ бота
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})
        user_histories[chat_id] = user_histories[chat_id][-10:]

        # Сохраняем историю в файл
        save_history(user_histories)

        formatted_reply = bot_reply.replace("**", "*")
    except Exception as e:
        formatted_reply = f"⚠️ Ошибка: {e}"

    await update.message.reply_text(f"💡 Ответ:\n{formatted_reply}", parse_mode="Markdown")


# 🏁 Запуск
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("model", set_model))
    app.add_handler(CommandHandler("models", list_models))
    app.add_handler(CommandHandler("current", current))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()


if __name__ == "__main__":
    main()
