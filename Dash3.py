#DashBoard Ainda em produção!
# Feita para melhorar e visualizao de como esta o volume do mercadoBTC nos ultimos dias
# A cada 30 segundos leio o banco e retorno um arquvio csv de com os dados para a tabela e graficos
# A cada 15 segundos leio o csv para gerar a tabela e graficos
## Existem pontos a serem melhorados e ja conhecimo alem do layout 


import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import sqlite3
import datetime

import plotly.graph_objs as go
import socket

# Crio uma chave de acesso para a Dash
VALID_USERNAME_PASSWORD_PAIRS = [
    ['hello', 'world']
]

app = dash.Dash('auth')
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# função que me gera os graficos
def grafico(table):

    lista = []
    for i in table['date'].tolist():
        lista.append(150)


    trace1 = go.Bar(
        x=table['date'].tolist(),
        y=table['amount'].tolist(),
        name = 'realizado'
    )

    data = [trace1]

    layout = dict(title = 'Volume diário',
                  xaxis = dict(title = 'Data'),
                  yaxis = dict(title = 'R$'),
                  )
    fig = dict(data=data, layout=layout)
    return fig


# Função para a tabela
def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# defino como sera a pagina principal 
page1 = html.Div([
    html.Div([html.Div(id='Output_temp'),
        dcc.Interval(
            id='interval-component_update',
            interval=30*1000, # in milliseconds
            n_intervals=0)
        ]),
    html.Div([
        html.H4('Volume do Mercado Bitcoin'),
        dcc.Graph(id='live-update-graph',className="six columns"),
        html.H4('Volume das Corretoras'),
        html.Div(id='table'),
        dcc.Interval(
            id='interval-component',
            interval=15*1000, # in milliseconds
            n_intervals=0)
    ]),
 ])

# Caso não exista a pagina retornara 404 Page not found
noPage = html.Div([  # 404

    html.P(["404 Page not found"])

    ], className="no-page")


app.config.suppress_callback_exceptions = True


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# callback para gerar um novo arquivo de leitura
@app.callback(Output('Output_temp', 'children'),
            [Input('interval-component_update', 'n_intervals')])

def live_file(n):

    conn = sqlite3.connect('Corretoras.db')
    # le o sql na tabela clientes
    min_date =pd.to_datetime(pd.read_sql_query("SELECT MAX(date) FROM Mercado_BTC",conn).values[0][0]).date()- datetime.timedelta(31)
    table = pd.read_sql_query("SELECT * FROM Mercado_BTC Where date > '{}'".format(str(min_date)),conn)
    conn.close()

    table['date'] = pd.to_datetime(table['date'])
    table['date'] = table['date'].apply(lambda x: x.date())

    table_pivot = table.pivot_table(index='date',values='amount',aggfunc='sum').reset_index()
    table_pivot['amount'] = table_pivot['amount'].apply(lambda x: round(x,5))

    table_pivot.to_csv('read_dash.csv',index=False)


# callback dos url
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/Page1':
        return page1
    else:
        return noPage

# callback do grafico
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])

def grafico_live(n):
    table = pd.read_csv('read_dash.csv')
    return grafico(table)

# callback da tabela
@app.callback(Output('table', 'children'),
              [Input('interval-component', 'n_intervals')])

def ticker_table(n):
    table = pd.read_csv('read_dash.csv')

    return generate_table(table)

app.scripts.config.serve_locally = True        
if __name__ == '__main__':

    ip =  socket.gethostbyname(socket.gethostname())
    
    app.run_server(debug= False,host= ip , port=888)
