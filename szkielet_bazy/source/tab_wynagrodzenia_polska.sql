create table tab_wynagrodzenia_polska
(
    data_generacji        TIMESTAMP not null,
    wynagrodzenia_rok     INT64     not null,
    wynagrodzenia_wartosc FLOAT64   not null,
    wynagrodzenia_waluta  STRING    not null
);

