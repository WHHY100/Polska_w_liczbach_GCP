#----------------------------------------------------------------------
# FUNCKJA - BY WOWOŁAĆ KOD W PLIKU AUTOSTART
#----------------------------------------------------------------------

def fnc_export_danych_do_csv():

    #----------------------------------------------------------------------
    # IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
    #----------------------------------------------------------------------

    import connect_big_query as conn_gcp
    import csv
    client = conn_gcp.connect_gcp()

    #----------------------------------------------------------------------
    # ZCZYTANIE WSZYSTKICH NAZW TABEL
    #----------------------------------------------------------------------

    query_name_table = "SELECT table_name FROM source.INFORMATION_SCHEMA.TABLES"
    query_name_table_result = client.query(query_name_table)

    arr_tab_names = []
    for i in query_name_table_result:
        arr_tab_names.append(i[0])

    #----------------------------------------------------------------------
    # ZCZYTANIE WSZYSTKICH REKORDOW Z TABELI I ZRZUT DO PLIKU
    #----------------------------------------------------------------------

    for i in arr_tab_names:
        query_record = "SELECT * FROM source." + str(i)
        query_record_result = client.query(query_record)

        query_colnames = ("SELECT column_name FROM source.INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"
                          + str(i) +
                          "'")
        query_colnames_result = client.query(query_colnames)

        # utworzenie pustej tabeli do której zaczytamy dane
        arr_record_table = []

        # pobranie i zapis nagłówków
        arr_colnames_table = []
        for j in query_colnames_result:
            arr_colnames_table.append(j[0])

        arr_record_table.append(arr_colnames_table)

        # pobranie i zapis rekordów
        for j in query_record_result:
            tb_len = len(j)

            x = 0
            arr_fields_in_record = []
            while x < tb_len:
                arr_fields_in_record.append(j[x])
                x = x + 1

            arr_record_table.append(arr_fields_in_record)

        # utworzenie i zapis danych do pliku
        file_name = "../GCP_POLSKA_W_LICZBACH/eksport_danych/" + str(i) +".csv"

        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(arr_record_table)

        print("Tabela: " + str(i) + " została poprawnie eksportowana!")