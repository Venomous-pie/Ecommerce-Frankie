from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import *

@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = 0 if subtotal >= 100 else 10
    total = subtotal + shipping
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    }
    return render(request, 'orders/cart.html', context)

@require_POST
@login_required
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
@login_required
def update_cart(request):
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = Cart.objects.get(user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id, size=size)
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Cart updated.")
    except CartItem.DoesNotExist:
        messages.error(request, "Cart item not found.")
    
    return redirect('orders:cart')

from decimal import Decimal

@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.items.count() == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('orders:cart')

    profile = request.user.profile
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': cart.total,
        'shipping_cost': Decimal('0.00') if cart.total >= 100 else Decimal('10.00'),
        'total': cart.total + (Decimal('0.00') if cart.total >= 100 else Decimal('10.00')),
        'profile': profile,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def place_order_view(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            messages.warning(request, "Cart is empty.")
            return redirect('orders:cart')

        shipping_address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        notes = request.POST.get('notes', '')

        subtotal = cart.total
        shipping_cost = Decimal('0.00') if subtotal >= 100 else Decimal('10.00')
        total = subtotal + shipping_cost

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone=phone,
            email=email,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            notes=notes,
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity,
                size=item.size,
                total=item.total,
            )

        cart.items.all().delete()
        messages.success(request, "Order placed successfully!")
        return redirect('orders:success', order_id=order.id)
    return redirect('orders:checkout')

@login_required
def order_success_view(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/order-success.html', {'order': order})