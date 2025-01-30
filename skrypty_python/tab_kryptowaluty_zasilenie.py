# ----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
# ----------------------------------------------------------------------

from datetime import datetime
import urllib.request, json
import connect_big_query.connect_big_query as conn_gcp
import time

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# NAZWA TABELI
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_kryptowaluty")

# ----------------------------------------------------------------------
# LISTA IMPORTOWANYCH KRYPTOWALUT
# ----------------------------------------------------------------------

arr_crypto = ['btc', 'eth', 'ltc', 'bch', 'bnb', 'eos', 'xrp', 'xlm', 'link', 'dot', 'yfi']

# ----------------------------------------------------------------------
# POBRANIE DANYCH Z API
# ----------------------------------------------------------------------

arr_wynik_api = []

for i in arr_crypto:
    url_api = "https://api.coingecko.com/api/v3/exchange_rates"
    print("Pobranie danych kryptowaluty: " + i)
    with urllib.request.urlopen(url_api) as url:
        data = json.load(url)
        v_btc_cena = data['rates']['pln']['value']
        v_crypto_nazwa = data['rates'][i]['name']
        v_crypto_jednostka = data['rates'][i]['unit']
        v_crypto_wartosc_w_btc = data['rates'][i]['value']

        v_crypto_wartosc_w_pln = round(v_btc_cena / v_crypto_wartosc_w_btc, 2)

        row = [{'data_generacji' : str(datetime.now()),
                "kryptowaluta_data" : datetime.today().strftime('%Y-%m-%d'),
                "kryptowaluta_cena" : v_crypto_wartosc_w_pln,
                "kryptowaluta_waluta" : "PLN",
                "kryptowaluta_nazwa" : v_crypto_nazwa.upper(),
                "kryptowaluta_kod" : v_crypto_jednostka.lower()}]

        arr_wynik_api.append(row)

    time.sleep(30)

# ----------------------------------------------------------------------
# USUNIĘCIE DANYCH Z TABELI Z KONKRETNEJ DATY
# ----------------------------------------------------------------------

try:
    query_delete = ("DELETE FROM source.tab_kryptowaluty WHERE kryptowaluta_data = '" +
                    str(datetime.today().strftime('%Y-%m-%d')) +
                    "'")

    job = client.query(query_delete)
    job.result()
    print("Jeżeli były dane za dziś w tabeli - zostały usunięte!")
except:
    print("Nie udało się usunać danych - najprawdopodobniej dane są w interwale strumieniowym!")

#----------------------------------------------------------------------
# ZAŁADOWANIE DANYCH DO TABELI
#----------------------------------------------------------------------

for i in arr_wynik_api:
    client.insert_rows(table_id, i)
    print("Załadowano rekord: " + str(i))

#----------------------------------------------------------------------
# INFORMACJE O STATUSIE PRZETWARZANIA
#----------------------------------------------------------------------

table_id_procedura_kontrolna = client.get_table("system.tab_statusy_przetwarzania")

arr_record = [{
    'data_generacji' : str(datetime.now()),
    'data_zasilenia' : datetime.today().strftime('%Y-%m-%d'),
    'typ_danych' : 'zasilenie - etl',
    'procedura_python' : 'tab_kryptowaluty_zasilenie',
    'tabela' : 'tab_kryptowaluty',
    'status' : 'ZAKOŃCZONO'
}]

client.insert_rows(table_id_procedura_kontrolna, arr_record)