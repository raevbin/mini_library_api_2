FROM python:3
RUN mkdir /data
WORKDIR /data
ADD requirements.txt /data
RUN cd / && wget http://download.redis.io/releases/redis-5.0.7.tar.gz
RUN cd / && tar xzf redis-5.0.7.tar.gz && cd redis-5.0.7 && make
RUN pip install -r requirements.txt
RUN pip install -U celery[redis]
ADD install/default/celeryd /etc/default/
ADD install/init.d/celeryd  /etc/init.d/
RUN chmod +x /etc/init.d/celeryd
RUN mkdir /var/log/celery/ && mkdir /var/run/celery/
RUN chmod 777 /var/log/celery/ && chmod 777 /var/run/celery/
RUN groupadd celery  && useradd -g celery -m celery
