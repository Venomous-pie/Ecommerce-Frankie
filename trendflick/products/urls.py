from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('category/<str:category>/', views.all_product, name='all_product'),
    path('detail/<int:product_id>/', views.detail, name='detail'),
    path('api/trending/', views.trending_products, name='trending_products'),
    path('api/related/<int:product_id>/', views.related_products, name='related_products'),
    path('add-to-cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('search/', views.search_products, name='search'),
] 