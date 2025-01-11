create table tab_wynagrodzenia_wojewodztwa
(
    data_generacji            DATETIME not null,
    wynagrodzenia_wojewodztwo STRING   not null,
    wynagrodzenia_rok         INT64    not null,
    wynagrodzenia_wartosc     FLOAT64  not null options (description ='przeciętna wartość wynagrodzenia w województwie'),
    wynagrodzenia_waluta      STRING   not null
);

