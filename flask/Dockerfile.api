FROM alpine:latest

RUN apt-get update \
 && apt-get install -y locales \
 && apt-get update \
 && dpkg-reconfigure -f noninteractive locales \
 && locale-gen C.UTF-8 \
 && /usr/sbin/update-locale LANG=C.UTF-8 \
 && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
 && locale-gen \
 && apt-get install -y curl unzip \
 && apt-get clean \
 && apt-get install -y gcc \
 && apt-get autoremove
 
 # Setting Home Directory for containers
WORKDIR /app

# Installing python dependencies and copying app
COPY . /app

# requirements.txt
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt  

ENV PORT 8080
EXPOSE $PORT

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 api:app

