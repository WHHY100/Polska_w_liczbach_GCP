# ----------------------------------------------------------------------
# IMPORT POTRZEBNYCH KOMPONENTÓW
# ----------------------------------------------------------------------

from datetime import datetime
import urllib.request, json
import connect_big_query.connect_big_query as conn_gcp
import time

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# USTAWIENIE NAZWY TABELI
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_mieszkania_polska")

# ----------------------------------------------------------------------
# USTAWIENIE ZMIENNYCH STARTOWYCH
# ----------------------------------------------------------------------

query_max_date = "SELECT max(mieszkania_rok) FROM source.tab_mieszkania_polska"
query_max_date_result = client.query(query_max_date)
query_max_date_result_row = next(query_max_date_result.result())

start_rok = query_max_date_result_row[0] + 1
koniec_rok = datetime.today().year

arr_lata_mieszkania = []

while start_rok <= koniec_rok:
    arr_lata_mieszkania.append(start_rok)
    start_rok = start_rok + 1

# ----------------------------------------------------------------------
# DEKLARACJA TABLICY PRZECHOWUJĄCEJ WYNIKI
# ----------------------------------------------------------------------

arr_ilosc_mieszkan = []

# ----------------------------------------------------------------------
# POBRANIE DANYCH O ILOŚCI MIESZKAN W WOJEWÓDZTWACH - NA WSI
# ----------------------------------------------------------------------

for i in arr_lata_mieszkania:
    url_bdl_api = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/60812?format=json&year="
                   + str(i)
                   + "&unit-level=0&page-size=100")
    try:
        with urllib.request.urlopen(url_bdl_api) as url:
            data_url_bdl_api = json.load(url)

            mieszkania_rok = data_url_bdl_api['results'][0]['values'][0]['year']
            mieszkania_wojewodztwo = data_url_bdl_api['results'][0]['values'][0]['val']

            arr_rekord = [{"data_generacji": str(datetime.now()),
                           "mieszkania_region": "wieś",
                           "mieszkania_rok": mieszkania_rok,
                           "mieszkania_ilosc": mieszkania_wojewodztwo,
                           }]

            arr_ilosc_mieszkan.append(arr_rekord)

        time.sleep(2)
    except:
        print("Nie udało się pobrać danych (mieszkania na wsi) za rok: " + str(i))

# ----------------------------------------------------------------------
# POBRANIE DANYCH O ILOŚCI MIESZKAN W WOJEWÓDZTWACH - W MIASTACH
# ----------------------------------------------------------------------

for i in arr_lata_mieszkania:
    url_bdl_api = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/60807?format=json&year="
                   + str(i)
                   + "&unit-level=0&page-size=100")
    try:
        with urllib.request.urlopen(url_bdl_api) as url:
            data_url_bdl_api = json.load(url)
            v_dl_obiektu = len(data_url_bdl_api['results'])

        mieszkania_rok = data_url_bdl_api['results'][0]['values'][0]['year']
        mieszkania_wojewodztwo = data_url_bdl_api['results'][0]['values'][0]['val']

        arr_rekord = [{"data_generacji": str(datetime.now()),
                       "mieszkania_region": "miasto",
                       "mieszkania_rok": mieszkania_rok,
                       "mieszkania_ilosc": mieszkania_wojewodztwo,
                       }]

        arr_ilosc_mieszkan.append(arr_rekord)

        time.sleep(2)
    except:
        print("Nie udało się pobrać danych (mieszkania w mieście) za rok: " + str(i))

# ----------------------------------------------------------------------
# ZAŁADOWANIE DANYCH DO TABELI
# ----------------------------------------------------------------------

if len(arr_ilosc_mieszkan) == 0:
    print("Nie załadowano nowych informacji o mieszkaniach w Polsce w podziale na regiony!")
else:
    for i in arr_ilosc_mieszkan:
        client.insert_rows(table_id, i)

print("Skrypt ładujący dane o mieszkaniach w Polsce w podziale na regiony zakończył działanie!")

#----------------------------------------------------------------------
# INFORMACJE O STATUSIE PRZETWARZANIA
#----------------------------------------------------------------------

table_id_procedura_kontrolna = client.get_table("system.tab_statusy_przetwarzania")

arr_record = [{
    'data_generacji' : str(datetime.now()),
    'data_zasilenia' : datetime.today().strftime('%Y-%m-%d'),
    'typ_danych' : 'zasilenie - etl',
    'procedura_python' : 'tab_mieszkania_polska_zasilenie',
    'tabela' : 'tab_mieszkania_polska',
    'status' : 'ZAKOŃCZONO'
}]

client.insert_rows(table_id_procedura_kontrolna, arr_record)
print("Skrypt ładujący dane o mieszkaniach w Polsce w podziale na regiony zakończył działanie!")