from aiogram import Router, types, F
import datetime
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import markdown
from DB import database

from Classes.order import Order
from DB.database import save_order_to_db

router = Router(name=__name__)


@router.callback_query(F.data.startswith("product_id:"))
async def view_details_product_callback(query: types.CallbackQuery):
    product_id = query.data.split(":")[1]
    user_id = query.from_user.id
    user_role = database.get_user(user_id)["role"]

    product = database.get_product_by_id(product_id)

    if product:
        gender = (
            " нього 👨‍🦱" if product['sex'] == "male"
            else " неї 👩" if product['sex'] == "female"
            else " нього та неї 👨‍🦱👩"
        )
        product_info = (
            f"🛍️ {markdown.hbold('Товар:')} {product['name']}\n"
            f"{markdown.hbold('Для:')} {gender}\n"
            f"🏷️ {markdown.hbold('Бренд:')} {product['brand']}\n"
            f"🌸 {markdown.hbold('Сезон:')} {product['season']}\n"
            f"💵 {markdown.hbold('Ціна:')} {product['price']} грн\n"
            f"💰 {markdown.hbold('Знижка:')} {'так' if product['discount_price'] else 'ні'}\n"
            f"🌈 {markdown.hbold('Кольори:')} {product['colors']}\n"
            f"📏 {markdown.hbold('Розміри:')} {product['sizes']}\n"
        )
        try:
            photo_path = product['image_path']
            photo_send = FSInputFile(photo_path)

            if user_role == "admin":
                markup = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text="Видалити позицію",
                        callback_data=f"remove_product_by_article:{product['article']}"
                    ),
                    InlineKeyboardButton(
                        text="Додати в улюблене",
                        callback_data=f"add_to_favorite:{product['article']}"
                    ),
                    InlineKeyboardButton(
                        text="Замовити",
                        callback_data=f"make_order_by_id:{product['id']}"
                    ),
                ]])
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text="Замовити",
                        callback_data=f"make_order_by_id:{product['id']}"
                    ),
                    InlineKeyboardButton(
                        text="Додати в улюблене",
                        callback_data=f"add_to_favorite:{product['article']}"
                    )
                ]])
            await query.message.answer_photo(photo_send, caption=product_info, reply_markup=markup)
        except Exception as e:
            await query.answer("Не вдалося завантажити фото товару.")
            print(f"Ошибка при загрузке фото: {e}")
    else:
        await query.message.answer("На жаль, не вдалося знайти товар з таким ID.")
    await query.answer()


@router.callback_query(F.data.startswith("remove_product_by_article:"))
async def remove_product_by_article_callback(query: types.CallbackQuery):
    product_article = query.data.split(":")[1]

    success = database.remove_product_by_article(product_article)

    if success:
        await query.answer("Товар успішно видалений з бази даних.")
        await query.message.edit_text("Товар успішно видалений.")
    else:
        await query.answer("Не вдалося видалити товар. Спробуйте ще раз.")


@router.callback_query(F.data.startswith("add_to_favorite:"))
async def add_to_favorite_callback(query: types.CallbackQuery):
    product_article = query.data.split(":")[1]
    user_id = query.from_user.id

    try:
        database.add_to_favorites(user_id, product_article)
        await query.answer("Товар добавлено в улюблене!", show_alert=True)
    except Exception as e:
        await query.answer("Не вдалося додати товар до улюблених.")
        print(f"Ошибка при добавлении товара в избранное: {e}")


@router.callback_query(F.data.startswith("make_order_by_id:"))
async def make_order_callback(query: types.CallbackQuery):
    product_id = query.data.split(":")[1]

    product = database.get_product_by_id(product_id)

    if product:
        customer_nickname = query.from_user.username or "Анонім"

        order = Order(
            order_id=None,
            customer_nickname=customer_nickname,
            product_name=product['name'],
            product_article=product['article'],
            order_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            amount_due=product['price']
        )

        save_order_to_db(order)

        await query.answer(f"Замовлення на товар '{order.product_name}' було успішно створене!"
                           f" Будь ласка, очікуйте. Менеджер напише Вам у Telegram")
    else:
        await query.answer("На жаль, не вдалося знайти товар з таким ID.")


@router.callback_query(F.data.startswith("order_processed:"))
async def process_order_callback(query: types.CallbackQuery):
    order_id = query.data.split(":")[1]

    success = database.mark_order_as_processed(order_id)

    if success:
        await query.answer(f"Замовлення з ID {order_id} було успішно опрацьовано.")
    else:
        await query.answer("Не вдалося опрацювати замовлення. Спробуйте ще раз.")
