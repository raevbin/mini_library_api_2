from rest_framework import serializers
from library.models import AuthorModel, BookModel
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorModel
        fields = [
            'url',
            'id',
            'name'
        ]


class BookSerializer(serializers.ModelSerializer):

    authors_objects = serializers.SerializerMethodField()

    class Meta:
        model = BookModel
        fields = [
            'url',
            'id', 'name',
            'author', 'publish_bouse', 'description', 'date',
            'authors_objects',
        ]

    def get_authors_objects(self, book_obj):
        authors_serial = AuthorSerializer(
                        instance=book_obj.author.all(),
                        many=True,
                        context={'request': self.context.get('request')}
                        )
        return authors_serial.data
