from django.urls import path
from library.views import AuthorsListView, AuthorUpdateView, BooksListView, BookUpdateView
from library.views import api_root

urlpatterns = [
    path('', api_root),
    path('authors/', AuthorsListView.as_view(), name='authors-list'),
    path('authors/<int:pk>/', AuthorUpdateView.as_view(), name='authormodel-detail'),
    path('books/', BooksListView.as_view(), name='books-list'),
    path('books/<int:pk>/', BookUpdateView.as_view(), name='bookmodel-detail'),
]
