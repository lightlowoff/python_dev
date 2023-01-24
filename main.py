from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('API_KEY'))
dp = Dispatcher(bot)

with open("users.txt", "r") as file:
    whitelist = [int(line.strip()) for line in file if line.strip() != ""]

admin = [int(os.getenv("ADMIN"))]

approved = lambda message: message.from_user.id in whitelist
guest = lambda message: message.from_user.id not in whitelist
owner = lambda message: message.from_user.id in admin


@dp.message_handler(approved, commands="start")
async def info_for_approved(message: types.Message):
    await message.reply("/help - Просмотр всех комманд.:")


@dp.message_handler(guest, commands="start")
async def info_for_guests(message: types.Message):
    await message.reply(
        f"Сначало получите доступ у администратора (@lighteezy)"
        f"\nПроверить доступ: /access"
    )


@dp.message_handler(owner, commands=["check_id"])
async def check_id(message: types.Message):
    authorized_users_str = '\n'.join(map(str, whitelist))
    await bot.send_message(message.chat.id, "ID в whitelist: \n\n" + authorized_users_str)


@dp.message_handler(owner, commands=["add_id"])
async def add_id(message: types.Message):
    user_id = message.text.split()[1]
    if int(user_id) in whitelist:
        await message.reply("Этот ID уже есть в whitelist.")
    else:
        whitelist.append(int(user_id))
        with open("users.txt", "a") as file:
            file.write(user_id + "\n")
        await message.reply(f"ID {user_id} добавлен в whitelist.")


@dp.message_handler(owner, commands=["remove_id"])
async def remove_id(message: types.Message):
    user_id = message.text.split()[1]
    if int(user_id) not in whitelist:
        await message.reply("Этого ID нет в whitelist.")
    else:
        whitelist.remove(int(user_id))
        with open("users.txt", "w") as file:
            for id in whitelist:
                file.write(str(id) + "\n")
        await message.reply(f"ID {user_id} был удален с whitelist.")


@dp.message_handler(content_types='text')
async def access(message: types.Message):
    if message.text == '/whitelist':
        await bot.send_message(
                message.chat.id, f"Количество людей с правами доступа: {len(whitelist)}"
            )

    elif message.text == '/access':
        if message.from_user.id in whitelist:
            await bot.send_message(message.chat.id, "У вас есть доступ.")
        else:
            await bot.send_message(message.chat.id, "У вас нету доступа.")

    elif message.text == '/chatid':
        await message.reply(
                f"Ваш уникальный ID: `{message.from_user.id}`", parse_mode="MARKDOWN"
            )

    elif message.text == '/help':
        await bot.send_message(
            message.chat.id, "Список команд:\n/access\n/chatid\n/whitelist"
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



