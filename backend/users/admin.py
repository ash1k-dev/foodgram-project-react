from django.contrib import admin
from django.contrib.admin import register

from .models import Subscriptions, User


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


@register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    pass

