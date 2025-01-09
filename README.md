### Opis projektu
___
Celem projektu jest utworzenie hurtowni danych zawierającej dane statystyczne na temat Polski. Zbiory będą rozszerzane wraz z czasem trwania projektu a wszystkie informacje w nim dostępne można pobrać z katalogu "eksport_danych".
Po stronie projektu dane odkładane są w środowisku Google Big Query i wszystkie skrypty są pisane z myślą o tej technologii. Natomiast by nie ograniczać potencjalnych odbiorców od konkretnej platformy, dane udostępniam w formacie CSV tak by można je 
załadować do innych systemów zarządzania danymi.

### Struktura projektu
###### Każdy z podpunktów odpowiada kolejnemu katalogowi.
___
* eksport_danych - w tym katalogu znajdziemy eksportowane dane w formacie CSV
* skrypty_python - w tym katalogu znajdziemy skrypty python użyte w projekcie
* szkielet_bazy - w tym katalogu znajdziemy skrypty tworzące tabele w bazie danych

___
##### Żródła danych:
###### * API GUS [https://api-dbw.stat.gov.pl/apidocs/index.html]
###### * API NBP [https://api.nbp.pl/]
###### Projekt jest tworzony przy pomocy narzędzi:  Google Cloud Platform, Pycharm Community Edition, Data Grip
___
