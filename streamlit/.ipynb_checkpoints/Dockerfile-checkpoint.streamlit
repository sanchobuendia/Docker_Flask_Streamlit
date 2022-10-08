FROM alpine:latest

RUN apt-get update \
 && apt-get install -y locales \
 && apt-get update \
 && dpkg-reconfigure -f noninteractive locales \
 && locale-gen C.UTF-8 \
 && /usr/sbin/update-locale LANG=C.UTF-8 \
 && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
 && locale-gen \
 && apt-get install -y curl unzip telnet \
 && apt-get clean \
 && apt-get install -y gcc \
 && apt-get autoremove
 
WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt  
 
EXPOSE 8080

ENTRYPOINT [ "streamlit", "run", "app.py","--server.port", "8080", "--server.address", "0.0.0.0"]

