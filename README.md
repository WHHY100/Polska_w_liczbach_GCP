### Opis projektu
___
Celem projektu jest stworzenie hurtowni danych zawierającej statystyki dotyczące Polski. 
Zbiory danych będą sukcesywnie rozbudowywane w trakcie realizacji projektu, 
a wszystkie dostępne informacje będzie można pobrać z katalogu „eksport_danych”. 
Dane są przechowywane w środowisku Google BigQuery, a wszystkie skrypty zostały opracowane z 
myślą o tej technologii. Jednocześnie, aby nie ograniczać dostępu do danych wyłącznie do 
użytkowników określonej platformy, udostępniam je w formacie CSV, co pozwala na ich import do 
dowolnych systemów zarządzania danymi.

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
