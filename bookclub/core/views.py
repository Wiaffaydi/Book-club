import requests
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse

from .models import *
from .forms import *


def index(request):
    """Головна сторінка"""
    # Отримуємо популярні книги з бази даних
    popular_books = Book.objects.all().order_by('-created_at')[:10]
    
    # Якщо книг немає в базі даних, отримуємо їх з Google Books API
    if not popular_books:
        query = 'bestsellers'
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10'

        response = requests.get(url)
        data = response.json()

        if 'items' in data:
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})

                        # Створюємо нову книгу в базі даних
                book = Book.objects.create(
                            title=volume_info.get('title', 'Невідома назва'),
                            author=', '.join(volume_info.get('authors', ['Невідомий автор'])),
                            description=volume_info.get('description', 'Опис відсутній'),
                            published_year=volume_info.get('publishedDate', '')[:4],
                            genre=', '.join(volume_info.get('categories', ['Невідомий жанр'])),
                            thumbnail=image_links.get('thumbnail', 'https://via.placeholder.com/300x450?text=No+Image'),
                            preview_link=volume_info.get('previewLink', '#'),
                            google_books_id=item.get('id')
                )

                        # Отримуємо створені книги
                popular_books = Book.objects.all().order_by('-created_at')[:10]

    return render(request, 'core/index.html', {'popular_books': popular_books})


def add_book(request):
    """Сторінка додання книг"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # або інший URL
    else:
        form = BookForm()

    return render(request, 'core/add_book.html', {'form': form})


def register_view(request):
    """Регістрація"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """Логін"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Вихід з облікового запису"""
    logout(request)
    return redirect('index')


def update_existing_books():
    """Обновление существующих книг на украинском языке"""
    try:
        # Получаем все книги
        books = Book.objects.all()
        
        for book in books:
            # Формируем URL для запроса к Google Books API
            api_url = f"https://www.googleapis.com/books/v1/volumes?q={book.title}&langRestrict=uk&maxResults=1"
            
            response = requests.get(api_url)
            data = response.json()
            
            if 'items' in data:
                volume_info = data['items'][0]['volumeInfo']
                
                # Обновляем информацию о книге
                book.title = volume_info.get('title', book.title)
                book.author = ', '.join(volume_info.get('authors', [book.author]))
                book.description = volume_info.get('description', book.description)
                book.genre = volume_info.get('categories', [book.genre])[0]
                book.thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', book.thumbnail)
                book.preview_link = volume_info.get('previewLink', book.preview_link)
                book.save()
                
    except Exception as e:
        print(f"Error updating books: {e}")


def book_search(request):
    """Пошук книг"""
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    page = request.GET.get('page', 1)
    
    # Сначала ищем книги в локальной базе
    books = Book.objects.all()
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )
    
    if genre:
        books = books.filter(genre=genre)
    
    # Если локальный поиск не дал результатов, ищем через Google Books API
    if not books.exists() and query:
        try:
            # Формируем URL для запроса к Google Books API с фильтром по украинскому и английскому языкам
            api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&langRestrict=uk,en"
            if genre:
                api_url += f"&subject:{genre}"
            
            response = requests.get(api_url)
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    volume_info = item['volumeInfo']
                    
                    # Проверяем язык книги
                    language = volume_info.get('language', '')
                    if language not in ['uk', 'en']:
                        continue
                    
                    # Проверяем наличие русских букв в названии и авторе
                    title = volume_info.get('title', '').lower()
                    author = ', '.join(volume_info.get('authors', ['Невідомий автор'])).lower()
                    
                    # Список русских букв для проверки
                    russian_chars = 'ёъыэ'
                    russian_words = ['россия', 'российский', 'русский', 'русь', 'москва', 'петербург']
                    
                    # Проверяем наличие русских букв и слов
                    if (any(char in title for char in russian_chars) or
                        any(char in author for char in russian_chars) or
                        any(word in title for word in russian_words) or
                        any(word in author for word in russian_words)):
                        continue
                    
                    # Проверяем, есть ли уже такая книга в базе
                    if not Book.objects.filter(google_books_id=item['id']).exists():
                        # Создаем новую книгу
                        book = Book(
                            title=volume_info.get('title', ''),
                            author=', '.join(volume_info.get('authors', ['Невідомий автор'])),
                            description=volume_info.get('description', ''),
                            genre=genre if genre else volume_info.get('categories', ['Невідомий жанр'])[0],
                            thumbnail=volume_info.get('imageLinks', {}).get('thumbnail', ''),
                            google_books_id=item['id'],
                            preview_link=volume_info.get('previewLink', '')
                        )
                        book.save()
                
                # После добавления книг, делаем новый запрос к локальной базе
                books = Book.objects.all()
                if query:
                    books = books.filter(
                        Q(title__icontains=query) |
                        Q(author__icontains=query) |
                        Q(description__icontains=query)
                    )
                if genre:
                    books = books.filter(genre=genre)
        except Exception as e:
            print(f"Error fetching from Google Books API: {e}")
    
    # Пагинация
    paginator = Paginator(books, 12)
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    
    # Получаем список всех жанров для фильтра
    genres = Book.objects.values_list('genre', flat=True).distinct()
    
    context = {
        'books': books,
        'query': query,
        'genre': genre,
        'genres': genres,
    }
    
    return render(request, 'core/book_search.html', context)


def delete_russian_books():
    """Видалення російськомовних книг"""
    try:
        # Отримуємо всі книги
        books = Book.objects.all()
        deleted_count = 0
        
        for book in books:
            # Перевіряємо, чи книга російськомовна
            if any(char in book.title for char in 'ёъыэ') or any(char in book.author for char in 'ёъыэ'):
                book.delete()
                deleted_count += 1
        
        return deleted_count
    except Exception as e:
        print(f"Помилка при видаленні російськомовних книг: {e}")
        return 0


def update_books(request):
    """Оновлення всіх книг"""
    if not request.user.is_staff:
        return redirect('book_search')
    
    # Видаляємо російськомовні книги
    deleted_count = delete_russian_books()
    
    # Оновлюємо існуючі книги
    update_existing_books()
    
    # Додаємо повідомлення про успішне оновлення
    messages.success(request, f'Оновлено книги. Видалено {deleted_count} російськомовних книг.')
    
    return redirect('book_search')


def book_detail(request, book_id):
    """Сторінка деталей книги"""
    try:
        # Сначала пробуем найти книгу по ID из Google Books API
        book = Book.objects.get(google_books_id=book_id)
    except Book.DoesNotExist:
        try:
            # Если не нашли, пробуем найти по числовому ID
            book = Book.objects.get(id=book_id)
        except (Book.DoesNotExist, ValueError):
            # Если книга не найдена, пробуем получить её из Google Books API
            try:
                url = f'https://www.googleapis.com/books/v1/volumes/{book_id}'
                response = requests.get(url)
                data = response.json()
                
                if 'error' in data:
                    return render(request, 'core/404.html', {'message': 'Книгу не знайдено'})
                
                volume_info = data.get('volumeInfo', {})
                book = Book.objects.create(
                    title=volume_info.get('title', 'Невідома назва'),
                    author=', '.join(volume_info.get('authors', ['Невідомий автор'])),
                    description=volume_info.get('description', 'Опис відсутній'),
                    published_year=volume_info.get('publishedDate', 'Невідомий рік')[:4],
                    genre=', '.join(volume_info.get('categories', ['Невідомий жанр'])),
                    thumbnail=volume_info.get('imageLinks', {}).get('thumbnail', ''),
                    preview_link=volume_info.get('previewLink', ''),
                    google_books_id=book_id
                )
            except Exception as e:
                print(f"Помилка при отриманні книги з API: {e}")
                return render(request, 'core/404.html', {'message': 'Книгу не знайдено'})
    
    # Записываем просмотр книги для авторизованного пользователя
    if request.user.is_authenticated:
        BookView.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={'viewed_at': timezone.now()}
        )
    
    # Обработка комментариев
    comments = book.comments.all()
    comment_form = CommentForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.book = book
            comment.user = request.user
            comment.save()
            return redirect('book_detail', book_id=book_id)
    
    context = {
        'book': book,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'core/book_detail.html', context)


def fetch_and_save_books(request):
    """Функція для автоматичного отримання та збереження книг"""
    # Отримуємо популярні книги з Google Books API
    query = 'bestsellers'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40'
    
    response = requests.get(url)
    data = response.json()

    saved_books = 0
    if 'items' in data:
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            google_books_id = item.get('id')
            
            # Перевіряємо, чи книга вже існує в базі
            if not Book.objects.filter(google_books_id=google_books_id).exists():
                try:
                    # Створюємо нову книгу
                    Book.objects.create(
                        title=volume_info.get('title', 'Невідома назва'),
                        author=', '.join(volume_info.get('authors', ['Невідомий автор'])),
                        description=volume_info.get('description', 'Опис відсутній'),
                        published_year=volume_info.get('publishedDate', 'Невідомий рік')[:4],  # Беремо тільки рік
                        genre=', '.join(volume_info.get('categories', ['Невідомий жанр'])),
                        thumbnail=volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        preview_link=volume_info.get('previewLink', ''),
                        google_books_id=google_books_id
                    )
                    saved_books += 1
                except Exception as e:
                    print(f"Помилка при збереженні книги: {e}")
    
    return render(request, 'core/fetch_books.html', {
        'total_books': len(data.get('items', [])),
        'saved_books': saved_books
    })


def discussions_list(request):
    """Список всіх обговорень"""
    discussions = Discussion.objects.all().order_by('-posted_at')
    return render(request, 'core/discussions_list.html', {'discussions': discussions})

def discussion_detail(request, discussion_id):
    """Детальна сторінка обговорення"""
    discussion = get_object_or_404(Discussion, id=discussion_id)
    comments = discussion.comments.all().order_by('created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = DiscussionCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.user = request.user
            comment.save()
            return redirect('discussion_detail', discussion_id=discussion.id)
    else:
        form = DiscussionCommentForm()
    
    return render(request, 'core/discussion_detail.html', {
        'discussion': discussion,
        'comments': comments,
        'form': form
    })

def create_discussion(request):
    """Створення нового обговорення"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.user = request.user
            discussion.save()
            return redirect('discussion_detail', discussion_id=discussion.id)
    else:
        form = DiscussionForm()
    
    return render(request, 'core/create_discussion.html', {'form': form})

def book_recommendations(request):
    """Сторінка рекомендацій книг"""
    # Отримуємо книги з бази даних
    books = Book.objects.all()
    
    # Якщо користувач авторизований, показуємо персоналізовані рекомендації
    if request.user.is_authenticated:
        # Отримуємо переглянуті книги користувача
        viewed_books = BookView.objects.filter(user=request.user).order_by('-viewed_at')
        if viewed_books.exists():
            # Отримуємо жанри переглянутих книг
            viewed_genres = set(book.book.genre for book in viewed_books)
            
            # Фільтруємо книги за жанрами
            recommended_books = Book.objects.filter(genre__in=viewed_genres).exclude(
                id__in=[book.book.id for book in viewed_books]
            ).order_by('?')[:12]  # Випадковий вибір 12 книг
            
            return render(request, 'core/book_recommendations.html', {
                'books': recommended_books,
                'is_personalized': True
            })
    
    # Якщо немає персоналізованих рекомендацій, показуємо загальні
    books = Book.objects.order_by('?')[:12]  # Випадковий вибір 12 книг
    return render(request, 'core/book_recommendations.html', {
        'books': books,
        'is_personalized': False
    })

def book_search_api(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'books': []})
    
    # Search only in local database
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    )[:5]
    
    books_data = []
    for book in books:
        # Проверяем, является ли thumbnail URL-ом или путем к файлу
        thumbnail_url = book.thumbnail
        if not thumbnail_url:
            thumbnail_url = '/static/core/images/no-cover.png'
        elif not thumbnail_url.startswith(('http://', 'https://')):
            # Если это путь к файлу, добавляем префикс для статических файлов
            thumbnail_url = f'/media/{thumbnail_url}'
        
        books_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'thumbnail': thumbnail_url
        })
    
    return JsonResponse({'books': books_data})


