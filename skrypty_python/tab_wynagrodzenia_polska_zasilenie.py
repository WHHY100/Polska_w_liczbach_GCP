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

table_id = client.get_table("source.tab_wynagrodzenia_polska")

# ----------------------------------------------------------------------
# USTAWIENIE ZMIENNYCH STARTOWYCH
# ----------------------------------------------------------------------

query_max_date = "SELECT max(wynagrodzenia_rok) FROM source.tab_wynagrodzenia_polska"
query_max_date_result = client.query(query_max_date)
query_max_date_result_row = next(query_max_date_result.result())

start_rok_v = query_max_date_result_row[0] + 1
koniec_rok = datetime.today().year

arr_lata_wynagrodzenia = []

while start_rok_v <= koniec_rok:
    arr_lata_wynagrodzenia.append(start_rok_v)
    start_rok_v = start_rok_v + 1

# ----------------------------------------------------------------------
# POBRANIE DANYCH Z API
# ----------------------------------------------------------------------

arr_wartosc_wynagrodzen = []
for i in arr_lata_wynagrodzenia:
    url_bdl_api = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/64428?format=json&year="
                   + str(i)
                   + "&unit-level=0&page-size=100")
    try:
        with urllib.request.urlopen(url_bdl_api) as url:
            data_url_bdl_api = json.load(url)
            v_dl_obiektu = len(data_url_bdl_api['results'])

            j = 0
            while j < v_dl_obiektu:
                v_rok = data_url_bdl_api['results'][j]['values'][0]['year']
                v_wartosc = data_url_bdl_api['results'][j]['values'][0]['val']

                arr_rekord = [{"data_generacji": str(datetime.now()),
                               "wynagrodzenia_rok": v_rok,
                               "wynagrodzenia_wartosc": v_wartosc,
                               "wynagrodzenia_waluta": "PLN"
                               }]

                arr_wartosc_wynagrodzen.append(arr_rekord)

                j = j + 1
            print("Pobrano dane o wynagrodzeniach za rok: " + str(i))
            time.sleep(5)
    except:
        print("Nie udało się pobrać danych za rok: " + str(i))

# ----------------------------------------------------------------------
# ZAŁADOWANIE DANYCH DO TABELI
# ----------------------------------------------------------------------

if len(arr_wartosc_wynagrodzen) == 0:
    print("Nie pobrano informacji z BDL, nie załadowano nowych danych do GCP!")
else:
    for i in arr_wartosc_wynagrodzen:
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
    'procedura_python' : 'tab_wynagrodzenia_polska_zasilenie',
    'tabela' : 'tab_wynagrodzenia_polska',
    'status' : 'ZAKOŃCZONO'
}]

client.insert_rows(table_id_procedura_kontrolna, arr_record)

print("Skrypt zakończył działanie!")