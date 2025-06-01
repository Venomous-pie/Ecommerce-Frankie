from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json
from .models import NewsletterSubscription
from products.models import Product
from products.models import Category
from django.views.decorators.csrf import csrf_protect


def home(request):
    categories = Category.objects.all()[:6]
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = NewsletterSubscription.objects.filter(email=request.user.email).exists()    # Get trending products
    trending_products = Product.objects.filter(trending=True).order_by('?')[:12]
    
    # Get featured products
    featured_products = Product.objects.filter(featured=True).order_by('?')[:12]

    return render(request, 'home.html', {
        'categories': categories,   
        'is_subscribed': is_subscribed,
        'featured_products': featured_products,
        'trending_products': trending_products,
    })

def about(request):
    categories = Category.objects.all()[:4]
    return render(request, 'core/about.html', {'categories': categories})

def faq(request):
    return render(request, 'core/faq.html')

def privacy(request):
    return render(request, 'core/privacy.html')

@require_POST
@csrf_protect
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

        return JsonResponse({'success': True, 'message': message})
    except IntegrityError:
        return JsonResponse({'success': False, 'message': 'This email is already subscribed'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
@csrf_exempt
def newsletter_unsubscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if email:
            try:
                subscriber = NewsletterSubscription.objects.get(email=email)
                subscriber.delete()
                return JsonResponse({'success': True, 'message': 'You have been unsubscribed.'})
            except NewsletterSubscription.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Email not found in subscription list.'})
        return JsonResponse({'success': False, 'message': 'Invalid email.'})
