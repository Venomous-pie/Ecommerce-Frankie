from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from products.models import Product
from .models import Cart, CartItem

@login_required
def cart(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
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

@login_required
def checkout(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('orders:cart')
    
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = 0 if subtotal >= 100 else 10
    total = subtotal + shipping
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    }
    return render(request, 'orders/checkout.html', context)

@require_POST
@login_required
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'})
        
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get_or_create(user=request.user)[0]
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Item added to cart',
            'cart': get_cart_data(cart)
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@login_required
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'})
        
        cart = Cart.objects.get(user=request.user)
        CartItem.objects.filter(cart=cart, product_id=product_id, size=size).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart': get_cart_data(cart)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@login_required
def update_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size')
        quantity = data.get('quantity')
        
        if not all([product_id, quantity]):
            return JsonResponse({'success': False, 'message': 'Product ID and quantity are required'})
        
        if quantity < 1:
            return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'})
        
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id, size=size)
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated',
            'cart': get_cart_data(cart)
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found in cart'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def get_cart_data(cart):
    return {
        'items': [
            {
                'id': item.product.id,
                'name': item.product.name,
                'price': str(item.product.price),
                'image': item.product.image.url if item.product.image else None,
                'size': item.size,
                'quantity': item.quantity,
                'total': str(item.product.price * item.quantity)
            }
            for item in cart.items.all()
        ],
        'total_items': sum(item.quantity for item in cart.items.all())
    }
