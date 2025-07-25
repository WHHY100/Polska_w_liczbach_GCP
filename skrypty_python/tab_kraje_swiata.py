# ----------------------------------------------------------------------
# KODOWANIE UTF-8 - WYMUSZENIE
# ----------------------------------------------------------------------

import sys
sys.stdout.reconfigure(encoding='utf-8')

# ----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
# ----------------------------------------------------------------------

import connect_big_query.connect_big_query as conn_gcp
import urllib.request, json, time
from datetime import datetime
client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# WCZYTANIE KRAJÓW KTÓRE SĄ JUŻ UZUPEŁNIONE W BAZIE
# ----------------------------------------------------------------------

query = "SELECT nazwa_skrocona FROM source.tab_kraje_swiata"
query_result = client.query(query)

arr_kraje_zasilone = []
for i in query_result:
    arr_kraje_zasilone.append(i[0])

# ----------------------------------------------------------------------
# NAZWA TABELI
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_kraje_swiata")

# ----------------------------------------------------------------------
# DANE Z API
# ----------------------------------------------------------------------

arr_rezultat_api = []

url_api = "https://restcountries.com/v3.1/all?fields=name"
with urllib.request.urlopen(url_api) as url:
    data = json.load(url)
    v_ilosc_rekordow = len(data)
    v_nazwy_panstw = []

    i = 0
    while i < v_ilosc_rekordow:
        v_nazwa_panstwa = data[i]['name']['common']

        if v_nazwa_panstwa not in arr_kraje_zasilone:
            v_nazwy_panstw.append(v_nazwa_panstwa)
        i = i + 1

    for i in v_nazwy_panstw:

        # -- obsluga znakow powodujacych error z wywolaniem -- #
        if i == "Saint Barthélemy":
            url_api_kraj = "https://restcountries.com/v3.1/name/Saint-Barth%C3%A9lemy"
        else:
            url_api_kraj = str.replace("https://restcountries.com/v3.1/name/" + i, " ", "%20")
            url_api_kraj = str.replace(url_api_kraj, "ç", "c")
            url_api_kraj = str.replace(url_api_kraj, "é", "e")
            url_api_kraj = str.replace(url_api_kraj, "ã", "a")
            url_api_kraj = str.replace(url_api_kraj, "í", "i")
            url_api_kraj = str.replace(url_api_kraj, "Å", "%C3%85")
        # ---------------------------------------------------- #
        print(url_api_kraj)
        # -- rozne indeksy w api (kraje wyjatki od reguly) --- #
        if i == "China":
            nr_indeks = 3
        elif i in["Mali", "Samoa", "Dominica", "Sudan", "India", "Iran", "Netherlands"]:
            nr_indeks = 1
        else:
            nr_indeks = 0
        # ---------------------------------------------------- #

        wiersz = []
        with urllib.request.urlopen(url_api_kraj) as url_kraj:
            data_kraj = json.load(url_kraj)

            try:
                v_nazwa_skrocona = data_kraj[nr_indeks]['name']['common']
            except:
                v_nazwa_skrocona = ''

            try:
                v_nazwa_oficjalna = data_kraj[nr_indeks]['name']['official']
            except:
                v_nazwa_oficjalna = ''

            try:
                v_nazwa_polska = data_kraj[nr_indeks]['translations']['pol']['common']
            except:
                v_nazwa_polska = ''

            try:
                v_waluta = list(data_kraj[nr_indeks]['currencies'].keys())[0]
            except:
                v_waluta = ''

            try:
                v_region = data_kraj[nr_indeks]['region']
            except:
                v_region = ''

            try:
                v_stolica = data_kraj[nr_indeks]['capital'][0]
            except:
                v_stolica = ''

            try:
                v_jezyk = list(data_kraj[nr_indeks]['languages'].values())[0]
            except:
                v_jezyk = ''

            try:
                v_populacja = data_kraj[nr_indeks]['population']
            except:
                v_populacja = 0

            wiersz = [
                {'data_generacji': str(datetime.now()),
                 'nazwa_skrocona': v_nazwa_skrocona,
                 'nazwa_oficjalna': v_nazwa_oficjalna,
                 'nazwa_polska': v_nazwa_polska,
                 'waluta': v_waluta,
                 'region': v_region,
                 'stolica': v_stolica,
                 'jezyk': v_jezyk,
                 'populacja': v_populacja}
            ]

        arr_rezultat_api.append(wiersz)
        time.sleep(1)

#----------------------------------------------------------------------
# ZAŁADOWANIE DANYCH DO TABELI I KOMUNIKAT KONCOWY
#----------------------------------------------------------------------
if len(arr_rezultat_api) == 0:
    print("Brak nowych danych do załadowania!")
else:
    for i in arr_rezultat_api:
        client.insert_rows(table_id, i)
        print("Załadowano rekord: " + str(i))