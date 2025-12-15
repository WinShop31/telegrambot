import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 🎯 Токен Telegram бота
TELEGRAM_TOKEN = "8574235178:AAHPhLYm0g4adMH0-evcj4Tsxp3hqyJax5Y"

# 🌐 Настройки API
API_URL = "https://litellm.tokengate.ru/v1/chat/completions"
API_KEY = "sk-q9e9WNdWoZra6XgZfMKiOw"

# 📚 Словарь моделей с ID, меткой и категорией
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

logging.basicConfig(level=logging.INFO)

# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я — твой умный бот 🤖\n"
        "Напиши мне что-нибудь, и я отвечу через выбранную LLM‑модель.\n\n"
        "⚙️ Управление:\n"
        "• /model — сменить модель\n"
        "• /models — категории моделей\n"
        "• /current — активная модель\n"
    )

# 🔄 Команда /model — выбор модели с цветными кружками
async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(MODELS["alice"]["label"], callback_data="alice")],
        [InlineKeyboardButton(MODELS["gigachat"]["label"], callback_data="gigachat")],
        [InlineKeyboardButton(MODELS["yandexgpt-lite"]["label"], callback_data="yandexgpt-lite")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔄 Выберите модель:\n"
        "🔵 Alice — универсальная, подходит для общения и повседневных задач\n"
        "🟣 GigaChat — мощная, лучше справляется с техническими и аналитическими запросами\n"
        "🟢 YandexGPT‑Lite — компактная, лёгкая и быстрая",
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

# 📋 Команда /models — категории с описанием
async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = [
        "🟢 Компактная — лёгкая и быстрая, подходит для ограниченных устройств",
        "🟡 Мультимодальная — работает с текстом, изображениями и другими типами данных",
        "🔵 Общего назначения — универсальная, сбалансированная для повседневных задач",
        "🟠 Программирование — справляется с кодом, логикой и техническими запросами",
        "🟣 Продвинутая — мощная, подходит для сложных рассуждений и аналитики",
        "⚪️ Рассуждения — строит логические цепочки и объясняет выводы"
    ]
    await update.message.reply_text("📚 Категории моделей:\n" + "\n".join(categories))

# 🔎 Команда /current — показывает активную модель и её категорию
async def current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    label = MODELS[current_model]["label"]
    category = MODELS[current_model]["category"]
    await update.message.reply_text(
        f"🔄 Текущая модель: *{label}*\nКатегория: {category}",
        parse_mode="Markdown"
    )

# 💬 Основной чат
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Фильтр: команды не отправляем на API
    if user_text.startswith("/"):
        return

    # Фейковое печатанье
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": MODELS[current_model]["id"],
        "messages": [{"role": "user", "content": user_text}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        result = response.json()
        bot_reply = result["choices"][0]["message"]["content"]
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
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()