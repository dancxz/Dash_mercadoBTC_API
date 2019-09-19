# Criação da Class Trades_MercadoBTC  para facilitar coletar e adicionar dados ao banco
# O banco de dados em sqlite foi feito para futuras analises desdo incio do ano de 2018
# coding: utf-8

import requests
import pandas as pd
import sqlite3
import datetime

class Trades_MercadoBTC:
    # Usa a api rest a partir apenas do tid
    def __init__(self):
        self.columns = [ 'tid', 'date', 'amount', 'price', 'type', 'date_brt', 'amount_brl']
        
    def get_trade_mercado_btc(self):

        self.url = 'https://www.mercadobitcoin.net/api/BTC/trades/?tid={}'.format(self.tid)
        self.trade_mercado_btc = requests.get(self.url).json()

        if len(self.trade_mercado_btc) == 0:
            return pd.DataFrame(columns=self.columns)

        self.trade_mercado_btc = pd.DataFrame(self.trade_mercado_btc)
        self.trade_mercado_btc = self.trade_mercado_btc[[ 'tid', 'date', 'amount', 'price', 'type']]

        self.trade_mercado_btc['date'] = pd.to_datetime(self.trade_mercado_btc['date'],unit='s')

        # converto UTC em BRT (UTC-3)
        self.trade_mercado_btc['date_brt'] = self.trade_mercado_btc['date'].apply(lambda x: pd.to_datetime(x).
                                                            tz_localize('UTC').tz_convert('America/Sao_Paulo').replace(tzinfo=None))

        ## Crio um coluna com o amount em brl
        self.trade_mercado_btc['amount_brl'] = self.trade_mercado_btc['amount'] * self.trade_mercado_btc['price']
        return self.trade_mercado_btc


    def save_mercado_btc(self,mercado_btc):
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

        # gero um loop por toda lista de dados para
        ## dar o comando de execute
        for i in list_trade:

            # inserindo dados na tabela
            self.cursor.execute("""
            INSERT INTO Mercado_BTC (tid, date, amount, price, type, date_brt, amount_brl)
            VALUES {}
            """.format(i))

        # gravando no bd
        self.conn.commit()
        self.conn.close()

    def save_new_trades(self):
        self.conn = sqlite3.connect('Corretoras.db')
        self.cursor = self.conn.cursor()

        # criando a tabela (Mercado_BTC)
        self.cursor.execute(""" 
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
        
        self.tid = pd.read_sql_query('SELECT max(tid) FROM Mercado_BTC',self.conn)['max(tid)'][0]

        if self.tid == None:
            self.tid =  2900000
            
        trade_mercado_btc = Trades_MercadoBTC.get_trade_mercado_btc(self)
        Trades_MercadoBTC.save_mercado_btc(self,trade_mercado_btc)
        
        print('Trades Adicionados ao Banco - {}'.format(datetime.datetime.now()))
