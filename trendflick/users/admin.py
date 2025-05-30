from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    ordering = ('-created_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    filter_horizontal = ('products',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'postal_code', 'country', 'is_default', 'created_at')
    list_filter = ('country', 'is_default')
    search_fields = ('user__username', 'full_name', 'city', 'state', 'postal_code')
    ordering = ('-is_default', '-created_at')

@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_used', 'created_at', 'is_valid_display')
    list_filter = ('is_used',)
    search_fields = ('user__username', 'code')
    readonly_fields = ('code', 'created_at', 'is_valid_display')

    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Is Valid?'