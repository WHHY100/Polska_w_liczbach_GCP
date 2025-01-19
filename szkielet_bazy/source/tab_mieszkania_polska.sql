create table tab_mieszkania_polska
(
    data_generacji    TIMESTAMP not null,
    mieszkania_region STRING    not null,
    mieszkania_rok    INT64     not null,
    mieszkania_ilosc  INT64     not null options (description ='ilość mieszkań w Polsce w podziale na region')
);

