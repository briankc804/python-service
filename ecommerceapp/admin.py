
from django.contrib import admin
from .models import Vendor, Customer, Cart, CartItem, Address, Product, ProductImage, Order, OrderItem

# Basic registration for all models
admin.site.register(Vendor)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(OrderItem)
