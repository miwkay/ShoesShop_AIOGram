from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# keyboard buttons
kb_catalog = 'К А Т А Л О Г   В З У Т Т Я  📦'
kb_about = 'Інформація 💡'
kb_size_info = 'Таблиця розмірів 📐'
complaint = 'Підтримка 🛠'
b_location = 'Самовивіз 📍'
b_delivery = 'Доставка 🚕'
set_product = 'Додати товар ➕'
del_product = 'Видалити товар ➖'
archive = 'Архів 🗂'
view_orders = 'Всі замовлення 🔎'
visits = 'Хто заходив 🕺'
clean_db = 'Видалити всі замовлення ❌'
clean_orders = 'Видалити замовлення!'
mailing = 'Розсилка 📮'
order = 'Замовити! 😎'

# main menu
kb_main = ReplyKeyboardMarkup(resize_keyboard=True)
b2 = KeyboardButton(kb_catalog)
b3 = KeyboardButton(kb_about)
b4 = KeyboardButton(kb_size_info)
kb_main.add(b2).add(b4, b3)

# directory on main menu
kb_catalog = ReplyKeyboardMarkup(resize_keyboard=True)
bc1 = KeyboardButton('Жіночі 👠')
bc2 = KeyboardButton('Чоловічі 🥾')
bc4 = KeyboardButton('На головну 🫡')
kb_catalog.add(bc1, bc2).add(bc4)

# info on main menu
kb_complaint = ReplyKeyboardMarkup(resize_keyboard=True)
kbc1 = KeyboardButton(complaint)
kbc2 = KeyboardButton(b_location)
kbc3 = KeyboardButton(b_delivery)
kb_complaint.add(kbc2, kbc3).add(kbc1, bc4)

# back to main menu
kb_on_main = ReplyKeyboardMarkup(resize_keyboard=True)
kb_on_main.add(bc4)

# admin menu
kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
ba1 = KeyboardButton(set_product)
ba2 = KeyboardButton(del_product)
ba3 = KeyboardButton(mailing)
ba4 = KeyboardButton(archive)
kb_admin.add(ba1, ba2).add(ba4, ba3, bc4)

# start ordering
kb_order = ReplyKeyboardMarkup(resize_keyboard=True)
bc3 = KeyboardButton('Замовити! 😎')
kb_order.add(bc3).add(bc4)

# admin menu archive
kb_admin_archive = ReplyKeyboardMarkup(resize_keyboard=True)
baa1 = KeyboardButton(view_orders)
baa2 = KeyboardButton(visits)
kb_admin_archive.add(baa1, baa2).add(bc4)

kb_clean_archive = ReplyKeyboardMarkup(resize_keyboard=True)
bca1 = KeyboardButton(clean_db)
kb_clean_archive.add(bca1).add(bc4)

kb_clean_orders = ReplyKeyboardMarkup(resize_keyboard=True)
bco1 = KeyboardButton(clean_orders)
kb_clean_orders.add(bco1).add(bc4)

kb_order_fin = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_order_fin.add(bc3, bc4)
