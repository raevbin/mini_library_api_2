from django.contrib import admin
from library.models import AuthorModel, BookModel
# Register your models here.
admin.site.register(AuthorModel)
admin.site.register(BookModel)
