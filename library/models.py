from django.db import models


class AuthorModel(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class BookModel(models.Model):
    author = models.ManyToManyField(AuthorModel)
    name = models.CharField(max_length=250)
    publish_bouse = models.CharField(max_length=250, blank=True, default='')
    description = models.TextField(blank=True, default='')
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
