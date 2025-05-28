from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('clothes', 'Clothes'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories'),
        ('sale', 'Sale'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/')
    sizes = models.JSONField(null=True, blank=True, help_text='List of available sizes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return round(discount)
        return 0