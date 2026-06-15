"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from shop.views import (
    home,
    product_detail,
    add_to_cart,
    cart,
    remove_from_cart,
    register,
    user_login,
    user_logout,
    checkout,
    place_order,
    my_orders,
    increase_quantity,
    decrease_quantity,
    add_to_wishlist,
    my_wishlist,
    payment,
    payment_success,
    profile,
    remove_from_wishlist,
    verify_otp,
    invoice,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('remove-from-cart/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('checkout/', checkout, name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('my-orders/', my_orders, name='my_orders'),
    path('my-wishlist/', my_wishlist, name='my_wishlist'),
    path('increase-quantity/<int:cart_id>/', increase_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:cart_id>/', decrease_quantity, name='decrease_quantity'),
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('payment/', payment, name='payment'),
    path('payment-success/<str:payment_method>/', payment_success, name='payment_success'),
    path('profile/', profile, name='profile'),
    path('remove-from-wishlist/<int:wishlist_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('invoice/<int:order_id>/', invoice, name='invoice'),
    path('product/<int:product_id>/', product_detail, name='product_detail')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
