from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from DB import database

router = Router(name=__name__)


class ProductSearchStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_brand = State()
    waiting_for_size = State()


@router.message(F.text == '❤️ Улюблене')
async def view_favorites(message: types.Message):
    user_id = message.from_user.id

    favorites_articles = database.get_user_favorites(user_id)

    if favorites_articles:
        response_text = "Твої улюблені товари:\n\n"
        kb_builder = InlineKeyboardBuilder()

        products = []
        for article in favorites_articles:
            product = database.get_product_by_article(article.strip())
            if product:
                products.append(product)

        for idx, product in enumerate(products, start=1):
            response_text += (
                f"{idx}. {product['name']}\n"
                f"Розміри: {product['sizes']}\n\n"
            )
            kb_builder.add(
                types.InlineKeyboardButton(
                    text=str(idx),
                    callback_data=f"product_id:{product['id']}"
                )
            )

        await message.answer(response_text, reply_markup=kb_builder.as_markup())
    else:
        await message.answer("У вас немає улюблених товарів.")


@router.message((F.text == '👨‍🦱 Для нього') | (F.text == '👩 Для неї'))
async def start_product_search(message: types.Message, state: FSMContext):
    gender = "male" if message.text == "👨‍🦱 Для нього" else "female"
    await state.update_data(gender=gender)

    await message.answer("Вкажіть бренд, який вас цікавить:")
    await state.set_state(ProductSearchStates.waiting_for_brand)


@router.message(ProductSearchStates.waiting_for_brand)
async def process_brand(message: types.Message, state: FSMContext):
    brand = message.text.lower()
    await state.update_data(brand=brand)

    await message.answer("Який розмір вам потрібен? Вкажіть один або декілька через кому:")
    await state.set_state(ProductSearchStates.waiting_for_size)


@router.message(ProductSearchStates.waiting_for_size)
async def process_size(message: types.Message, state: FSMContext):
    sizes = message.text.lower().split(",")
    await state.update_data(sizes=sizes)
    data = await state.get_data()

    products = database.search_products_for_user(
        sex=data['gender'],
        brand=data['brand'],
        size=','.join(data['sizes']).lower()
    )

    if products:
        response_text = "Ось товари, які підходять під ваші критерії:\n\n"
        kb_builder = InlineKeyboardBuilder()

        for idx, product in enumerate(products, start=1):
            response_text += (
                f"{idx}. {product['name']}\n"
                f"Розміри: {product['sizes']}\n\n"
            )
            kb_builder.add(
                types.InlineKeyboardButton(
                    text=str(idx),
                    callback_data=f"product_id:{product['id']}"
                )
            )

        await message.answer(response_text, reply_markup=kb_builder.as_markup())
    else:
        await message.answer("На жаль, немає товарів, які відповідають вашим критеріям.")

    await state.clear()
