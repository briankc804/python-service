
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name

class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.postal_code}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    @property
    def tax(self):
        return self.subtotal * Decimal('0.10')

    @property
    def shipping(self):
        return Decimal('5.00')

    @property
    def total(self):
        return self.subtotal + self.tax + self.shipping

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.quantity > self.product.stock:
            raise ValueError(f"Quantity {self.quantity} exceeds stock {self.product.stock}")
        super().save(*args, **kwargs)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Processing')

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"