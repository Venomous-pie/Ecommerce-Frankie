from django.shortcuts import render, redirect
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

@login_required
def profile(request):
    if request.method == 'POST':
        # Add your profile update logic here
        pass
    return render(request, 'users/profile.html')

@login_required
def orders(request):
    return render(request, 'users/orders.html')

@login_required
def wishlist(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    context = {
        'wishlist_items': wishlist.products.all()
    }
    return render(request, 'users/wishlist.html', context)

def password_reset(request):
    if request.method == 'POST':
        # Add your password reset logic here
        pass
    return render(request, 'users/password_reset.html')

@require_POST
@login_required
def add_to_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'})
        
        product = Product.objects.get(id=product_id)
        wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
        
        if product not in wishlist.products.all():
            wishlist.products.add(product)
            return JsonResponse({
                'success': True,
                'message': 'Item added to wishlist',
                'wishlist': get_wishlist_data(wishlist)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Item already in wishlist'
            })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@login_required
def remove_from_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'})
        
        wishlist = Wishlist.objects.get(user=request.user)
        product = Product.objects.get(id=product_id)
        wishlist.products.remove(product)
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from wishlist',
            'wishlist': get_wishlist_data(wishlist)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def get_wishlist_data(wishlist):
    return {
        'items': [
            {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url if product.image else None,
                'category': product.category
            }
            for product in wishlist.products.all()
        ],
        'total_items': wishlist.products.count()
    }
