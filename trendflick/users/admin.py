from django.contrib import admin
from .models import Profile, Wishlist

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
