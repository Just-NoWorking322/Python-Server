from decimal import Decimal
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from services.models import Service, ServiceCategory
from services.signals import TOP_5_SERVICES_CACHE_KEY


class ServiceTestCase(APITestCase):
    def setUp(self):
        cache.clear()

        # Создаем пользователей
        self.master1 = User.objects.create_user(username="master1", password="password123")
        self.master2 = User.objects.create_user(username="master2", password="password123")
        self.admin = User.objects.create_superuser(username="superadmin", password="password123", email="admin@example.com")

        # Создаем начальные услуги
        self.service1 = Service.objects.create(
            title="Установка стиральной машины",
            description="Подключение к воде и канализации",
            category=ServiceCategory.REPAIR,
            price=Decimal("2000.00"),
            discount=10,
            is_active=True,
            author=self.master1
        )
        self.service2 = Service.objects.create(
            title="Генеральная уборка квартиры",
            description="Чистка всех комнат и санузла",
            category=ServiceCategory.CLEANING,
            price=Decimal("4000.00"),
            discount=20,
            is_active=True,
            author=self.master2
        )

    def test_final_price_calculation(self):
        """
        Проверка: сервер сам рассчитывает готовую итоговую цену со скидкой.
        2000 - 10% = 1800.00
        4000 - 20% = 3200.00
        """
        self.assertEqual(self.service1.final_price, Decimal("1800.00"))
        self.assertEqual(self.service2.final_price, Decimal("3200.00"))

    def test_anonymous_can_view_services_catalog(self):
        """
        Проверка: любой неавторизованный посетитель может просматривать каталог.
        """
        response = self.client.get('/api/services/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем пагинацию
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_anonymous_cannot_create_service(self):
        """
        Проверка: неавторизованный пользователь не может создать услугу (401).
        """
        data = {
            "title": "Новая услуга ремонта",
            "description": "Описание услуги",
            "category": "repair",
            "price": "1500.00",
            "discount": 0,
            "is_active": True
        }
        response = self.client.post('/api/services/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_master_can_create_service(self):
        """
        Проверка: авторизованный мастер создает услугу, автор проставляется автоматически.
        """
        self.client.force_authenticate(user=self.master1)
        data = {
            "title": "Ремонт электрики в квартире",
            "description": "Замена проводки и розеток",
            "category": "repair",
            "price": "3000.00",
            "discount": 15,
            "is_active": True
        }
        response = self.client.post('/api/services/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author_username'], "master1")
        # Проверяем расчет итоговой цены: 3000 - 15% = 2550.00
        self.assertEqual(Decimal(str(response.data['final_price'])), Decimal("2550.00"))

    def test_validation_short_title(self):
        """
        Проверка валидации: название короче 5 символов отклоняется.
        """
        self.client.force_authenticate(user=self.master1)
        data = {
            "title": "Рем",
            "description": "Короткое название",
            "category": "repair",
            "price": "1000.00",
            "discount": 0
        }
        response = self.client.post('/api/services/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_validation_discount_limit(self):
        """
        Проверка валидации: скидка более 90% отклоняется.
        """
        self.client.force_authenticate(user=self.master1)
        data = {
            "title": "Услуга с огромной скидкой",
            "description": "Описание работы",
            "category": "repair",
            "price": "1000.00",
            "discount": 95
        }
        response = self.client.post('/api/services/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('discount', response.data)

    def test_master_cannot_edit_or_delete_other_master_service(self):
        """
        Проверка безопасности: мастер 2 НЕ МОЖЕТ изменить или удалить услугу мастера 1!
        """
        self.client.force_authenticate(user=self.master2)
        # Попытка изменить чужую услугу
        update_data = {"title": "Взломанное название услуги"}
        response = self.client.patch(f'/api/services/{self.service1.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Попытка удалить чужую услугу
        delete_response = self.client.delete(f'/api/services/{self.service1.id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_edit_and_delete_own_service(self):
        """
        Проверка: автор услуги может ее редактировать и удалять.
        """
        self.client.force_authenticate(user=self.master1)
        response = self.client.patch(f'/api/services/{self.service1.id}/', {"discount": 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount'], 30)

        del_response = self.client.delete(f'/api/services/{self.service1.id}/')
        self.assertEqual(del_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_edit_and_delete_any_service(self):
        """
        Проверка: администратор может редактировать и удалять любую услугу.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/services/{self.service1.id}/', {"title": "Отредактировано админом"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        del_response = self.client.delete(f'/api/services/{self.service1.id}/')
        self.assertEqual(del_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_and_search(self):
        """
        Проверка: фильтрация по категории и поиск по названию/описанию.
        """
        # Фильтр по категории
        res_filter = self.client.get('/api/services/?category=cleaning')
        self.assertEqual(res_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_filter.data['results']), 1)
        self.assertEqual(res_filter.data['results'][0]['category'], 'cleaning')

        # Поиск
        res_search = self.client.get('/api/services/?search=стиральной')
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_search.data['results']), 1)
        self.assertIn("стиральной", res_search.data['results'][0]['title'])

    def test_top_5_services_caching_and_invalidation(self):
        """
        Проверка работы кэша «Топ-5 популярных услуг» и мгновенной инвалидации.
        """
        # Первый запрос -> MISS, данные сохраняются в кэш
        resp1 = self.client.get('/api/services/top/')
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertEqual(resp1['X-Cache'], 'MISS')

        # Второй запрос -> HIT (из быстрой памяти)
        resp2 = self.client.get('/api/services/top/')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2['X-Cache'], 'HIT')

        # Мастер добавляет новую услугу -> кэш сбрасывается
        self.client.force_authenticate(user=self.master1)
        self.client.post('/api/services/', {
            "title": "Новейшая супер услуга мастера",
            "description": "Новинка в сервисе",
            "category": "it",
            "price": "5000.00",
            "discount": 10,
            "is_active": True
        })

        # Следующий запрос к топу должен быть MISS (кэш мгновенно обновился)
        resp3 = self.client.get('/api/services/top/')
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(resp3['X-Cache'], 'MISS')
