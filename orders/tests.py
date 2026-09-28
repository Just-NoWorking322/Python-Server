from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from services.models import Service, ServiceCategory
from orders.models import Order


class OrderTestCase(APITestCase):
    def setUp(self):
        self.master1 = User.objects.create_user(username="master1", password="password123")
        self.master2 = User.objects.create_user(username="master2", password="password123")
        self.admin = User.objects.create_superuser(username="admin_user", password="password123")

        self.service1 = Service.objects.create(
            title="Услуга сантехника",
            description="Качественный ремонт",
            category=ServiceCategory.REPAIR,
            price=Decimal("1000.00"),
            discount=0,
            is_active=True,
            author=self.master1
        )
        self.service2 = Service.objects.create(
            title="Услуга уборки",
            description="Чистота в доме",
            category=ServiceCategory.CLEANING,
            price=Decimal("2000.00"),
            discount=0,
            is_active=True,
            author=self.master2
        )

        # Заявка на услугу мастера 1
        self.order1 = Order.objects.create(
            service=self.service1,
            client_name="Иван",
            client_phone="+996555111222",
            comment="Ул. Токтогула 10"
        )
        # Заявка на услугу мастера 2
        self.order2 = Order.objects.create(
            service=self.service2,
            client_name="Мария",
            client_phone="+996777333444",
            comment="Ул. Чуй 45"
        )

    def test_anonymous_client_can_create_order(self):
        """
        Проверка: любой клиент (даже гость) может оставить заявку («Заказать»).
        """
        data = {
            "service_id": self.service1.id,
            "client_name": "Алексей",
            "client_phone": "+996555998877",
            "comment": "Позвоните за час до приезда"
        }
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['client_name'], "Алексей")
        self.assertEqual(response.data['service_title'], self.service1.title)

    def test_master_only_sees_orders_for_own_services(self):
        """
        Проверка конфиденциальности: мастер 1 видит ТОЛЬКО заявки на свои услуги.
        Чужие заявки (мастера 2) ему видеть нельзя!
        """
        self.client.force_authenticate(user=self.master1)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В результатах пагинации только order1
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.order1.id)

    def test_admin_sees_all_orders(self):
        """
        Проверка: администратор видит все поступившие заявки сервиса.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_master_cannot_delete_order(self):
        """
        Проверка: мастер НЕ МОЖЕТ удалить заявку (403 Forbidden).
        Удалять заявки разрешено только администратору!
        """
        self.client.force_authenticate(user=self.master1)
        response = self.client.delete(f'/api/orders/{self.order1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Убеждаемся, что заявка осталась в базе
        self.assertTrue(Order.objects.filter(id=self.order1.id).exists())

    def test_admin_can_delete_order(self):
        """
        Проверка: администратор сервиса может удалить заявку (204 No Content).
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/orders/{self.order1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order1.id).exists())
