import os
import dotenv
import asyncio
from warehouse import funcs
from warehouse import markups as m
import logging
import django.db.utils
from emoji import emojize
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(Path(BASE_DIR, '.env'))
token = os.environ['BOT_TOKEN']
owners = os.environ['OWNERS_IDS'].split()
owners_ids = []
for owner_id in owners:
    owners_ids.append(int(owner_id))

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
client_id = {}
owner_id = {}
qr_dic = {}


class UserState(StatesGroup):
    mail = State()
    mail_ow = State()
    mail_l = State()
    standby = State()
    mass = State()
    sq = State()
    period = State()
    order = State()
    client = State()
    msg = State()
    order_own = State()
    order_exp = State()
    customers = State()
    qr = State()


# ======= GREETINGS BLOCK (START) ============================================================================
@dp.message_handler()
async def start_conversation(msg: types.Message):
    await msg.answer("""Welcome to the Self Storage service!
Seasonal items that take up a lot of space in the apartment are not always convenient to store.
In many cases, there is no place in the apartment for them.
It also happens that things get boring, accumulate and take up all the space, interfering with life, \
but it's a pity to get rid of them.
Renting a small warehouse will solve your problem.""")
    status = await sync_to_async(funcs.identify_user)(msg.from_user.username)
    if status == 'owner':
        await msg.answer(
            f'hello owner, please add to the field "chat_id for Bot" in admin {msg.from_user.id}\n')
        await msg.answer(f'glad to see you {emojize(":eyes:")}', reply_markup=m.owner_start_markup)
    elif type(status) is int:
        await msg.answer(f'Hi, {msg.from_user.first_name}. You have {status} orders.')
        await msg.answer('Main menu', reply_markup=m.client_start_markup)
    else:
        await msg.answer(f'Hello dear {msg.from_user.first_name}')
        await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.message_handler(state=[UserState.mass, UserState.sq, UserState.standby, UserState.order, UserState.order_own,
                           UserState.order_exp, UserState.customers])
async def incorrect_input_proceeding(msg: types.Message):
    # await msg.delete()
    if await sync_to_async(funcs.identify_user)(msg.from_user.username) == 'owner':
        await msg.answer('Main menu', reply_markup=m.owner_start_markup)
    else:
        await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.message_handler(lambda msg: msg.text[0] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    state=[UserState.period])
async def incorrect_input_proceeding(msg: types.Message):
    if await sync_to_async(funcs.identify_user)(msg.from_user.username) == 'owner':
        await msg.answer('Main menu', reply_markup=m.owner_start_markup)
    else:
        await msg.answer('Main menu', reply_markup=m.client_start_markup)

#
# @dp.callback_query_handler(text='faq', state='*')
# async def faq_proceeding(cb: types.CallbackQuery):
#     await cb.message.answer('https://telegra.ph/Usloviya-hraneniya-04-22', reply_markup=m.exit_markup)
#     await cb.answer()


@dp.callback_query_handler(text="exit", state=[UserState, None])
async def exit_client_proceeding(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer('Main menu', reply_markup=m.client_start_markup)
    await cb.answer()


@dp.callback_query_handler(text='exit_owner', state='*')
async def exit_owner_proceeding(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer('Main menu', reply_markup=m.owner_start_markup)
    await cb.answer()


# ======= GREETINGS BLOCK (END) ============================================================================


# ======= CLIENT BLOCK (START) ==============================================================================
@dp.callback_query_handler(Text('put_things'), state=[UserState, None])
async def choose_weight(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer('Choose weight', reply_markup=m.choose_weight)
    await UserState.mass.set()
    await cb.answer()


@dp.callback_query_handler(Text(['mass_100', 'mass_70_100', 'mass_40_70', 'mass_25_40', 'mass_10_25', 'mass_0_10']),
                           state=UserState.mass)
async def get_weight_component_price(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    for btn_data in ['mass_100', 'mass_70_100', 'mass_40_70', 'mass_25_40', 'mass_10_25', 'mass_0_10']:
        if cb.data == btn_data:
            data = await sync_to_async(funcs.get_cost_field)(cb.data)
            await state.update_data(mass=btn_data, mass_cfn=data)
            break
    data = await state.get_data()
    await cb.message.answer(f"Coefficient to price {data['mass_cfn']}")
    await UserState.sq.set()
    await cb.message.answer('Choose square', reply_markup=m.choose_square)
    await cb.answer()


@dp.callback_query_handler(Text(['metr_10', 'metr_7_10', 'metr_3_7', 'metr_0_3']), state=UserState.sq)
async def get_square_component_price(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    for btn_data in ['metr_10', 'metr_7_10', 'metr_3_7', 'metr_0_3']:
        if cb.data == btn_data:
            data = await sync_to_async(funcs.get_cost_field)(cb.data)
            await state.update_data(sq=btn_data, sq_cfn=data)
            break
    data = await state.get_data()
    await cb.message.answer(f"Cost for 1 day rent: {data['sq_cfn']}")
    await UserState.period.set()
    await cb.message.answer("Input rent's period in days", reply_markup=m.exit_markup)
    await cb.answer()


@dp.message_handler(lambda msg: msg.text[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    state=UserState.period)
async def get_period_component_price(msg: types.Message, state: FSMContext):
    data = int(msg.text)
    await state.update_data(period=data)
    data = await state.get_data()
    await msg.answer(f"Your price is: {data['period'] * data['mass_cfn'] * data['sq_cfn']} RUR",
                     reply_markup=m.choose_delivery)
    await UserState.standby.set()


@dp.callback_query_handler(Text(['delivery_yes', 'delivery_no']), state=UserState.standby)
async def choose_delivery_method(cb: types.CallbackQuery):
    await cb.message.delete()
    if cb.data == 'delivery_yes':
        await cb.message.answer('For delivery details call: +7-777-777-77-77')
        await cb.message.answer('You can make order', reply_markup=m.make_order)
    else:
        await cb.message.answer('You can make order', reply_markup=m.make_order)
    await cb.answer()


@dp.callback_query_handler(Text(['order_yes', 'order_no']), state=UserState.standby)
async def choose_make_order(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    if cb.data == 'order_no':
        await cb.message.answer('We were glad to see you', reply_markup=m.exit_markup)
        await cb.answer()
    else:
        status = await sync_to_async(funcs.identify_user)(cb.from_user.username)
        if status == 'owner':
            await cb.message.answer(f'It was funny {emojize(":eyes:")}', reply_markup=m.exit_owner)
        elif type(status) is int:
            data = await state.get_data()
            amount = data["mass_cfn"] * data["sq_cfn"] * data["period"]
            tg_account = cb.from_user.username
            await cb.message.answer(f'Specs your order:\nmass: {data["mass"]}\nsquare: {data["sq"]}\nperiod: '
                                    f'{data["period"]}\nuser:{cb.from_user.username}')
            await sync_to_async(funcs.make_order)(mass=data["mass"], sq=data["sq"], period=data["period"],
                                                  amount=amount, tg_account=tg_account)
            await cb.message.answer(f'Your order has been registered\nfor pay: {amount}', reply_markup=m.exit_markup)
            for owner_id in owners_ids:
                await bot.send_message(owner_id,
                                       f'New order has been registered,\namount: {amount}\nclient: {tg_account}')
            await state.finish()
            await cb.answer()
        else:
            chat_id = cb.from_user.id
            await cb.message.answer('Before making order you need get registration')
            await cb.message.answer('For registration please read document about personal data')
            await bot.send_document(chat_id=chat_id, document=open(Path('warehouse', 'permitted.pdf'), 'rb'),
                                    reply_markup=m.accept_personal_data)
            await cb.answer()


@dp.callback_query_handler(Text(['personal_yes', 'personal_no']), state=UserState.standby)
async def accepting_permission(cb: types.CallbackQuery):
    await cb.message.delete()
    if cb.data == 'personal_no':
        await cb.message.answer('We were glad to see you', reply_markup=m.exit_markup)
        await cb.answer()
    else:
        await cb.message.answer('For ending registration input your email')
        await UserState.mail.set()
        await cb.answer()


@dp.message_handler(state=UserState.mail)
async def registrate_new_client(msg: types.Message, state: FSMContext):
    chat_id = msg.from_user.id
    tg_account = msg.from_user.username
    mail = msg.text
    data = await state.get_data()
    amount = data["mass_cfn"] * data["sq_cfn"] * data["period"]
    try:
        await sync_to_async(funcs.registration_client)(tg_account, chat_id, mail)
        for owner_id in owners_ids:
            await bot.send_message(owner_id,
                                   f'New client has been registered,\nchat_id: {chat_id}\ntg_account: {tg_account}',
                                   reply_markup=m.exit_owner)
        await msg.answer('You have been registered', reply_markup=m.exit_markup)
        await sync_to_async(funcs.make_order)(mass=data["mass"], sq=data["sq"], period=data["period"], amount=amount,
                                              tg_account=tg_account)
        for owner_id in owners_ids:
            await bot.send_message(owner_id, f'New order has been registered,\namount: {amount}\nclient: {tg_account}',
                                   reply_markup=m.exit_owner)
        await msg.answer(f'Your order has been registered\nfor pay: {amount}', reply_markup=m.exit_markup)
    except django.db.utils.IntegrityError:
        await msg.answer('For registration you need get nickname in Telegram', reply_markup=m.exit_markup)
    await state.finish()


@dp.callback_query_handler(Text(['boxes']), state=[UserState, None])
async def create_existing_orders(cb: types.CallbackQuery):
    await cb.message.delete()
    status = await sync_to_async(funcs.identify_user)(cb.from_user.username)
    if status == 'owner':
        await cb.message.answer(f'It was funny {emojize(":eyes:")}', reply_markup=m.exit_owner)
        await cb.answer()
    elif status == 'User is not registered':
        await cb.message.answer('Sorry, you are not registered', reply_markup=m.exit_markup)
        await cb.answer()
    else:
        orders = await sync_to_async(funcs.get_client_orders)(cb.from_user.username)
        if orders:
            orders_markup = types.InlineKeyboardMarkup(row_width=1)
            orders_btn = []
            for order in orders:
                orders_btn.append(types.InlineKeyboardButton(f'id: {order["id"]} cost: {order["amount"]}',
                                                             callback_data=f'/{order["id"]}'))
            orders_btn.append(types.InlineKeyboardButton('Exit', callback_data='exit'))
            orders_markup.add(*orders_btn)
            await cb.message.answer(f'Choose order', reply_markup=orders_markup)
            await UserState.order.set()
            await cb.answer()
        else:
            await cb.message.answer('You have not any orders', reply_markup=m.exit_markup)
            await cb.answer()


@dp.callback_query_handler(lambda cb: cb.data[0] == '/', state=UserState.order)
async def output_order_attributes(cb: types.CallbackQuery, state: FSMContext):
    orders = await sync_to_async(funcs.get_client_orders)(cb.from_user.username)
    if orders:
        await state.update_data(id=int(cb.data[1:]))
        order = {}
        for order in orders:
            if order['id'] == cb.data[1:]:
                order = order
                break
        await state.update_data(order2=order)
        for key in order:
            await cb.message.answer(f'{key}: {order[key]}')
        await cb.message.answer('What you wanna do?', reply_markup=m.manage_order)
    else:
        await cb.message.answer('No orders', reply_markup=m.exit_markup)
    await cb.answer()


@dp.callback_query_handler(Text(['access_order', 'close_order']), state=UserState.order)
async def manage_order(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    client_id[cb.from_user.username] = cb.from_user.id
    if cb.data == 'access_order':
        data = await state.get_data()
        id_order = data['id']
        order = await sync_to_async(funcs.get_order)(id_order)
        qr_str = ''
        for key in order:
            qr_str += f' {key}: {order[key]}.'
        qr_dic[cb.from_user.username]=qr_str
        for owner_id in owners_ids:
            await bot.send_message(owner_id, f'Client {cb.from_user.username} wanna get access to warehouse,\n{qr_str}',
                                   reply_markup=m.owner_send_qr)
            await bot.send_message(owner_id, 'Exit', reply_markup=m.exit_owner)
        await cb.message.answer('You will get QR, when owner reply')
        await cb.message.answer('Exit', reply_markup=m.exit_markup)
        await cb.answer()
    else:
        data = await state.get_data()
        await sync_to_async(funcs.delete_order)(data['id'])
        await cb.message.answer(f'Your order with id: {data["id"]} has closed', reply_markup=m.exit_markup)
        for owner_id in owners_ids:
            await bot.send_message(owner_id, f'Client: {cb.from_user.username} close his order with id: {data["id"]}',
                                   reply_markup=m.exit_owner)
        await state.finish()
        await cb.answer()


@dp.callback_query_handler(Text(['qr']), state='*')
async def send_qr(cb: types.CallbackQuery, state: FSMContext):
    qr_str = qr_dic[cb.message.text.split()[1]]
    await sync_to_async(funcs.get_qr)(qr_str)
    cl_id = client_id[cb.message.text.split()[1]]
    with open('last.png', 'rb') as photo:
        await bot.send_photo(cl_id, photo=photo)
    await bot.send_message(cl_id, 'Exit', reply_markup=m.exit_markup)
    await cb.message.answer('Main menu', reply_markup=m.owner_start_markup)
    await cb.answer()


@dp.callback_query_handler(Text(['msg_for_owner']), state='*')
async def message_start_client(cb: types.CallbackQuery):
    await cb.message.delete()
    await UserState.client.set()
    await cb.message.answer('Input your message to owner:', reply_markup=m.exit_markup)
    await cb.answer()


@dp.message_handler(state=UserState.client)
async def message_start_client(msg: types.Message, state: FSMContext):
    client_id[msg.from_user.username] = msg.from_user.id
    for owner_id in owners_ids:
        # await bot.send_message(owner_id, 'exit', reply_markup=m.exit_owner)
        await bot.send_message(owner_id, f'message from {msg.from_user.username}:\n{msg.text}',
                               reply_markup=m.owner_reply_message)
    # await msg.answer('exit', reply_markup=m.exit_markup)
    await state.finish()


@dp.callback_query_handler(Text(['reply']), state='*')
async def message_start_client(cb: types.CallbackQuery, state: FSMContext):
    cl_id = client_id[cb.message.text.split()[2][:-1]]
    # await cb.message.answer('exit', reply_markup=m.exit_owner)
    for owner_id in owners_ids:
        await bot.send_message(owner_id, f'input your reply for {cb.message.text.split()[2]}')
    await UserState.msg.set()
    await state.update_data(client_id=cl_id)
    await cb.answer()


@dp.message_handler(state=UserState.msg)
async def message_start_client(msg: types.Message, state: FSMContext):
    cl_id = await state.get_data()
    await bot.send_message(cl_id['client_id'], f'Message from {msg.from_user.username}:\n{msg.text}',
                           reply_markup=m.exit_markup)
    # await msg.answer('exit', reply_markup=m.exit_owner)
    await state.finish()


# ======= CLIENT BLOCK (END) ==============================================================================

# ======= OWNER BLOCK (START) ==============================================================================
@dp.callback_query_handler(Text(['orders']), state='*')
async def proceed_orders(cb: types.CallbackQuery):
    await cb.message.delete()
    orders = await sync_to_async(funcs.get_orders)()
    if orders:
        orders_markup = types.InlineKeyboardMarkup(row_width=1)
        orders_btn = []
        for order in orders:
            orders_btn.append(types.InlineKeyboardButton(f'{order["client"]}, cost: {order["amount"]}, end: '
                                                         f'{order["date_closed"]}',
                                                         callback_data=f'/{order["id"]}'))
        orders_btn.append(types.InlineKeyboardButton('Exit', callback_data='exit_owner'))
        orders_markup.add(*orders_btn)
        await cb.message.answer(f'Choose order', reply_markup=orders_markup)
        await UserState.order_own.set()
        await cb.answer()
    else:
        await cb.message.answer('You have not any orders', reply_markup=m.exit_markup)
        await cb.answer()


@dp.callback_query_handler(lambda cb: cb.data[0] == '/', state=UserState.order_own)
async def output_order_attributes(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    orders = await sync_to_async(funcs.get_orders)()
    if orders:
        await state.update_data(id=int(cb.data[1:]))
        order = {}
        for order in orders:
            if order['id'] == cb.data[1:]:
                order = order
                break
        for key in order:
            await cb.message.answer(f'{key}: {order[key]}')
        await cb.message.answer('What you wanna do?', reply_markup=m.manage_order_owner)
    else:
        await cb.message.answer('No orders', reply_markup=m.exit_owner)
    await cb.answer()


@dp.callback_query_handler(Text(['close_ord']), state=UserState.order_own)
async def manage_order(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    data = await state.get_data()
    chat_id = await sync_to_async(funcs.delete_order)(data['id'])
    for owner_id in owners_ids:
        await bot.send_message(owner_id, f'Order with id: {data["id"]} has closed by {cb.from_user.username}',
                               reply_markup=m.exit_owner)
    await bot.send_message(chat_id, f'Your order with id: {data["id"]} has closed',
                           reply_markup=m.exit_markup)
    await state.finish()
    await cb.answer()


@dp.callback_query_handler(Text(['exp_orders']), state='*')
async def proceed_orders(cb: types.CallbackQuery):
    await cb.message.delete()
    orders = await sync_to_async(funcs.get_expired_orders)()
    if orders:
        orders_markup = types.InlineKeyboardMarkup(row_width=1)
        orders_btn = []
        for order in orders:
            orders_btn.append(types.InlineKeyboardButton(f'{order["client"]}, id: {order["id"]}, overdays: '
                                                         f'{order["expired_days"]}',
                                                         callback_data=f'/{order["id"]}'))
        orders_btn.append(types.InlineKeyboardButton('Exit', callback_data='exit_owner'))
        orders_markup.add(*orders_btn)
        await cb.message.answer(f'Choose order', reply_markup=orders_markup)
        await UserState.order_exp.set()
        await cb.answer()
    else:
        await cb.message.answer('You have not any expired orders', reply_markup=m.exit_owner)
        await cb.answer()


@dp.callback_query_handler(lambda cb: cb.data[0] == '/', state=UserState.order_exp)
async def output_order_attributes(cb: types.CallbackQuery, state: FSMContext):
    orders = await sync_to_async(funcs.get_orders)()
    if orders:
        await state.update_data(id=int(cb.data[1:]))
        order = {}
        for order in orders:
            if order['id'] == cb.data[1:]:
                order = order
                break
        for key in order:
            await cb.message.answer(f'{key}: {order[key]}')
        await cb.message.answer('What you wanna do?', reply_markup=m.manage_order_owner)
    else:
        await cb.message.answer('No orders', reply_markup=m.exit_owner)
    await cb.answer()


@dp.callback_query_handler(Text(['close_ord']), state=UserState.order_exp)
async def manage_order(cb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = await sync_to_async(funcs.delete_order)(data['id'])
    for owner_id in owners_ids:
        await bot.send_message(owner_id, f'Order with id: {data["id"]} has closed by {cb.from_user.username}',
                               reply_markup=m.exit_owner)
    await bot.send_message(chat_id, f'Your order with id: {data["id"]} has closed',
                           reply_markup=m.exit_markup)
    await state.finish()
    await cb.answer()


@dp.callback_query_handler(Text(['clients']), state='*')
async def proceed_orders(cb: types.CallbackQuery):
    await cb.message.delete()
    clients = await sync_to_async(funcs.get_clients)()
    if clients:
        clients_markup = types.InlineKeyboardMarkup(row_width=1)
        clients_btn = []
        for client in clients:
            clients_btn.append(types.InlineKeyboardButton(f'{client["client"]}', callback_data=f'/{client["id"]}'))
        clients_btn.append(types.InlineKeyboardButton('Exit', callback_data='exit_owner'))
        clients_markup.add(*clients_btn)
        await cb.message.answer(f'Choose client', reply_markup=clients_markup)
        await UserState.customers.set()
        await cb.answer()
    else:
        await cb.message.answer('You have not any orders', reply_markup=m.exit_markup)
        await cb.answer()


@dp.callback_query_handler(lambda cb: cb.data[0] == '/', state=UserState.customers)
async def output_client_attributes(cb: types.CallbackQuery, state: FSMContext):
    clients = await sync_to_async(funcs.get_clients)()
    if clients:
        await state.update_data(id=int(cb.data[1:]))
        client = {}
        for client in clients:
            if client['id'] == cb.data[1:]:
                client = client
                break
        for key in client:
            await cb.message.answer(f'{key}: {client[key]}')
        await state.update_data(username=client['client'])
        await state.update_data(chat_id=client['chat_id'])
        data = await state.get_data()
        client_id[data['username']] = data['chat_id']
        await cb.message.answer('What you wanna do?', reply_markup=m.manage_client_owner)
    else:
        await cb.message.answer('No clients', reply_markup=m.exit_owner)
    await cb.answer()


@dp.callback_query_handler(Text(['close_ow']), state='*')
async def manage_order(cb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = await sync_to_async(funcs.delete_client)(data['id'])
    for owner_id in owners_ids:
        await bot.send_message(owner_id,
                               f'Registration for client {data["username"]} has closed by {cb.from_user.username}',
                               reply_markup=m.exit_owner)
    await bot.send_message(chat_id, f'Your registration are closed by {cb.from_user.username}',
                           reply_markup=m.exit_markup)
    await state.finish()
    await cb.answer()


@dp.callback_query_handler(Text(['msg_ow']), state='*')
async def message_start_owner(cb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    client_id[cb.from_user.username] = data['chat_id']
    # await cb.message.answer('exit', reply_markup=m.exit_markup)
    await cb.message.answer('Input your message', reply_markup=m.exit_owner)
    await UserState.mail_ow.set()
    await cb.answer()


@dp.message_handler(state=UserState.mail_ow)
async def message_start_owner(msg: types.Message):
    chat_id = client_id[msg.from_user.username]
    owner_id[msg.from_user.username] = msg.from_user.id
    # await msg.answer('exit', reply_markup=m.exit_owner)
    # await bot.send_message(chat_id, 'exit', reply_markup=m.exit_markup)
    await bot.send_message(chat_id, f'Message from {msg.from_user.username}:\n{msg.text}', reply_markup=m.owner_reply)
    await UserState.standby.set()


@dp.callback_query_handler(Text(['repl']), state='*')
async def message_start_owner(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.answer('Input your reply', reply_markup=m.exit_markup)
    await UserState.mail_l.set()
    own_id = owner_id[cb.message.text.split()[2][:-1]]
    own = cb.message.text.split()[2][:-1]
    await state.update_data(own=own, own_id=own_id)


@dp.message_handler(state=UserState.mail_l)
async def message_start_owner(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_message(data['own_id'], f'Message from {msg.from_user.username}:\n{msg.text}',
                           reply_markup=m.exit_owner)
    # await msg.answer('exit', reply_markup=m.exit_markup)


# ======= SENTINEL BLOCK (START) ============================================================================
async def sentinel():
    while 1:
        whole_orders = await sync_to_async(funcs.get_terms_orders)()
        for orders in whole_orders[:-1]:
            for order in orders:
                await bot.send_message(order['chat_id'],
                                       f'{-order["expired days"]} days till expired your order {order["order"]}')
        for order in whole_orders[-1]:
            await bot.send_message(order['chat_id'], f'Expired order: {order["order"]},\nexpired days: '
                                                     f'{order["expired days"]}\n===========')
            for owner_id in owners_ids:
                await bot.send_message(owner_id,
                                       f'Expired order: {order["order"]},\nclient: {order["client"]}\n'
                                       f'Expired days: {order["expired days"]}\n===========')
        await asyncio.sleep(86400)


async def on_startup(_):
    asyncio.create_task(sentinel())


# ======= SENTINEL BLOCK (END) ============================================================================


executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
