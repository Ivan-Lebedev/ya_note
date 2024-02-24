from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.LOGIN_URL = reverse('users:login')
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель заметки')
        # Создаём заметку:
        cls.note = Note.objects.create(
            text='Текст заметки', author=cls.author, slug='some_note'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:detail', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_from_page_with_argument_for_anonymous_client(self):
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('notes:edit', 'notes:detail', 'notes:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы
                # просмотра, редактирования или удаления заметки:
                url = reverse(name, args=(self.note.slug,))
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором
                # передаётся адрес страницы,
                # с которой пользователь был переадресован.
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)

    def test_redirect_from_page_without_argument_for_anonymous_client(self):
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                # Получаем адрес страницы добавления, просмотра списка заметок
                # и успешного выполнения операции:
                url = reverse(name)
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором
                # передаётся адрес страницы,
                # с которой пользователь был переадресован.
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
