#----------------------------------------------------------------------
# IMPORT PLIKÓW
#----------------------------------------------------------------------

import zasilenie_bdl_wynagrodzenia_wojewodztwa
import zasilenie_dbw_miesieczna_inflacja
import zasilenie_dbw_roczna_inflacja
import zasilenie_nbp_ceny_zlota
import zasilenie_nbp_kursy_walut
import export_danych_do_csv
import zasilenie_bdl_wynagrodzenia_polska

#----------------------------------------------------------------------
# WYWOŁANIE ZASILEŃ
#----------------------------------------------------------------------

zasilenie_bdl_wynagrodzenia_wojewodztwa.fnc_zasilenie_bdl_wynagrodzenia_wojewodztwa()
zasilenie_dbw_miesieczna_inflacja.fnc_zasilenie_dbw_miesieczna_inflacja()
zasilenie_dbw_roczna_inflacja.fnc_zasilenie_dbw_roczna_inflacja()
zasilenie_nbp_ceny_zlota.fnc_zasilenie_nbp_ceny_zlota()
zasilenie_nbp_kursy_walut.fnc_zasilenie_nbp_kursy_walut()
zasilenie_bdl_wynagrodzenia_polska.fnc_zasilenie_bdl_wynagrodzenia_polska()

#----------------------------------------------------------------------
# WYWOŁANIE EKSPORTU
#----------------------------------------------------------------------

export_danych_do_csv.fnc_export_danych_do_csv()