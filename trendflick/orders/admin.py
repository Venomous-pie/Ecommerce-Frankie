from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, PromoCode

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'total_items', 'created_at')
    inlines = [CartItemInline]
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'user__email', 'tracking_number')
    ordering = ('-created_at',)

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'expiration_date', 'usage_limit', 'times_used', 'active')
    list_filter = ('active',)
    search_fields = ('code',)
    ordering = ('-expiration_date',)
