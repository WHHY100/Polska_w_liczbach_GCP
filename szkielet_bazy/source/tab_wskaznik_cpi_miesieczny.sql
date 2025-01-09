create table tab_wskaznik_cpi_miesieczny
(
    wskaznik_data    DATE    not null options (description ='data wskaźnika'),
    wskaznik_wartosc FLOAT64 not null options (description ='wskaźnik wzrostu cen w porównaniu do poprzedniego miesiąca')
);

