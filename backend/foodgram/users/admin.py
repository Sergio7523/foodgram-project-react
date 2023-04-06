from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from foodgram.settings import EMPTY_VALUE_DISPLAY
from users.models import Follow, User


class UserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = EMPTY_VALUE_DISPLAY


class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user',)
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email',
    )
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
