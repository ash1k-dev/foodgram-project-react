from django.contrib import admin
from django.contrib.admin import register
from users.models import Subscribe, User


@register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_display_links = ('id', 'username')
    list_filter = ('email', 'username')
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'


@register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)
