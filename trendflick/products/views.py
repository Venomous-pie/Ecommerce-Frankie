from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from orders.models import CartItem, Cart
from users.models import Wishlist


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        if not product_id:
            messages.error(request, "Invalid product.")
            return redirect('products:category', category='all')

        product = get_object_or_404(Product, id=product_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, f"Added {product.name} to your cart.")
        return redirect(request.META.get('HTTP_REFERER', 'products:category'))

    return render(request, 'orders/cart.html')


@login_required
def remove_from_cart(request, product_id):
    if not product_id:
        messages.error(request, "Invalid product.")
        return redirect('products:category', category='all')

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found.")
        return redirect(request.META.get('HTTP_REFERER', 'products:category'))

    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    if cart_item:
        cart_item.delete()
        messages.success(request, "Removed from cart.")
    else:
        messages.error(request, "Item not found in cart.")

    return redirect(request.META.get('HTTP_REFERER', 'products:category'))


def category(request, category):
    products_list = Product.objects.filter(category=category) if category != 'all' else Product.objects.all()

    # Handle sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products_list = products_list.order_by('price')
    elif sort == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort == 'name':
        products_list = products_list.order_by('name')
    else:
        products_list = products_list.order_by('-created_at')

    cart_product_ids = set()
    wishlist_product_ids = set()

    if request.user.is_authenticated:
        cart_product_ids = set(
            CartItem.objects.filter(cart__user=request.user).values_list('product_id', flat=True)
        )
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_product_ids = set(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass


    # Pagination
    paginator = Paginator(products_list, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Annotate products with flags only for authenticated users
    for product in products:
        product.in_cart = product.id in cart_product_ids
        product.in_wishlist = product.id in wishlist_product_ids

    context = {
        'category': category,
        'products': products,
        'current_sort': sort
    }
    return render(request, 'products/category.html', context)

def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'products/product_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
    ) if query else Product.objects.none()
    
    context = {
        'query': query,
        'products': products
    }
    return render(request, 'products/search.html', context)

def trending_products(request):
    products = Product.objects.all()[:4]
    return JsonResponse({
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url if product.image else None,
                'category': product.category
            }
            for product in products
        ]
    })

def related_products(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Get products in the same category, excluding the current product
    related = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    return JsonResponse({
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url if product.image else None,
                'category': product.category
            }
            for product in related
        ]
    })
