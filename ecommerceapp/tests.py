from django.test import TestCase
from rest_framework.test import APIClient
from .models import Customer, Order

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(name="Test User", code="C001", phone="+254123456789")

    def test_create_order(self):
        self.client.force_authenticate(user=self.customer.user)
        response = self.client.post('/api/orders/', {'customer': self.customer.id, 'total_amount': 100.0})
        self.assertEqual(response.status_code, 201)



        