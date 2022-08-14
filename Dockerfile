FROM python:3.7

LABEL Author="Pedro Russo, Aureliano Sancho"
LABEL E-mail="pedro.russo@grupofleury.com.br, aureliano.paiva@fleury.com.br"
LABEL Version="1.0.0"

WORKDIR /opt/app

ADD . .

RUN pip3 install pip --upgrade
RUN pip3 install -r requirements.txt
RUN cp sessionstate.py /usr/local/lib/python3.7/site-packages/hydralit
RUN ls


# If you want run on docker locally you cause the default 8501 port
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port= 8501", "--server.address=0.0.0.0"]


# But if you want run on GCP it is necessary to use the 8080 port
#EXPOSE 8080
#CMD streamlit run --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false app.py