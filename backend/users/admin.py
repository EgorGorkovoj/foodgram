from django.contrib import admin

from users.models import User, Subscription


class ApiUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email', )
    list_filter = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_display_links = ('username',)


class ApiSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'user__email')


admin.site.register(User, ApiUserAdmin)
admin.site.register(Subscription, ApiSubscriptionAdmin)
