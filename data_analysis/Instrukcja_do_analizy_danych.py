# =====================================================================================
#  INSTRUKCJA DO ANALIZY DANYCH
#  Ten plik pokazuje, jak dostać się do danych z lat 2001–2025, jak są one zbudowane
#  i jak w spokoju je przeglądać oraz wybierać ich fragmenty.
# =====================================================================================


# =====================================================================================
#  0. KONFIGURACJA ŚRODOWISKA (jednorazowo, przed pierwszym uruchomieniem)
# =====================================================================================
# Potrzebne są:
#   - conda (np. Miniforge: https://github.com/conda-forge/miniforge),
#   - biblioteki: pandas, numpy, matplotlib, openpyxl – są wypisane w pliku environment.yml
#     w głównym folderze projektu. sqlite3 i pathlib są wbudowane w Pythona.
#
# Krok 1. Utworzenie środowiska (w terminalu, w głównym folderze projektu):
#       conda env create -f environment.yml
# Krok 2. Włączenie środowiska (za każdym razem przed pracą):
#       conda activate mgla-balice
# Krok 3. Uruchomienie tego pliku (z dowolnego folderu):
#       python data_analysis/Instrukcja_do_analizy_danych.py
#
# W VS Code: Ctrl+Shift+P -> "Python: Select Interpreter" -> wybrać środowisko "mgla-balice".
#
# Wszystkie dane są w bazie data_scripts/baza.db, która jest w repozytorium – po sklonowaniu
# projektu można od razu z nich korzystać, bez pobierania surowych danych.
#
# UWAGA – NIE ZMIENIAMY baza.db:
#   - z bazy tylko CZYTAMY, przez funkcję data_import() (otwiera bazę tylko do odczytu),
#   - NIE uruchamiamy data_scripts/import_IMGW_to_sql.py ani import_GIOS_to_sql.py
#     i nie wysyłamy baza.db w swoich commitach,
#   - jeśli "git status" pokazuje baza.db jako zmienioną:  git restore data_scripts/baza.db
#   - bazę aktualizuje tylko opiekun projektu; potrzebną zmianę w bazie zgłaszamy jemu.
# Szczegóły i powód: README.md, sekcja "Jak zacząć".


# =====================================================================================
#  1. WCZYTANIE DANYCH
# =====================================================================================
# Żeby dostać się do wszystkich wartości z lat 2001–2025, korzystamy z funkcji data_import()
# z pliku data_scripts/data_import_from_sql.py. Plik leży w innym folderze, więc najpierw
# dopisujemy folder projektu do miejsc, w których Python szuka modułów (sys.path).

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))   # folder projektu

from data_scripts.data_import_from_sql import data_import

df = data_import()

# Teraz wszystkie nasze dane są zapisane w zmiennej df (tabela pandas, czyli DataFrame).
# Nie trzeba importować pandas, żeby używać df.loc, df.iloc, df.shape itd. – to są części
# samego obiektu df. "import pandas as pd" jest potrzebne dopiero do rzeczy typu pd.read_csv(...).


# =====================================================================================
#  2. CO JEST W TABELI df
# =====================================================================================
# Tabela ma 20 kolumn, w każdej jest inna zmienna. Poniżej podsumowanie (przygotowane przez Claude),
# co znajduje się w poszczególnych kolumnach i jak to rozumieć:
#
# Funkcja data_import() zwraca tabelę df z 20 kolumnami, lata 2001–2025, co 1 h:
#   - kolumny 1–16 pochodzą z plików CSV IMGW (tabela IMGW w bazie, schema.sql),
#   - kolumny 17–18 wylicza baza (widok IMGW_cechy w schema.sql),
#   - kolumnę 19 dodaje funkcja data_import() podczas czyszczenia danych,
#   - kolumna 20 (PM10) pochodzi z GIOŚ (tabela GIOS_PM10, dołączana w widoku IMGW_cechy).
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
#  3. NA CO UWAŻAĆ W DANYCH
# =====================================================================================
#  - Czas (GG) jest w UTC, a nie w czasie polskim (Polska = UTC + 1 h zimą, UTC + 2 h latem).
#  - KRWR: 0 = cisza, 999 = wiatr zmienny – nie wolno liczyć z tych wartości zwykłej średniej kierunku.
#  - POGB to KOD, a nie liczba – średnia z POGB nie ma sensu.
#  - CLCM: wartość 9 = niebo niewidoczne (nie jest zamieniana na 8, w odróżnieniu od NOG).
#  - DT_3H ma 3 braki (NaN) na samym początku 2001 r. – to normalne.
#  - PM10 ma braki (NaN) w całym 2001 i 2002 r. (GIOŚ ma wtedy tylko średnie dobowe) i w ok. 1,5% godzin
#    2003–2025. Przy liczeniu np. średniej pandas sam pomija NaN; przy porównaniach lat pamiętaj o 2001–2002.
#  - PM10 pochodzi z Krakowa (Al. Krasińskiego + ul. Bulwarowa), a nie z lotniska – to wskaźnik
#    zanieczyszczenia całego miasta, nie dokładna wartość nad Balicami.
#  - Mgła (to, co przewidujemy) = WID <= 3, czyli widzialność < 1000 m.
#  - Prognozy robimy tylko dla sezonu wrzesień–marzec (patrz punkt 6).


# =====================================================================================
#  4. PIERWSZE SPOJRZENIE NA DANE
# =====================================================================================
print(df.shape)             # rozmiar tabeli: (liczba wierszy, liczba kolumn)
print(df.isna().sum())      # liczba braków (NaN) w każdej kolumnie
print(df.head())            # kilka pierwszych wierszy
print(df.describe())        # dla każdej kolumny: liczba wartości, średnia, min, max, kwartyle
print(df["WID"].value_counts().sort_index())   # ile razy występuje każdy kod widzialności


# =====================================================================================
#  5. WYBIERANIE FRAGMENTÓW TABELI: iloc i loc
# =====================================================================================
# iloc i loc to nie są zwykłe funkcje, tylko tzw. indeksery z biblioteki pandas – dlatego
# piszemy je z nawiasami KWADRATOWYMI, a nie okrągłymi. Oba mają postać:
#       df.iloc[KTÓRE_WIERSZE, KTÓRE_KOLUMNY]
#       df.loc[KTÓRE_WIERSZE, KTÓRE_KOLUMNY]
#
# iloc – wybiera po NUMERZE wiersza/kolumny (liczonym od 0).
# Np. losowa godzina do sprawdzenia – wiersz nr 7640 (":" oznacza "wszystkie kolumny"):
print(df.iloc[7640, :])

# loc – wybiera po WARUNKACH i NAZWACH kolumn (np. konkretny rok, miesiąc, temperatura).

# Wszystkie wiersze tylko z 2002 roku (bez podawania kolumn = wszystkie kolumny):
rok_2002 = df.loc[df["ROK"] == 2002].reset_index(drop=True)
# reset_index(drop=True) numeruje wiersze od nowa, od 0. Bez tego wiersze z 2002 r. zachowałyby
# numery z całej tabeli, czyli zaczynałyby się od 8760 (= 365 * 24 godzin roku 2001).
# drop=True wyrzuca stare numery (bez tego zostałyby zapisane jako dodatkowa kolumna "index").

# Tylko temperatura z 2002 roku:
temperatura_2002 = df.loc[df["ROK"] == 2002, "TEMP"].reset_index(drop=True)

# Temperatura i widzialność dla stycznia z lat 2001, 2002, 2003 i 2004:
x1 = df.loc[(df["ROK"] < 2005) & (df["MC"] == 1), ["TEMP", "WID"]].reset_index(drop=True)
print(x1)

# To samo, ale razem z rokiem, miesiącem, dniem i godziną, żeby wiedzieć, której chwili dotyczy wiersz:
x2 = df.loc[(df["ROK"] < 2005) & (df["MC"] == 1), ["ROK", "MC", "DZ", "GG", "TEMP", "WID"]].reset_index(drop=True)
print(x2)

# ZASADY PISANIA WARUNKÓW w loc:
#   - kilka warunków łączymy znakiem  &  ("i")  albo  |  ("lub"),  ~  oznacza zaprzeczenie ("nie"),
#   - KAŻDY warunek musi być w osobnych nawiasach okrągłych:
#         dobrze:  df.loc[(df["ROK"] < 2005) & (df["MC"] == 1)]
#         źle:     df.loc[df["ROK"] < 2005 & df["MC"] == 1]       -> ValueError
#   - warunki na wiersze oddzielamy od kolumn JEDNYM przecinkiem:
#         źle:     df.loc[df["ROK"] < 2005, df["MC"] == 1, "TEMP"] -> IndexingError: Too many indexers
#   - kilka kolumn podajemy jako LISTĘ w nawiasach kwadratowych:  ["TEMP", "WID"]
#     ("TEMP" + "WID" skleja napisy w "TEMPWID", a takiej kolumny nie ma).
#
# Zmiany we fragmencie wyciętym z df (np. w rok_2002) nie zmieniają samego df – w pandas 3
# taki fragment zachowuje się jak osobna kopia.


# =====================================================================================
#  6. PRZYKŁADY DLA NASZEGO PROJEKTU – MGŁA I SEZON
# =====================================================================================
# Mgła: widzialność < 1000 m, czyli kod WID <= 3. Wynik to kolumna True/False dla każdej godziny.
mgla = df["WID"] <= 3
print("Liczba godzin z mgłą (2001–2025):", mgla.sum())

# Częstość mgły w każdym miesiącu (średnia z True/False = ułamek godzin z mgłą; * 100 = procent):
print((mgla.groupby(df["MC"]).mean() * 100).round(2))

# Tylko sezon, dla którego robimy prognozy: wrzesień–marzec.
# isin([...]) sprawdza, czy wartość jest na liście.
sezon = df.loc[df["MC"].isin([9, 10, 11, 12, 1, 2, 3])].reset_index(drop=True)
print("Godzin w sezonie IX–III:", len(sezon), " w tym z mgłą:", (sezon["WID"] <= 3).sum())
