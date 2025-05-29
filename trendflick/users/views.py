from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from .models import PasswordResetCode, Wishlist, Address
from products.models import Product
from orders.models import Order

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
        pass
    return render(request, 'users/manage_account.html')

def change_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        user.username = username
        user.email = email

        if password or confirm_password:
            if password == confirm_password:
                user.set_password(password)
                messages.success(request, 'Password updated successfully.')
            else:
                return redirect('change_password')

        user.save()
        messages.success(request, 'Account details updated successfully.')
        return redirect('users:login')
    return render(request, 'users/change_password.html') 

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders.html', {'orders': orders})

@login_required
def wishlist(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    context = {
        'wishlist_items': wishlist.products.all()
    }
    return render(request, 'orders/wishlist.html', context)

def password_reset(request):
    if request.method == 'POST':
        pass
    return render(request, 'users/password_reset.html')

@login_required
@require_POST
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(pk=product.pk).exists():
        wishlist.products.remove(product)
        in_wishlist = False
    else:
        wishlist.products.add(product)
        in_wishlist = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'in_wishlist': in_wishlist})

    return redirect(request.META.get('HTTP_REFERER', '/'))

def addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/addresses.html', {
        'addresses': addresses,
        'user': request.user
    })

@login_required(login_url='login')
def add_address(request):
    if request.method == 'POST':
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
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
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
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('addresses')

def set_default_address(request):
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

def is_social_user(user):
    return hasattr(user, 'socialaccount_set') and user.socialaccount_set.exists()

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if is_social_user(user):
                messages.error(request, "This account uses Google/Facebook login. Please login through social provider.")
                return redirect('users:password_reset')

            reset_code = PasswordResetCode.objects.create(user=user)
            reset_url = request.build_absolute_uri(f"/users/password-reset/verify/?code={reset_code.code}")

            send_mail(
                'Password Reset Request',
                f'Use the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "A reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
    return render(request, 'users/password_reset.html')

def password_reset_verify(request):
    code = request.GET.get('code')
    try:
        reset_entry = PasswordResetCode.objects.get(code=code, is_used=False)
        if not reset_entry.is_valid():
            messages.error(request, "This reset link has expired.")
            return redirect('users:password_reset')
        return render(request, 'users/password_reset_verify.html', {'code': code})
    except PasswordResetCode.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('users:password_reset')

def password_reset_complete(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(f'/users/password-reset/verify/?code={code}')

        try:
            reset_entry = PasswordResetCode.objects.get(code=code, is_used=False)
            if not reset_entry.is_valid():
                messages.error(request, "Reset link has expired.")
                return redirect('users:password_reset')

            user = reset_entry.user
            user.set_password(password)
            user.save()
            reset_entry.is_used = True
            reset_entry.save()

            messages.success(request, "Password has been reset. You may now log in.")
            return redirect('users:login')
        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Invalid reset code.")
    return redirect('users:password_reset')
