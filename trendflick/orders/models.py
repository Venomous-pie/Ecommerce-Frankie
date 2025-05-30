from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal
from django.utils import timezone
from users.models import Address


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0, editable=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        if not self.active:
            return False
        if self.expiration_date and timezone.now() > self.expiration_date:
            return False
        if self.usage_limit is not None and self.times_used >= self.usage_limit:
            return False
        return True

    def apply_discount(self, original_price):
        if not self.is_valid():
            return original_price

        if self.discount_percent:
            discounted_price = original_price * (1 - self.discount_percent / 100)
            # Ensure price doesn't go below zero
            discounted_price = max(discounted_price, 0)
        else:
            discounted_price = original_price

        return discounted_price

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    @property
    def total_before_discount(self):
        return sum(item.total for item in self.items.all())

    @property
    def shipping_cost(self):
        return Decimal('0.00') if self.total_before_discount >= 100 else Decimal('10.00')

    @property
    def total_after_discount(self):
        return max(self.total_before_discount + self.shipping_cost - self.discount_amount, 0)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total(self):  # Optional: use this for subtotal only
        return self.total_before_discount


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_product_cartitems')  # <--- add this
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

    @property
    def total(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
        ('gcash', 'GCash'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')  # <-- NEW
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Snapshot of product name
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=10, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order #{self.order.id}"

    def save(self, *args, **kwargs):
        if not self.product_name and self.product:
            self.product_name = self.product.name
        if not self.product_price and self.product:
            self.product_price = self.product.price
        if not self.total:
            self.total = self.product_price * self.quantity
        super().save(*args, **kwargs)