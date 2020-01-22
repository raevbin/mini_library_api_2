from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
import re
from rest_framework.views import APIView

from celery import group
from library.tasks import count_records
from django.apps import apps
from django.db import connection
from datetime import datetime


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



class StatisticView(APIView):

    def inquiry_async(self):
        start = datetime.now()
        job_list = []
        app_conf = apps.get_app_config('library')

        for model in app_conf.get_models():
            name = 'library.'+model.__name__
            job_list.append(count_records.s(name))

        job = group(job_list)
        result = job.apply_async()
        rows = result.join()

        data = {
            'timeout': datetime.now() - start,
            'result': {}
        }
        for row in rows:
            data['result'][row[0]] = row[1]

        return data

    def inquiry_sql(self):
        start = datetime.now()
        cursor = connection.cursor()
        query = '''
            SELECT (SELECT COUNT(id) FROM library_authormodel),
                    (SELECT COUNT(id) FROM library_bookmodel)
        '''
        cursor.execute(query)
        row = cursor.fetchone()
        data = {
            'timeout': datetime.now() - start,
            'result': {
                'Authors': row[0] if len(row) else None,
                'Books': row[1] if len(row) > 1 else None
            }
        }
        return data


    def get(self, request, format=None):
        id = request.query_params.get('id')
        status = request.query_params.get('status')
        if 'sql' in request.query_params:
            return Response(self.inquiry_sql())
        return Response(self.inquiry_async())
