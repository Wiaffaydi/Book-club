from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=100)
    thumbnail = models.URLField()
    google_books_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    preview_link = models.URLField(null=True, blank=True)
    published_year = models.CharField(max_length=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        return round(self.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0, 2)


class Discussion(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Обговорення для {self.book.title}'


class DiscussionComment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Коментар від {self.user.username} до обговорення {self.discussion.book.title}'


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Коментар від {self.user.username} до {self.book.title}'


class BookView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_views')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-viewed_at']
        # Добавляем уникальное ограничение, чтобы у пользователя была только одна запись для каждой книги
        unique_together = ['user', 'book']

    def save(self, *args, **kwargs):
        # Обновляем время просмотра при повторном просмотре
        self.viewed_at = timezone.now()
        super().save(*args, **kwargs)


class BookRating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 звёзд
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f"{self.user.username} — {self.book.title}: {self.rating}★"
