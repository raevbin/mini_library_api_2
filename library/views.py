from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
import re


from library.serializers import AuthorSerializer, BookSerializer
from library.models import AuthorModel, BookModel
# Create your views here.


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'authors': reverse('authors-list', request=request, format=format),
        'books': reverse('books-list', request=request, format=format),
    })


class AuthorsListView(generics.ListCreateAPIView):
    serializer_class = AuthorSerializer
    # queryset = AuthorModel.objects.all()

    def get_queryset(self):
        name = self.request.query_params.get('name')

        if name:
            return AuthorModel.objects.filter(name__regex='(?i)'+name)
        else:
            return AuthorModel.objects.all()


class AuthorUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AuthorSerializer
    queryset = AuthorModel.objects.all()

    def delete(self, request, *args, **kwargs):
        books_list = BookModel.objects.filter(author=kwargs.get('pk'))
        books_list_ser = BookSerializer(books_list, many=True,
                                        context={'request': request})
        if len(books_list_ser.data):
            data = {
                "detail": "not delete. that object is associated with others",
                'result': books_list_ser.data
                }
            return Response(data, status=status.HTTP_423_LOCKED)
        return self.destroy(request, *args, **kwargs)


class BooksListView(generics.ListCreateAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        filter = {}
        pattern = {
            'name': ['name__regex', '(?i)'],
            'author_name': ['author__name__regex', '(?i)'],
            'author': ['author', '']
        }
        for el in pattern:
            el_val = self.request.query_params.get(el)
            if el_val:
                filter[pattern[el][0]] = pattern[el][1] + el_val

        if filter:
            return BookModel.objects.filter(**filter)
        else:
            return BookModel.objects.all()


class BookUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    queryset = BookModel.objects.all()
