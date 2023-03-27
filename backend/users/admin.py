from django.contrib import admin
from django.contrib.admin import register
from users.models import Subscribe, User


class BaseAdminSettings(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_filter = ('email', 'username')

@register(User)
class UsersAdmin(BaseAdminSettings):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_display_links = ('id', 'username')
    search_fields = ('username', 'email',)


@register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)
