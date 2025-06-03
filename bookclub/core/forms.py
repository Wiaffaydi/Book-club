from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Book, Comment, Discussion, DiscussionComment


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'genre', 'thumbnail', 'preview_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.URLInput(attrs={'class': 'form-control'}),
            'preview_link': forms.URLInput(attrs={'class': 'form-control'}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Електронна пошта')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишіть ваш коментар...'
            })
        }


class DiscussionCommentForm(forms.ModelForm):
    class Meta:
        model = DiscussionComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишіть ваш коментар...'
            })
        }


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['book', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишіть ваше обговорення...'
            })
        }