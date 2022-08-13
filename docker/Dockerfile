FROM python:3.7-slim

LABEL Author="Pedro Russo, Aureliano Sancho"
LABEL E-mail="pedro.russo@grupofleury.com.br, aureliano.paiva@fleury.com.br"
LABEL Version="1.0.0"

WORKDIR /app

ADD . .

RUN pip3 install pip --upgrade
RUN pip3 install -r requirements.txt
RUN cp sessionstate.py /usr/local/lib/python3.7/site-packages/hydralit
RUN ls

EXPOSE 8501

COPY . /app

ENTRYPOINT [ "streamlit", "run" ]

CMD [ "/app/streamlit/app.py" ]