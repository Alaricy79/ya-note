from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author_1 = User.objects.create(username='Author1')
        cls.author_2 = User.objects.create(username='Author2')
        cls.note_1 = (Note.objects.create(
            title='Title1',
            text=f'Note text information from {cls.author_1.username}',
            author=cls.author_1,
            slug='note_1')
        )
        cls.note_2 = (Note.objects.create(
            title='Title2',
            text=f'Note text information from {cls.author_2.username}',
            author=cls.author_2,
            slug='note_2')
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author_1)
        cls.form_data = {'text': 'some text information',
                         'title': 'some title',
                         'slug': 'same_slug'}
        cls.form_data_same_slag = {'text': 'some text information',
                                   'title': 'next some title',
                                   'slug': 'same_slug'}
        cls.form_data_auto_slag = {'text': 'some text information',
                                   'title': 'сложные щи',
                                   }
        cls.auto_slug = slugify(cls.form_data_auto_slag['title'])
        cls.add_url = reverse('notes:add')

        cls.NEW_TEXT = 'text to check editability'

    def test_anonymous_user_cant_create_note(self):
        notes_count_prev = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_prev)

    def test_auth_user_can_create_note(self):
        notes_count_prev = Note.objects.count()
        self.auth_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_prev + 1)

    def test_can_create_two_same_slugs(self):
        notes_count_prev = Note.objects.count()
        self.auth_client.post(self.add_url, data=self.form_data)
        self.auth_client.post(self.add_url, data=self.form_data_same_slag)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_prev + 1)

    def test_auto_slug(self):
        self.auth_client.post(self.add_url, data=self.form_data_auto_slag)
        last_note = Note.objects.order_by('-id').first()
        self.assertEqual(self.auto_slug, last_note.slug)

    def test_author_can_delete(self):
        delete_url = reverse('notes:delete', args=(self.note_1.slug,))
        notes_count_prev = Note.objects.count()
        self.auth_client.delete(delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_prev - 1, notes_count)

    def test_imposter_cant_delete(self):
        delete_url = reverse('notes:delete', args=(self.note_2.slug,))
        notes_count_prev = Note.objects.count()
        self.auth_client.delete(delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_prev, notes_count)

    def test_author_can_edit(self):
        edit_url = reverse('notes:edit', args=(self.note_1.slug,))
        response = self.auth_client.post(edit_url,
                                         data={'title': 'some title',
                                               'text': self.NEW_TEXT})
        self.assertRedirects(response, reverse('notes:success'))
        self.note_1.refresh_from_db()
        self.assertEqual(self.note_1.text, self.NEW_TEXT)

    def test_imposter_cant_edit(self):
        edit_url = reverse('notes:edit', args=(self.note_2.slug,))
        response = self.auth_client.post(edit_url,
                                         data={'title': 'some title',
                                               'text': self.NEW_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

