from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from django.utils import timezone
import uuid
import random


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist"

    class Meta:
        ordering = ['-created_at']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profile_avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_default_address(self):
        return self.user.addresses.filter(is_default=True).first()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name}'s address in {self.city}"
    
    def formatted(self):
        return f"{self.full_name}\n{self.street_address}\n{self.city}, {self.state} {self.postal_code}\n{self.country}\nPhone: {self.phone_number}"

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']

def generate_unique_numeric_code():
    while True:
        code = ''.join(str(random.randint(0, 5)) for _ in range(6))
        if not PasswordResetCode.objects.filter(code=code).exists():
            return code

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_numeric_code()
        super().save(*args, **kwargs)

    def is_valid(self):
        return (timezone.now() - self.created_at).total_seconds() < 900  # 15 minutes

    def __str__(self):
        return f"PasswordResetCode({self.user.username}, {self.code}, Used: {self.is_used})"