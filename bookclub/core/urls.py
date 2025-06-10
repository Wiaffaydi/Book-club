from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-book/', views.add_book, name='add_book'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.book_search, name='book_search'),
    re_path(r'^book/(?P<book_id>[^/]+)/$', views.book_detail, name='book_detail'),
    path('fetch-books/', views.fetch_and_save_books, name='fetch_books'),
    path('update-books/', views.update_books, name='update_books'),
    path('recommendations/', views.book_recommendations, name='book_recommendations'),
    path('discussions/', views.discussions_list, name='discussions_list'),
    path('discussions/<int:discussion_id>/', views.discussion_detail, name='discussion_detail'),
    path('discussions/create/', views.create_discussion, name='create_discussion'),
    path('book-search/', views.book_search, name='book_search'),
    path('book-search-api/', views.book_search_api, name='book_search_api'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
]