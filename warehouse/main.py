import os
import dotenv
import datetime
import asyncio
import funcs
import markups as m
from emoji import emojize
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text, Command
from asgiref.sync import sync_to_async
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(Path(BASE_DIR, 'venv', '.env'))
token = os.environ['BOT_TOKEN']
owner_id = os.environ['OWNER_ID']
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
today = datetime.date.today()

previous_markup = None
client_id = {}


class UserState(StatesGroup):
    mail = State()
    standby = State()
    storage = State()
    mass = State()
    sq = State()
    period = State()
    exit = State()
    order = State()
    client = State()
    msg = State()


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
            f'hello owner, please add to the field "chat_id for Bot" in admin {msg.from_user.id}\n '
            f'for continue type /next')
        await msg.answer(f'glad to see you {emojize(":eyes:")}', reply_markup=m.client_start_markup)
    elif type(status) is int:
        await msg.answer(f'Hi, {msg.from_user.first_name}. You have {status} orders.')
        await msg.answer('Main menu', reply_markup=m.client_start_markup)
    else:
        await msg.answer(f'Hello dear {msg.from_user.first_name}')
        await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.message_handler(state=[UserState.mass, UserState.sq, UserState.standby, UserState.order])
async def incorrect_input_proceeding(msg: types.Message):
    await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.message_handler(lambda msg: msg.text[0] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    state=[UserState.period])
async def incorrect_input_proceeding(msg: types.Message):
    await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text='faq', state=[UserState, None])
async def faq_proceeding(cb: types.CallbackQuery):
    global previous_markup
    previous_markup = 'client_start_markup'
    await cb.message.answer('Storage conditions... Blah blah blah ....', reply_markup=m.exit_markup)
    await cb.answer()


@dp.callback_query_handler(text="exit", state=[UserState, None])
async def exit_proceeding(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.answer('Main menu', reply_markup=m.client_start_markup)
    await cb.message.answer('type anything for restart')
    await state.finish()
    await cb.answer()


# ======= GREETINGS BLOCK (END) ============================================================================


# ======= CLIENT BLOCK (START) ==============================================================================
@dp.callback_query_handler(Text('put_things'), state=[UserState, None])
async def choose_weight(cb: types.CallbackQuery):
    await cb.message.answer('choose weight', reply_markup=m.choose_weight)
    await UserState.mass.set()
    await cb.answer()


@dp.callback_query_handler(Text(['mass_100', 'mass_70_100', 'mass_40_70', 'mass_25_40', 'mass_10_25', 'mass_0_10']),
                           state=UserState.mass)
async def get_weight_component_price(cb: types.CallbackQuery, state: FSMContext):
    for btn_data in ['mass_100', 'mass_70_100', 'mass_40_70', 'mass_25_40', 'mass_10_25', 'mass_0_10']:
        if cb.data == btn_data:
            data = await sync_to_async(funcs.get_cost_field)(cb.data)
            await state.update_data(mass=btn_data, mass_cfn=data)
            break
    data = await state.get_data()
    await cb.message.answer(f"coefficient to price {data}")
    await UserState.sq.set()
    await cb.message.answer('choose square', reply_markup=m.choose_square)
    await cb.answer()


@dp.callback_query_handler(Text(['metr_10', 'metr_7_10', 'metr_3_7', 'metr_0_3']), state=UserState.sq)
async def get_square_component_price(cb: types.CallbackQuery, state: FSMContext):
    for btn_data in ['metr_10', 'metr_7_10', 'metr_3_7', 'metr_0_3']:
        if cb.data == btn_data:
            data = await sync_to_async(funcs.get_cost_field)(cb.data)
            await state.update_data(sq=btn_data, sq_cfn=data)
            break
    data = await state.get_data()
    await cb.message.answer(f"cost for 1 day rent: {data['sq']}")
    await UserState.period.set()
    await cb.message.answer("input rent's period in days", reply_markup=m.exit_markup)
    await cb.answer()


@dp.message_handler(lambda msg: msg.text[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    state=UserState.period)
async def get_period_component_price(msg: types.Message, state: FSMContext):
    data = int(msg.text)
    await state.update_data(period=data)
    data = await state.get_data()
    await msg.answer(f"your price is: {data['period'] * data['mass_cfn'] * data['sq_cfn']} RUR",
                     reply_markup=m.choose_delivery)
    await UserState.standby.set()


@dp.callback_query_handler(Text(['delivery_yes', 'delivery_no']), state=UserState.standby)
async def choose_delivery_method(cb: types.CallbackQuery):
    if cb.data == 'delivery_yes':
        await cb.message.answer('for delivery details call: +7-777-777-77-77')
        await cb.message.answer('you can make order', reply_markup=m.make_order)
    else:
        await cb.message.answer('you can make order', reply_markup=m.make_order)
    await cb.answer()


@dp.callback_query_handler(Text(['order_yes', 'order_no']), state=UserState.standby)
async def choose_make_order(cb: types.CallbackQuery, state: FSMContext):
    if cb.data == 'order_no':
        await cb.message.answer('we were glad to see you', reply_markup=m.exit_markup)
        await cb.answer()
    else:
        status = await sync_to_async(funcs.identify_user)(cb.from_user.username)
        if status == 'owner':
            await cb.message.answer(f'it was funny {emojize(":eyes:")}', reply_markup=m.client_start_markup)
        elif type(status) is int:
            data = await state.get_data()
            amount = data["mass_cfn"] * data["sq_cfn"] * data["period"]
            tg_account = cb.from_user.username
            await cb.message.answer(f'Specs your order:\nmass: {data["mass"]}\nsquare: {data["sq"]}\nperiod: '
                                    f'{data["period"]}\nuser:{cb.from_user.username}')
            await sync_to_async(funcs.make_order)(mass=data["mass"], sq=data["sq"], period=data["period"],
                                                  amount=amount, tg_account=tg_account)
            await cb.message.answer(f'Your order has been registered\nfor pay: {amount}')
            await bot.send_message(owner_id, f'new order has been registered,\namount: {amount}\nclient: {tg_account}')
            await cb.message.answer('Main menu', reply_markup=m.client_start_markup)
            await state.finish()
            await cb.answer()
        else:
            chat_id = cb.from_user.id
            await cb.message.answer('before making order you need get registration')
            await cb.message.answer('for registration please read document about personal data')
            await bot.send_document(chat_id=chat_id, document=open('permitted.pdf', 'rb'),
                                    reply_markup=m.accept_personal_data)
            await cb.answer()


@dp.callback_query_handler(Text(['personal_yes', 'personal_no']), state=UserState.standby)
async def accepting_permission(cb: types.CallbackQuery):
    if cb.data == 'personal_no':
        await cb.message.answer('we were glad to see you', reply_markup=m.exit_markup)
        await cb.answer()
    else:
        await cb.message.answer('for ending registration input your email')
        await UserState.mail.set()
        await cb.answer()


@dp.message_handler(state=UserState.mail)
async def registrate_new_client(msg: types.Message, state: FSMContext):
    chat_id = msg.from_user.id
    tg_account = msg.from_user.username
    mail = msg.text
    data = await state.get_data()
    amount = data["mass_cfn"] * data["sq_cfn"] * data["period"]
    await sync_to_async(funcs.registration_client)(tg_account, chat_id, mail)
    await bot.send_message(owner_id, f'new client has been registered,\nchat_id: {chat_id}\ntg_account: {tg_account}')
    await msg.answer('You have been registered')
    await sync_to_async(funcs.make_order)(mass=data["mass"], sq=data["sq"], period=data["period"], amount=amount,
                                          tg_account=tg_account)
    await bot.send_message(owner_id, f'new order has been registered,\namount: {amount}\nclient: {tg_account}')
    await msg.answer(f'Your order has been registered\nfor pay: {amount}')
    await msg.answer('Main menu', reply_markup=m.client_start_markup)
    await state.finish()


@dp.callback_query_handler(Text(['boxes']), state=[UserState, None])
async def create_existing_orders(cb: types.CallbackQuery):
    status = await sync_to_async(funcs.identify_user)(cb.from_user.username)
    if status == 'owner':
        await cb.message.answer(f'it was funny {emojize(":eyes:")}', reply_markup=m.client_start_markup)
        await cb.answer()
    elif status == 'User is not registered':
        await cb.message.answer('Sorry, you are not registered')
        await cb.answer()
    else:
        orders = await sync_to_async(funcs.get_orders)(cb.from_user.username)
        if orders:
            orders_markup = types.InlineKeyboardMarkup(row_width=1)
            orders_btn = []
            for order in orders:
                orders_btn.append(types.InlineKeyboardButton(f'id: {order["id"]}_cost: {order["amount"]}',
                                                             callback_data=f'/{order["id"]}'))
            orders_btn.append(types.InlineKeyboardButton('Exit', callback_data='exit'))
            orders_markup.add(*orders_btn)
            await cb.message.answer(f'choose order {orders[0]["id"]}', reply_markup=orders_markup)
            await UserState.order.set()
            await cb.answer()
        else:
            await cb.message.answer('you have not any orders')
            await cb.answer()


@dp.callback_query_handler(lambda cb: cb.data[0] == '/', state=UserState.order)
async def output_order_attributes(cb: types.CallbackQuery, state: FSMContext):
    orders = await sync_to_async(funcs.get_orders)(cb.from_user.username)
    await state.update_data(id=int(cb.data[1:]))
    for order in orders:
        if order['id'] == cb.data[1:]:
            order = order
            break
    for key in order:
        await cb.message.answer(f'{key}: {order[key]}')
    await cb.message.answer('what you wanna do?', reply_markup=m.manage_order)
    await cb.answer()


@dp.callback_query_handler(Text(['access_order', 'close_order']), state=UserState.order)
async def manage_order(cb: types.CallbackQuery, state: FSMContext):
    if cb.data == 'access_order':
        client_id[cb.from_user.username] = cb.from_user.id
        await bot.send_message(owner_id, f'client {cb.from_user.username} wanna get access to warehouse, send QR',
                               reply_markup=m.owner_send_qr)
        await cb.message.answer('Main menu', reply_markup=m.client_start_markup)
        await cb.answer()
    else:
        data = await state.get_data()
        await sync_to_async(funcs.delete_order)(data['id'])
        await cb.message.answer(f'your order with id: {data["id"]} has closed')
        await bot.send_message(owner_id, f'order client: {cb.from_user.username} with id: {data["id"]} has closed')
        await state.finish()
        await cb.message.answer('Main menu', reply_markup=m.client_start_markup)
        await cb.answer()


@dp.callback_query_handler(Text(['qr']), state='*')
async def send_qr(cb: types.CallbackQuery):
    qr = await sync_to_async(funcs.get_qr)()
    cl_id = client_id[cb.message.text.split()[1]]
    await bot.send_message(cl_id, f' your QR: {qr}')
    await cb.answer()


@dp.callback_query_handler(Text(['msg']), state='*')
async def message_for_owner(cb: types.CallbackQuery):
    await UserState.client.set()
    await cb.message.answer('input your message')
    await cb.answer()


@dp.message_handler(state=UserState.client)
async def proceed_message(msg: types.Message, state: FSMContext):
    client_id[msg.from_user.username] = msg.from_user.id
    await bot.send_message(owner_id, f'message from {msg.from_user.username}:\n{msg.text}',
                           reply_markup=m.owner_reply_message)
    await state.finish()


@dp.callback_query_handler(Text(['reply']), state='*')
async def reply(cb: types.CallbackQuery, state: FSMContext):
    cl_id = client_id[cb.message.text.split()[2][:-1]]
    await bot.send_message(owner_id, f'input your reply for {cb.message.text.split()[2]}')
    await  cb.message.answer('Main menu', reply_markup=m.client_start_markup)
    await UserState.msg.set()
    await state.update_data(client_id=cl_id)
    await cb.answer()


@dp.message_handler(state=UserState.msg)
async def forward_message(msg: types.Message, state: FSMContext):
    cl_id = await state.get_data()
    await bot.send_message(cl_id['client_id'], f'message from {msg.from_user.username}:\n{msg.text}')
    await msg.answer('Main menu', reply_markup=m.client_start_markup)
    await state.finish()


# ======= CLIENT BLOCK (END) ==============================================================================


# ======= SENTINEL BLOCK (START) ============================================================================
async def sentinel():
    while 1:
        whole_orders = await sync_to_async(funcs.get_terms_orders)()
        for orders in whole_orders[:-1]:
            for order in orders:
                await bot.send_message(order['chat_id'],
                                       f'{-order["expired days"]} days till expired your order {order["order"]}')
        for order in whole_orders[-1]:
            await bot.send_message(order['chat_id'], f'expired order: {order["order"]},\nexpired days: '
                                                     f'{order["expired days"]}\n===========')
            await bot.send_message(owner_id,
                                   f'expired order: {order["order"]},\nclient: {order["client"]}\n'
                                   f'expired days: {order["expired days"]}\n===========')
        await asyncio.sleep(86400)


async def on_startup(_):
    asyncio.create_task(sentinel())


# ======= SENTINEL BLOCK (END) ============================================================================


executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
