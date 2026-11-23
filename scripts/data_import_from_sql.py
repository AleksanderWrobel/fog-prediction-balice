# Data import


# Najważniejsze dane, które należy zgrać do trenowania pierwszych modeli (lata 2001–2025) to:
# IMGW:
#
# Nr kolumny = numer kolumny w plikach s_t_566_*.csv, liczony od 1 (tak jak w Excelu: A = 1).
# W Pythonie/pandas indeks jest o 1 mniejszy (usecols=[nr - 1]).
# Status = kolumna ze statusem pomiaru ("8" brak pomiaru, "9" brak zjawiska); "-" = pole nie ma statusu.
#
#  Lp. | Parametr                              | Skrót | Nr kolumny | Status (nr kolumny)
#  ----+---------------------------------------+-------+------------+--------------------
#   1. | Rok                                   | ROK   |   3        | -
#   2. | Miesiąc                               | MC    |   4        | -
#   3. | Dzień                                 | DZ    |   5        | -
#   4. | Godzina (UTC)                         | GG    |   6        | -
#   5. | Widzialność [kod]                     | WID   |  16        | WWID   (17)
#   6. | Pogoda bieżąca                        | POGB  |  53        | -
#   7. | Temperatura powietrza                 | TEMP  |  30        | WTEMP  (31)
#   8. | Temperatura punktu rosy               | TPTR  |  40        | WTPTR  (41)
#   9. | Wilgotność względna                   | WLGW  |  38        | WWLGW  (39)
#  10. | Prędkość wiatru                       | FWR   |  26        | WFWR   (27)
#  11. | Kierunek wiatru                       | KRWR  |  24        | WKRWR  (25)
#  12. | Zachmurzenie ogólne                   | NOG   |  22        | WNOG   (23)
#  13. | Zachmurzenie niskie                   | CLCM  |  55        | WCLCM  (56)
#  14. | Wysokość podstawy chmur (niższej)     | HPON  |   9        | WHPON  (10)
#  15. | Ciśnienie na poziomie morza           | PPPM  |  44        | WPPPM  (45)
#  16. | Opad za 6 godzin                      | WO6G  |  49        | WWO6G  (50)
#  17. | Temperatura gruntu na głębokości 5 cm | TG05  |  78        | WTG05  (79)
#  18. | Usłonecznienie                        | USLN  |  70        | WUSLN  (71)
#  19. | Występowanie rosy                     | ROSW  |  72        | WROSW  (73)
#
# Widzialność: bierzemy WID (kod), a nie WIDA (automat, kolumna 20) ani WIDO (operator, kolumna 18).
# WID jest wypełnione we wszystkich latach 2001–2025, a WIDA/WIDO dopiero od 2011 r.
# (WIDA brak w 2024 r. i w części 2025 r.).
