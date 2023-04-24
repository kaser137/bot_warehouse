from aiogram import types

# ======= CLIENT BLOCK (START) ==============================================================================
client_start_markup = types.InlineKeyboardMarkup(row_width=2)
client_start_markup_buttons = [
    types.InlineKeyboardButton('Storage conditions (FAQ)', url='https://telegra.ph/Usloviya-hraneniya-04-22'),
    types.InlineKeyboardButton('Put things in storage', callback_data='put_things'),
    types.InlineKeyboardButton('My boxes', callback_data='boxes'),
    types.InlineKeyboardButton('Message for owner', callback_data='msg_for_owner'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
client_start_markup.add(*client_start_markup_buttons)

choose_weight = types.InlineKeyboardMarkup(row_width=3)
choose_weight_buttons = [
    types.InlineKeyboardButton('0-10 kg', callback_data='mass_0_10'),
    types.InlineKeyboardButton('10-25 kg', callback_data='mass_10_25'),
    types.InlineKeyboardButton('25-40 kg', callback_data='mass_25_40'),
    types.InlineKeyboardButton('40-70 kg', callback_data='mass_40_70'),
    types.InlineKeyboardButton('70-100 kg', callback_data='mass_70_100'),
    types.InlineKeyboardButton('100+ kg', callback_data='mass_100'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
choose_weight.add(*choose_weight_buttons)

choose_square = types.InlineKeyboardMarkup(row_width=2)
choose_square_buttons = [
    types.InlineKeyboardButton('0-3 sq.m', callback_data='metr_0_3'),
    types.InlineKeyboardButton('3-7 sq.m', callback_data='metr_3_7'),
    types.InlineKeyboardButton('7-10 sq.m', callback_data='metr_7_10'),
    types.InlineKeyboardButton('10+ sq.m', callback_data='metr_10'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
choose_square.add(*choose_square_buttons)

choose_delivery = types.InlineKeyboardMarkup(row_width=2)
choose_delivery_buttons = [
    types.InlineKeyboardButton('our delivery', callback_data='delivery_yes'),
    types.InlineKeyboardButton('your delivery', callback_data='delivery_no'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
choose_delivery.add(*choose_delivery_buttons)

make_order = types.InlineKeyboardMarkup(row_width=2)
make_order_buttons = [
    types.InlineKeyboardButton('make order', callback_data='order_yes'),
    types.InlineKeyboardButton('no, thanks', callback_data='order_no'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
make_order.add(*make_order_buttons)

accept_personal_data = types.InlineKeyboardMarkup(row_width=2)
accept_personal_data_buttons = [
    types.InlineKeyboardButton('Accept', callback_data='personal_yes'),
    types.InlineKeyboardButton('Decline', callback_data='personal_no'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
accept_personal_data.add(*accept_personal_data_buttons)

manage_order = types.InlineKeyboardMarkup(row_width=2)
manage_order_buttons = [
    types.InlineKeyboardButton('Get access', callback_data='access_order'),
    types.InlineKeyboardButton('Close order', callback_data='close_order'),
    types.InlineKeyboardButton('Exit', callback_data='exit'),
]
manage_order.add(*manage_order_buttons)

exit_markup = types.InlineKeyboardMarkup(row_width=1)
exit_markup_btn = types.InlineKeyboardButton('Exit', callback_data='exit')
exit_markup.add(exit_markup_btn)
# ======= CLIENT BLOCK (END) ===============================================================================

# ======= OWNER BLOCK (START) ===============================================================================
exit_owner = types.InlineKeyboardMarkup(row_width=1)
exit_owner_btn = types.InlineKeyboardButton('Exit', callback_data='exit_owner')
exit_owner.add(exit_owner_btn)

owner_start_markup = types.InlineKeyboardMarkup(row_width=2)
owner_start_markup_buttons = [
    types.InlineKeyboardButton('Clients', callback_data='clients'),
    types.InlineKeyboardButton('Orders', callback_data='orders'),
    types.InlineKeyboardButton('Expired orders', callback_data='exp_orders'),
    types.InlineKeyboardButton('Count clicks', callback_data='clicks'),
    types.InlineKeyboardButton('Exit', callback_data='exit_owner'),
]
owner_start_markup.add(*owner_start_markup_buttons)

owner_send_qr = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Send QR', callback_data='qr'))

owner_reply_message = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton('Reply', callback_data='reply'))

owner_reply = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton('Reply', callback_data='repl'))

manage_order_owner = types.InlineKeyboardMarkup(row_width=1)
manage_order_owner_buttons = [
    types.InlineKeyboardButton('Close?', callback_data='close_ord'),
    types.InlineKeyboardButton('Exit', callback_data='exit_owner'),
]
manage_order_owner.add(*manage_order_owner_buttons)

manage_client_owner = types.InlineKeyboardMarkup(row_width=2)
manage_client_owner_buttons = [
    types.InlineKeyboardButton('Close?', callback_data='close_ow'),
    types.InlineKeyboardButton('Message', callback_data='msg_ow'),
    types.InlineKeyboardButton('Exit', callback_data='exit_owner'),
]
manage_client_owner.add(*manage_client_owner_buttons)
