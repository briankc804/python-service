from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vendors', views.VendorViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('get-token/', views.GetTokenView.as_view(), name='get_token'),
    path('signup/', views.signup_view, name='api_signup'),
    path('confirm/<int:user_id>/', views.confirm_email, name='confirm_email'),
]