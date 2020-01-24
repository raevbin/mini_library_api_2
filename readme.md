
# Мини библиотека.


## Порядок запуска:
  перейти в папку с проектом
  создать контейнер (эта операция займет от 5 до 10 мин)
> docker build -t library .

  первый запуск системы
> docker container run --name webserver -it -p 8000:8000 library

  последующие запуски
> docker container start  webserver -i

  после удачного старта можно открыть в браузере
  http://127.0.0.1:8000/api-v1/

  по умолчанию включен режим отладки и инструмент BrowsableAPIRenderer для удобства тестирования

  запуск unittest (в новом терминале!)
> docker exec -it webserver sh -c "python manage.py test"


=======================================================
Документация по REST API

#--------------------------------------------------------------
**GET /api-v1/**

*Корневая директория API*

 - responses:

		200: OK
		"application/json"

		    {
		      "authors": "http://127.0.0.1:8000/api-v1/authors/",
		      "books": "http://127.0.0.1:8000/api-v1/books/",
		      "statistics": "http://127.0.0.1:8000/api-v1/statistics/"
		    }

#--------------------------------------------------------------
**GET /api-v1/authors/**  [?page={str}&name={str}]

*Список авторов. Есть поиск по имени и пагинация страниц*

 - parameters:

	    query:
		    page = <int: номер страницы. опционально >
		    name = <str: ноисковое слово. опционально>

 - responses:

		200: OK
		"application/json"

		    {
		      "count": <int: количество найденных записей>,
		      "next": <str: url следующей страницы>,
		      "previous": <str: url предыдущей страницы>,
		      "results": [
		          {
		              "url": <str: url экземпляра записи автора>,
		              "id": <int: id,
		              "name": <str>
		          },
		          ...
		          ...
		      ]
		    }
#--------------------------------------------------------------
**POST /api-v1/authors/**

*Добавление записи*

 - parameters:

		body:  ("application/x-www-form-urlencoded")
			name = <str: имя автора. обязательное поле>

 - responses:

		200: OK
		"application/json"

			{
			  "url":<str>,
			  "id": <int>,
			  "name": <str>,
			}

		400: Bad Request
		"application/json"

			{
				<nameField>: [
					"This field may not be blank."
				],
				.....
			}

#--------------------------------------------------------------
**GET /api-v1/authors/{authorID}/**

 *Запись об авторе*

 - parameters:

		path:
			authorID: <int: обязательный параметр>

 - responses:

		200: Ответ такой же как POST /api-v1/authors/

		404: Not found
			"application/json"

			{
				"detail": "Not found."
			}

#--------------------------------------------------------------
**PUT /api-v1/authors/{authorID}/**

*Обновления записи*

 - parameters:

		path: по аналогии с GET /api-v1/authors/{authorID}/
		body: по аналогии с POST /api-v1/authors/

 - responses:

		200: по аналогии с POST /api-v1/authors/
		404: по аналогии с GET /api-v1/authors/{authorID}/
		400: по аналогии с POST /api-v1/authors/

#--------------------------------------------------------------
**GET /api-v1/books/**  [?page={str}&name={str}&author_name={str}&author={int}]

*Список книг. Есть пагинация страниц,  поиск по названию книги и по имени автора*

 - parameters:

		query:
			page = <int: номер страницы. опционально >
			name = <str: поиск по названию книги. опционально>
			author_name = <str: поиск по имени автора. опционально>
			author = <int: поиск по ID автора. опционально>

 - responses:

		200: OK
		"application/json"

	    {
	      "count": <int: количество найденных записей>,
	      "next": <str: url следующей страницы>,
	      "previous": <str: url предыдущей страницы>,
	      "results": [
		          {
		              "url": <str>,
		              "id": <int>,
		              "name": <str: название книги>,
		              "author": <list: список ID авторов>,
		              "publish_bouse": <str>,
		              "description": <str>,
		              "date": <str>,
		              "authors_objects": <list: список авторов. поля такие же как в GET /api-v1/authors/{authorID}/>
		          },
	          ...
	          ...
		      ]
	      }
#--------------------------------------------------------------
**POST /api-v1/books/**

*Добавление записи*

 - parameters:

		body:  ("application/x-www-form-urlencoded")
			name = <str: название книги. обязательное поле>
			author = <int: ID существующего автора. обязательное поле>
			(полей author может быть несколько, с разными ID)
			publish_bouse = <str>
			description = <str>
			date = <date: год публикации>

 - responses:

		200: OK
		"application/json"

			{
			  "url":<str>,
			  "id": <int>,
		      "name": <str: название книги>,
		      "author": <list: список ID авторов>,
		      "publish_bouse": <str>,
		      "description": <str>,
		      "date": <str>,
		      "authors_objects": <list: список авторов. поля такие же как в GET /api-v1/authors/{authorID}/>
			}

		400: Bad Request
		"application/json"

			{
				<nameField>: [
					"This field may not be blank."
				],
				.....
			}

#--------------------------------------------------------------
**GET /api-v1/books/{bookID}/**

*Отдельная книга*

 - parameters:

		path:
			bookID: <int: обязательный параметр>

 - responses:

		200: Ответ такой же как POST /api-v1/books/

		404: Not found
		"application/json"

			{
				"detail": "Not found."
			}

#--------------------------------------------------------------
**PUT /api-v1/books/{bookID}/**

*Обновления записи*

 - parameters:

		path: по аналогии с GET /api-v1/books/{bookID}/
		body: по аналогии с POST /api-v1/books/

 - responses:

		200: по аналогии с POST /api-v1/books/
		404: по аналогии с GET /api-v1/books/{bookID}/
		400: по аналогии с POST /api-v1/books/

#--------------------------------------------------------------
**GET /api-v1/statistics/**  [?sql]

*Статистика по количеству записей в базе*

 - parameters:

		query:
			sql: флаг, переключающий режим сбора статистики. Без этого флага статистика собирается асинхронным методом используя ORM. С включенным флагом - делается прямой запрос к базе с помощью sql

 - responses

		200: OK
		"application/json"

		    {
		      "timeout": <float: время выполнения задачи>,
		      "results": {
		          "Authors": <int>,
		          "Books": <int>,
		      }
		    }
