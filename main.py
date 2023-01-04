import ast
import sqlite3
import logging
import aiogram.utils.markdown as md
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton

from config import BOT_TOKEN, chat_id_admin
from keyboards import kb_main, kb_catalog, kb_complaint, kb_on_main, kb_admin, kb_order, \
    kb_admin_archive, kb_clean_archive, kb_clean_orders
from messages import HELP_COMMAND, START_MESSAGE, NOT_DEFINED, DELIVERY
from sql import add_shoes_db, check_and_add_user, clean_db_orders

logging.basicConfig(level=logging.INFO)


id_admin = chat_id_admin
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    print('Bot has been started..')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.id == id_admin:
        await bot.send_sticker(message.from_user.id,
                               sticker="CAACAgUAAxkBAAEGzN5jlu9tw02BOAPlVWg8M8N6KMeQ6QACkQMAAukKyAN2IcIPRrR79SsE")
        await message.answer(text=f"Привіт {message.from_user.first_name}! 🫡\n"
                                  f"Режим <b>адміністратора</b> активовано. 😎",
                             parse_mode="HTML",
                             reply_markup=kb_admin)
        await message.delete()
    else:
        check_and_add_user(message)
        await message.answer(text=f"<b>Привіт {message.from_user.first_name}!</b> 👋 {START_MESSAGE}",
                             parse_mode="HTML",
                             reply_markup=kb_main)
        await message.delete()


# Для add інформацію в БД
class FormAdd(StatesGroup):
    model = State()  # Модель
    description = State()  # Опис
    gender = State()  # Стать
    price = State()  # Ціна
    foto1 = State()  # Фото1
    foto2 = State()  # Фото2
    foto3 = State()  # Фото3


# Для створення повідомлення адміну
class FormSupport(StatesGroup):
    mailing = State()  # Розсилка
    support = State()  # Підтримка


# Для оформлення замовлення
class Form(StatesGroup):
    size = State()  # Розмір
    name = State()  # Ім'я
    phone = State()  # Телефон
    address = State()  # Адреса


@dp.message_handler(Text(equals='Додати товар ➕'))
async def add_item_name(message: types.Message):
    if message.from_user.id == id_admin:
        await FormAdd.model.set()
        await message.answer(text="<b>Назва моделі:</b>\n"
                                  "(<em>наприклад:</em> Nike Air Max Vg-R)",
                             parse_mode="HTML")
    else:
        await message.answer(text="Потрібні права адміністратора!", reply_markup=kb_main)


@dp.message_handler(state=FormAdd.model)
async def add_item_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['model'] = message.text
    await FormAdd.next()
    await message.answer(text="<b>Опис:</b>\n"
                              "(<em>Характеристики та інше</em>)",
                         parse_mode="HTML")


@dp.message_handler(state=FormAdd.description)
async def add_item_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await FormAdd.next()
    ikb_gender = ReplyKeyboardMarkup(resize_keyboard=True)
    ib_m = InlineKeyboardButton('ч')
    ib_w = InlineKeyboardButton('ж')
    ikb_gender.add(ib_m, ib_w)
    await message.answer(text="<b>Стать:</b>\n"
                              "(<em>Чоловіча чи Жіноча</em>)\n"
                              "НАТИСНИ ВІДПОВІДНУ КНОПКУ 👇",
                         parse_mode="HTML",
                         reply_markup=ikb_gender)


@dp.message_handler(state=FormAdd.gender)
async def add_item_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    await FormAdd.next()
    await message.answer(text="<b>Ціна у грн:</b>\n"
                              "(<em>наприклад:</em> 485)",
                         parse_mode="HTML")


@dp.message_handler(lambda message: not message.text.isdigit(), state=FormAdd.price)
async def item_price_only_digits(message: types.Message):
    return await message.reply("Ціна складається лише з цифр.\nСпробуй ще раз: (digits only)")


@dp.message_handler(state=FormAdd.price)
async def add_item_photo1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await FormAdd.next()
    await message.answer(text="<b>Фото 1 з 3:</b>\n"
                              "(<em>Посилання на фото товару</em>)",
                         parse_mode="HTML")


@dp.message_handler(state=FormAdd.foto1)
async def add_item_photo2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['foto1'] = message.text
        await FormAdd.next()
        await message.answer(text="<b>Фото 2 з 3:</b>\n"
                                  "(<em>Посилання на фото товару</em>)",
                             parse_mode="HTML")


@dp.message_handler(state=FormAdd.foto2)
async def add_item_photo3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['foto2'] = message.text
        await FormAdd.next()
        await message.answer(text="<b>Фото 3 з 3:</b>\n"
                                  "(<em>Посилання на фото товару</em>)",
                             parse_mode="HTML")


@dp.message_handler(state=FormAdd.foto3)
async def demonstration_item_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['foto3'] = message.text
        await FormAdd.next()
        # add item in db
        add_shoes_db(data['model'],
                     data['price'],
                     data['description'],
                     data['gender'],
                     data['foto1'],
                     data['foto2'],
                     data['foto3'])

        await message.answer(text="<b>Готово!</b>", parse_mode="HTML", reply_markup=kb_admin)


# Видалити товар із БД
def delete_item_kb(data_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton("Видалити", callback_data="['del', '" + str(data_id) + "']")
    keyboard.add(button)
    return keyboard


# Видалити товар із БД
@dp.message_handler(Text(equals='Видалити товар ➖'))
async def delete_item(message: types.Message):
    if message.from_user.id == id_admin:
        with sqlite3.connect('shop.db', check_same_thread=False) as db:
            cur = db.cursor()
            cur.execute("SELECT model, price, gender FROM shoes")
            data = cur.fetchall()
            for i in data:
                await message.answer(text=f'<b>{i[0]} ({i[2]}) : {i[1]} грн</b>',
                                     parse_mode="HTML",
                                     reply_markup=delete_item_kb(i[0]))

    else:
        await message.answer(text="Потрібні права адміністратора!", reply_markup=kb_main)


@dp.callback_query_handler()
async def callback_order(callback: types.CallbackQuery):
    if callback.data.startswith("['buy'"):
        with sqlite3.connect('shop.db', check_same_thread=False) as db:
            cursor = db.cursor()
            cursor.execute("SELECT model, price, id FROM shoes WHERE model = ?",
                           (ast.literal_eval(callback.data)[1],))
            data_buy = cursor.fetchall()
            model = data_buy[0][0]
            price = f'{data_buy[0][1]} грн.'
            item_id = data_buy[0][2]
            await callback.message.answer(text=f'Замовити <b>{model}</b>\n'
                                               f'за ціною <b>{price}</b>?\n'
                                               f'Тисни кнопку 👇',
                                          parse_mode="HTML",
                                          reply_markup=kb_order)
            con = sqlite3.connect('shop.db')
            cur = con.cursor()
            cur.execute('INSERT INTO cart\n'
                        '(user_id, item_id)\n'
                        'VALUES (?, ?)',
                        (callback.message.from_user.id, item_id))
            con.commit()
            cur.close()

    if callback.data.startswith("['del'"):
        with sqlite3.connect('shop.db', check_same_thread=False) as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM shoes WHERE model = ?", (ast.literal_eval(callback.data)[1],))
            await callback.answer(text='Видалено!')
            await callback.message.reply(text='Видалено!')
    await callback.answer(text='Ok!')


# Оформлення замовлення
@dp.message_handler(Text(equals='Замовити! 😎'))
async def order_by_size(message: types.Message):
    await Form.size.set()
    await message.answer("Напиши свій розмір взуття:")


@dp.message_handler(state=Form.size)
async def order_by_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = message.text
    await Form.next()
    await message.answer("Напиши своє ФІО:")


@dp.message_handler(state=Form.name)
async def order_by_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    await message.answer("Напиши свій номер телефону:")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.phone)
async def process_phone_invalid(message: types.Message):
    return await message.reply("Номер повинен складатись тільки з цифр.\nСпробуй ще раз: (digits only)")


@dp.message_handler(state=Form.phone)
async def order_by_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await Form.next()
    await message.answer("Вкажи адресу та службу доставки:")


@dp.message_handler(state=Form.address)
async def demonstration_order_by_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
        with sqlite3.connect('shop.db', check_same_thread=False) as db:
            cur = db.cursor()
            item = cur.execute("SELECT item_id FROM cart").fetchall()
            item = item[-1][-1]
            item = cur.execute("SELECT model, gender, price FROM shoes WHERE id == ?", (item,)).fetchall()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text("Заказ оформлено!\n"
                        "Ім'я:", md.bold(data['name'])),
                md.text('Телефон:', md.code(data['phone'])),
                md.text('Адреса:', data['address']),
                md.text('Модель:', item[0][0]),
                md.text('Розмір:', md.code(data['size'])),
                md.text('Стать:', item[0][1]),
                md.text('Ціна:', f'{item[0][2]} грн.'),
                md.text("Продавець незабаром зв'яжеться для підтвердження замовлення.\n"
                        "Дякую що обрали нас!"),
                sep='\n',
            ),
            reply_markup=kb_on_main,
            parse_mode=ParseMode.MARKDOWN,
        )
        await bot.send_message(
            id_admin,
            md.text(
                md.text("Новий заказ:\n"
                        "Ім'я:", md.bold(data['name'])),
                md.text('Телефон:', md.code(data['phone'])),
                md.text('Адреса:', data['address']),
                md.text('Модель:', item[0][0]),
                md.text('Розмір:', md.code(data['size'])),
                md.text('Стать:', item[0][1]),
                md.text('Ціна:', f'{item[0][2]} грн.'),
                sep='\n',
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
        con = sqlite3.connect('shop.db')
        cur = con.cursor()
        cur.execute('INSERT INTO orders\n'
                    '(user_id, name, phone, address, model, size,\n'
                    'gender, price, date, username, first_name, last_name)\n'
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (message.from_user.id,
                                                                    md.text(data['name']),
                                                                    md.text(data['phone']),
                                                                    md.text(data['address']),
                                                                    md.text(item[0][0]),
                                                                    md.text(data['size']),
                                                                    md.text(item[0][1]),
                                                                    md.text(item[0][2]),
                                                                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                    message.from_user.username,
                                                                    message.from_user.first_name,
                                                                    message.from_user.last_name))
        cur.execute('DELETE FROM cart')
        con.commit()
        cur.close()
    await state.finish()


@dp.message_handler(Text(equals='Архів 🗂'))
async def show_archive(message: types.Message):
    await message.answer(text="<b>Тисни що цікавить:</b>", parse_mode="HTML", reply_markup=kb_admin_archive)


@dp.message_handler(Text(equals='Всі замовлення 🔎'))
async def delete_data_archive(message: types.Message):
    if message.from_user.id == id_admin:
        with sqlite3.connect('shop.db', check_same_thread=False) as db:
            cur = db.cursor()
            cur.execute("SELECT order_id, user_id, name, phone, address, model, size, gender,\n"
                        "price, date, username, first_name, last_name FROM orders")
            data = cur.fetchall()
            num = 0
            for i in data:
                await message.answer(text=f'<b>Замовлення: {i[0]}</b>\n'
                                          f'{i[5]}\n'
                                          f'({i[7]}) {i[6]}р. - {i[8]} грн.\n'
                                          f'{i[2]}\n'
                                          f'т: {i[3]}\n'
                                          f'{i[4]}\n'
                                          f'<em>Додаткова інформація баєра:</em>\n'
                                          f'username: @{i[10]}\n'
                                          f'user_id: {i[1]}\n'
                                          f'first_name: {i[11]}\n'
                                          f'last_name: {i[12]}\n'
                                          f'<b>{i[9]}</b>',
                                     parse_mode="HTML")
                num += 1
            await message.answer(text=f'Усього <b>{num}</b> замовлень!',
                                 parse_mode="HTML",
                                 reply_markup=kb_clean_archive)
    else:
        await message.answer(text="Потрібні права адміністратора!", reply_markup=kb_main)


@dp.message_handler(Text(equals='Хто заходив 🕺'))
async def visit_data(message: types.Message):
    if message.from_user.id == id_admin:
        with sqlite3.connect('shop.db', check_same_thread=False) as db:
            cur = db.cursor()
            cur.execute("SELECT user_id, username, first_name, last_name, date FROM users")
            data = cur.fetchall()
            num = 0
            for i in data:
                await message.answer(text=f'<b>{i[4]}</b>\n'
                                          f'user_id: {i[0]}\n'
                                          f'username: @{i[1]}\n'
                                          f'first_name: {i[2]}\n'
                                          f'last_name: {i[3]}\n',
                                     parse_mode="HTML", reply_markup=kb_admin)
                num += 1
            await message.answer(text=f'Усього <b>{num}</b> людей знають про твій магазин!', parse_mode="HTML")
    else:
        await message.answer(text="Потрібні права адміністратора!", reply_markup=kb_main)


@dp.message_handler(Text(equals='Видалити всі замовлення ❌'))
async def delete_data_orders(message: types.Message):
    if message.from_user.id == id_admin:
        await message.answer(text="Видалення даних без можливості відновлення?", reply_markup=kb_clean_orders)
    else:
        await message.answer(text="Потрібні права адміністратора!", reply_markup=kb_main)


@dp.message_handler(Text(equals='Видалити замовлення!'))
async def delete_data_orders_done(message: types.Message):
    if message.from_user.id == id_admin:
        clean_db_orders()
        await message.answer(text="Видалено! ✅", reply_markup=kb_admin)
    else:
        await message.answer(text="Потрібні права адміністратора!", reply_markup=kb_main)


@dp.message_handler(Text(equals='К А Т А Л О Г   В З У Т Т Я  📦'))
async def open_kb_catalog(message: types.Message):
    await message.answer(text='Обери відповідну категорію:', reply_markup=kb_catalog)
    await message.delete()


@dp.message_handler(Text(equals='На головну 🫡'))
async def open_kb_main(message: types.Message):
    await message.answer(text='<b>Головна сторінка!</b>' + HELP_COMMAND,
                         parse_mode="HTML",
                         reply_markup=kb_main)
    await message.delete()


@dp.message_handler(Text(equals='Інформація 💡'))
async def open_kb_info(message: types.Message):
    await message.answer(text='Тут буде вказана <b>корисна покупцеві</b> інформація!\n'
                              'Типу "наш магазин бла-бла-бла"',
                         parse_mode="HTML",
                         reply_markup=kb_complaint)
    await message.delete()


@dp.message_handler(Text(equals='Розсилка 📮'))
async def mailing(message: types.Message):
    await FormSupport.mailing.set()
    await message.answer(text="<b>Текст розсилки:</b>",
                         parse_mode="HTML",
                         reply_markup=kb_main)


@dp.message_handler(state=FormSupport.mailing)
async def process_mailing(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mailing'] = message.text
    with sqlite3.connect('shop.db', check_same_thread=False) as db:
        cur = db.cursor()
        cur.execute("SELECT user_id FROM users")
        user_id = cur.fetchall()
        num_y = 0
        num_n = 0
    for i in user_id:
        try:
            await bot.send_message(i[0], md.text(data['mailing']), disable_notification=True)
            num_y += 1
        except:
            num_n += 1
    await message.answer(md.text(f'<b>{num_n}</b> користувачів <b>НЕ ОТРИМАЛИ</b> повідомлення!\n'
                                 f'\n'
                                 f'<b>{num_y}</b> користувачів <b>ОТРИМАЛИ</b> повідомлення!\n',
                                 data['mailing']),
                         parse_mode="HTML",
                         reply_markup=kb_main)
    await state.finish()


@dp.message_handler(Text(equals='Підтримка 🛠'))
async def cmd_support(message: types.Message):
    await FormSupport.support.set()
    await message.answer(text="<b>Залишити повідомлення:</b>",
                         parse_mode="HTML",
                         reply_markup=kb_main)


@dp.message_handler(state=FormSupport.support)
async def process_support(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['support'] = message.text
    await message.answer(text=f'Дякую {message.from_user.first_name}, ваше повідомлення передано!', reply_markup=kb_main)
    await bot.send_message(id_admin, md.text(f"‼️‼️ПІДТРИМКА‼️‼️\n"
                                             f"Нік: @{message.from_user.username}\n"
                                             f"Ім'я: {message.from_user.first_name} {message.from_user.last_name}\n"
                                             f"ID: {message.from_user.id}\n"
                                             f" - ", data['support']),
                           parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(Text(equals='Таблиця розмірів 📐'))
async def table_of_sizes(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id,
                         photo='https://shoes-poland.com.ua/image/catalog/womens-shoes/5243/size.jpg',
                         reply_markup=kb_main)
    await message.delete()


@dp.message_handler(Text(equals='Самовивіз 📍'))
async def pickup(message: types.Message):
    await bot.send_location(chat_id=message.chat.id,
                            latitude=22.2744134,  # широта
                            longitude=114.1778873,  # довгота
                            reply_markup=kb_on_main)
    await message.answer(text='За попередньою домовленістю.')
    await message.delete()


@dp.message_handler(Text(equals='Доставка 🚕'))
async def delivery(message: types.Message):
    await message.answer(text=DELIVERY,
                         parse_mode="HTML",
                         reply_markup=kb_on_main)
    await message.delete()


# Замовити товар із БД Keyboard
def buy_item_kb(data_id, coast):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(f"Замовити за {coast} грн.", callback_data="['buy', '" + str(data_id) + "']")
    keyboard.add(button)
    return keyboard


# Жіночий товар із БД
@dp.message_handler(Text(equals='Жіночі 👠'))
async def woman_data_item(message: types.Message):
    with sqlite3.connect('shop.db', check_same_thread=False) as db:
        cur = db.cursor()
        cur.execute("SELECT model, description, price, gender, foto1, foto2, foto3 FROM shoes")
        data = cur.fetchall()
        for i in data:
            if i[3] == 'ж':
                media = types.MediaGroup()
                media.attach_photo(i[4])
                media.attach_photo(i[5])
                media.attach_photo(i[6])
                await message.reply_media_group(media=media)
                await message.answer(text=f'<b>{i[0]}</b>\n'
                                          f'Ціна: {i[2]} грн.\n'
                                          f'\n    {i[1]}', parse_mode="HTML", reply_markup=buy_item_kb(i[0], i[2]))


# Чоловічий товар із БД
@dp.message_handler(Text(equals='Чоловічі 🥾'))
async def man_data_item(message: types.Message):
    with sqlite3.connect('shop.db', check_same_thread=False) as db:
        cur = db.cursor()
        cur.execute("SELECT model, description, price, gender, foto1, foto2, foto3 FROM shoes")
        data = cur.fetchall()
        for i in data:
            if i[3] == 'ч':
                media = types.MediaGroup()
                media.attach_photo(i[4])
                media.attach_photo(i[5])
                media.attach_photo(i[6])
                await message.reply_media_group(media=media)
                await message.answer(text=f'<b>{i[0]}</b>\n'
                                          f'Ціна: {i[2]} грн.\n'
                                          f'\n    {i[1]}', parse_mode="HTML", reply_markup=buy_item_kb(i[0], i[2]))


@dp.callback_query_handler()
async def error(callback: types.CallbackQuery):
    await callback.answer(text='Error!')


@dp.message_handler()
async def not_defined(message: types.Message):
    await message.reply(NOT_DEFINED)


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)
