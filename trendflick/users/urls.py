from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('view-profile/', views.view_profile, name='view_profile'),
    path('manage-account/', views.manage_account, name='manage_account'),
    path('orders/', views.orders, name='orders'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('wishlist/add/<str:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<str:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
] 