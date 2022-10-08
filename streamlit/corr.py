import streamlit as st
import pandas as pd
from pandas import json_normalize
import numpy as np
import requests
import json
import datetime
from datetime import datetime

from google.cloud import bigquery
from google.oauth2 import service_account

import matplotlib.pyplot as plt
import seaborn           as sns

ip = 'http://172.18.0.2:5001/returnjson'

st.set_page_config(layout="centered")

with st.sidebar:
    option = st.selectbox(
     'Frequência do retornos',
     ['1h','1d', '1w', '30d']
     )

    option2 = st.selectbox(
     'Índice',
     ['Low', 'High', 'Open', 'Close']
     )

    data_inicial = st.date_input('Data Inicial',
                                value=datetime(2020, 1, 1),
                                min_value=datetime(2020, 1, 1), 
                                max_value=datetime(2021, 1, 1)
                                )

    data_final = st.date_input('Data Final',
                                value=datetime(2021, 1, 1),
                                min_value=datetime(2020, 1, 1),
                                max_value=datetime(2021, 1, 1)
                                )

col = st.columns(1)

format_code = '%Y-%m-%d'
ativos_port = pd.read_csv('C:\\Users\\aureliano.paiva_tc\\Documents\\GitHub\\TCAppCorr\\data\\raw\\stocks_volume.csv')
ativos = list(ativos_port['acronym'].unique())

at_def = ['OIBR3','BBDC4','COGN3','ITUB4','B3SA3']

att = st.multiselect("Ativos", ativos, at_def)

############################## API FLASK ########################################

url  = (ip + 
        '?init_date='+data_inicial+
        '&end_date=' + data_final +
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
                            n=5, center="light", as_cmap=True)

sns.set(rc={"figure.figsize":(1.5, 1.5)})     
fig, ax = plt.subplots()

res = sns.heatmap(corr, vmin=-1, vmax=1, center=0,cbar_kws={'shrink': 0.7},
            cmap= cmap,
            square=True, annot=True, mask=matrix, annot_kws={'size': 5}
            )

res.set_xticklabels(res.get_xmajorticklabels(), fontsize = 6)
res.set_yticklabels(res.get_xmajorticklabels(), fontsize = 6)

ax.set_xticklabels(
                ax.get_xticklabels(),
                rotation=45,
                horizontalalignment='right')

st.write(fig)
