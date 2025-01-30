# ----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
# ----------------------------------------------------------------------

from datetime import datetime, timedelta, date
import urllib.request, json
import connect_big_query.connect_big_query as conn_gcp

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# UTWORZENIE TABELI DAT
# ----------------------------------------------------------------------

query_max_date = "SELECT max(data_waluty) as max_dt FROM source.tab_ceny_zlota"
query_max_date_result = client.query(query_max_date)
query_max_date_result_row = next(query_max_date_result.result())
start_dt_qr = query_max_date_result_row.max_dt + timedelta(days=1)
end_dt_qr = query_max_date_result_row.max_dt + timedelta(days=30)

date_start = date(start_dt_qr.year, start_dt_qr.month, start_dt_qr.day)
date_end = date(end_dt_qr.year, end_dt_qr.month, end_dt_qr.day)
table_id = client.get_table("source.tab_ceny_zlota")

arr_dates = []
while date_start <= date_end:
    arr_dates.append(date_start)
    date_start = date_start + timedelta(days=1)

# ----------------------------------------------------------------------
# ODPYTUJEMY API I ZAPISUJEMY DO LISTY
# ----------------------------------------------------------------------

result_api = []

for i in arr_dates:
    try:
        url = "https://api.nbp.pl/api/cenyzlota/" + str(i)

        with urllib.request.urlopen(url) as url:
            data = json.load(url)

            value_date = data[0]['data']
            value_price = data[0]['cena']

            row = [{'data_generacji': str(datetime.now()), "data_waluty": value_date, "zloto_cena": value_price}]
            result_api.append(row)
    except:
        print("No data for the selected day: " + str(i))

# ----------------------------------------------------------------------
# ZAŁĄDOWANIE DANYCH DO TABELI
# ----------------------------------------------------------------------

for i in result_api:
    client.insert_rows(table_id, i)
    print("Data for the day was added: " + str(i[0]['data_waluty'] + ", gold price: " + str(str(i[0]['zloto_cena']))))

#----------------------------------------------------------------------
# INFORMACJE O STATUSIE PRZETWARZANIA
#----------------------------------------------------------------------

table_id_procedura_kontrolna = client.get_table("system.tab_statusy_przetwarzania")

arr_record = [{
    'data_generacji' : str(datetime.now()),
    'data_zasilenia' : datetime.today().strftime('%Y-%m-%d'),
    'typ_danych' : 'zasilenie - etl',
    'procedura_python' : 'tab_ceny_zlota_zasilenie',
    'tabela' : 'tab_ceny_zlota',
    'status' : 'ZAKOŃCZONO'
}]

client.insert_rows(table_id_procedura_kontrolna, arr_record)

print("Skrypt zakończył działanie!")
