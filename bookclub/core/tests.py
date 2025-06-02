from django.test import TestCase
from .models import Book, Discussion, DiscussionComment, Comment, BookView
from django.contrib.auth import get_user_model
from django.urls import reverse

class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            genre='Test Genre',
            thumbnail='http://example.com/image.jpg',
            google_books_id='testid',
            preview_link='http://example.com/preview',
            published_year='2020',
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test Book')

class DiscussionModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            genre='Test Genre',
            thumbnail='http://example.com/image.jpg',
            google_books_id='testid2',
            preview_link='http://example.com/preview',
            published_year='2020',
        )
        self.discussion = Discussion.objects.create(book=self.book, user=self.user, comment='Test Comment')

    def test_discussion_str(self):
        self.assertIn('Обговорення для', str(self.discussion))

class DiscussionCommentModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser2', password='testpass')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            genre='Test Genre',
            thumbnail='http://example.com/image.jpg',
            google_books_id='testid3',
            preview_link='http://example.com/preview',
            published_year='2020',
        )
        self.discussion = Discussion.objects.create(book=self.book, user=self.user, comment='Test Comment')
        self.comment = DiscussionComment.objects.create(discussion=self.discussion, user=self.user, text='Test Text')

    def test_discussion_comment_str(self):
        self.assertIn('Коментар від', str(self.comment))

class CommentModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser3', password='testpass')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            genre='Test Genre',
            thumbnail='http://example.com/image.jpg',
            google_books_id='testid4',
            preview_link='http://example.com/preview',
            published_year='2020',
        )
        self.comment = Comment.objects.create(book=self.book, user=self.user, text='Test Comment')

    def test_comment_str(self):
        self.assertIn('Коментар від', str(self.comment))

class BookViewModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser4', password='testpass')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            genre='Test Genre',
            thumbnail='http://example.com/image.jpg',
            google_books_id='testid5',
            preview_link='http://example.com/preview',
            published_year='2020',
        )
        self.bookview = BookView.objects.create(user=self.user, book=self.book)

    def test_bookview_unique(self):
        # Проверяем, что нельзя создать второй просмотр для той же пары user-book
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            BookView.objects.create(user=self.user, book=self.book)

# Тесты для views
from django.test import Client

class IndexViewTest(TestCase):
    def test_index_status_code(self):
        client = Client()
        response = client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class BookSearchViewTest(TestCase):
    def test_book_search_status_code(self):
        client = Client()
        response = client.get(reverse('book_search'))
        self.assertEqual(response.status_code, 200)
