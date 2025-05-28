from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import *
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

def addresses_view(request):
    """View for managing user addresses."""
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/addresses.html', {
        'addresses': addresses,
        'user': request.user
    })

@login_required(login_url='login')
def add_address(request):
    """Add a new address."""
    if request.method == 'POST':
        # If setting as default, unset other default addresses
        if request.POST.get('is_default'):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            street_address=request.POST.get('street_address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country'),
            phone_number=request.POST.get('phone_number'),
            is_default=bool(request.POST.get('is_default'))
        )
        messages.success(request, 'Address added successfully!')
        return redirect('addresses')
    
    return render(request, 'users/add_address.html')


def edit_address(request, address_id):
    """Edit an existing address."""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        # If setting as default, unset other default addresses
        if request.POST.get('is_default'):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        address.full_name = request.POST.get('full_name')
        address.street_address = request.POST.get('street_address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postal_code = request.POST.get('postal_code')
        address.country = request.POST.get('country')
        address.phone_number = request.POST.get('phone_number')
        address.is_default = bool(request.POST.get('is_default'))
        address.save()
        
        messages.success(request, 'Address updated successfully!')
        return redirect('addresses')
    
    return render(request, 'users/edit_address.html', {'address': address})


def delete_address(request, address_id):
    """Delete an address."""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('addresses')

def set_default_address(request):
    """Get the default address for the user."""
    try:
        address = Address.objects.get(user=request.user, is_default=True)
        return JsonResponse({
            'status': 'success',
            'address': {
                'full_name': address.full_name,
                'street_address': address.street_address,
                'city': address.city,
                'state': address.state,
                'postal_code': address.postal_code,
                'country': address.country,
                'phone_number': address.phone_number
            }
        })
    except Address.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No default address found.'})