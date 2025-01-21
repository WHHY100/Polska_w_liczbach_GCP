#----------------------------------------------------------------------
# IMPORT PLIKÓW
#----------------------------------------------------------------------

import zasilenie_bdl_wynagrodzenia_wojewodztwa
import zasilenie_dbw_miesieczna_inflacja
import zasilenie_dbw_roczna_inflacja
import zasilenie_nbp_ceny_zlota
import zasilenie_nbp_kursy_walut
import zasilenie_bdl_wynagrodzenia_polska
import zasilenie_bdl_mieszkania_wojewodztwa
import zasilenie_bdl_mieszkania_polska
import zasilenie_bld_sr_cena_metra_kwadratowego
import export_danych_do_csv

#----------------------------------------------------------------------
# WYWOŁANIE ZASILEŃ
#----------------------------------------------------------------------

zasilenie_bdl_wynagrodzenia_wojewodztwa.fnc_zasilenie_bdl_wynagrodzenia_wojewodztwa()
zasilenie_dbw_miesieczna_inflacja.fnc_zasilenie_dbw_miesieczna_inflacja()
zasilenie_dbw_roczna_inflacja.fnc_zasilenie_dbw_roczna_inflacja()
zasilenie_nbp_ceny_zlota.fnc_zasilenie_nbp_ceny_zlota()
zasilenie_nbp_kursy_walut.fnc_zasilenie_nbp_kursy_walut()
zasilenie_bdl_wynagrodzenia_polska.fnc_zasilenie_bdl_wynagrodzenia_polska()
zasilenie_bdl_mieszkania_wojewodztwa.fnc_zasilenie_bdl_mieszkania_wojewodztwa()
zasilenie_bdl_mieszkania_polska.fnc_zasilenie_bdl_mieszkania_polska()
zasilenie_bld_sr_cena_metra_kwadratowego.zasilenie_bld_sr_cena_metra_kwadratowego()

#----------------------------------------------------------------------
# WYWOŁANIE EKSPORTU
#----------------------------------------------------------------------

export_danych_do_csv.fnc_export_danych_do_csv()