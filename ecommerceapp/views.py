from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Vendor, Customer, Product, Order, Cart, CartItem, Address, OrderItem
from .serializers import (VendorSerializer, CustomerSerializer, ProductSerializer, 
                         OrderSerializer, CartSerializer, CartItemSerializer, AddressSerializer)
import africastalking
from decimal import Decimal
from django.conf import settings

# Initialize Africa's Talking SMS service
africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms = africastalking.SMS

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vendor.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def register(self, request):
        if hasattr(request.user, 'vendor'):
            return Response({"error": "Already a vendor"}, status=400)
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Must be signed in to create products")
        serializer.save(vendor=self.request.user.vendor)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(customer__user=self.request.user)
        return Cart.objects.filter(session_key=self.request.session.session_key)

    def get_cart(self):
        if self.request.user.is_authenticated:
            customer, _ = Customer.objects.get_or_create(
                user=self.request.user,
                defaults={
                    'name': self.request.user.username,
                    'code': f'C{self.request.user.id}',
                    'phone': ''
                }
            )
            cart, _ = Cart.objects.get_or_create(customer=customer)
        else:
            if not self.request.session.session_key:
                self.request.session.create()
            cart, _ = Cart.objects.get_or_create(session_key=self.request.session.session_key)
        return cart

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        product = Product.objects.get(id=product_id)
        if quantity > product.stock:
            raise ValidationError(f"Only {product.stock} in stock")
        cart = self.get_cart()
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created and cart_item.quantity + quantity <= product.stock:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    def remove(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        cart_item = cart.items.get(product=product_id)
        cart_item.delete()
        return Response(CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        if not request.user.is_authenticated:
            raise PermissionDenied("Please sign in to checkout")
        cart = self.get_object()
        if not cart.items.exists():
            raise ValidationError("Cart is empty")
        address_id = request.data.get('address_id')
        address = Address.objects.get(id=address_id, customer=cart.customer)
        
        order = Order.objects.create(
            customer=cart.customer,
            address=address,
            total_amount=cart.total
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
        
        # Send SMS notification
        message = f"Your order #{order.id} is being processed."
        try:
            sms.send(message, [cart.customer.phone])
            print(f"SMS sent to {cart.customer.phone}")
        except Exception as e:
            print(f"SMS failed: {e}")
        
        cart.items.all().delete()
        return Response({
            "message": "Checkout successful! Your order is being processed.",
            "order": OrderSerializer(order).data
        })

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user.customer)
        # Send SMS notification when an order is created
        message = f"New order placed: {order.id} for {order.total_amount}"
        try:
            sms.send(message, [order.customer.phone])
            print(f"SMS sent to {order.customer.phone}")
        except Exception as e:
            print(f"SMS failed: {e}")

class GetTokenView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=401)
        try:
            token = user.social_auth.get(provider='google-oauth2').access_token
            return Response({'token': token})
        except Exception as e:
            return Response({'error': f'No token available: {str(e)}'}, status=400)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already linked to an account'}, status=400)
    user = User.objects.create_user(username=email, email=email, password=password)
    user.is_active = False
    user.save()
    send_mail(
        'Welcome to Ecommerce',
        f'Hi {email},\n\nYou’ve created an account on Ecommerce. Please confirm your email by visiting: http://127.0.0.1:8000/api/confirm/{user.id}/',
        'briancheruiyot220@gmail.com',
        [email],
        fail_silently=False,
    )
    return Response({'message': 'Account created! Check your email to confirm.'}, status=201)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def confirm_email(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return Response({'message': 'Email confirmed! You can now sign in.'})