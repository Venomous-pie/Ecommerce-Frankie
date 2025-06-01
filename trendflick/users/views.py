from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .models import PasswordResetCode, Wishlist, Address
from products.models import Product
from orders.models import Order
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from django.contrib.auth import update_session_auth_hash


def login_view(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Check if it's an email
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password')
                return render(request, 'users/login.html')
        else:
            username = username_or_email

        user = authenticate(request, username=username, password=password)

        if user is not None:
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

@login_required(login_url='users:login')
def manage_account(request):
    user = request.user
    profile = user.profile

    dob_error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('gender', '').strip()
        dob_str = request.POST.get('date_of_birth')

        avatar_file = request.FILES.get('avatar')
        if avatar_file:
            profile.avatar = avatar_file

        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                profile.date_of_birth = dob
            except ValueError:
                dob_error = "Invalid date format."
        else:
            profile.date_of_birth = None

        profile.phone = phone
        profile.gender = gender

        if name:
            name_parts = name.split(maxsplit=1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        if not dob_error:
            user.save()
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('users:manage_account')

    context = {
        'dob_error': dob_error,
        'request': request,
    }
    return render(request, 'users/manage_account.html', context)

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
                return redirect('users:change_password')

        user.save()
        messages.success(request, 'Account details updated successfully.')
        return redirect('users:login')
    return render(request, 'users/change_password.html') 

@login_required(login_url='users:login')
def update_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        password = request.POST.get('new_password')

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'users/change_password.html')
        else:
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully.")
            return redirect('users:manage_account')
        
    return render(request, 'users/change_password.html')

@login_required(login_url='users:login')
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders.html', {'orders': orders})

@login_required(login_url='users:login')
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

@login_required(login_url='users:login')
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

@login_required(login_url='users:login')
@require_POST
def clear_wishlist(request):
    Wishlist.objects.filter(user=request.user).first().products.clear()
    return redirect('users:wishlist')

def addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/addresses.html', {
        'addresses': addresses,
        'user': request.user
    })

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
            phone_number=request.user.profile.phone,
            is_default=bool(request.POST.get('is_default'))
        )
        messages.success(request, 'Address added successfully!')
        return redirect('users:addresses')
    
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
        return redirect('users:addresses')
    
    return render(request, 'users/edit_address.html', {'address': address})

def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('users:addresses')

def set_default_address(request, address_id):
    """Set an address as default."""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated successfully!')
    return redirect('users:addresses')

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

            subject = 'Your Password Reset Code'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            # Render the HTML email template with context
            html_content = render_to_string('users/password_reset_email.html', {
                'username': user.username,
                'reset_code': reset_code.code,
            })

            # Create email with both plain text and HTML alternatives
            text_content = (
                f"Hello {user.username},\n\n"
                f"You requested a password reset. Use the following code to reset your password:\n\n"
                f"{reset_code.code}\n\n"
                "If you did not request this, please ignore this email.\n\n"
                "Thanks,\n"
                "Your Website Team"
            )
            email_message = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            email_message.attach_alternative(html_content, "text/html")
            email_message.send(fail_silently=False)

            return redirect('users:password_reset_verify')

        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
    return render(request, 'users/password_reset.html')

def password_reset_verify(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        if not code or not code.isdigit() or len(code) != 6:
            messages.error(request, "Invalid reset code format.")
            return render(request, 'users/password_reset_verify.html')

        try:
            reset_entry = PasswordResetCode.objects.get(code=code, is_used=False)
            if not reset_entry.is_valid():
                messages.error(request, "Reset code has expired.")
                return redirect('users:password_reset')

            # ✅ Store code in session
            request.session['reset_code'] = code

            return redirect('users:password_reset_complete')

        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Invalid reset code.")
            return render(request, 'users/password_reset_verify.html')

    return render(request, 'users/password_reset_verify.html')

def password_reset_complete(request):
    code = request.session.get('reset_code', '').strip()

    try:
        reset_entry = PasswordResetCode.objects.get(code=code, is_used=False)
        if not reset_entry.is_valid():
            messages.error(request, "Reset code has expired.")
            return redirect('users:password_reset')
    except PasswordResetCode.DoesNotExist:
        messages.error(request, "Unauthorized or invalid reset code.")
        return redirect('users:password_reset')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/password_reset_complete.html')

        user = reset_entry.user
        user.set_password(password)
        user.save()

        reset_entry.is_used = True
        reset_entry.save()

        # Cleanup session
        del request.session['reset_code']

        messages.success(request, "Password has been reset. You may now log in.")
        return redirect('users:login')

    return render(request, 'users/password_reset_complete.html')