#----------------------------------------------------------------------
# FUNCKJA - BY WOWOŁAĆ KOD W PLIKU AUTOSTART
#----------------------------------------------------------------------

def zasilenie_bld_sr_cena_metra_kwadratowego():

    # ----------------------------------------------------------------------
    # IMPORT POTRZEBNYCH KOMPONENTÓW
    # ----------------------------------------------------------------------

    from datetime import datetime
    import urllib.request, json
    import connect_big_query.connect_big_query as conn_gcp
    import time

    client = conn_gcp.connect_gcp()

    # ----------------------------------------------------------------------
    # USTAWIENIE ODPOWIEDNIEGO TABLE ID
    # ----------------------------------------------------------------------

    table_id_wojewodztwo = client.get_table("source.tab_mieszkania_ceny_wojewodztwa")
    table_id_polska = client.get_table("source.tab_mieszkania_ceny_polska")

    # ----------------------------------------------------------------------
    # USTAWIANIE ZMIENNYCH STARTOWYCH
    # ----------------------------------------------------------------------

    query_max_date = ("with tab_data_zasilenia as (" +
                      "select max(mieszkania_cena_rok) as rok from source.tab_mieszkania_ceny_polska" +
                      " union all " +
                      "select max(mieszkania_cena_rok) as rok from source.tab_mieszkania_ceny_wojewodztwa) " +
                      "select min(rok) from tab_data_zasilenia")

    query_max_date_result = client.query(query_max_date)
    query_max_date_result_row = next(query_max_date_result.result())

    rok_start = query_max_date_result_row[0] + 1
    rok_koniec = datetime.today().year

    arr_lata = []

    while rok_start <= rok_koniec:
        arr_lata.append(rok_start)
        rok_start = rok_start + 1

    # ----------------------------------------------------------------------
    # POBRANIE DANYCH Z API
    # ----------------------------------------------------------------------

    arr_result_api_wojewodztwa = []
    arr_result_api_polska = []

    for i in arr_lata:
        try:
            url_bld_wojewodztwa = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/633692?format=json&year="
                                   + str(i)
                                   + "&unit-level=2&page-size=100")

            url_bdl_polska = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/633692?format=json&year="
                                   + str(i)
                                   + "&unit-level=0&page-size=100")

            # -------------------------------------------------------------
            # ZASILENIE -> SREDNIA CENA ZA METR KWADRATOWY W WOJEWÓDZTWACH
            # -------------------------------------------------------------

            with urllib.request.urlopen(url_bld_wojewodztwa) as url_wojewodztwa:
                data_url_bdl_api = json.load(url_wojewodztwa)

                v_dlugosc_obiektu = len(data_url_bdl_api['results'])

                j = 0

                while j < v_dlugosc_obiektu:

                    v_nazwa_wojewdzotwa = data_url_bdl_api['results'][j]['name']
                    v_srednia_cena_za_m2_mieszkania = data_url_bdl_api['results'][j]['values'][0]['val']
                    v_srednia_cena_za_m2_rok = data_url_bdl_api['results'][j]['values'][0]['year']

                    arr_rekord = [{"data_generacji": str(datetime.now()),
                                   "mieszkania_cena_rok": v_srednia_cena_za_m2_rok,
                                   "mieszkania_cena_wojewodztwo": v_nazwa_wojewdzotwa,
                                   "mieszkania_cena_metr_kwadratowy": v_srednia_cena_za_m2_mieszkania,
                                   "mieszkania_cena_waluta": "PLN"
                                   }]

                    j = j + 1

                    arr_result_api_wojewodztwa.append(arr_rekord)

            time.sleep(2)

            # -------------------------------------------------------------
            # ZASILENIE -> SREDNIA CENA ZA METR KWADRATOWY W POLSCE
            # -------------------------------------------------------------

            with urllib.request.urlopen(url_bdl_polska) as url_polska:
                data_url_bdl_api = json.load(url_polska)

                v_srednia_cena_za_m2_mieszkania_polska = data_url_bdl_api['results'][0]['values'][0]['val']
                v_srednia_cena_za_m2_rok_polska = data_url_bdl_api['results'][0]['values'][0]['year']

                arr_rekord_polska = [{"data_generacji": str(datetime.now()),
                               "mieszkania_cena_rok": v_srednia_cena_za_m2_rok_polska,
                               "mieszkania_cena_metr_kwadratowy": v_srednia_cena_za_m2_mieszkania_polska,
                               "mieszkania_cena_waluta": "PLN"
                               }]

                arr_result_api_polska.append(arr_rekord_polska)

            time.sleep(2)

        except:
            print("Nie udało się pobrać danych za rok: " + str(i) + "!")

    # ----------------------------------------------------------------------
    # ZAŁADOWANIE DANYCH DO TABELI
    # ----------------------------------------------------------------------

    for i in arr_result_api_wojewodztwa:
        client.insert_rows(table_id_wojewodztwo, i)

    for i in arr_result_api_polska:
        client.insert_rows(table_id_polska, i)

    print("Skrypt ładowania danych o średniej cenie transakcyjnej za metr kwadratowy w Polsce zakończył działanie!")