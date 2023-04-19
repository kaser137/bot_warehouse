from django.contrib import admin
from .models import Client, Order, Storage, Owner

admin.site.register(Order)
admin.site.register(Client)
admin.site.register(Owner)


@admin.register(Storage)
class StoragerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'area', 'free_space']
