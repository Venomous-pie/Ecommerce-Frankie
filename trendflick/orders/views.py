from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import *
from django.utils import timezone
from decimal import Decimal


from decimal import Decimal

@login_required(login_url='users:login')
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('0.00') if subtotal >= 100 else Decimal('10.00')
    discount = Decimal('0.00')
    promo_code_obj = None
    promo_code_error = None
    promo_code_success = None
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        promo_code_input = request.POST.get('promo_code', '').strip()

        if promo_code_input:
            try:
                promo_code_obj = PromoCode.objects.get(
                    code__iexact=promo_code_input,
                    expiration_date__gte=timezone.now(),
                    active=True,
                )

                if promo_code_obj.usage_limit is not None and promo_code_obj.times_used >= promo_code_obj.usage_limit:
                    promo_code_error = "This promo code has reached its usage limit."
                    request.session.pop('promo_code_id', None)
                    request.session.pop('discount', None)
                else:
                    if promo_code_obj.discount_percent:
                        discount = (subtotal * promo_code_obj.discount_percent) / Decimal('100')
                    else:
                        discount = Decimal('0.00')

                    discount = min(discount, subtotal)

                    # Save promo code info in session as string for accuracy
                    request.session['promo_code_id'] = promo_code_obj.id
                    request.session['discount'] = str(discount)

                    promo_code_success = f'Promo code "{promo_code_obj.code}" applied! You saved ₱{discount:.2f}.'

            except PromoCode.DoesNotExist:
                promo_code_error = "Invalid or expired promo code."
                request.session.pop('promo_code_id', None)
                request.session.pop('discount', None)
    else:
        # On GET: load promo code info from session if available
        promo_code_id = request.session.get('promo_code_id')
        discount = Decimal(request.session.get('discount', '0.00'))
        if promo_code_id:
            try:
                promo_code_obj = PromoCode.objects.get(id=promo_code_id)
            except PromoCode.DoesNotExist:
                promo_code_obj = None
                discount = Decimal('0.00')

    total = subtotal + shipping - discount
    if total < 0:
        total = Decimal('0.00')

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'discount': discount,
        'total': total,
        'promo_code': promo_code_obj,
        'promo_code_error': promo_code_error,
        'promo_code_success': promo_code_success,
        'form_submitted': form_submitted,
    }
    return render(request, 'orders/cart.html', context)

@require_POST
@login_required(login_url='users:login')
def remove_from_cart(request, product_id):
    try:
        product_id = int(product_id)
        cart = Cart.objects.get(user=request.user)
        
        deleted, _ = CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        
        if deleted:
            messages.success(request, "Item removed from cart.")
        else:
            messages.warning(request, "Item not found in cart.")
    except (Cart.DoesNotExist, ValueError):
        messages.error(request, "Cart or Product not found.")

    return redirect('orders:cart')

@require_POST
@login_required(login_url='users:login')
def update_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    action = request.POST.get('action')

    cart = Cart.objects.get(user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        
        # Handle +/- buttons
        if action == "increase" and cart_item.quantity < 10:
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.quantity = quantity  # Manual input fallback

        cart_item.save()
        messages.success(request, "Cart updated.")
    except CartItem.DoesNotExist:
        messages.error(request, "Cart item not found.")

    return redirect('orders:cart')


@login_required(login_url='users:login')
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.items.count() == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('orders:cart')

    profile = request.user.profile
    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    
    if not addresses:
        messages.warning(request, "Please add a shipping address before checkout.")
        return redirect('users:add_address')

    discount = Decimal(request.session.get('discount', 0))
    promo_code_id = request.session.get('promo_code_id')
    promo_code_obj = None
    if promo_code_id:
        try:
            promo_code_obj = PromoCode.objects.get(id=promo_code_id)
        except PromoCode.DoesNotExist:
            promo_code_obj = None
            discount = Decimal('0')

    subtotal = sum(item.product.price * item.quantity for item in cart.items.all())
    shipping_cost = Decimal('0.00') if subtotal >= 100 else Decimal('10.00')
    total = subtotal + shipping_cost - discount
    if total < 0:
        total = Decimal('0.00')

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount': discount,
        'total': total,
        'promo_code': promo_code_obj,
        'profile': profile,
        'addresses': addresses,
        'address': addresses.first() if addresses else None,
    }
    return render(request, 'orders/checkout.html', context)

@login_required(login_url='users:login')
def place_order_view(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            messages.warning(request, "Cart is empty.")
            return redirect('orders:cart')

        address_id = request.POST.get('address_id')
        if not address_id:
            messages.error(request, "Please provide a shipping address.")
            return redirect('orders:checkout')

        try:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        except (ValueError, Address.DoesNotExist):
            messages.error(request, "Invalid address selected.")
            return redirect('orders:checkout')

        phone = request.POST.get('phone_number')
        if not phone:
            phone = request.user.profile.phone
        if not phone:
            messages.error(request, "Please provide a phone number.")
            return redirect('orders:checkout')

        email = request.user.email
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'cod')

        # Get discount info from session
        discount = Decimal(request.session.get('discount', 0))
        promo_code_id = request.session.get('promo_code_id')
        promo_code_obj = None
        if promo_code_id:
            try:
                promo_code_obj = PromoCode.objects.get(id=promo_code_id)
            except PromoCode.DoesNotExist:
                promo_code_obj = None
                discount = Decimal('0')

        # Calculate totals
        subtotal = sum(item.product.price * item.quantity for item in cart.items.all())
        shipping_cost = Decimal('0.00') if subtotal >= 100 else Decimal('10.00')
        total = subtotal + shipping_cost - discount
        if total < 0:
            total = Decimal('0.00')

        # Create the order
        order = Order.objects.create(
            user=request.user,
            address=address,
            shipping_address=address.formatted(),
            phone=phone,
            email=email,
            subtotal=subtotal,
            discount=discount,
            shipping_cost=shipping_cost,
            total=total,
            notes=notes,
            promo_code=promo_code_obj,
            payment_method=payment_method
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity,
                size=item.size,
                total=item.product.price * item.quantity,
            )

        # Clean up
        cart.items.all().delete()
        request.session.pop('promo_code_id', None)
        request.session.pop('discount', None)

        messages.success(request, "Order placed successfully!")
        return redirect('orders:success', order_id=order.id)

    return redirect('orders:checkout')

@login_required(login_url='users:login')
def order_success_view(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/order-success.html', {'order': order})

@login_required(login_url='users:login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})