from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import User, Wishlist
from products.models import Product

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        # Add your registration logic here
        pass
    return render(request, 'users/register.html')

@login_required
def profile(request):
    if request.method == 'POST':
        # Add your profile update logic here
        pass
    return render(request, 'users/profile.html')

@login_required
def orders(request):
    # Add your orders view logic here
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
