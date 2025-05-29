from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('api/cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/update/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('success/<int:order_id>/', views.order_success_view, name='success'),

    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]
