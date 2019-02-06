# Criação da Class Trades_MercadoBTC  para facilitar coletar e adicionar dados ao banco
# O banco de dados em sqlite foi feito para futuras analises desdo incio do ano de 2018
# coding: utf-8

import requests
import pandas as pd
import sqlite3
import datetime

class Trades_MercadoBTC():
    # Usa a api rest a partir apenas do tid
    def get_trade_mercado_btc(tid):

        url = 'https://www.mercadobitcoin.net/api/BTC/trades/?tid={}'.format(tid)
        trade_mercado_btc = requests.get(url).json()

        if len(trade_mercado_btc) == 0:
            return pd.DataFrame(columns=[ 'tid', 'date', 'amount', 'price', 'type', 'date_brt', 'amount_brl'])
            print('Todos os Trades foram coletados por enquanto\nVamos dar um time de 5 minutos!')
        else:
            trade_mercado_btc = pd.DataFrame(trade_mercado_btc)
            trade_mercado_btc = trade_mercado_btc[[ 'tid', 'date', 'amount', 'price', 'type']]

            trade_mercado_btc['date'] = pd.to_datetime(trade_mercado_btc['date'],unit='s')

            # converto UTC em BRT (UTC-3)
            trade_mercado_btc['date_brt'] = trade_mercado_btc['date'].apply(lambda x: pd.to_datetime(x).
                                                                tz_localize('UTC').tz_convert('America/Sao_Paulo').replace(tzinfo=None))
            ## Crio um coluna com o amount em brl
            trade_mercado_btc['amount_brl'] = trade_mercado_btc['amount'] * trade_mercado_btc['price']
            
            return trade_mercado_btc

    # Função para Salvar os dados no Banco.
    def save_mercado_btc (mercado_btc):
        list_trade = []
        # criando uma lista de dados
        for i in mercado_btc.index:
            list_trade.append((mercado_btc['tid'][i],
            str(mercado_btc['date'][i]),
            mercado_btc['amount'][i],
            mercado_btc['price'][i],
            mercado_btc['type'][i],
            str(mercado_btc['date_brt'][i]),
            mercado_btc['amount_brl'][i]))

        # conecto ao banco
        conn = sqlite3.connect('Corretoras.db')
        cursor = conn.cursor()

        # gero um loop por toda lista de dados para
        ## dar o comando de execute
        for i in list_trade:

            # inserindo dados na tabela
            cursor.execute("""
            INSERT INTO Mercado_BTC (tid, date, amount, price, type, date_brt, amount_brl)
            VALUES {}
            """.format(i))

        # gravando no bd
        conn.commit()
        conn.close()


    # A partir do ultimo dado do banco executo apenas essa função para gerar novos dados
    def save_new_trades():
        conn = sqlite3.connect('Corretoras.db')
        cursor = conn.cursor()

        # criando a tabela (Mercado_BTC)
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS Mercado_BTC (
                tid INTEGER NOT NULL PRIMARY KEY,
                date TIMESTAMP NOT NULL,
                amount FLOAT NOT NULL,
                price FLOAT NOT NULL,
                type TEXT NOT NULL,
                date_brt TIMESTAMP NOT NULL,
                amount_brl FLOAT NOT NULL
        );
        """)

        # tid maximo encontrado no banco
        tid_max = pd.read_sql_query('SELECT max(tid) FROM Mercado_BTC',conn)['max(tid)'][0]

        if tid_max == None:
            trade_mercado_btc = Trades_MercadoBTC.get_trade_mercado_btc(1800000)
            Trades_MercadoBTC.save_mercado_btc (trade_mercado_btc)
        else:
            trade_mercado_btc = Trades_MercadoBTC.get_trade_mercado_btc(tid_max)
            Trades_MercadoBTC.save_mercado_btc(trade_mercado_btc)

        print('Trades Adicionados ao Banco - {}'.format(datetime.datetime.now()))
