#----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
#----------------------------------------------------------------------

from datetime import datetime, timedelta, date
import urllib.request, json
import connect_big_query as conn_gcp
import time
from dateutil.relativedelta import *
client = conn_gcp.connect_gcp()

#----------------------------------------------------------------------
# NAZWA TABELI
#----------------------------------------------------------------------

table_id = client.get_table( "source.tab_wskaznik_cpi_miesieczny")

#----------------------------------------------------------------------
# UTWORZENIE TABLICY Z LATAMI DO ZACZYTANIA
# -> start: 2013
# -> koniec: rok bieżązy
#----------------------------------------------------------------------

query_max_date = "SELECT max(wskaznik_data) as max_dt FROM source.tab_wskaznik_cpi_miesieczny"
query_max_date_result = client.query(query_max_date)
query_max_date_result_row = next(query_max_date_result.result())

query_max_date_result_row_month = query_max_date_result_row[0].month
query_max_date_result_row_year = query_max_date_result_row[0].year

#----------------------------------------------------------------------
# UTWORZENIE TABLICY Z ODPOWIEDNIMI ID OKRESU
# -> 247 - styczeń
# -> 258 - grudzień
#----------------------------------------------------------------------

arr_id_okresu = []

i = 247
while i <= 258:
    arr_id_okresu.append(i)
    i = i + 1

rok_start = query_max_date_result_row_year
rok_koniec = query_max_date_result_row_year + 1

arr_rok_dbw = []

while rok_start <= rok_koniec:
    arr_rok_dbw.append(rok_start)
    rok_start = rok_start + 1

#----------------------------------------------------------------------
# POŁĄCZENIE ID OKRESU I ROKU
#----------------------------------------------------------------------

arr_rok_id_comp = []

for i in arr_rok_dbw:
    for j in arr_id_okresu:
        row = [{'rok' : i, 'id_miesiac' : j, 'miesiac_numer' : int(j) - 247 + 1}]

        if i == query_max_date_result_row_year and row[0]['miesiac_numer'] > query_max_date_result_row_month:
            arr_rok_id_comp.append(row)
        elif i > query_max_date_result_row_year:
            arr_rok_id_comp.append(row)

#----------------------------------------------------------------------
# POBRANIE DANYCH Z API
#----------------------------------------------------------------------

result_api = []

for i in arr_rok_id_comp:

    v_rok = i[0]['rok']
    v_miesiac_okres = i[0]['id_miesiac']
    v_miesiac_numer = i[0]['miesiac_numer']
    v_data = date(int(v_rok), int(v_miesiac_numer), 1) + relativedelta(months=1) - timedelta(days=1)

    try:

        url = ("https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-data-section?id-zmienna=305&id" +
               "-przekroj=739&id-rok=" + str(v_rok) + "&id-okres=" + str(v_miesiac_okres) +
               "&ile-na-stronie=5000&numer-strony=0&lang=pl")

        with urllib.request.urlopen(url) as url:
            data_url = json.load(url)
            v_wskaznik_cpi = data_url['data'][0]['wartosc']

            row = [{"wskaznik_data" : v_data, "wskaznik_wartosc" : v_wskaznik_cpi}]
            result_api.append(row)
            time.sleep(2)

        print("Pobrano dane za: " + str(v_data))
    except:
        print("Nie pobrano danych za okres: " + str(v_data) + "!")

#----------------------------------------------------------------------
# ZAŁADOWANIE DANYCH DO TABELI
#----------------------------------------------------------------------

for i in result_api:
    client.insert_rows(table_id, i)
    print("Załadowano dane: " + str(i[0]['wskaznik_data']) + ", wartość CPI: " + str(str(i[0]['wskaznik_wartosc'])))