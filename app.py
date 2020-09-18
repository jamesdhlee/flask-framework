import pandas as pd
from threading import Thread
from flask import Flask,render_template,request,redirect
import json
import requests
import datetime
import jinja2

from bokeh.embed import server_document, components 
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool, TextInput, CustomJS
from bokeh.io import curdoc, output_file
from bokeh.plotting import figure, output_file, show
from bokeh.server.server import Server
from bokeh.themes import Theme

app = Flask(__name__)

app.vars={}

@app.route('/')
def main():
   return redirect('/index')

@app.route('/index', methods=['GET'])
def index():
   return render_template('index.html')

@app.route('/graph', methods=['POST'])
def graph():
    app.vars['symbol'] = request.form['symbol']
    #val = input("Enter Stock Ticker (MUST BE VALID INPUT): ")
    #set API url
    url = "https://www.alphavantage.co/query"
    #define API call paramers
    param = {"function": "TIME_SERIES_DAILY",
             "symbol": app.vars['symbol'],
             "outputsize": "compact",
             "datatype": "json",
             "apikey": "IYLBKM89W10NCRMI"}

    #call the API with given url and parameters using requests library
    response = requests.get(url, param)
    #isolate json part of response
    response_json = response.json()

    #populate json as pandas dataframe - need to transform so that date is first column/index
    df = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient= 'index').sort_index(axis=1)
    #rename columns
    df = df.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'})
    #set index to datetime
    df.index = pd.to_datetime(df.index)
    #take the last 31 days as "past month"
    df1=df.last('31D')

    output_file('templates/output.html')
    #output_notebook()

    #define x and y
    x = df1.index
    y = df1.Close
    p = figure(title=app.vars['symbol'], x_axis_type="datetime")
    p.line(x,y)
    p.xaxis.axis_label = "Date (Last 31 Days)"
    p.yaxis.axis_label = "Closing Price ($)"
    #show(p)
    return render_template('output.html')
    
if __name__ == '__main__':
   app.run(port=33507)