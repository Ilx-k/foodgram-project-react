from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription


@admin.register(FoodgramUser)
class UserAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('username',)
    list_editable = (
        'email',
        'first_name',
        'last_name'
    )
    list_fields = ('first_name',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author'
    )
    search_fields = (
        'user',
        'author'
    )
    list_editable = (
        'user',
        'author'
    )
    empty_value_display = '-пусто-'
