from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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
        cls.notes_list_url = reverse('notes:list',)

    def test_note_in_notes_list(self):
        self.client.force_login(self.author_1)
        response = self.client.get(self.notes_list_url)
        self.assertIn(self.note_1, response.context['object_list'])

    def test_note_not_in_notes_list(self):
        self.client.force_login(self.author_1)
        response = self.client.get(self.notes_list_url)
        self.assertNotIn(self.note_2, response.context['object_list'])

    def test_is_form_come_to_edit(self):
        self.client.force_login(self.author_1)
        edit_url = reverse('notes:edit', args=(self.note_1.slug,))
        response = self.client.get(edit_url)
        self.assertIn('form', response.context)

    def test_is_form_come_to_add(self):
        self.client.force_login(self.author_1)
        edit_url = reverse('notes:add',)
        response = self.client.get(edit_url)
        self.assertIn('form', response.context)
