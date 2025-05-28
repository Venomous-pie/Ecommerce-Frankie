from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    # path('checkout/', views.checkout, name='checkout'),
    path('api/cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/update/', views.update_cart, name='update_cart'),
]
