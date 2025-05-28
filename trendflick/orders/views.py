from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem

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
