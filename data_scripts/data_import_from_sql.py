# =====================================================================================
#  OPIS DANYCH UŻYWANYCH W PROJEKCIE
#  Źródło 1: IMGW-PIB, dane terminowe SYNOP, stacja Kraków-Balice (kod 12566),
#  pliki raw_data/IMGW_PIB_dane_terminowe_SYNOP/s_t_566_*.csv (bez nagłówka, kodowanie cp1250).
#  Pełny opis wszystkich 107 kolumn pliku CSV: raw_data/IMGW_PIB_dane_terminowe_SYNOP/s_t_format.txt.
#  Źródło 2: GIOŚ, bank danych pomiarowych – godzinowe stężenia PM10 w Krakowie,
#  pliki raw_data/GIOŚ_PM10/RRRR_PM10_1g.xlsx (tabela GIOS_PM10 w bazie, skrypt import_GIOS_to_sql.py).
# =====================================================================================
#
# Funkcja data_import() (niżej w tym pliku) zwraca tabelę df z 20 kolumnami, lata 2001–2025, co 1 h:
#   - kolumny 1–16 pochodzą z plików CSV IMGW (tabela IMGW w bazie, schema.sql),
#   - kolumny 17–18 wylicza baza (widok IMGW_cechy w schema.sql),
#   - kolumnę 19 dodaje funkcja data_import() podczas czyszczenia danych,
#   - kolumna 20 pochodzi z GIOŚ (tabela GIOS_PM10, dołączana w widoku IMGW_cechy).
#
# Nr kolumny = numer kolumny w plikach s_t_566_*.csv liczony OD 0, tak jak indeks w pandas
#              (df.iloc[:, nr]). W Excelu kolumna ma numer o 1 większy (A = 1).
# Status     = kolumna ze statusem pomiaru: "8" = brak pomiaru (-> NULL w bazie),
#              "9" = brak zjawiska (np. brak opadu -> 0), pusty = pomiar poprawny; "-" = pole nie ma statusu.
#
#  KOLUMNY Z PLIKÓW CSV IMGW
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
#  14. | Wysokość podstawy chmur [kod]         | HPOD  |   6        | WHPOD  (7)
#  15. | Ciśnienie na poziomie morza           | PPPM  |  43        | WPPPM  (44)
#  16. | Opad za 6 godzin                      | WO6G  |  48        | WWO6G  (49)
#
#  KOLUMNY WYLICZANE (nie ma ich w plikach CSV)
#  Lp. | Parametr                              | Skrót              | Skąd się bierze
#  ----+---------------------------------------+--------------------+-----------------------------
#  17. | Deficyt punktu rosy                   | DEFICYT            | widok IMGW_cechy (schema.sql)
#  18. | Zmiana temperatury za 3 h             | DT_3H              | widok IMGW_cechy (schema.sql)
#  19. | Niebo niewidoczne (flaga 0/1)         | NIEBO_NIEWIDOCZNE  | funkcja data_import()
#
#  KOLUMNY Z GIOŚ (inne źródło niż IMGW, osobna tabela w bazie)
#  Lp. | Parametr                              | Skrót | Skąd się bierze
#  ----+---------------------------------------+-------+------------------------------------------------
#  20. | Stężenie pyłu PM10                    | PM10  | tabela GIOS_PM10 (import_GIOS_to_sql.py),
#      |                                       |       | dołączana w widoku IMGW_cechy (schema.sql)
#
#  Z pierwotnej listy usunięto TG05 (temperatura gruntu), USLN (usłonecznienie) i ROSW (rosa) –
#  w latach 2001–2025 są prawie puste (TG05: tylko 2011–2015 i część 2025, USLN: prawie tylko 2025,
#  ROSW: dopiero od kwietnia 2015 r.).
#
#
# -------------------------------------------------------------------------------------
#  OPIS KAŻDEJ ZMIENNEJ: co to jest, w jakich jednostkach, jak czytać kody
#  (zakresy wartości sprawdzone w danych 2001–2025)
# -------------------------------------------------------------------------------------
#
#  1–4. ROK, MC, DZ, GG – CZAS OBSERWACJI
#       Rok, miesiąc (1–12), dzień miesiąca (1–31), godzina (0–23).
#       Godzina jest w czasie UTC (standard depesz SYNOP), czyli bez czasu letniego.
#       Czas polski = UTC + 1 h zimą, UTC + 2 h latem.
#       Od 2001 r. obserwacje są co 1 h (24 wiersze na dobę).
#
#  5.   WID – WIDZIALNOŚĆ [kod 0–9]
#       Największa odległość, z której obserwator widzi i rozpoznaje obiekt.
#       Zapisana kodem, który oznacza PRZEDZIAŁ odległości:
#           kod:  0      1        2        3         4        5        6         7          8          9
#           od:   0 m    50 m     200 m    500 m     1 km     2 km     4 km      10 km      20 km      50 km
#           do:   50 m   200 m    500 m    1000 m    2 km     4 km     10 km     20 km      50 km      i więcej
#       (przedziały sprawdzone na WIDO w metrach z lat 2011–2025; kod 0 w danych nie występuje)
#       MGŁA = WID <= 3, czyli widzialność < 1000 m – to jest ETYKIETA naszych modeli.
#       Dlaczego kod, a nie metry: WIDA (automat, kolumna 19) i WIDO (obserwator, kolumna 17)
#       są dopiero od 2011 r., a WIDA brakuje w 2024 r. i w części 2025 r. WID jest we wszystkich latach.
#
#  6.   POGB – POGODA BIEŻĄCA [kod 00–99, międzynarodowa tabela WMO "ww"]
#       Opis tego, co obserwator widzi w chwili obserwacji. Najważniejsze grupy kodów:
#           00–03  brak zjawisk (01 chmury zanikają, 02 bez zmian, 03 chmury narastają)
#           04–05  dym, zmętnienie (smog, pył) – widzialność ograniczona przez suche cząstki
#           10     zamglenie – widzialność >= 1 km, wilgotne powietrze (często "przedsionek" mgły)
#           11–12  płytka mgła przy ziemi (płatami / ciągła)
#           13, 17 błyskawice / burza bez opadu
#           20–29  zjawisko w OSTATNIEJ godzinie, ale nie teraz (np. 28 = mgła w ostatniej godzinie)
#           36     zamieć śnieżna niska
#           40–49  MGŁA:
#                  40 mgła w oddali (nie na stacji), 41 mgła płatami,
#                  42/43 mgła rzednie, 44/45 bez zmian, 46/47 mgła powstała lub gęstnieje,
#                  48/49 mgła osadzająca szadź;
#                  kody parzyste = niebo widoczne, nieparzyste = niebo niewidoczne
#           50–59  mżawka,  60–69 deszcz,  70–79 śnieg,  80–99 przelotne opady i burze
#       To KOD, a nie liczba – "46" nie jest "większe" od "10". Dla modelu lepiej zamienić
#       go na flagi grup (np. czy jest mgła 40–49, czy jest zamglenie 10).
#
#  7.   TEMP – TEMPERATURA POWIETRZA [°C]
#       Mierzona na wysokości 2 m nad gruntem, w klatce meteorologicznej. Zakres w danych: -26,5 … 37,2.
#
#  8.   TPTR – TEMPERATURA PUNKTU ROSY [°C]
#       Temperatura, do której trzeba ochłodzić powietrze, żeby para wodna zaczęła się skraplać.
#       Zawsze <= TEMP. Im mniejsza różnica TEMP − TPTR (kolumna DEFICYT), tym bliżej do
#       nasycenia i do mgły. Zakres w danych: -29,1 … 23,4.
#
#  9.   WLGW – WILGOTNOŚĆ WZGLĘDNA [%]
#       Ile pary wodnej jest w powietrzu w stosunku do maksimum możliwego w tej temperaturze.
#       100% = nasycenie. Mgła pojawia się zwykle przy 95–100%. Zakres w danych: 9 … 100.
#
#  10.  FWR – PRĘDKOŚĆ WIATRU [m/s]
#       Średnia prędkość wiatru (liczby całkowite). Zakres w danych: 0 … 22.
#       0 = cisza. Słaby wiatr (ok. 0,5–3 m/s) sprzyja mgle radiacyjnej.
#
#  11.  KRWR – KIERUNEK WIATRU [stopnie, 0–360]
#       Kierunek, Z KTÓREGO wieje wiatr, mierzony zgodnie z ruchem wskazówek zegara od północy:
#           90 = wiatr ze wschodu, 180 = z południa, 270 = z zachodu, 360 = z północy.
#       Wartości specjalne:
#           0   = cisza (zawsze razem z FWR = 0) – kierunku nie ma, to NIE jest "północ",
#           999 = wiatr zmienny (kierunek się zmienia, nie da się go określić).
#       Dla modelu lepiej zamienić na składowe u, v (bo 359° i 1° to prawie ten sam kierunek).
#
#  12.  NOG – ZACHMURZENIE OGÓLNE [oktanty, 0–8]
#       Jaka część nieba jest zakryta chmurami, w ósmych częściach:
#           0 = niebo bezchmurne, 4 = połowa nieba zakryta, 8 = całe niebo zakryte.
#       Wartość specjalna: 9 = niebo niewidoczne (zwykle przez mgłę) – to NIE jest "9 oktantów".
#       W df z data_import(): 9 jest zamienione na 8, a informację przechowuje kolumna NIEBO_NIEWIDOCZNE.
#
#  13.  CLCM – ZACHMURZENIE NISKIE [oktanty, 0–8]
#       Ilość chmur piętra niskiego (np. stratus, cumulus); gdy ich nie ma – chmur piętra średniego.
#       Skala jak w NOG: 0 = brak, 8 = całe niebo. 9 = niebo niewidoczne.
#
#  14.  HPOD – WYSOKOŚĆ PODSTAWY CHMUR [kod 0–9]
#       Wysokość nad gruntem, na której zaczyna się najniższa warstwa chmur. Kod oznacza przedział:
#           kod:  0      1       2        3        4        5         6          7          8          9
#           od:   0 m    50 m    100 m    200 m    300 m    600 m     1000 m     1500 m     2000 m     2500 m
#           do:   50 m   100 m   200 m    300 m    600 m    1000 m    1500 m     2000 m     2500 m     i więcej / brak chmur
#       Brak wartości ("/" w pliku, NULL w bazie) = niebo niewidoczne (NOG = 9), zwykle przez mgłę.
#       W df z data_import(): brak jest zamieniony na 0 (chmura przy ziemi), a odróżnia go flaga NIEBO_NIEWIDOCZNE.
#       Dlaczego kod, a nie metry: HPON (metry) jest dopiero od 2011 r., HPOD jest we wszystkich latach.
#       Niska podstawa (kody 0–2) przy dużym zachmurzeniu to niski stratus, który może opaść i dać mgłę.
#
#  15.  PPPM – CIŚNIENIE NA POZIOMIE MORZA [hPa]
#       Ciśnienie atmosferyczne przeliczone ("zredukowane") na poziom morza, żeby dało się je
#       porównywać między stacjami na różnych wysokościach. Zakres w danych: 975,3 … 1051,4.
#       Wysokie ciśnienie (wyż) = słaby wiatr, bezchmurne noce, inwersja – warunki sprzyjające mgle.
#
#  16.  WO6G – OPAD ZA 6 GODZIN [mm]
#       Suma opadu (deszcz, śnieg przeliczony na wodę) z POPRZEDNICH 6 godzin. 1 mm = 1 litr na m².
#       Podawana TYLKO o 00, 06, 12 i 18 UTC – w pozostałych godzinach jest pusta (NULL).
#       Status "9" = nie padało -> 0 mm. Zakres w danych: 0 … 63,1.
#       W df z data_import(): puste godziny są uzupełnione ostatnią znaną wartością (ffill),
#       czyli w każdej godzinie jest "opad z ostatniego zakończonego 6-godzinnego okresu".
#
#  17.  DEFICYT – DEFICYT PUNKTU ROSY [°C]
#       Liczony w bazie (widok IMGW_cechy) jako TEMP − TPTR, zaokrąglony do 0,1 °C.
#       Mówi, o ile stopni trzeba jeszcze ochłodzić powietrze, żeby osiągnęło nasycenie:
#           0 = powietrze nasycone (mgła możliwa), 1–2 °C = blisko nasycenia, > 5 °C = powietrze suche.
#       Zwykle najważniejsza pojedyncza cecha dla prognozy mgły.
#
#  18.  DT_3H – ZMIANA TEMPERATURY ZA 3 GODZINY [°C]
#       Liczona w bazie (widok IMGW_cechy) jako TEMP teraz − TEMP 3 godziny wcześniej.
#           ujemna = powietrze się ochładza (np. wieczorem i w nocy – może zbliżać się do punktu rosy),
#           dodatnia = powietrze się ogrzewa (np. po wschodzie Słońca – mgła zwykle się rozprasza).
#       UWAGA: SQL cofa się o 3 WIERSZE, a nie o 3 godziny – to to samo tylko dlatego, że od 2001 r.
#       nie brakuje żadnej godziny. Pierwsze 3 godziny 2001 r. mają brak (NaN), bo nie ma danych sprzed nich.
#
#  19.  NIEBO_NIEWIDOCZNE – FLAGA [0/1]
#       Dodawana w funkcji data_import() (nie ma jej w bazie).
#           1 = obserwator nie widzi nieba (w danych źródłowych NOG = 9 i brak HPOD), zwykle przez mgłę,
#           0 = niebo widoczne.
#       Przechowuje informację, która ginie po zamianie NOG 9 -> 8 i HPOD brak -> 0.
#       To NIE jest etykieta mgły: obejmuje tylko ok. 28% godzin z mgłą (przy płytkiej mgle niebo często widać).
#
#  20.  PM10 – STĘŻENIE PYŁU ZAWIESZONEGO PM10 [µg/m³]
#       Masa cząstek o średnicy do 10 µm w 1 m³ powietrza. Źródło: GIOŚ, nie IMGW.
#       Wartość = średnia z dwóch krakowskich stacji: Al. Krasińskiego (centrum, przy ruchliwej ulicy)
#       i ul. Bulwarowej (Nowa Huta) – z tych, które w danej godzinie mają pomiar.
#       Tylko te dwie stacje mierzą co godzinę przez cały okres 2003–2025 (Krasińskiego nie ma w 2022 r.,
#       wtedy PM10 = sama Bulwarowa). W bazie, w tabeli GIOS_PM10, są też obie stacje osobno
#       (PM10_KRAS, PM10_BULW) – do df trafia tylko średnia.
#       Czas: GIOŚ podaje czas CET (UTC+1) i godzinę KOŃCA uśredniania; w bazie jest to przeliczone na UTC,
#       więc PM10 w wierszu o godzinie GG = średnia z godziny GG−1 … GG UTC (tuż przed obserwacją IMGW).
#       Braki (NaN): cały 2001 i 2002 r. (GIOŚ ma wtedy tylko średnie dobowe) oraz ok. 1,5% godzin
#       2003–2025 (awarie obu stacji naraz). Nie uzupełniamy ich – drzewa (boosting) radzą sobie z NaN.
#       Zakres w danych: 1 … 847,5. Norma dobowa: 50 µg/m³.
#       Dlaczego ważne dla mgły: cząstki pyłu są jądrami kondensacji, na których skrapla się para wodna,
#       a wysokie PM10 zimą oznacza słaby wiatr i inwersję – te same warunki sprzyjają mgle.
#       W sezonie IX–III średnie PM10 przy mgle to ok. 111 µg/m³, bez mgły ok. 64 µg/m³.



# =====================================================================================
#  PRZYGOTOWANIE DANYCH DO TRENINGU
#  Wczytuje widok IMGW_cechy z bazy, uzupełnia braki i poprawia wartości specjalne IMGW.
#  Uruchamianie (z dowolnego folderu):  python data_scripts/data_import_from_sql.py
# =====================================================================================


import sqlite3
import pandas as pd
from pathlib import Path



def data_import():
    # =====================================================================================
    #  1. WCZYTANIE DANYCH Z BAZY
    # =====================================================================================
    # Otwieramy bazę baza.db tylko do odczytu (mode=ro), żeby przypadkiem niczego w niej nie zmienić,
    # i wczytujemy widok IMGW_cechy do tabeli pandas (DataFrame).
    #
    # SELECT * FROM IMGW_cechy zwraca:
    # - wszystkie kolumny z tabeli IMGW (dzięki SELECT * w widoku),
    # - dwie wyliczone kolumny: DEFICYT (T − Td) i DT_3H (zmiana temperatury za 3 h),
    # - kolumnę PM10 z tabeli GIOS_PM10 (dane GIOŚ, dołączone po dacie i godzinie),
    # - tylko wiersze z lat 2001 i późniejszych.
    path = Path(__file__).resolve().parent / "baza.db"     # baza.db leży obok tego pliku, w data_scripts/
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    df = pd.read_sql_query("SELECT * FROM IMGW_cechy", connection)
    connection.close()


    # =====================================================================================
    #  2. OPAD ZA 6 GODZIN (WO6G) – UZUPEŁNIENIE GODZIN BEZ POMIARU
    # =====================================================================================
    # WO6G to ZMIERZONA suma opadu z POPRZEDNICH 6 h, podawana tylko o 00, 06, 12 i 18 UTC.
    # ffill przepisuje ostatnią znaną wartość W DÓŁ, na kolejne 5 godzin (np. wartość z 06 trafia na 07–11).
    # Nie interpolujemy: wartość z 12 UTC znamy dopiero o 12:00, więc interpolacja zaglądałaby w przyszłość.
    df["WO6G"] = df["WO6G"].ffill()


    # =====================================================================================
    #  3. NIEBO NIEWIDOCZNE (NOG = 9) – FLAGA, PODSTAWA CHMUR (HPOD) I ZACHMURZENIE (NOG)
    # =====================================================================================
    # Gdy obserwator nie widzi nieba (najczęściej przez mgłę), IMGW zapisuje:
    #   - NOG  = 9    (to NIE jest "9 oktantów" – skala zachmurzenia ma tylko 0–8),
    #   - HPOD = brak (NaN) – podstawy chmur nie da się wtedy zmierzyć.
    # W danych 2001–2025 to 1796 godzin; w 1761 z nich obserwator notuje mgłę (POGB 40–49).
    # To NIE są zgubione pomiary, tylko opis stanu w chwili t, więc tych wierszy nie usuwamy
    # i nie przepisujemy wartości z sąsiednich godzin (ffill/interpolacja byłyby fizycznie błędne).
    #
    # KOLEJNOŚĆ MA ZNACZENIE: flagę trzeba utworzyć PRZED zamianą NOG 9 -> 8,
    # bo potem nie byłoby już po czym rozpoznać tych godzin.

    # 3a. Flaga: nowa kolumna 0/1 – 1 = niebo niewidoczne (NOG = 9), 0 = niebo widoczne.
    #     Przechowuje informację, którą tracimy w krokach 3b i 3c.
    #     UWAGA: to NIE jest etykieta mgły – obejmuje tylko ok. 28% godzin z mgłą
    #     (1761 z 6263 godzin z POGB 40–49); przy płytkiej mgle niebo często widać.
    df["NIEBO_NIEWIDOCZNE"] = (df["NOG"] == 9).astype(int)

    # 3b. HPOD: brak -> 0. Kod 0 = podstawa chmur poniżej 50 m, czyli "chmura leży przy ziemi",
    #     co fizycznie najlepiej opisuje niebo zasłonięte mgłą.
    #     (HPOD to wysokość PODSTAWY CHMUR, nie widzialność – widzialność jest w kolumnie WID.)
    #     Kod 0 występuje też naturalnie (bardzo niska chmura) – odróżnia je flaga z kroku 3a.
    df["HPOD"] = df["HPOD"].fillna(0)

    # 3c. NOG: 9 -> 8. Niebo zasłonięte traktujemy jak całkowite zachmurzenie (8 oktantów),
    #     żeby model nie widział "9" jako "więcej chmur niż pełne zachmurzenie".
    df.loc[df["NOG"] == 9, "NOG"] = 8


    # =====================================================================================
    #  4. PM10 – PRZENIESIENIE NA KONIEC TABELI
    # =====================================================================================
    # PM10 pochodzi z innego źródła (GIOŚ), więc stawiamy ją jako ostatnią kolumnę (nr 20).
    # Braków (NaN) celowo NIE uzupełniamy – patrz opis kolumny 20 na górze pliku.
    df["PM10"] = df.pop("PM10")      # pop wyjmuje kolumnę z tabeli, przypisanie dokleja ją na końcu

    return df




if __name__ == "__main__":
    df = data_import()          # wywołujemy funkcję i zapisujemy zwróconą tabelę

    # =====================================================================================
    #  5. KONTROLA – ROZMIAR TABELI I BRAKI DANYCH
    # =====================================================================================
    print(df.shape)             # rozmiar tabeli: (liczba wierszy, liczba kolumn)
    print(df.isna().sum())      # liczba braków (NaN) w każdej kolumnie

    print(df.iloc[7640,:])





