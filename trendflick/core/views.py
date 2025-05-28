from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json
from .models import NewsletterSubscription
from products.models import Product
from django.core.paginator import Paginator
from django.db.models import Q
from orders.models import CartItem, Cart
from users.models import Wishlist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'core/about.html')

def about(request):
    return render(request, 'core/about.html')

def faq(request):
    return render(request, 'core/faq.html')

def privacy(request):
    return render(request, 'core/privacy.html')

@require_POST
@csrf_exempt
def newsletter_subscribe(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            message = 'Successfully subscribed to newsletter'
        else:
            if not subscription.is_active:
                subscription.is_active = True
                subscription.save()
                message = 'Your subscription has been reactivated'
            else:
                message = 'You are already subscribed to our newsletter'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'This email is already subscribed'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def search(request):
    query = request.GET.get('q', '').strip()
    current_sort = request.GET.get('sort', 'newest')

    products_list = Product.objects.all()

    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Optional price filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    # Sorting
    if current_sort == 'price_low':
        products_list = products_list.order_by('price')
    elif current_sort == 'price_high':
        products_list = products_list.order_by('-price')
    elif current_sort == 'name':
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
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    for product in products:
        product.in_cart = product.id in cart_product_ids
        product.in_wishlist = product.id in wishlist_product_ids

    cart_product_ids = set()
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_product_ids = set(
                CartItem.objects.filter(cart=cart).values_list('product_id', flat=True)
            )
        except Cart.DoesNotExist:
            pass


    context = {
        'products': products,
        'query': query,
        'current_sort': current_sort
    }
    return render(request, 'products/search_results.html', context)
