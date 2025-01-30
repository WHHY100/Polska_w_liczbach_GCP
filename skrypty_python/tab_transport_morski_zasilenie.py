# ----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
# ----------------------------------------------------------------------

import urllib.request, json
import connect_big_query.connect_big_query as conn_gcp
import math
from datetime import datetime

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# NAZWA TABELI
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_transport_morski")

# ----------------------------------------------------------------------
# ROK START i ROK KONIEC
# ----------------------------------------------------------------------

query_max_date = "SELECT max(transport_morski_rok) FROM source.tab_transport_morski"
query_max_date_result = client.query(query_max_date)
query_max_date_result_row = next(query_max_date_result.result())

v_start = query_max_date_result_row[0] + 1
v_koniec = datetime.today().year

i = v_start
arr_lata_api = []
while i <= v_koniec:
    arr_lata_api.append(i)
    i = i + 1

# ----------------------------------------------------------------------
# ODPYTANIE API O DANE
# -> 75951 załadunek łącznie z tranzytem
# -> 75952 wyładunek łącznie z tranzytem
# ----------------------------------------------------------------------

arr_klucze_zmiennych = [75951, 75952]
arr_zbior_api = []

try:
    for i in arr_lata_api:

        for v_zmienna_wartosc in arr_klucze_zmiennych:

            url_bdl_api = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/" + str(v_zmienna_wartosc) +
                           "?format=json&unit-level=5&page-size" +
                           "=100&year=" + str(i))

            # --------------------- #
            # oblicz ile jest stron #
            # --------------------- #
            with urllib.request.urlopen(url_bdl_api) as url:
                data_url_bdl_api = json.load(url)
                v_page_ilosc = math.floor(data_url_bdl_api['totalRecords'] / 100) + 1

            arr_liczba_page = []
            j = 0
            while j < v_page_ilosc:
                url_bdl_api_port = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/" + str(v_zmienna_wartosc) +
                                    "?format=json&unit-level=5&page-size" +
                                    "=100&year=" + str(i) + "&page="+str(j))

                with urllib.request.urlopen(url_bdl_api_port) as url_port:
                    data_url_bdl_api_port = json.load(url_port)

                    v_dlugosc_obiekt = len(data_url_bdl_api_port['results'])

                    z = 0
                    while z < v_dlugosc_obiekt:
                        if data_url_bdl_api_port['results'][z]['name'] in ('Powiat m. Gdańsk', 'Powiat m. Gdynia',
                                                                           'Powiat m. Szczecin', 'Powiat m. Świnoujście',
                                                                           'Powiat kołobrzeski', 'Powiat m. Słupsk',
                                                                           'Powiat sławieński', 'Powiat m. Elbląg'):

                            v_rok = data_url_bdl_api_port['results'][z]['values'][0]['year']
                            v_nazwa_powiatu = data_url_bdl_api_port['results'][z]['name']
                            v_wartosc = data_url_bdl_api_port['results'][z]['values'][0]['val']

                            # ------------------------ #
                            # wyznacz kategorię danych #
                            # ------------------------ #
                            if v_zmienna_wartosc == 75951:
                                v_nazwa_zmiennej = 'załadunek łącznie z tranzytem (w tys ton)'
                            elif v_zmienna_wartosc == 75952:
                                v_nazwa_zmiennej = 'wyładunek łącznie z tranzytem (w tys ton)'

                            # ------------------------ #
                            # wyznacz nazwę portu      #
                            # ------------------------ #
                            if v_nazwa_powiatu == 'Powiat m. Gdańsk':
                                v_nazwa_portu = 'port w Gdańsku'
                            elif v_nazwa_powiatu == 'Powiat m. Gdynia':
                                v_nazwa_portu = 'port w Gdyni'
                            elif v_nazwa_powiatu == 'Powiat m. Szczecin':
                                v_nazwa_portu = 'port w Szczecinie'
                            elif v_nazwa_powiatu == 'Powiat m. Świnoujście':
                                v_nazwa_portu = 'port w Świnoujściu'
                            elif v_nazwa_powiatu == 'Powiat kołobrzeski':
                                v_nazwa_portu = 'port w Kołobrzegu'
                            elif v_nazwa_powiatu == 'Powiat m. Słupsk':
                                v_nazwa_portu = 'port w Ustce i Władysławowie'
                            elif v_nazwa_powiatu == 'Powiat sławieński':
                                v_nazwa_portu = 'port w Darłowie'
                            elif v_nazwa_powiatu == 'Powiat m. Elbląg':
                                v_nazwa_portu = 'port w Elblągu'

                            record = [{
                                'data_generacji': str(datetime.now())
                                ,'transport_morski_rok': v_rok
                                ,'transport_morski_port_nazwa': v_nazwa_portu
                                ,'transport_morski_powiat_nazwa': v_nazwa_powiatu
                                ,'transport_morski_typ_zmiennej': v_nazwa_zmiennej
                                ,'transport_towary_tys_ton' : v_wartosc
                            }]

                            arr_zbior_api.append(record)

                        z = z + 1
                j = j + 1
except:
    print("Brak danych do pobrania za nowy okres!")

# ----------------------------------------------------------------------
# ZAŁADOWANE DANYCH DO TABELI
# ----------------------------------------------------------------------

for i in arr_zbior_api:
    client.insert_rows(table_id, i)

#----------------------------------------------------------------------
# INFORMACJE O STATUSIE PRZETWARZANIA
#----------------------------------------------------------------------

table_id_procedura_kontrolna = client.get_table("system.tab_statusy_przetwarzania")

arr_record = [{
    'data_generacji' : str(datetime.now()),
    'data_zasilenia' : datetime.today().strftime('%Y-%m-%d'),
    'typ_danych' : 'zasilenie - etl',
    'procedura_python' : 'tab_transport_morski_zasilenie',
    'tabela' : 'tab_transport_morski',
    'status' : 'ZAKOŃCZONO'
}]

client.insert_rows(table_id_procedura_kontrolna, arr_record)
print("Skrypt zakończył działanie!")