# Dash_mercadoBTC_API
 Projeto para coleta e demostração dos Movimentos em tempo real, se ultilizandod e API, Banco de dados e a Dashboard do plotly:
 - Corretoras.db nele so tem uma tabela "Mercado_BTC";
 - API.py Contem as chamadas de API (get_trade_mercado_btc), metodo para salvar no db (save_mercado_btc ) e metodo para coletar novos dados (save_new_trades);
 - Schedule.py Agendo a cada 20 segundos para rodar a função save_new_trades;
 - Dash.py scrip para montar a Dashboard com o grafico e tabela do volume diario
