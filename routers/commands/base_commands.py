from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils import markdown
from DB import database
import config

router = Router(name=__name__)


@router.message(CommandStart())
async def start_command(message: types.Message):
    url = config.URL_HI_PHOTO
    user_id = message.from_user.id
    print(f"USER IF {user_id}")
    username = message.from_user.username
    user = database.get_user(user_id)

    if not user:
        role = "user"
        database.add_user(user_id, username, role)
        user = database.get_user(user_id)

    if user and user["role"] == "admin":
        btn1 = types.KeyboardButton(text="👨‍🦱 Для нього")
        admin_btn = types.KeyboardButton(text="🛒 Товари магазину")
        show_orders = types.KeyboardButton(text="📋 Замовлення")
        fav_btn = types.KeyboardButton(text="❤️ Улюблене")
        btn2 = types.KeyboardButton(text="👩 Для неї")
        markup = types.ReplyKeyboardMarkup(keyboard=[[btn1, admin_btn, show_orders, fav_btn, btn2]], resize_keyboard=True)
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"{markdown.hide_link(url)}Адміністратор {markdown.hbold(message.from_user.full_name)}, вітаємо."
                 f" Що будемо робити?",
            reply_markup=markup,
        )
    elif user["role"] == "user":
        btn1 = types.KeyboardButton(text="👨‍🦱 Для нього")
        fav_btn = types.KeyboardButton(text="❤️ Улюблене")
        btn2 = types.KeyboardButton(text="👩 Для неї")
        markup = types.ReplyKeyboardMarkup(keyboard=[[btn1, btn2, fav_btn]], resize_keyboard=True)
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"{markdown.hide_link(url)}{markdown.hbold(message.from_user.full_name)}, вітаємо в нашому магазині! "
                 f"Скористайтесь навігацією, щоб обрати одяг для себе. "
                 f"Або введіть артикул, щоб переглянути товар",
            reply_markup=markup,
        )
