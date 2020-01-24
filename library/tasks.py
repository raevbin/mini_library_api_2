from __future__ import absolute_import, unicode_literals
from django.apps import apps
from celery import shared_task
from library.models import AuthorModel, BookModel


@shared_task
def count_records(name_model):
    model = apps.get_model(name_model)
    name = model.__name__.replace('Model', 's')
    all_records = model.objects.count()
    return (name, all_records)
