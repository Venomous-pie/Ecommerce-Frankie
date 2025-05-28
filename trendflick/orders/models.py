from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    @property
    def total(self):
        return sum(item.total for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.subtotal + self.shipping_cost
        super().save(*args, **kwargs)

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
