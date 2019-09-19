import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import sqlite3
import datetime
import time

import plotly.graph_objs as go
import socket

def dados_mercado():
    conn = sqlite3.connect('Corretoras.db') 

    query = """SELECT  date(MB.date_brt) AS Data,
    SUM(MB.amount_brl) AS Volume,
    MIN(MB.price) AS Mínimo,
    MAX(MB.price) AS Máximo,
    SUM(CASE WHEN MB.type = 'buy' THEN MB.amount_brl 
         ELSE 0
         END) as Volume_Compra,
    SUM(CASE WHEN MB.type = 'sell' THEN MB.amount_brl 
         ELSE 0
         END) as Volume_Venda
    FROM Mercado_BTC AS MB
    WHERE MB.date_brt >= (SELECT date(max(date_brt), "-15 day") FROM Mercado_BTC)
    group by date(MB.date_brt)"""
    
    table = pd.read_sql_query(query,conn)
    conn.close()
    table['Data'] = pd.to_datetime(table['Data'])
    return table

def grafico_barras(table,colx,coly,nome,titulo,t_colx,t_coly):
    trace = go.Bar(
        x=table[colx].tolist(),
        y=table[coly].tolist(),
        name = nome
    )
    data = [trace]
    layout = dict(title = titulo,
                  xaxis = dict(title = t_colx),
                  yaxis = dict(title = t_coly),
                  )
    fig = dict(data=data, layout=layout)
    return fig

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )    

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)
app.title = 'Dados Relacao '

layout = html.Div([
        html.H4('Volume do Mercado Bitcoin'),
        dcc.Graph(id='live-update-graph',className="six columns"),
        html.H4('Volume das Corretoras'),
        html.Div(id='live-update-table'),
        dcc.Interval(
            id='interval-component',
            interval=15*1000, # in milliseconds
            n_intervals=0)
    ])
app.layout = layout 
# callback do grafico
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def grafico_live(n):
    global tabela
    tabela = dados_mercado()
    #table = pd.read_csv('read_dash.csv')
    return grafico_barras(tabela,'Data','Volume','Volume Negociações BRL','Volume Diário','Data','R$')

# callback da tabela
@app.callback(Output('live-update-table', 'children'),
              [Input('interval-component', 'n_intervals')])
def ticker_table(n):
    time.sleep(2)
    
    tabela ['Volume'] = tabela['Volume'].apply(lambda x: round(x,4))
    tabela ['Mínimo'] = tabela['Mínimo'].apply(lambda x: round(x,2))
    tabela ['Máximo'] = tabela['Máximo'].apply(lambda x: round(x,2))

    return generate_table(tabela[['Data','Volume','Mínimo','Máximo']].tail(9))

app.scripts.config.serve_locally = True
if __name__ == '__main__':
    ip =  socket.gethostbyname(socket.gethostname())
    app.run_server(debug= False,host= ip , port=888)