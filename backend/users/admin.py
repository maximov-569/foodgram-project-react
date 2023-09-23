from django.contrib import admin
from users.models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    """Admin model for Users."""
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
