from django.urls import path
from library.views import AuthorsListView, AuthorUpdateView, BooksListView
from library.views import api_root, BookUpdateView, StatisticView

urlpatterns = [
    path('', api_root),
    path('authors/', AuthorsListView.as_view(), name='authors-list'),
    path('authors/<int:pk>/',
         AuthorUpdateView.as_view(),
         name='authormodel-detail'),
    path('books/', BooksListView.as_view(), name='books-list'),
    path('books/<int:pk>/', BookUpdateView.as_view(), name='bookmodel-detail'),
    path('statistics/', StatisticView.as_view(), name='stat-list'),
]
