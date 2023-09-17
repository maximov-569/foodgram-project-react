from django.contrib import admin

from users.models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'email']


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
