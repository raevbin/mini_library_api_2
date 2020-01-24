FROM python:3
RUN mkdir /data
WORKDIR /data
ADD requirements.txt /data
RUN cd / && wget http://download.redis.io/releases/redis-5.0.7.tar.gz
RUN cd / && tar xzf redis-5.0.7.tar.gz && cd redis-5.0.7 && make
RUN pip install -r requirements.txt
RUN pip install -U celery[redis]
COPY . /data
RUN chmod +x /data/start.sh
CMD /data/start.sh
