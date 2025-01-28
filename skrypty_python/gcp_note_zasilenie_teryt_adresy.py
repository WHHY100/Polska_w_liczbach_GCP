#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# SKRYPT ZAIMPLEMENTOWANY W HARMONOGRAMIE GCP:
# -> ODPYTANIE API RAZ NA MIESIAC (DŁUGI CZAS PRZETWARZANIA)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ----------------------------------------------------------------------
# IMPORT WYMAGANYCH MODULÓW I BIBLIOTEK
# ----------------------------------------------------------------------

from datetime import datetime
import connect_big_query.connect_big_query as conn_gcp
from zeep import Client
from zeep.wsse.username import UsernameToken

client = conn_gcp.connect_gcp()

# ----------------------------------------------------------------------
# NAZWA TABELI - DEFINICJA
# ----------------------------------------------------------------------

table_id = client.get_table("source.tab_teryt_miejscowosci")

# ----------------------------------------------------------------------
# USUNIĘCIE POPRZEDNIEGO ZASILENIA Z TABELI
# ----------------------------------------------------------------------

try:
    query_delete = "DELETE FROM source.tab_teryt_miejscowosci WHERE TRUE;"
    job = client.query(query_delete)
    job.result()
    print("Jeżeli istniały dane z poprzedniego zasilenia zostały skutecznie usunięte z tabeli!")
except:
    print("Nie udało się usunać danych - najprawdopodobniej dane są w interwale strumieniowym!")

# ------------------------------------------------------
# DATA DANYCH
# ------------------------------------------------------

v_curr_date = datetime.today().strftime('%Y-%m-%d')

# ------------------------------------------------------
# POŁĄCZENIE Z TESTOWYM API TERYT
# ------------------------------------------------------

WSDL_URL = "https://uslugaterytws1test.stat.gov.pl/wsdl/terytws1.wsdl"

LOGIN = ""
PASSWORD = ""

client_teryt = Client(WSDL_URL, wsse=UsernameToken(LOGIN, PASSWORD))
service = client_teryt.bind('TerytWs1', 'custom')

# ------------------------------------------------------
# POBRANIE LISTY WOJEWÓDZTW W POLSCE
# ------------------------------------------------------

v_wojewodztwa = service.PobierzListeWojewodztw(v_curr_date)
v_dl_obiektu_wojewodztwa = len(v_wojewodztwa)
arr_wojewodztwa = []

i = 0
while i < v_dl_obiektu_wojewodztwa:
    record = {'wojewodztwo_nazwa' : v_wojewodztwa[i]['NAZWA'], 'wojewodztwo_kod' : v_wojewodztwa[i]['WOJ']}
    arr_wojewodztwa.append(record)
    i = i + 1

print("Zakończono pobieranie województw!")

# ------------------------------------------------------
# POBRANIE LISTY POWIATÓW
# ------------------------------------------------------

arr_powiaty = []
for i in arr_wojewodztwa:
    v_powiat = service.PobierzListePowiatow(i['wojewodztwo_kod'], v_curr_date)
    v_dl_obiektu_powiat = len(v_powiat)

    arr_record = []
    j = 0
    while j < v_dl_obiektu_powiat:
        v_powiat_nazwa = v_powiat[j]['NAZWA']
        v_powiat_kod = v_powiat[j]['POW']

        record_powiat = {'powiat_nazwa' : v_powiat_nazwa, 'powiat_kod' : v_powiat_kod}
        arr_record.append(record_powiat)

        j = j + 1

    obiekt_powiat = {'wojewodztwo_nazwa' : i['wojewodztwo_nazwa'],
                     'wojewodztwo_kod' : i['wojewodztwo_kod'],
                     'wojewodztwo_powiaty' : arr_record}

    arr_powiaty.append(obiekt_powiat)

print("Zakończono pobieranie powiatów!")

# ------------------------------------------------------
# POBRANIE LISTY GMIN
# ------------------------------------------------------

arr_gminy = []
for i in arr_powiaty:
    v_wojewodztwa_kod = i['wojewodztwo_kod']
    v_wojewodztwa_nazwa = i['wojewodztwo_nazwa']

    arr_powiaty_gmina = []
    for j in i['wojewodztwo_powiaty']:
        v_powiat_nazwa = j['powiat_nazwa']
        v_powiat_kod = j['powiat_kod']

        v_gmina_obiekt = service.PobierzListeGmin(v_wojewodztwa_kod, v_powiat_kod, v_curr_date)

        v_dl_obiektu_gmina = len(v_gmina_obiekt)

        v_gminy_w_powiecie_record = []
        z = 0
        while z < v_dl_obiektu_gmina:
            v_gmina_nazwa = v_gmina_obiekt[z]['NAZWA']
            v_gmina_typ = v_gmina_obiekt[z]['NAZWA_DOD']
            v_gmina_kod = v_gmina_obiekt[z]['GMI']

            v_gmina_record = {'gmina_powiat_nazwa' : v_powiat_nazwa,
                              'gmina_powiat_kod': v_powiat_kod,
                              'gmina_nazwa' : v_gmina_nazwa,
                              'gmina_typ' : v_gmina_typ,
                              'gmina_kod' : v_gmina_kod}

            v_gminy_w_powiecie_record.append(v_gmina_record)

            z = z + 1

        record_do_arr_powiaty = {'wojewodztwo_powiaty' : i['wojewodztwo_powiaty'],
                                'wojewodztwo_gminy' : v_gminy_w_powiecie_record}

        arr_powiaty_gmina.append(record_do_arr_powiaty)

    record_do_arr_gminy_f = {
        'wojewodztwo_kod': v_wojewodztwa_kod,
        'wojewodztwo_nazwa': v_wojewodztwa_nazwa,
        'wojewodztwo_powiaty_gminy' : arr_powiaty_gmina
    }

    arr_gminy.append(record_do_arr_gminy_f)

print("Zakończono pobieranie gmin!")

# ------------------------------------------------------
# UKŁADANIE TABELI Z:
# -> województwami
# -> powiatami
# -> gminami
# -> miejscowosc
# ------------------------------------------------------

arr_miejscowosci_w_gminach = []
for i in arr_gminy:
    for j in i['wojewodztwo_powiaty_gminy']:
        for z in j['wojewodztwo_gminy']:
            if (z['gmina_typ'] == "gmina wiejska"
                    or z['gmina_typ'] == "gmina miejsko-wiejska"
                    or z['gmina_typ'] == "gmina miejska"):

                v_miejscowosc_obiekt = (service.PobierzListeMiejscowosciWGminie
                                        (i['wojewodztwo_nazwa'],
                                         z['gmina_powiat_nazwa'],
                                         z['gmina_nazwa'],
                                         v_curr_date))
                v_miejscowosc_obiekt_dlugosc = len(v_miejscowosc_obiekt)
                y = 0

                while y < v_miejscowosc_obiekt_dlugosc:
                    miejsc_GmiRodzaj = v_miejscowosc_obiekt[y]['GmiRodzaj']
                    miejsc_GmiSymbol = v_miejscowosc_obiekt[y]['GmiSymbol']
                    miejsc_Gmina = v_miejscowosc_obiekt[y]['Gmina']
                    miejsc_Nazwa = v_miejscowosc_obiekt[y]['Nazwa']
                    miejsc_PowSymbol = v_miejscowosc_obiekt[y]['PowSymbol']
                    miejsc_Powiat = v_miejscowosc_obiekt[y]['Powiat']
                    miejsc_Symbol = v_miejscowosc_obiekt[y]['Symbol']
                    miejsc_WojSymbol = v_miejscowosc_obiekt[y]['WojSymbol']
                    miejsc_Wojewodztwo = v_miejscowosc_obiekt[y]['Wojewodztwo']

                    record = {
                        'wojewodztwo_kod' : i['wojewodztwo_kod']
                        ,'wojewodztwo_nazwa' : i['wojewodztwo_nazwa']
                        ,'powiat_nazwa' : z['gmina_powiat_nazwa']
                        ,'powiat_kod' : z['gmina_powiat_kod']
                        ,'gmina_typ' : z['gmina_typ']
                        ,'gmina_kod' : z['gmina_kod']
                        ,'gmina_nazwa' : z['gmina_nazwa']
                        ,'miejsc_GmiRodzaj' : miejsc_GmiRodzaj
                        ,'miejsc_GmiSymbol' : miejsc_GmiSymbol
                        ,'miejsc_Gmina' : miejsc_Gmina
                        ,'miejsc_Nazwa': miejsc_Nazwa
                        ,'miejsc_PowSymbol': miejsc_PowSymbol
                        ,'miejsc_Powiat': miejsc_Powiat
                        ,'miejsc_Symbol': miejsc_Symbol
                        ,'miejsc_WojSymbol': miejsc_WojSymbol
                        ,'miejsc_Wojewodztwo': miejsc_Wojewodztwo
                    }

                    arr_miejscowosci_w_gminach.append(record)
                    y = y + 1

print("Zakończono pobieranie miejscowości!")

# ------------------------------------------------------
# UKŁADANIE TABELI Z:
# -> województwami
# -> powiatami
# -> gminami
# -> miejscowosc
# -> ulica
# ------------------------------------------------------

numer_rekord = 1
arr_finalny_zbior = []
for i in arr_miejscowosci_w_gminach:
    v_ulice_w_miejscowosci = (service.PobierzListeUlicDlaMiejscowosci
                                (
                                    i['wojewodztwo_kod'],
                                     i['powiat_kod'],
                                     i['gmina_kod'],
                                     i['miejsc_GmiRodzaj'],
                                     i['miejsc_Symbol'],
                                     1,
                                     0,
                                     v_curr_date
                                )
                              )

    if str(type(v_ulice_w_miejscowosci)) == "<class 'NoneType'>":
        arr_finalny_zbior_record = [{
            'id': numer_rekord,
            'data_generacji': str(datetime.now()),
            'wojewodztwo_nazwa': i['wojewodztwo_nazwa'],
            'powiat_nazwa': i['powiat_nazwa'],
            'gmina_nazwa': i['gmina_nazwa'],
            'gmina_typ': i['gmina_typ'],
            'miejscowosc_nazwa': i['miejsc_Nazwa'],
            'ulica_cecha': '',
            'ulica_nazwa': i['miejsc_Nazwa']
        }]

        arr_finalny_zbior.append(arr_finalny_zbior_record)
        numer_rekord = numer_rekord + 1
    else:
        v_dlugosc_obiektu_ulica = len(v_ulice_w_miejscowosci)

        j = 0
        while j < v_dlugosc_obiektu_ulica:

            if str(v_ulice_w_miejscowosci[j]['Nazwa2']) != "None":
                v_ulica_nazwa = v_ulice_w_miejscowosci[j]['Nazwa1'] + ' ' + v_ulice_w_miejscowosci[j]['Nazwa2']
            else:
                v_ulica_nazwa = v_ulice_w_miejscowosci[j]['Nazwa1']

            arr_finalny_zbior_record = [{
                'id' : numer_rekord,
                'data_generacji': str(datetime.now()),
                'wojewodztwo_nazwa': i['wojewodztwo_nazwa'],
                'powiat_nazwa': i['powiat_nazwa'],
                'gmina_nazwa': i['gmina_nazwa'],
                'gmina_typ': i['gmina_typ'],
                'miejscowosc_nazwa': i['miejsc_Nazwa'],
                'ulica_cecha': v_ulice_w_miejscowosci[j]['Cecha'],
                'ulica_nazwa': v_ulica_nazwa
            }]
            arr_finalny_zbior.append(arr_finalny_zbior_record)
            numer_rekord = numer_rekord + 1
            j = j + 1

print("Zakończono pobieranie ulic!")

# ------------------------------------------------------
# ZAŁADUJ DO TABELI
# ------------------------------------------------------

for i in arr_finalny_zbior:
    client.insert_rows(table_id, i)

print("Skutecznie zasilono tabelę tab_teryt_miejscowosci!")