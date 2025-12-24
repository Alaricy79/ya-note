from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')        
        cls.note = Note.objects.create(title='Заголовок', text='Текст', author = cls.author)   
        
        cls.add_succ_list_url = ('notes:add', 'notes:success', 'notes:list',)
        cls.edit_del_detail_url = ('notes:edit', 'notes:delete', 'notes:detail', )


    def test_pages_availability(self):
        for name in ('notes:home', 'users:login', 'users:signup'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
                            )
        
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in self.edit_del_detail_url:  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
        for name in self.add_succ_list_url:
            with self.subTest(self.reader, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)         

    # служебная функция с повторяющимсся кодом по перенаправлению на логин
    def _assert_redirect_for_anonymous(self, name, args=None):
        login_url = reverse('users:login')
        url = reverse(name, args=args)
        redirect_url = f'{login_url}?next={url}'
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client(self):
        for name in self.add_succ_list_url:
            with self.subTest(name=name):
                self._assert_redirect_for_anonymous(name)
        for name in self.edit_del_detail_url:
            with self.subTest(name=name):
                self._assert_redirect_for_anonymous(name, args=(self.note.slug,))
