from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)

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