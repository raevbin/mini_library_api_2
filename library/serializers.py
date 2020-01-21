from rest_framework import serializers
from library.models import AuthorModel, BookModel


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorModel
        fields = ['url', 'id', 'name']
        # fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BookModel
        fields = [
        'url', 'id', 'name', 'author', 'publish_bouse', 'description', 'date', 'author_name']

    def get_author_name(self, book_obj):
        return book_obj.author.name if book_obj.author else None
