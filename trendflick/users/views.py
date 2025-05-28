from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import User, Wishlist
from products.models import Product
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


def login_view(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return render(request, 'home.html')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            User.objects.create(
                username=username,
                email=email,
                password=make_password(password1)
            )
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('users:login')

    return render(request, 'users/register.html')

def manage_account(request):
    if request.method == 'POST':
        # Add your account management logic here
        pass
    return render(request, 'users/manage_account.html')

@login_required
def view_profile(request):
    if request.method == 'POST':
        # Add your profile update logic here
        pass
    return render(request, 'users/view_profile.html')

@login_required
def orders(request):
    return render(request, 'users/orders.html')

@login_required
def wishlist(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    context = {
        'wishlist_items': wishlist.products.all()
    }
    return render(request, 'orders/wishlist.html', context)


def password_reset(request):
    if request.method == 'POST':
        # Add your password reset logic here
        pass
    return render(request, 'users/password_reset.html')

@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(pk=product.pk).exists():
        messages.info(request, "Item already in wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, "Item added to wishlist.")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist = get_object_or_404(Wishlist, user=request.user)

    if wishlist.products.filter(pk=product.pk).exists():
        wishlist.products.remove(product)
        messages.success(request, "Item removed from wishlist.")
    else:
        messages.info(request, "Item not found in wishlist.")

    return redirect(request.META.get('HTTP_REFERER', '/'))