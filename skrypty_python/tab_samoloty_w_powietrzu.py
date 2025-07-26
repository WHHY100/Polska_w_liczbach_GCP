# ----------------------------------------------------------------------
# IMPORT POTRZEBNYCH KOMPONENTÓW
# ----------------------------------------------------------------------

from datetime import datetime
import urllib.request, json
import connect_big_query.connect_big_query as conn_gcp

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# USTAWIENIE NAZWY TABELI
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_samoloty_w_powietrzu")

# ----------------------------------------------------------------------
# POBIERZ DANE O SAMOLOTACH W POWIETRZU
# ----------------------------------------------------------------------

url_api = "https://opensky-network.org/api/states/all"

with urllib.request.urlopen(url_api) as url:
    data_url_bdl_api = json.load(url)

    arr_samoloty = []
    dt_danych = datetime.fromtimestamp(data_url_bdl_api['time'])
    for i in data_url_bdl_api['states']:
        try:
            unikalny_numer_lotu = i[0]
            liniowy_numer_lotu = i[1]
            kraj_samolotu = i[2]
            lot_ostatni_kontakt = datetime.fromtimestamp(i[4])
            dlugosc_geograficzna = i[5]
            szerokosc_geograficzna = i[6]
            czy_samolot_na_ziemi = i[8]
            predkosc_pozioma_w_kilometrach = round(i[9] * 3.6, 2)
            predkosc_pionowa_w_metrach = i[11]
            wysokosc_w_metrach = i[13]
            kod_transpodera = i[14]
        except:
            print("Nie pobrano danych o locie: " + str(i))

        arr_rekord = [{"data_danych": dt_danych,
                       "unikalny_numer_lotu": unikalny_numer_lotu.strip(),
                       "liniowy_numer_lotu": liniowy_numer_lotu.strip(),
                       "kraj_samolotu": kraj_samolotu,
                       "lot_ostatni_kontakt": lot_ostatni_kontakt,
                       "dlugosc_geograficzna": dlugosc_geograficzna,
                       "szerokosc_geograficzna": szerokosc_geograficzna,
                       "czy_samolot_na_ziemi": czy_samolot_na_ziemi,
                       "predkosc_pozioma_w_kilometrach": predkosc_pozioma_w_kilometrach,
                       "predkosc_pionowa_w_metrach": predkosc_pionowa_w_metrach,
                       "wysokosc_w_metrach": wysokosc_w_metrach,
                       "kod_transpodera": kod_transpodera,
                       }]

        arr_samoloty.append(arr_rekord)

# ----------------------------------------------------------------------
# ZAŁADOWANIE DANYCH DO TABELI
# ----------------------------------------------------------------------

for i in arr_samoloty:
    client.insert_rows(table_id, i)

print("Dane o samolotach w powietrzu zostały załadowane!")