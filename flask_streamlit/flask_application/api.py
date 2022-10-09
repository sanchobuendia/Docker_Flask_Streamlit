# Bibliotecas
import pandas as pd
import numpy as np
import io
import requests
import json
import os
from flask import Response
from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/returnjson", methods=['POST','GET']) 

# http://127.0.0.1:8080/returnjson?init_date=2022-01-01&end_date=2022-01-30&freq_time=1h&index=Close&tickers=SPY&tickers=AAPL&tickers=MMM

def ticker() -> "matriz de correlação":
    
    tickers = request.args.getlist("tickers")
    init_date = request.args.get('init_date') # '2022-01-01'
    end_date = request.args.get('end_date')   # '2022-01-30'
    freq_time = request.args.get('freq_time') 
    # Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # Intraday data cannot extend last 60 days
    index = request.args.get('index')         # 'Adj Close','Close', 'High', 'Open'

    df = yf.download(tickers, interval = str(freq_time), start=str(init_date), end= str(end_date)) 
    df = df.reset_index()
    corr = df[str(index)]
    corr = corr.corr()
    corr = corr.to_dict()

    return jsonify(corr)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
