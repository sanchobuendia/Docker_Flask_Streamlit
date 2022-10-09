import streamlit as st
import pandas as pd
from pandas import json_normalize
import numpy as np
import requests
import json
import datetime
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn           as sns

ip = 'http://127.0.0.1:8080/returnjson'

st.set_page_config(layout="centered")

with st.sidebar:
    option = st.selectbox(
     'Frequência do retornos',
     ['1d','5d','1wk']
     )

    option2 = st.selectbox(
     'Índice',
     ['Close', 'High', 'Open']
     )

    data_inicial = st.date_input('Data Inicial',
                                value=datetime(2020, 1, 1),
                                min_value=datetime(2020, 1, 1), 
                                max_value=datetime(2021, 7, 1)
                                )

    data_final = st.date_input('Data Final',
                                value=datetime(2021, 3, 1),
                                min_value=datetime(2020, 3, 1),
                                max_value=datetime(2021, 9, 1)
                                )

col = st.columns(1)

at_def = ['AAPL','MSFT','AMZN','TSLA','GOOGL']
ativos = ['AAPL','MSFT','AMZN','TSLA','GOOGL', 'GOOG','UNH','JNJ','XOM','JPM','NVDA','META','PG','HD','ABBV','PFE','PEP']

att = st.multiselect("Ativos", ativos, at_def)

############################## API FLASK ########################################
# http://127.0.0.1:8080/returnjson?init_date=2022-01-01&end_date=2022-01-30&freq_time=1h&index=Close&tickers=SPY&tickers=AAPL&tickers=MMM


url  = (ip + 
        '?init_date='+ str(data_inicial)+
        '&end_date=' + str(data_final) +
        '&freq_time=' + option + 
        '&index=' + option2 + 
        '&tickers='+'&tickers='.join(att)
       )

response = requests.request(
                     "GET", 
                     url)

corr = json.loads(response.text)

###################################################################################

corr = pd.DataFrame(corr)

matrix = np.triu(np.ones_like(corr, dtype=bool))

cmap = sns.diverging_palette(100, 7, s=75, l=40,
                            n=18, center="light", as_cmap=True)

sns.set(rc={"figure.figsize":(2.5, 2.5)})     
fig, ax = plt.subplots()

res = sns.heatmap(corr, vmin=-1, vmax=1, center=0,cbar_kws={'shrink': 0.7},
            cmap= cmap,
            square=True, annot=True, mask=matrix, annot_kws={'size': 4}
            )


ax.set_xticklabels(
                ax.get_xticklabels(),
                rotation=45,
                horizontalalignment='right',fontsize = 6)

ax.set_yticklabels(
                ax.get_yticklabels(),
                #rotation=45,
                horizontalalignment='right',fontsize = 6)

st.write(fig)
