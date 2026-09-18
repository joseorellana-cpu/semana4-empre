from django.db import IntegrityError, models
from django.test import TestCase
from django.urls import reverse

from .models import (
    Author,
    AuthorProfile,
    Book,
    Category,
    Publication,
    Publisher,
)


class ModelRelationshipTests(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name='Robert',
            last_name='Martin',
            email='robert.martin@example.com',
        )
        self.profile = AuthorProfile.objects.create(
            author=self.author,
            biography='Clean Code author.',
            website='https://cleancoder.com',
        )
        self.category = Category.objects.create(
            name='Software Engineering',
            description='Quality software practices.',
        )
        self.publisher = Publisher.objects.create(
            name='Prentice Hall',
            address='New Jersey, USA',
            website='https://www.pearson.com',
        )
        self.book = Book.objects.create(
            title='Clean Architecture',
            isbn='9780134494166',
            summary='Software structure principles.',
            author=self.author,
        )
        self.book.categories.add(self.category)
        Publication.objects.create(
            book=self.book,
            publisher=self.publisher,
            publication_date='2017-09-25',
            edition=1,
        )

    def test_forward_and_reverse_accessors(self):
        self.assertEqual(
            self.book.author.profile.website,
            'https://cleancoder.com',
        )
        self.assertIn('Clean Architecture',
                      [item.title for item in self.author.books.all()])

    def test_cascade_deletes_book_and_profile(self):
        self.author.delete()
        self.assertFalse(Book.objects.filter(isbn='9780134494166').exists())
        self.assertFalse(AuthorProfile.objects.filter(
            author__email='robert.martin@example.com').exists())

    def test_publication_unique_together(self):
        with self.assertRaises(IntegrityError):
            Publication.objects.create(
                book=self.book,
                publisher=self.publisher,
                publication_date='2018-01-01',
                edition=1,
            )


class OnDeleteConfigurationTests(TestCase):

    def test_all_relationships_use_cascade(self):
        self.assertEqual(
            Book._meta.get_field('author').remote_field.on_delete,
            models.CASCADE,
        )
        self.assertEqual(
            AuthorProfile._meta.get_field('author').remote_field.on_delete,
            models.CASCADE,
        )
        self.assertEqual(
            Publication._meta.get_field('book').remote_field.on_delete,
            models.CASCADE,
        )
        self.assertEqual(
            Publication._meta.get_field('publisher').remote_field.on_delete,
            models.CASCADE,
        )

    def test_book_publishers_uses_through_model(self):
        through_model = Book._meta.get_field('publishers').remote_field.through
        self.assertIs(through_model, Publication)


class BookDetailViewTests(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name='Robert',
            last_name='Martin',
            email='robert.martin@example.com',
        )
        AuthorProfile.objects.create(
            author=self.author,
            biography='Clean Code author.',
            website='https://cleancoder.com',
        )
        self.book = Book.objects.create(
            title='Clean Code',
            isbn='9780132350884',
            summary='How to write readable code.',
            author=self.author,
        )

    def test_book_detail_renders_full_info(self):
        url = reverse('library:book_detail', kwargs={'pk': self.book.pk})
        response = self.client.get(url, HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clean Code')
        self.assertContains(response, 'robert.martin@example.com')
        self.assertContains(response, 'cleancoder.com')

    def test_book_detail_returns_404_for_missing_book(self):
        url = reverse('library:book_detail', kwargs={'pk': 9999})
        response = self.client.get(url, HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 404)
