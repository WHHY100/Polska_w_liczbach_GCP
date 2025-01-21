#----------------------------------------------------------------------
# FUNCKJA - BY WOWOŁAĆ KOD W PLIKU AUTOSTART
#----------------------------------------------------------------------

def fnc_zasilenie_nbp_kursy_walut():

    #----------------------------------------------------------------------
    # IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
    #----------------------------------------------------------------------

    from datetime import datetime, timedelta, date
    import urllib.request, json
    import connect_big_query.connect_big_query as conn_gcp
    client = conn_gcp.connect_gcp()

    #----------------------------------------------------------------------
    # WYBRANIE DATY:
    # -> START (OSTATNIA DATA W TABELI)
    # -> KONIEC (+ 30 DNI OD DATY W TABELI)
    #----------------------------------------------------------------------

    query_max_date = "SELECT max(data_waluty) as max_dt FROM source.tab_kursy_walut"
    query_max_date_result = client.query(query_max_date)
    query_max_date_result_row = next(query_max_date_result.result())
    start_dt_qr = query_max_date_result_row.max_dt + timedelta(days=1)
    end_dt_qr = query_max_date_result_row.max_dt + timedelta(days=30)

    date_start = date(start_dt_qr.year, start_dt_qr.month, start_dt_qr.day)
    date_end = date(end_dt_qr.year, end_dt_qr.month, end_dt_qr.day)
    table_id = client.get_table( "source.tab_kursy_walut")

    #----------------------------------------------------------------------
    # UTWORZENIE ARR Z DATAMI
    #----------------------------------------------------------------------

    arr_dates = []

    while date_start <= date_end:
        arr_dates.append(date_start)
        date_start = date_start + timedelta(days=1)

    #----------------------------------------------------------------------
    # POBRANIE DANYCH Z API ZA KAZDY DZIEN
    #----------------------------------------------------------------------

    row_to_insert = []
    for i in arr_dates:
        try:
            url_api = "https://api.nbp.pl/api/exchangerates/tables/a/" + str(i) + "/" + str(i) + "?format=json"
            with urllib.request.urlopen(url_api) as url:
                data = json.load(url)

                json_api_date = data[0]['effectiveDate']
                json_api_N_cr = len(data[0]['rates'])

                i = 0

                while i < json_api_N_cr:
                    json_api_code = data[0]['rates'][i]['code']
                    json_api_mid = data[0]['rates'][i]['mid']

                    row = [{'data_generacji': str(datetime.now()), 'data_waluty': str(json_api_date),
                            'waluta_kod': str(json_api_code), 'waluta_kurs': json_api_mid}]
                    row_to_insert.append(row)
                    i = i + 1
        except:
            print("No data for the selected day: " + str(i))

    #----------------------------------------------------------------------
    # WSADZ REKORDY Z ARR DO TABELI
    #----------------------------------------------------------------------

    for i in row_to_insert:
        client.insert_rows(table_id, i)
        print("Data for the day was added: " + str(i[0]['data_waluty'] + ", currency: " + str(str(i[0]['waluta_kod']))))