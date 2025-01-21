create table tab_mieszkania_ceny_wojewodztwa
(
    data_generacji                  TIMESTAMP not null,
    mieszkania_cena_rok             INT64     not null,
    mieszkania_cena_wojewodztwo     STRING    not null,
    mieszkania_cena_metr_kwadratowy FLOAT64   not null,
    mieszkania_cena_waluta          STRING    not null
);

