import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)

API_TOKEN = "7401192069:AAFbzB5VJ92irSegGpu74yORCOY2-VOwayI"

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# Личка → сообщение "неа..."
@dp.message(F.chat.type == "private")
async def private_only(msg: types.Message):
    await msg.reply("неа, данный бот исключительно для групп, ибо его кодер долбаеб")

# Команда /100 в группах
@dp.message(F.text == "/100")
async def hundred(msg: types.Message):
    if msg.chat.type in ("group", "supergroup"):
        user = msg.from_user
        mention = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
        text = f'ты що ебнулся брад ? {mention}, давай не шали.'
        await msg.reply(text, reply=False)
    else:
        await msg.reply("неа, данный бот исключительно для групп, ибо его кодер долбаеб")

# Новая команда /100info
@dp.message(F.text == "/100info")
async def hundred_info(msg: types.Message):
    info_text = (
        "мета разработчик - @fillsofficial\n"
        "поддержка на сервере - FCORP"
    )
    await msg.reply(info_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())