from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTestCase(APITestCase):
    def test_user_registration_success(self):
        """
        Проверка регистрации нового специалиста.
        """
        data = {
            "username": "new_master",
            "email": "master@test.com",
            "first_name": "Эркин",
            "last_name": "Уста",
            "password": "strongpassword123",
            "password_confirm": "strongpassword123"
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="new_master").exists())

    def test_password_mismatch(self):
        """
        Проверка валидации: несовпадение паролей при регистрации.
        """
        data = {
            "username": "bad_user",
            "password": "password123",
            "password_confirm": "different123"
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_token_obtain_and_profile_access(self):
        """
        Проверка получения JWT-токена и доступа к эндпоинту профиля /api/auth/me/.
        """
        User.objects.create_user(username="testuser", password="mypassword123")
        
        # Получаем JWT токен
        token_resp = self.client.post('/api/auth/token/', {
            "username": "testuser",
            "password": "mypassword123"
        })
        self.assertEqual(token_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_resp.data)
        self.assertIn('refresh', token_resp.data)

        access_token = token_resp.data['access']

        # Запрашиваем профиль с Bearer токеном
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_resp = self.client.get('/api/auth/me/')
        self.assertEqual(profile_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_resp.data['username'], "testuser")
