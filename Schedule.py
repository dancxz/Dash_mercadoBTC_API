# coding: utf-8
# Script para alimentar o Banco de Dados em tempos em tempos
# A cada 20 segundos uso da da class Trades_MercadoBTC para coletar dados da APi e alimentar o Banco

import schedule
import time
import datetime
from API import Trades_MercadoBTC


# Agendo para a cada 20 segundos rodar save_new_trades
schedule.every(20).seconds.do(Trades_MercadoBTC.save_new_trades)

print('Inicio as - {}'.format(datetime.datetime.now()))

Trades_MercadoBTC.save_new_trades()
while True:
    schedule.run_pending()
    time.sleep(1)