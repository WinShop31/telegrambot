import asyncio
import json
import os
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

API_TOKEN = "7401192069:AAGtnlXUtaJN4qQ5EEchbBOkdl3HaAynLhI"

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

DATA_FILE = "texts.json"
USER_LIMIT = 20
DEFAULT_LANG = "ru"


# ---------------------- ФАЙЛОВЫЕ ОПЕРАЦИИ ----------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data({"texts": [], "settings": {}})
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------------------- ЛОКАЛИЗАЦИЯ ----------------------

def get_chat_lang(chat_id):
    data = load_data()
    return data.get("settings", {}).get(str(chat_id), {}).get("lang", DEFAULT_LANG)


def set_chat_lang(chat_id, lang):
    data = load_data()
    if "settings" not in data:
        data["settings"] = {}
    data["settings"][str(chat_id)] = {"lang": lang}
    save_data(data)


# ---------------------- ТЕКСТЫ ЛОКАЛИЗАЦИИ ----------------------

L = {
    "ru": {
        "add_short": "Текст слишком короткий.",
        "add_long": "Текст слишком длинный (макс 300 символов).",
        "add_exists": "Такой текст уже существует.",
        "add_limit": "Ты достиг лимита текстов.",
        "add_ok": "Твой текст сохранён!\n🆔 ID: <b>{id}</b>",

        "my_none": "У тебя нет добавленных текстов.",
        "my_title": "📚 <b>Твои тексты:</b>",

        "del_not_found": "Текст с таким ID не найден.",
        "del_not_owner": "Ты не можешь удалить чужой текст.",
        "del_ok": "Текст удалён.",

        "100_none": "Пока нет ни одного пользовательского текста.",

        "settings_title": "🌐 <b>Выбери язык интерфейса:</b>",
        "settings_ru": "✨ Язык изменён на <b>Русский</b>.",
        "settings_en": "✨ Language changed to <b>English</b>.",

        "help": (
            "{mention}, вот что я умею:\n\n"
            "🔥 <b>/100</b> — выдать случайный пользовательский текст с твоим тегом.\n"
            "📝 <b>/addtext &lt;текст&gt;</b> — добавить свой текст.\n"
            "📚 <b>/mytexts</b> — показать твои тексты.\n"
            "🗑 <b>/deltext &lt;id&gt;</b> — удалить свой текст.\n"
            "🌐 <b>/100settings</b> — выбрать язык.\n"
            "ℹ️ <b>/100info</b> — информация.\n"
            "❓ <b>/100help</b> — это меню.\n\n"
            "⚠️ Лимиты:\n"
            f"• максимум <b>{USER_LIMIT}</b> текстов\n"
            "• нельзя добавлять одинаковые строки\n"
            "• бот работает только в группах\n"
        ),

        "private": "неа, данный бот исключительно для групп, ибо его кодер долбаеб"
    },

    "en": {
        "add_short": "Text is too short.",
        "add_long": "Text is too long (max 300 chars).",
        "add_exists": "This text already exists.",
        "add_limit": "You reached your text limit.",
        "add_ok": "Your text has been saved!\n🆔 ID: <b>{id}</b>",

        "my_none": "You have no added texts.",
        "my_title": "📚 <b>Your texts:</b>",

        "del_not_found": "Text with this ID not found.",
        "del_not_owner": "You cannot delete someone else's text.",
        "del_ok": "Text deleted.",

        "100_none": "There are no user texts yet.",

        "settings_title": "🌐 <b>Select interface language:</b>",
        "settings_ru": "✨ Language changed to <b>Russian</b>.",
        "settings_en": "✨ Language changed to <b>English</b>.",

        "help": (
            "{mention}, here is what I can do:\n\n"
            "🔥 <b>/100</b> — send a random user text with your mention.\n"
            "📝 <b>/addtext &lt;text&gt;</b> — add your own text.\n"
            "📚 <b>/mytexts</b> — show your texts.\n"
            "🗑 <b>/deltext &lt;id&gt;</b> — delete your text.\n"
            "🌐 <b>/100settings</b> — choose language.\n"
            "ℹ️ <b>/100info</b> — info.\n"
            "❓ <b>/100help</b> — this menu.\n\n"
            "⚠️ Limits:\n"
            f"• max <b>{USER_LIMIT}</b> texts\n"
            "• no duplicates\n"
            "• bot works only in groups\n"
        ),

        "private": "nope, this bot works only in groups"
    }
}


# ---------------------- /addtext ----------------------

@dp.message(F.text.startswith("/addtext"))
async def add_text(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    T = L[lang]

    data = load_data()

    parts = msg.text.split(" ", 1)
    if len(parts) < 2:
        return await msg.reply("Usage: /addtext <text>")

    text = parts[1].strip()

    if len(text) < 3:
        return await msg.reply(T["add_short"])

    if len(text) > 300:
        return await msg.reply(T["add_long"])

    for t in data["texts"]:
        if t["text"].lower() == text.lower():
            return await msg.reply(T["add_exists"])

    user_texts = [t for t in data["texts"] if t["author_id"] == msg.from_user.id]
    if len(user_texts) >= USER_LIMIT:
        return await msg.reply(T["add_limit"])

    new_id = max([t["id"] for t in data["texts"]], default=0) + 1

    data["texts"].append({
        "id": new_id,
        "author_id": msg.from_user.id,
        "author_name": msg.from_user.username or msg.from_user.full_name,
        "text": text
    })

    save_data(data)

    await msg.reply(T["add_ok"].format(id=new_id))


# ---------------------- /mytexts ----------------------

@dp.message(F.text == "/mytexts")
async def my_texts(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    T = L[lang]

    data = load_data()
    user_texts = [t for t in data["texts"] if t["author_id"] == msg.from_user.id]

    if not user_texts:
        return await msg.reply(T["my_none"])

    out = T["my_title"] + "\n\n"
    for t in user_texts:
        out += f"🆔 <b>{t['id']}</b>: {t['text']}\n"

    await msg.reply(out)


# ---------------------- /deltext ----------------------

@dp.message(F.text.startswith("/deltext"))
async def del_text(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    T = L[lang]

    data = load_data()

    parts = msg.text.split(" ", 1)
    if len(parts) < 2:
        return await msg.reply("Usage: /deltext <id>")

    try:
        tid = int(parts[1])
    except:
        return await msg.reply("ID must be a number.")

    for t in data["texts"]:
        if t["id"] == tid:
            if t["author_id"] != msg.from_user.id:
                return await msg.reply(T["del_not_owner"])
            data["texts"].remove(t)
            save_data(data)
            return await msg.reply(T["del_ok"])

    await msg.reply(T["del_not_found"])


# ---------------------- /100 ----------------------

@dp.message(F.text == "/100")
async def hundred(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    T = L[lang]

    if msg.chat.type not in ("group", "supergroup"):
        return await msg.reply(T["private"])

    data = load_data()

    if not data["texts"]:
        return await msg.reply(T["100_none"])

    chosen = random.choice(data["texts"])

    mention = f'<a href="tg://user?id={msg.from_user.id}">{msg.from_user.full_name}</a>'

    final_text = (
        f"{chosen['text'].replace('{mention}', mention)}\n\n"
        f"👤 <i>Added by:</i> <b>{chosen['author_name']}</b>" if lang == "en"
        else f"{chosen['text'].replace('{mention}', mention)}\n\n"
             f"👤 <i>Добавил:</i> <b>{chosen['author_name']}</b>"
    )

    await msg.reply(final_text, reply_to_message_id=msg.message_id)


# ---------------------- /100settings ----------------------

@dp.message(F.text == "/100settings")
async def settings_cmd(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    T = L[lang]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data=f"setlang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data=f"setlang_en")
        ]
    ])

    await msg.reply(T["settings_title"], reply_markup=kb)


@dp.callback_query(F.data.startswith("setlang_"))
async def set_language(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    set_chat_lang(call.message.chat.id, lang)

    if lang == "ru":
        await call.message.edit_text(L["ru"]["settings_ru"])
    else:
        await call.message.edit_text(L["en"]["settings_en"])

    await call.answer()


# ---------------------- /100help ----------------------

@dp.message(F.text == "/100help")
async def help_cmd(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    T = L[lang]

    mention = f'<a href="tg://user?id={msg.from_user.id}">{msg.from_user.full_name}</a>'

    await msg.reply(T["help"].format(mention=mention))


# ---------------------- /100info ----------------------

@dp.message(F.text == "/100info")
async def hundred_info(msg: types.Message):
    await msg.reply("мета разработчик — @fillsofficial\nподдержка — FCORP")


# ---------------------- ЛИЧКА ----------------------

@dp.message(F.chat.type == "private")
async def private_only(msg: types.Message):
    lang = get_chat_lang(msg.chat.id)
    await msg.reply(L[lang]["private"])


# ---------------------- СТАРТ ----------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
