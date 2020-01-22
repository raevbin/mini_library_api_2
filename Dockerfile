FROM python:3
RUN mkdir /data
WORKDIR /data
ADD requirements.txt /data
RUN cd / && wget http://download.redis.io/releases/redis-5.0.7.tar.gz
RUN cd / && tar xzf redis-5.0.7.tar.gz && cd redis-5.0.7 && make
RUN pip install -r requirements.txt
RUN pip install -U celery[redis]
CMD /redis-5.0.7/src/redis-server
CMD cd /data && celery -A tasks worker --loglevel=info
