from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('category/<str:category>/', views.category, name='category'),
    path('detail/<int:product_id>/', views.detail, name='detail'),
    path('search/', views.search, name='search'),
    path('api/trending/', views.trending_products, name='trending_products'),
    path('api/related/<int:product_id>/', views.related_products, name='related_products'),
] 