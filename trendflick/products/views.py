from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product

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
    else:  # newest
        products_list = products_list.order_by('-created_at')

    # Pagination
    paginator = Paginator(products_list, 9)  # Show 9 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

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
    # For demo purposes, just return the first 4 products
    # In a real app, you would implement proper trending logic
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
