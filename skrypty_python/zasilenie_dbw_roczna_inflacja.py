#----------------------------------------------------------------------
# FUNCKJA - BY WOWOŁAĆ KOD W PLIKU AUTOSTART
#----------------------------------------------------------------------

def fnc_zasilenie_dbw_roczna_inflacja():

    #----------------------------------------------------------------------
    # IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
    #----------------------------------------------------------------------

    from datetime import datetime
    import urllib.request, json
    import connect_big_query.connect_big_query as conn_gcp
    import time
    client = conn_gcp.connect_gcp()

    #----------------------------------------------------------------------
    # NAZWA TABELI
    #----------------------------------------------------------------------

    table_id = client.get_table( "source.tab_wskaznik_cpi_roczny")

    #----------------------------------------------------------------------
    # UTWORZENIE TABLICY Z LATAMI DO ZACZYTANIA
    #----------------------------------------------------------------------

    query_max_date = "SELECT max(wskaznik_rok) as max_dt FROM source.tab_wskaznik_cpi_roczny"
    query_max_date_result = client.query(query_max_date)
    query_max_date_result_row = next(query_max_date_result.result())

    query_max_date_result_row_year = query_max_date_result_row[0] + 1

    #----------------------------------------------------------------------
    # UTWORZENIE TABLICY Z LATAMI
    #----------------------------------------------------------------------

    rok_start = query_max_date_result_row_year
    rok_koniec = datetime.today().year

    arr_rok_dbw = []

    while rok_start <= rok_koniec:
        arr_rok_dbw.append(rok_start)
        rok_start = rok_start + 1

    #----------------------------------------------------------------------
    # POBRANIE DANYCH Z API
    #----------------------------------------------------------------------

    result_api = []

    for i in arr_rok_dbw:

        try:

            url = ("https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-data-section?id-zmienna=305&id-przekroj=" +
                   "739&id-rok=" + str(i) + "&id-okres=282&ile-na-stronie=5000&numer-strony=0&lang=pl")

            with urllib.request.urlopen(url) as url:
                data_url = json.load(url)
                v_wskaznik_cpi = data_url['data'][0]['wartosc']

                row = [{"data_generacji" : str(datetime.now()), "wskaznik_rok" : i, "wskaznik_wartosc" : v_wskaznik_cpi}]
                result_api.append(row)
                time.sleep(2)

            print("Pobrano dane za: " + str(i))
        except:
            print("Nie pobrano danych za okres: " + str(i) + "!")

    #----------------------------------------------------------------------
    # ZAŁADOWANIE DANYCH DO TABELI
    #----------------------------------------------------------------------

    for i in result_api:
        client.insert_rows(table_id, i)
        print("Załadowano dane: " + str(i[0]['wskaznik_rok']) + ", wartość CPI: " + str(str(i[0]['wskaznik_wartosc'])))