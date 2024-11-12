from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import markdown

from DB import database

router = Router(name=__name__)


class ProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_sex = State()
    waiting_for_brand = State()
    waiting_for_season = State()
    waiting_for_price = State()
    waiting_for_discount_price = State()
    waiting_for_colors = State()
    waiting_for_sizes = State()
    waiting_for_image = State()
    waiting_for_article = State()


@router.message(F.text == '📋 Замовлення')
async def show_orders_command(message: types.Message):
    user_id = message.from_user.id
    user = database.get_user(user_id)

    if user["role"] != "admin":
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="У вас немає доступу до цієї команди.",
        )
        return

    orders = database.get_all_orders()

    if not orders:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Немає замовлень.",
        )
        return

    for order in orders:
        response_text = (
            f"🆔 ID: {order['order_id']}\n"
            f"👤 Нікнейм: @{order['customer_nickname']}\n"
            f"🛍️ Товар: {order['product_name']}\n"
            f"🆔 Артикул: {order['product_article']}\n"
            f"🕒 Час замовлення: {order['timestamp']}\n"
            f"💵 Сума до оплати: {order['amount_due']} грн\n"
            f"-----------------\n"
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Опрацьовано",
                callback_data=f"order_processed:{order['order_id']}"
            )
        ]])

        await message.bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_markup=markup
        )


@router.message(F.text == '🛒 Товари магазину')
async def products_command(message: types.Message):
    user_id = message.from_user.id
    user = database.get_user(user_id)
    if not (user["role"] == "admin"):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Зробіть вибір",
        )
        return
    btn1 = types.KeyboardButton(text="🛒 Додати товар")
    markup = types.ReplyKeyboardMarkup(keyboard=[[btn1]], resize_keyboard=True)
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=f"Введіть артикул для пошуку товару або додайте новий товар",
        reply_markup=markup,
    )


@router.message(F.text == '🛒 Додати товар')
async def add_product_command(message: types.Message, state: FSMContext):
    await message.answer("Введіть артикул товару:")
    await state.set_state(ProductStates.waiting_for_article)


@router.message(ProductStates.waiting_for_article)
async def process_product_article(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    await message.answer("Введіть назву товару:")
    await state.set_state(ProductStates.waiting_for_name)


@router.message(ProductStates.waiting_for_name)
async def process_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    btn1 = types.KeyboardButton(text="Для нього")
    btn2 = types.KeyboardButton(text="Для неї")
    btn3 = types.KeyboardButton(text="Унісекс")
    markup = types.ReplyKeyboardMarkup(keyboard=[[btn1, btn3, btn2]], resize_keyboard=True)
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=f"Для кого цей одяг",
        reply_markup=markup,
    )
    await state.set_state(ProductStates.waiting_for_sex)


@router.message(ProductStates.waiting_for_sex)
async def process_product_sex(message: types.Message, state: FSMContext):
    if message.text == "Для нього":
        await state.update_data(sex="male")
    elif message.text == "Для неї":
        await state.update_data(sex="female")
    else:
        await state.update_data(sex="unisex")
    await message.answer("Введіть бренд товару:")
    await state.set_state(ProductStates.waiting_for_brand)


@router.message(ProductStates.waiting_for_brand)
async def process_product_brand(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Який сезон? (літо, весна/осінь, зима):")
    await state.set_state(ProductStates.waiting_for_season)


@router.message(ProductStates.waiting_for_season)
async def process_product_season(message: types.Message, state: FSMContext):
    await state.update_data(season=message.text)
    await message.answer("Вкажіть ціну:")
    await state.set_state(ProductStates.waiting_for_price)


@router.message(ProductStates.waiting_for_price)
async def process_product_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Чи це знижена ціна? (так/ні):")
    await state.set_state(ProductStates.waiting_for_discount_price)


@router.message(ProductStates.waiting_for_discount_price)
async def process_product_discount(message: types.Message, state: FSMContext):
    discount_response = message.text.lower()
    if discount_response == 'так':
        await state.update_data(discount_price=True)
    else:
        await state.update_data(discount_price=False)
    await message.answer("Введіть доступні кольори через кому:")
    await state.set_state(ProductStates.waiting_for_colors)


@router.message(ProductStates.waiting_for_colors)
async def process_product_colors(message: types.Message, state: FSMContext):
    await state.update_data(colors=message.text)
    await message.answer("Введіть доступні розміри через кому:")
    await state.set_state(ProductStates.waiting_for_sizes)


@router.message(ProductStates.waiting_for_sizes)
async def process_product_sizes(message: types.Message, state: FSMContext):
    await state.update_data(sizes=message.text)
    await message.answer("Завантажте фото:")
    await state.set_state(ProductStates.waiting_for_image)


@router.message(ProductStates.waiting_for_image)
async def process_product_image(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Відправте, будь ласка, фото товару.")
        return
    file_id = message.photo[-1].file_id
    file_path = await message.bot.get_file(file_id)  # Получаем файл
    await message.bot.download_file(file_path.file_path, f'res/{file_path.file_path.split("/")[-1]}')
    image_path = f'res/{file_path.file_path.split("/")[-1]}'

    await state.update_data(image_path=image_path)
    data = await state.get_data()

    database.add_product(
        name=data['name'],
        sex=data['sex'],
        brand=data['brand'],
        season=data['season'],
        price=data['price'],
        discount_price=data['discount_price'],
        article=data['article'],
        colors=data['colors'],
        sizes=data['sizes'],
        image_path=data['image_path']
    )

    await message.answer("Товар успішно додано!")
    await state.clear()


@router.message(F.text)
async def search_product_command(message: types.Message, state: FSMContext):
    article = message.text.strip()

    product = database.get_product_by_article(article)

    print("Product data:", product)

    if product:
        gender = "невідомий"
        if product.get('sex') == "male":
            gender = " нього 👨‍🦱"
        elif product.get('sex') == "female":
            gender = " неї 👩"
        else:
            gender = " нього та неї 👨‍🦱👩"

        product_info = (
            f"🛍️ {markdown.hbold('Товар:')} {product.get('name', 'невідомий')}\n"
            f"{markdown.hbold('Для:')} {gender}\n"
            f"🏷️ {markdown.hbold('Бренд:')} {product.get('brand', 'невідомий')}\n"
            f"🌸 {markdown.hbold('Сезон:')} {product.get('season', 'невідомий')}\n"
            f"💵 {markdown.hbold('Ціна:')} {product.get('price', 'невідомий')} грн\n"
            f"💰 {markdown.hbold('Знижка:')} {'так' if product.get('discount_price') else 'ні'}\n"
            f"🌈 {markdown.hbold('Кольори:')} {product.get('colors', 'невідомі')}\n"
            f"📏 {markdown.hbold('Розміри:')} {product.get('sizes', 'невідомі')}\n"
            f"{markdown.hbold('Артикул:')} {product.get('article', 'невідомий')}\n"
        )

        try:
            if product.get('image_path'):
                photo_path = product['image_path']
                photo_send = FSInputFile(photo_path)
                print("Photo path:", photo_path)

                user_id = message.from_user.id
                user_role = database.get_user(user_id)["role"]

                if user_role == "admin":
                    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[
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
                    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(
                            text="Замовити",
                            callback_data=f"make_order_by_id:{product['id']}"
                        ),
                        InlineKeyboardButton(
                            text="Додати в улюблене",
                            callback_data=f"add_to_favorite:{product['article']}"
                        )
                    ]])

                await message.answer_photo(photo_send, caption=product_info, reply_markup=inline_kb)
            else:
                await message.answer(product_info)

        except Exception as e:
            await message.answer("Не вдалося завантажити фото товару.")
            print(f"Ошибка при загрузке фото: {e}")
    else:
        await message.answer("Товар з таким артикулом не знайдено.")
