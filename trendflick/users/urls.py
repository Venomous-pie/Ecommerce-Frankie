from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('manage-account/', views.manage_account, name='manage_account'),
    path('orders/', views.orders, name='orders'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('change-password/', views.change_password, name='change_password'),
    path('toggle-wishlist/<str:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('clear-wishlist/', views.clear_wishlist, name='clear_wishlist'),

    # Address management URLs
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),

    path('password-reset-request/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),

] 