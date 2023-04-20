import datetime
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse.settings')
import django

django.setup()

from admin_warehouse.models import Client, Storage, Order, Owner
from email_validate import validate


def get_terms_orders():
    orders30 = Order.objects.filter(date_closed=datetime.date.today() + datetime.timedelta(days=30)).exclude(
        is_expired=True)
    orders14 = Order.objects.filter(date_closed=datetime.date.today() + datetime.timedelta(days=14)).exclude(
        is_expired=True)
    orders3 = Order.objects.filter(date_closed=datetime.date.today() + datetime.timedelta(days=3)).exclude(
        is_expired=True)
    orders00 = Order.objects.filter(date_closed__lt=datetime.date.today()).exclude(is_expired=True)
    ord = [[], [], [], []]
    orders_terms = [orders30, orders14, orders3, orders00]
    for orders in orders_terms:
        for order in orders:
            expired_orderes = {
                'order': order,
                'chat_id': order.client.chat_id,
                'client': order.client,
                'storage': order.storage,
                'expired days': -(order.date_closed - datetime.date.today()).days
            }
            ord[orders_terms.index(orders)].append(expired_orderes)
    return ord[0], ord[1], ord[2], ord[3]


def identify_user(tg_account: str):
    try:
        owner = Owner.objects.get(tg_account=tg_account)
        return 'owner'
    except Owner.DoesNotExist:
        try:
            client = Client.objects.get(tg_account=tg_account)
            return client.status()
        except Client.DoesNotExist:
            return 'Not_reg'


def registration_client(tg_account, chat_id, mail):
    Client.objects.create(tg_account=tg_account, chat_id=chat_id, mail=mail)


def check_mail(txt):
    return validate(txt)


def get_available_storages():
    return [storage for storage in Storage.objects.all() if storage.free_space() > 0]
