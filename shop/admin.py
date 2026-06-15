from django.contrib import admin
from .models import Product, Cart, Order,Wishlist, Review, Profile

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(Profile)