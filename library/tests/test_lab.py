import json
import urllib
import string
from io import StringIO
from pprint import pprint


import factory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from library.models import AuthorModel, BookModel
from root.settings import REST_FRAMEWORK


class AuthorFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = AuthorModel

    name = factory.Sequence(lambda n: 'Writer-%04d' % n)


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookModel

    name = factory.Faker('text')


class LibraryTests(APITestCase):
    content_type = "application/x-www-form-urlencoded"
    initial_data_entry = 20
    author_test_name = 'Ibragim'
    book_test_name = 'A book about tasty and healthy PEOPLE'

    def setUp(self):
        for _ in range(self.initial_data_entry):
            book = BookFactory()
            book.author.add(AuthorFactory())

    def has_content(self, parm_list, obj):
        return (set(parm_list) == set(obj.keys()))

    def has_data(self, send_data, response_data):
        '''checking compliance of the sent and saved data'''
        list_data = {}
        check_list = []
        for el_set in send_data:
            key = el_set[0]
            val = response_data.get(key)
            if type(response_data[key]).__name__ == 'list':
                try:
                    response_data[key].index(el_set[1])
                    check_list.append(True)
                except Exception:
                    check_list.append(False)
            else:
                check_list.append((el_set[1] == val))

        return all(check_list)

    def create_update_record(self, send_data, url, metod='post'):
        data = urllib.parse.urlencode(send_data)
        proc = getattr(self.client, metod)
        response = proc(url, data, content_type=self.content_type)
        response_data = json.loads(response.content)
        return response_data, response.status_code

    def test_statistics_get(self):
        url = '/api-v1/statistics/'
        async_response = self.client.get(url)
        self.assertEqual(async_response.status_code, 200)

        url = url+'?sql'
        sql_response = self.client.get(url)
        self.assertEqual(sql_response.status_code, 200)
        sql_response_data = json.loads(sql_response.content)
        is_contents = self.has_content(
                                    ['results', 'timeout'], sql_response_data)
        self.assertEqual(is_contents, True)
        statistics_data = sql_response_data['results']
        self.assertEqual(statistics_data['Authors'], self.initial_data_entry)
        self.assertEqual(statistics_data['Books'], self.initial_data_entry)

    def test_root_request(self):
        url = '/api-v1/'
        response = self.client.get(url)
        exp_result = {
                    "authors": "http://testserver/api-v1/authors/",
                    "books": "http://testserver/api-v1/books/",
                    'statistics': "http://testserver/api-v1/statistics/",
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), exp_result)

    def test_authors_get(self):
        url = '/api-v1/authors/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        is_contents = self.has_content(
                                ['results', 'previous', 'next', 'count'], data)
        self.assertEqual(is_contents, True)

        self.assertEqual(len(data['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(data['next'], 'http://testserver/api-v1/authors/?page=2')
        self.assertEqual(data['count'], self.initial_data_entry)

        author = data['results'][0]
        self.assertEqual(author['url'], 'http://testserver/api-v1/authors/1/')

        response = self.client.get(data['next'])
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(data['previous'], 'http://testserver/api-v1/authors/')

    def test_search_authors(self):
        url = '/api-v1/authors/'
        search_name = self.author_test_name[0:4].lower()
        send_data = [('name', self.author_test_name)]
        cerate_response_data, status_create = self.create_update_record(
                                    send_data, url='/api-v1/authors/')
        query_list = [('name', search_name)]
        query = urllib.parse.urlencode(query_list)
        search_response = self.client.get(url + '?' + query)
        self.assertEqual(search_response.status_code, 200)
        data = json.loads(search_response.content)
        self.assertEqual(len(data['results']), 1)
        self.client.delete(data['results'][0]['url'])

    def test_search_books(self):
        url = '/api-v1/books/'
        search_name = self.book_test_name.lower()
        send_data = [('name', self.book_test_name), ('author', 1)]
        cerate_response_data, status_create = self.create_update_record(
                                    send_data, url='/api-v1/books/')

        query_list = [('name', search_name)]
        query = urllib.parse.urlencode(query_list)
        book_name_search_response = self.client.get(url + '?' + query)
        self.assertEqual(book_name_search_response.status_code, 200)
        book_name_search_data = json.loads(book_name_search_response.content)
        self.assertEqual(book_name_search_data['count'], 1)

        query_list = [('author_name', 'writer')]
        query = urllib.parse.urlencode(query_list)
        author_name_search_response = self.client.get(url + '?' + query)
        self.assertEqual(author_name_search_response.status_code, 200)
        author_name_search_data = json.loads(
                                        author_name_search_response.content)
        self.assertEqual(author_name_search_data['count'],
                                                self.initial_data_entry + 1)

        query_list = [('author_name', 'writer'), ('name', search_name)]
        query = urllib.parse.urlencode(query_list)
        search_several_parameters_response = self.client.get(url + '?' + query)
        self.assertEqual(search_several_parameters_response.status_code, 200)
        author_name_search_data = json.loads(
                                    search_several_parameters_response.content)
        self.assertEqual(author_name_search_data['count'], 1)

        query_list = [('author', 1)]
        query = urllib.parse.urlencode(query_list)
        all_books_of_author_response = self.client.get(url + '?' + query)
        self.assertEqual(all_books_of_author_response.status_code, 200)
        all_books_of_author_data = json.loads(
                                    all_books_of_author_response.content)
        self.assertEqual(all_books_of_author_data['count'], 2)

        self.client.delete(book_name_search_data['results'][0]['url'])

    def test_books_get(self):
        url = '/api-v1/books/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # pprint(data)

        is_contents = self.has_content(
                                ['results', 'previous', 'next', 'count'], data)
        self.assertEqual(is_contents, True)

        self.assertEqual(len(data['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(data['next'], 'http://testserver/api-v1/books/?page=2')
        self.assertEqual(data['count'], self.initial_data_entry)

        book = data['results'][0]
        self.assertEqual(book['url'], 'http://testserver/api-v1/books/1/')
        self.assertEqual(len(book['authors_objects']), 1)
        self.assertEqual(
                            book['authors_objects'][0]['url'],
                            'http://testserver/api-v1/authors/1/')

        response = self.client.get(data['next'])
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(data['previous'], 'http://testserver/api-v1/books/')

    def test_author_create_update_delete(self):
        send_data = [('name', self.author_test_name)]
        cerate_response_data, status_create = self.create_update_record(
                                            send_data, url='/api-v1/authors/')
        self.assertEqual(status_create, 201)

        self.assertEqual(self.has_data(send_data, cerate_response_data), True)
        send_data = [('name', 'New_name')]
        update_response_data, status_update = self.create_update_record(
                send_data, url=cerate_response_data.get('url'), metod='put')
        self.assertEqual(status_update, 200)
        self.assertEqual(self.has_data(send_data, update_response_data), True)

        delete_response = self.client.delete(update_response_data.get('url'))
        self.assertEqual(delete_response.status_code, 204)

    def test_book_create_update_delete(self):
        # For this test, there must be initial_data_entry >= 2
        send_data = [
                        ('name', self.book_test_name),
                        ('author', 1),
                        ('author', 2),
                        ('publish_bouse', 'Kharkov'),
                        ('description', 'This book is good'),
                        ('date', '2020-01-01')
                    ]
        cerate_response_data, status_create = self.create_update_record(
                                            send_data, url='/api-v1/books/')
        self.assertEqual(status_create, 201)

        self.assertEqual(self.has_data(send_data, cerate_response_data), True)
        send_data = [('name', 'New_name'), ('author', 1), ('author', 2)]
        update_response_data, status_update = self.create_update_record(
                send_data, url=cerate_response_data.get('url'), metod='put')
        self.assertEqual(status_update, 200)
        self.assertEqual(self.has_data(send_data, update_response_data), True)

        delete_response = self.client.delete(update_response_data.get('url'))
        self.assertEqual(delete_response.status_code, 204)

    def test_author_crash(self):
        url = '/api-v1/authors/'
        # add 300 characters
        oversize_name = string.printable * 3
        send_data = [('name', oversize_name)]
        _, status_oversize_name = self.create_update_record(
                                                            send_data, url=url)
        self.assertEqual(status_oversize_name, 400)

        # required parameter
        send_data = []
        _, status_required_param = self.create_update_record(
                                                            send_data, url=url)
        self.assertEqual(status_required_param, 400)

    def test_book_crash(self):
        url = '/api-v1/books/'
        # add 300 characters
        oversize_name = string.printable * 3
        send_data = [('name', oversize_name)]
        _, status_oversize_name = self.create_update_record(
                                                            send_data, url=url)
        self.assertEqual(status_oversize_name, 400)

        # required parameter
        send_data = []
        a, status_required_param = self.create_update_record(
                                                            send_data, url=url)
        self.assertEqual(status_required_param, 400)

        # object does not exist
        send_data = [('name', 'qwer'), ('author', self.initial_data_entry + 5)]
        _, status_non_existing_obj = self.create_update_record(
                                                            send_data, url=url)
        self.assertEqual(status_non_existing_obj, 400)

    def test_author_get_item(self):
        url_prefix = '/api-v1/authors/'
        existing_item = 1
        existing_item_response = self.client.get(
                                            url_prefix+str(existing_item)+'/')
        self.assertEqual(existing_item_response.status_code, 200)
        data = json.loads(existing_item_response.content)
        is_contents = self.has_content(
                                ['id', 'name', 'url'], data)
        self.assertEqual(is_contents, True)

        non_existing_item = self.initial_data_entry + 5
        non_existing_item_response = self.client.get(
                                        url_prefix+str(non_existing_item)+'/')
        self.assertEqual(non_existing_item_response.status_code, 404)

    def test_book_get_item(self):
        url_prefix = '/api-v1/books/'
        existing_item = 1
        existing_item_response = self.client.get(
                                            url_prefix+str(existing_item)+'/')
        self.assertEqual(existing_item_response.status_code, 200)
        data = json.loads(existing_item_response.content)
        is_contents = self.has_content([
                                'id', 'name', 'url',
                                'author', 'authors_objects',
                                'date', 'description', 'publish_bouse',
                                ], data)
        self.assertEqual(is_contents, True)

        non_existing_item = self.initial_data_entry + 5
        non_existing_item_response = self.client.get(
                                        url_prefix+str(non_existing_item)+'/')
        self.assertEqual(non_existing_item_response.status_code, 404)
