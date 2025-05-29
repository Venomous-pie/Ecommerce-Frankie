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
from products.models import Category


def home(request):
    categories = Category.objects.all()[:6]
    return render(request, 'home.html', {'categories': categories})

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