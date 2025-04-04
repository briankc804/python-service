"""
URL configuration for coreproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.conf.urls.static import static

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Welcome to the E-commerce API',
        'endpoints': {
            'products': '/api/products/',
            'vendors': '/api/vendors/',
            'customers': '/api/customers/',
            'orders': '/api/orders/',
            'cart': '/api/cart/',
            'signup': '/api/signup/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ecommerceapp.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', api_root, name='api_root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)