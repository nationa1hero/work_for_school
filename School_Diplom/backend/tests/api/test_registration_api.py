from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from backend.models import ProfileData, Student


class RegistrationAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_register_success(self):
        """
        При корректных данных:
        - должно быть перенаправление на страницу логина (302),
        - пользователь и связанная модель Student должны сохраниться в БД.
        """
        data = {
            'login':   'testuser',
            'password':  'strongpassword123',
            'password2': 'strongpassword123',
            'name':    'Иван Иванов',
            'clazz':   '10A',
        }
        response = self.client.post(self.url, data)
        # ожидаем редирект на login
        self.assertEqual(response.status_code, 302)
        # проверяем, что пользователь создался
        self.assertTrue(ProfileData.objects.filter(login='testuser').exists())
        user = ProfileData.objects.get(login='testuser')
        # и что для него создался Student
        self.assertTrue(Student.objects.filter(profile_data=user).exists())

    def test_register_password_mismatch(self):
        """
        При несовпадении паролей:
        - код 200 с отрисовкой формы,
        - в ответе должно быть сообщение об ошибке "Пароли не совпадают".
        """
        data = {
            'login':   'user2',
            'password':  'abc123',
            'password2': 'def456',
            'name':    'Пётр Петров',
            'clazz':   '9Б',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пароли не совпадают')

    def test_register_duplicate_login(self):
        """
        Если логин уже существует:
        - форма должна вернуться с ошибкой уникальности,
        - новый пользователь не создаётся.
        """
        # создаём первого пользователя
        ProfileData.objects.create_user(
            login='duplicate', password='pass1', name='A', clazz='8A'
        )

        data = {
            'login':   'duplicate',
            'password':  'newpass',
            'password2': 'newpass',
            'name':    'B',
            'clazz':   '8A',
        }
        response = self.client.post(self.url, data)
        # форма рендерится заново
        self.assertEqual(response.status_code, 200)
        # дубли не должны создаваться
        self.assertEqual(ProfileData.objects.filter(login='duplicate').count(), 1)
        # в HTML должна быть подсказка про уникальность
        self.assertContains(response, 'already exists', status_code=200)
