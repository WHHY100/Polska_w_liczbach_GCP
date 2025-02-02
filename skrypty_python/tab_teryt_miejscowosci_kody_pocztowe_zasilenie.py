# ----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
# ----------------------------------------------------------------------

import connect_big_query.connect_big_query as conn_gcp
import requests
from urllib.parse import quote
from datetime import datetime

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# USTAWIENIE NAZWY TABELI
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_teryt_miejscowosci_kody_pocztowe")

# ----------------------------------------------------------------------
# POBRANIE ID ULIC I MIAST
# ----------------------------------------------------------------------

query_lokacje = (
            "SELECT distinct miejscowosc_nazwa FROM source.tab_teryt_miejscowosci " +
            "WHERE miejscowosc_nazwa not in (SELECT miejscowosc FROM source.tab_teryt_miejscowosci_kody_pocztowe) " +
            "ORDER BY miejscowosc_nazwa LIMIT 100"
)


query_lokacje_result = client.query(query_lokacje)
arr_lokacje = []
for i in query_lokacje_result:
    v_miejscowosc_nazwa = i[0]

    row = {'miejscowosc_nazwa' : v_miejscowosc_nazwa}
    arr_lokacje.append(row)

# ----------------------------------------------------------------------
# POBRANIE KODÓW POCZTOWYCH PRZYPISANYCH DO MIEJSCOWOSCI
# ----------------------------------------------------------------------

arr_miejscowosci_kody_pocztowe = []
try:
    for i in arr_lokacje:
        v_api_miejscowosc = i['miejscowosc_nazwa']
        url_api = "http://kodpocztowy.intami.pl/city/" + quote(v_api_miejscowosc)

        headers = {'Accept': 'application/json'}
        response = requests.get(url_api, headers=headers)
        rezultat_api = response.json()
        rezultat_api_dl = len(rezultat_api)

        if rezultat_api_dl > 0:
            for j in rezultat_api:
                row = [{
                    "data_generacji": str(datetime.now()),
                    'miejscowosc': v_api_miejscowosc,
                    'kod_pocztowy': j
                }]

                arr_miejscowosci_kody_pocztowe.append(row)
        else:
            row = [{
                    "data_generacji": str(datetime.now()),
                    'miejscowosc': v_api_miejscowosc,
                    'kod_pocztowy': ''
                }]
            arr_miejscowosci_kody_pocztowe.append(row)
except:
    print("Nie udalo sie pobrac danych!")

# ------------------------------------------------------
# ZAŁADUJ DO TABELI
# ------------------------------------------------------

for i in arr_miejscowosci_kody_pocztowe:
    client.insert_rows(table_id, i)

# ------------------------------------------------------
# INFORMACJA O STATUSIE PRZETWARZANIA
# ------------------------------------------------------

table_id_procedura_kontrolna = client.get_table("system.tab_statusy_przetwarzania")

arr_record = [{
      'data_generacji' : str(datetime.now()),
      'data_zasilenia' : datetime.today().strftime('%Y-%m-%d'),
      'typ_danych' : 'zasilenie - etl',
      'procedura_python' : 'zasilenia_codzienne_tabele',
      'tabela' : 'tab_teryt_miejscowosci_kody_pocztowe',
      'status' : 'ZAKOŃCZONO'
}]

if len(arr_miejscowosci_kody_pocztowe) > 0:
    print("Załadowano następujące kody pocztowe: ")
    for i in arr_miejscowosci_kody_pocztowe:
        print(i)
else:
    print("Nie załadowano nowych danych do tabeli!")