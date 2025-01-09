create table tab_kursy_walut
(
    data_generacji TIMESTAMP not null,
    data_waluty    DATE      not null,
    waluta_kod     STRING(3) not null,
    waluta_kurs    FLOAT64   not null
);

