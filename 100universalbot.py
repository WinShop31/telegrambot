import asyncio
import json
import os
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)

API_TOKEN = "7401192069:AAFbzB5VJ92irSegGpu74yORCOY2-VOwayI"

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

DATA_FILE = "texts.json"
USER_LIMIT = 20  # лимит текстов на пользователя


# ---------------------- ФАЙЛОВЫЕ ОПЕРАЦИИ ----------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data({"texts": []})
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------------------- КРАСИВЫЕ ОТВЕТЫ ----------------------

def ok(text):
    return f"✨ <b>Готово!</b>\n{text}"

def err(text):
    return f"🚫 <b>Ошибка:</b> {text}"

def info(text):
    return f"📌 {text}"


# ---------------------- /addtext ----------------------

@dp.message(F.text.startswith("/addtext"))
async def add_text(msg: types.Message):
    data = load_data()

    parts = msg.text.split(" ", 1)
    if len(parts) < 2:
        return await msg.reply(err("Использование: /addtext <твой текст>"))

    text = parts[1].strip()

    if len(text) < 3:
        return await msg.reply(err("Текст слишком короткий."))

    if len(text) > 300:
        return await msg.reply(err("Текст слишком длинный (макс 300 символов)."))

    # антиспам: нельзя одинаковые
    for t in data["texts"]:
        if t["text"].lower() == text.lower():
            return await msg.reply(err("Такой текст уже существует."))

    # лимит на пользователя
    user_texts = [t for t in data["texts"] if t["author_id"] == msg.from_user.id]
    if len(user_texts) >= USER_LIMIT:
        return await msg.reply(err(f"Ты достиг лимита ({USER_LIMIT}) текстов."))

    new_id = max([t["id"] for t in data["texts"]], default=0) + 1

    data["texts"].append({
        "id": new_id,
        "author_id": msg.from_user.id,
        "author_name": msg.from_user.username or msg.from_user.full_name,
        "text": text
    })

    save_data(data)

    await msg.reply(ok(f"Твой текст сохранён!\n🆔 ID: <b>{new_id}</b>"))


# ---------------------- /mytexts ----------------------

@dp.message(F.text == "/mytexts")
async def my_texts(msg: types.Message):
    data = load_data()
    user_texts = [t for t in data["texts"] if t["author_id"] == msg.from_user.id]

    if not user_texts:
        return await msg.reply(info("У тебя нет добавленных текстов."))

    out = "📚 <b>Твои тексты:</b>\n\n"
    for t in user_texts:
        out += f"🆔 <b>{t['id']}</b>: {t['text']}\n"

    await msg.reply(out)


# ---------------------- /deltext <id> ----------------------

@dp.message(F.text.startswith("/deltext"))
async def del_text(msg: types.Message):
    data = load_data()

    parts = msg.text.split(" ", 1)
    if len(parts) < 2:
        return await msg.reply(err("Использование: /deltext <id>"))

    try:
        tid = int(parts[1])
    except:
        return await msg.reply(err("ID должен быть числом."))

    for t in data["texts"]:
        if t["id"] == tid:
            if t["author_id"] != msg.from_user.id:
                return await msg.reply(err("Ты не можешь удалить чужой текст."))
            data["texts"].remove(t)
            save_data(data)
            return await msg.reply(ok("Текст удалён."))

    await msg.reply(err("Текст с таким ID не найден."))


# ---------------------- /100 ----------------------

@dp.message(F.text == "/100")
async def hundred(msg: types.Message):
    if msg.chat.type not in ("group", "supergroup"):
        return await msg.reply("неа, данный бот исключительно для групп, ибо его кодер долбаеб")

    data = load_data()

    if not data["texts"]:
        return await msg.reply(info("Пока нет ни одного пользовательского текста."))

    chosen = random.choice(data["texts"])

    # тег пользователя, вызвавшего команду
    mention = f'<a href="tg://user?id={msg.from_user.id}">{msg.from_user.full_name}</a>'

    # подставляем тег в текст
    final_text = (
        f"{chosen['text'].replace('{mention}', mention)}\n\n"
        f"👤 <i>Добавил:</i> <b>{chosen['author_name']}</b>"
    )

    await msg.reply(final_text, reply_to_message_id=msg.message_id)


# ---------------------- /100help ----------------------

@dp.message(F.text == "/100help")
async def help_cmd(msg: types.Message):
    mention = f'<a href="tg://user?id={msg.from_user.id}">{msg.from_user.full_name}</a>'

    text = (
        f"{mention}, вот что я умею:\n\n"
        "🔥 <b>/100</b> — выдать случайный пользовательский текст с твоим тегом.\n"
        "📝 <b>/addtext &lt;текст&gt;</b> — добавить свой текст в базу.\n"
        "📚 <b>/mytexts</b> — показать твои добавленные тексты.\n"
        "🗑 <b>/deltext &lt;id&gt;</b> — удалить свой текст по ID.\n"
        "ℹ️ <b>/100info</b> — информация о разработчике.\n"
        "❓ <b>/100help</b> — показать это меню.\n\n"
        "⚠️ Лимиты и правила:\n"
        f"• максимум <b>{USER_LIMIT}</b> текстов на пользователя\n"
        "• нельзя добавлять одинаковые строки\n"
        "• бот работает только в группах\n"
    )

    await msg.reply(text)


# ---------------------- /100info ----------------------

@dp.message(F.text == "/100info")
async def hundred_info(msg: types.Message):
    info_text = (
        "мета разработчик — @fillsofficial\n"
        "поддержка на сервере — FCORP"
    )
    await msg.reply(info_text)


# ---------------------- ЛИЧКА ----------------------

@dp.message(F.chat.type == "private")
async def private_only(msg: types.Message):
    await msg.reply("неа, данный бот исключительно для групп, ибо его кодер долбаеб")


# ---------------------- СТАРТ ----------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
