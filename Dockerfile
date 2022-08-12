#FROM python:3.6.8
FROM python:3.7

LABEL Author="Pedro Russo"
LABEL E-mail="pedro.russo@grupofleury.com.br"
LABEL Version="1.0.0"

WORKDIR /opt/streamlit_diabetes

ADD . .

#ENV http_proxy http://10.206.255.37
#ENV https_proxy http://10.206.255.37

RUN pip3 install pip --upgrade
RUN pip3 install -r requirements.txt
RUN cp sessionstate.py /usr/local/lib/python3.7/site-packages/hydralit
RUN ls

#EXPOSE 8501
EXPOSE 8080

#ENTRYPOINT [ "streamlit", "run"] 
#CMD ["src/host_app.py"]

#ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
CMD streamlit run --server.port 8080 --server.enableCORS false app.py