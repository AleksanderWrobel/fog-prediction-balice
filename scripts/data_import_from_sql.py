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
#   1. | Rok                                   | ROK   |   2        | -
#   2. | Miesiąc                               | MC    |   3        | -
#   3. | Dzień                                 | DZ    |   4        | -
#   4. | Godzina (UTC)                         | GG    |   5        | -
#   5. | Widzialność [kod]                     | WID   |  15        | WWID   (16)
#   6. | Pogoda bieżąca                        | POGB  |  52        | -
#   7. | Temperatura powietrza                 | TEMP  |  29        | WTEMP  (30)
#   8. | Temperatura punktu rosy               | TPTR  |  39        | WTPTR  (40)
#   9. | Wilgotność względna                   | WLGW  |  37        | WWLGW  (38)
#  10. | Prędkość wiatru                       | FWR   |  25        | WFWR   (26)
#  11. | Kierunek wiatru                       | KRWR  |  23        | WKRWR  (24)
#  12. | Zachmurzenie ogólne                   | NOG   |  21        | WNOG   (22)
#  13. | Zachmurzenie niskie                   | CLCM  |  54        | WCLCM  (55)
#  14. | Wysokość podstawy chmur (niższej)     | HPON  |   8        | WHPON  (9)
#  15. | Ciśnienie na poziomie morza           | PPPM  |  43        | WPPPM  (44)
#  16. | Opad za 6 godzin                      | WO6G  |  48        | WWO6G  (49)
#  17. | Temperatura gruntu na głębokości 5 cm | TG05  |  77        | WTG05  (78)
#  18. | Usłonecznienie                        | USLN  |  69        | WUSLN  (70)
#  19. | Występowanie rosy                     | ROSW  |  71        | WROSW  (72)
#
# Widzialność: bierzemy WID (kod), a nie WIDA (automat, kolumna 20) ani WIDO (operator, kolumna 18).
# WID jest wypełnione we wszystkich latach 2001–2025, a WIDA/WIDO dopiero od 2011 r.
# (WIDA brak w 2024 r. i w części 2025 r.).

