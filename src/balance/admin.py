from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'type', 'create']

@admin.register(Cards)
class CardsAdmin(admin.ModelAdmin):
    list_display = ['card', 'status', 'user']