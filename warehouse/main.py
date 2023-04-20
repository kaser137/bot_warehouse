import os
import dotenv
import datetime
import asyncio
import time
import funcs
from emoji import emojize
from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from asgiref.sync import sync_to_async, async_to_sync
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(Path(BASE_DIR, 'venv', '.env'))
token = os.environ['BOT_TOKEN']
owner_id = os.environ['OWNER_ID']
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
today = datetime.date.today()


class UserState(StatesGroup):
    mail = State()
    phone = State()
    storage = State()


# start division____________________________________________________________
@dp.message_handler(lambda msg: not msg.text[0] == '/' or msg.text == '/start')
async def start_conversation(msg: types.Message):
    status = await sync_to_async(funcs.identify_user)(msg.from_user.username)
    if status == 'owner':
        await msg.answer(
            f'hello owner, please add to the field "chat_id for Bot" in admin {msg.from_user.id}\n for continue type /next')
        await msg.answer(f'glad to see you {emojize(":eyes:")}')
    elif type(status) is int:
        await msg.answer(f'hi {msg.from_user.first_name} you have {status} orders')
    else:
        await msg.answer(f'Hello dear {msg.from_user.first_name},\nsorry, but you are not registered')
        await msg.answer('some .................\ncool..................\npromotion')
        await msg.answer('Wanna join? type /registration')


# end start division___________________________________________________________________________________
# client div____________________________________________________________________________________________
@dp.message_handler(commands=['registration'])
async def propose_registration(msg: types.Message):
    chat_id = msg.from_user.id
    await msg.answer('for registration please read document')
    await bot.send_document(chat_id=chat_id, document=open('permitted.pdf', 'rb'))
    await msg.answer('if you agree, type /accept')
    await msg.answer('if you dont agree, type /cancel')


@dp.message_handler(commands=['cancel'])
async def cancel_registration(msg: types.Message):
    await msg.answer('Take care')


@dp.message_handler(commands=['accept'])
async def accept_registration(msg: types.Message):
    client = await sync_to_async(funcs.identify_user)(msg.from_user.username)
    if client == 'Not_reg':
        await msg.answer('Input your email')
        await UserState.mail.set()
    else:
        await msg.answer('You are registered')


@dp.message_handler(lambda msg: not msg.text[0] == '/', state=UserState.mail)
async def registrate_client(msg: types.Message, state: FSMContext):
    chat_id = msg.from_user.id
    tg_account = msg.from_user.username
    mail = msg.text
    await sync_to_async(funcs.registration_client)(tg_account, chat_id, mail)
    await bot.send_message(owner_id, f'new client has been registered,\nchat_id: {chat_id}\ntg_account: {tg_account}')
    await msg.answer('You have been registered\n for list storages type /storages')
    await state.finish()


@dp.message_handler(lambda msg: msg.text[0] == '/', state=UserState.mail)
async def catch_invalid_eail(msg: types.Message):
    await msg.answer('Incorrect email, repeat input')


@dp.message_handler(commands=['storages'])
async def output_list_sorages(msg: types.Message):
    storages = await sync_to_async(funcs.get_available_storages)()
    for storage in storages:
        await msg.answer(
            f'№ storage: {storage.id}\naddress storage: {storage.address}\navailable area: {await sync_to_async(storage.free_space)()}\n===========')
    await msg.answer('for make new order type № of storage\nfor cancel type /cancel')
    await UserState.storage.set()


@dp.message_handler(lambda msg: msg.text[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    state=UserState.storage)
async def choose_storage(msg: types.Message, state: FSMContext):
    await msg.answer('all is good')
    await state.finish()


@dp.message_handler(lambda msg: msg.text[0] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    state=UserState.storage)
async def catch_invalid_storage(msg: types.Message):
    await msg.answer('Incorrect №, repeat input')


async def p():
    await asyncio.sleep(3)
    print('5')


async def sentinel():
    while 1:
        await asyncio.sleep(10)
        orders = await sync_to_async(funcs.get_expired_orders)()
        print(orders)
        for order in orders:
            print(order)
            await bot.send_message(order['chat_id'],
                                   f'expired order: {order["order"]},\nclient: {order["client"]}\nstorage: {order["storage"]}\n'
                                   f'expired days: {order["expired days"]}\n===========')
            await bot.send_message(owner_id,
                                   f'expired order: {order["order"]},\nclient: {order["client"]}\nstorage: {order["storage"]}\n'
                                   f'expired days: {order["expired days"]}\n===========')

async def sentinel3():
    while 1:
        await asyncio.sleep(7)
        orders = await sync_to_async(funcs.get_terms_orders3)()
        print(3333333)
        for order in orders:
            print(3)
            await bot.send_message(order['chat_id'],
                                   f'expired order: {order["order"]},\nclient: {order["client"]}\nstorage: {order["storage"]}\n'
                                   f'expired days: {order["expired days"]}\n===========')
            await bot.send_message(owner_id,
                                   f'expired order: {order["order"]},\nclient: {order["client"]}\nstorage: {order["storage"]}\n'
                                   f'expired days: {order["expired days"]}\n===========')



async def on_startup(_):
    asyncio.gather(sentinel(), sentinel3())


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(5, repeat, coro, loop)


# loop = asyncio.get_event_loop()
# loop=asyncio.new_event_loop()
# loop.call_later(5, repeat, sentinel, loop)
# asyncio.set_event_loop(loop)
# loop.run_until_complete(p())
executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
