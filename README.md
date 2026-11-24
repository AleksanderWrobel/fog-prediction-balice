# Prognozowanie mgły w rejonie lotniska Kraków-Balice

> Projekt w ramach przedmiotu **Podstawy fizyki środowiska**.
> Cel: model uczenia maszynowego (drzewa decyzyjne), który na podstawie danych meteorologicznych z ostatnich godzin podaje prawdopodobieństwo wystąpienia mgły na lotnisku Kraków-Balice (EPKK) w kolejnych 1–5 godzinach.
> Kluczowym celem projektu jest **porównanie dwóch sposobów prognozy wielohoryzontowej**: pięciu osobnych modeli (po jednym na każdy horyzont) i jednego modelu z pięcioma wyjściami (patrz rozdział 6).

---

## Jak zacząć

1. **Sklonuj repozytorium** i wejdź do jego folderu.
2. **Utwórz środowisko conda** (potrzebna jest conda, np. [Miniforge](https://github.com/conda-forge/miniforge)). Biblioteki (pandas, numpy, matplotlib, openpyxl) są wypisane w `environment.yml`:
   ```bash
   conda env create -f environment.yml
   conda activate mgla-balice
   ```
   W VS Code wybierz to środowisko: `Ctrl+Shift+P` → „Python: Select Interpreter” → `mgla-balice`.
3. **Uruchom instrukcję do analizy danych**. Pokazuje, jak wczytać dane, co jest w każdej kolumnie i jak wybierać fragmenty tabeli:
   ```bash
   python data_analysis/Instrukcja_do_analizy_danych.py
   ```

W każdym własnym skrypcie dane wczytuje się funkcją `data_import()` z `data_scripts/data_import_from_sql.py` (przykład na początku instrukcji).

**Wszystkie dane są w bazie `data_scripts/baza.db`**, która jest w repozytorium. Po sklonowaniu projektu można od razu z nich korzystać, bez pobierania surowych danych.

W bazie są dwie tabele, po jednej na każde źródło, i widok, który je łączy:

| Obiekt w bazie | Co zawiera | Skąd się bierze |
|---|---|---|
| tabela `IMGW` | obserwacje SYNOP z Balic (WID, TEMP, TPTR, wiatr, chmury, …), co 1 h od 2001 r. | `data_scripts/import_IMGW_to_sql.py` |
| tabela `GIOS_PM10` | godzinowe PM10 z dwóch stacji w Krakowie (Al. Krasińskiego, ul. Bulwarowa) i ich średnia, 2003–2025, czas w UTC | `data_scripts/import_GIOS_to_sql.py` |
| widok `IMGW_cechy` | wszystkie godziny IMGW od 2001 r. + cechy wyliczane (`DEFICYT`, `DT_3H`) + kolumna `PM10` z GIOŚ | `data_scripts/schema.sql` |

Funkcja `data_import()` czyta widok `IMGW_cechy` i zwraca tabelę z 20 kolumnami (19 z IMGW i cech wyliczanych + `PM10`). Opis każdej kolumny jest na początku `data_scripts/data_import_from_sql.py` i w instrukcji do analizy danych.

> ⚠️ **Zasada dla członków projektu: nie zmieniamy `baza.db`.**
> - Z bazy **tylko czytamy** – przez funkcję `data_import()`. Otwiera ona bazę w trybie tylko do odczytu, więc nic w niej nie zmienia.
> - **Nie uruchamiamy** `data_scripts/import_IMGW_to_sql.py` ani `data_scripts/import_GIOS_to_sql.py` i nie edytujemy bazy ręcznie. Nawet ponowny import bez zmian w kodzie tworzy nowy plik, który git uzna za zmieniony.
> - **Nie wysyłamy `baza.db` w swoich commitach.** Jeśli `git status` pokazuje ją jako zmienioną, przywróć wersję z repozytorium: `git restore data_scripts/baza.db`.
> - Bazę aktualizuje **tylko jedna osoba – opiekun projektu**. Jeśli potrzebujesz zmiany w bazie (np. nowej kolumny albo cechy w `schema.sql`), zgłoś to opiekunowi. Po aktualizacji wystarczy `git pull`.
>
> Dlaczego: `baza.db` to plik binarny. Gdy dwie osoby wyślą różne wersje, git nie potrafi ich połączyć i jedną z nich trzeba wyrzucić.

Surowe dane (folder `raw_data/`, poza gitem) są potrzebne tylko opiekunowi do odbudowania bazy (linki w rozdziale 11):
- pliki IMGW w `raw_data/IMGW_PIB_dane_terminowe_SYNOP/`, potem `python data_scripts/import_IMGW_to_sql.py` (ok. 7 s),
- pliki GIOŚ `RRRR_PM10_1g.xlsx` w `raw_data/GIOŚ_PM10/`, potem `python data_scripts/import_GIOS_to_sql.py` (ok. 2 min).

Każdy skrypt usuwa i tworzy od nowa tylko swoją tabelę, więc można je uruchamiać w dowolnej kolejności.

### Struktura folderów

| Folder | Zawartość |
|---|---|
| `data_scripts/` | baza danych, jej schemat, import surowych danych i funkcja `data_import()` |
| `data_analysis/` | analizy i wykresy danych, instrukcja do analizy danych |
| `prediction/` | przygotowanie danych do treningu, modele, trening i testy |
| `raw_data/` | surowe pliki IMGW i GIOŚ (tylko lokalnie, poza gitem) |

---

## Spis treści

0. [Jak zacząć](#jak-zacząć)
1. [Źródła danych](#1-źródła-danych)
2. [Zakres przestrzenny](#2-zakres-przestrzenny)
3. [Struktura danych](#3-struktura-danych)
4. [Okno wejściowe modelu](#4-okno-wejściowe-modelu)
5. [Parametry](#5-parametry)
6. [Modele](#6-modele)
7. [Ocena modeli](#7-ocena-modeli)
8. [Zakres sezonowy](#8-zakres-sezonowy)
9. [Plan budowy prognozy](#9-plan-budowy-prognozy)
10. [Pułapki](#10-pułapki-o-których-warto-wiedzieć-od-początku)
11. [Źródła i literatura](#11-źródła-i-literatura)

---

## 1. Źródła danych

| Źródło | Co zawiera | Rozdzielczość | Uwagi |
|---|---|---|---|
| **IMGW-PIB – dane terminowe SYNOP** | Obserwacje ze stacji synoptycznej Kraków-Balice (kod 12566): widzialność, pogoda bieżąca, T, Td, RH, wiatr, chmury, ciśnienie, grunt, śnieg | godzinowa od 2001 r., wcześniej co 3 h | Podstawowe źródło. Archiwum od 1966 r. Opis pól w pliku `s_t_format.txt`. |
| **METAR – Iowa Environmental Mesonet (IEM)** | Depesze lotniskowe EPKK: widzialność, chmury, zjawiska, T, Td, wiatr, ciśnienie | co 30 min | **Etap 2:** źródło godzinowych obserwacji sprzed 2001 r., kiedy IMGW ma krok 3 h. Zasięg archiwum dla EPKK do sprawdzenia. |
| **GIOŚ – jakość powietrza** | **tylko PM10**, średnia ze stacji Kraków, Al. Krasińskiego i Kraków, ul. Bulwarowa | godzinowa (`1g`) od 2003 r.; w 2001–2002 tylko dobowa (`24g`), której nie używamy | **Już w bazie** (tabela `GIOS_PM10`, kolumna `PM10`). Czas w plikach GIOŚ jest w **CET** (UTC+1, bez czasu letniego) – import przelicza go na UTC. |

IMGW-PIB - dane terminowe SYNOP (Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy - dane terminowe surface synoptic observations)

METAR - Iowa Environmental Mesonet (IEM) (Meteorological Aerodrome Report)

GIOŚ - jakość powietrza - (Główny Inspektorat Ochrony Środowiska)

### Etapy zbierania danych

| Etap | Okres | Dane stacyjne | Krok |
|---|---|---|---|
| **1 – pierwsze treningi** | 2001–2025 | wyłącznie **IMGW SYNOP** | 1 h |
| **2 – rozszerzenie wstecz** | lata sprzed 2001 (np. od 1980) | **METAR (IEM)** | 1 h |

- **Etap 1.** Pierwsze treningi opieramy tylko na danych godzinowych IMGW z lat 2001–2025. To 25 sezonów chłodnych bez żadnej interpolacji. METAR na tym etapie byłby w dużej mierze duplikatem, bo pochodzi z tego samego lotniska.
- **Etap 2.** Dopiero w kolejnych podejściach dokładamy lata sprzed 2001. IMGW ma wtedy obserwacje tylko co 3 h, więc żeby zachować krok godzinowy, bierzemy obserwacje z METAR (IEM) zamiast interpolować dane IMGW.
  - **Warunek:** archiwum IEM dla EPKK musi sięgać odpowiednio daleko wstecz. Trzeba to sprawdzić przed rozpoczęciem etapu 2.
  - **Plan awaryjny:** jeśli METAR-ów sprzed 2001 r. nie ma, stosujemy model z krokiem 3 h na pełnym okresie, bez interpolacji.
- GIOŚ dokładamy jako **osobny eksperyment** i mierzymy, o ile poprawia wynik względem modelu na samym IMGW.

---

## 2. Zakres przestrzenny

Dane stacyjne bierzemy **tylko z lotniska w Balicach**. Pozostałe stacje synoptyczne są dość rozrzucone po mapie, a różnice w ukształtowaniu terenu (lotnisko leży w obniżeniu, w pobliżu dolin Wisły i Rudawy) sprawiają, że przenoszenie ich wartości na Balice ma niewielki sens.

> **Doprecyzowanie:** wyjątkiem są dane o jakości powietrza.
> - **GIOŚ** nie ma stacji na lotnisku. Bierzemy **PM10 jako średnią z dwóch stacji w Krakowie: Al. Krasińskiego (centrum) i ul. Bulwarowa (Nowa Huta)** – z tych, które w danej godzinie mają pomiar.
>   - **Dlaczego te stacje:** tylko one mierzą PM10 co godzinę przez cały okres 2003–2025. Pokrycie sprawdzone w plikach GIOŚ:
>
>     | Stacja | Kod (stary → od 2015 r.) | Dane godzinowe |
>     |---|---|---|
>     | Al. Krasińskiego | `MpKrakowWIOSAKra6117` → `MpKrakAlKras` | 2003–2025, **brak całego 2022 r.** |
>     | ul. Bulwarowa | `MpKrakowWIOSBulw6118` → `MpKrakBulwar` | 2003–2025 |
>     | ul. Bujaka | `MpKrakowWIOSBuja6119` → `MpKrakBujaka` | od 2010 r. |
>     | Złoty Róg (najbliżej Balic) | `MpKrakZloRog` | od 2016 r. |
>
>     Średnia z dwóch stacji wypełnia rok 2022 (wtedy PM10 = sama Bulwarowa) i jest mniej wrażliwa na lokalne źródła przy jednej stacji. Złoty Róg leży najbliżej, ale ponad połowa lat treningowych nie miałaby wtedy PM10.
>   - **Ograniczenie:** Al. Krasińskiego to **stacja komunikacyjna** przy ruchliwej ulicy, a Bulwarowa leży w dzielnicy przemysłowej, ok. 20 km od Balic. Bezwzględne stężenia są więc wyższe niż przy lotnisku. Zakładamy, że epizody smogowe przy inwersji mają w Krakowie charakter regionalny, więc **zmienność w czasie** jest podobna jak przy Balicach.
>   - **Do sprawdzenia:** korelacja tej średniej z PM10 ze Złotego Rogu lub z Zabierzowa (`MpZabieWapie`) w latach, w których działają obie serie. Wysoka korelacja uzasadnia ten wybór.
>   - **Kody stacji:** w 2015 r. GIOŚ zmienił kody stacji (tabela wyżej). Skrypt importu łączy stary i nowy kod w jedną serię.
>   - **Czas:** GIOŚ podaje czas CET (UTC+1) i godzinę **końca** uśredniania („01:00” = średnia z 00:00–01:00 CET). Po przeliczeniu na UTC wartość `PM10` w wierszu o godzinie GG to średnia z godziny GG−1 … GG UTC, czyli tuż przed obserwacją IMGW – model nie dostaje informacji z przyszłości.
>
> Sąsiednich stacji nie trzeba by interpolować: w modelu mogłyby być osobnymi cechami (np. widzialność w Katowicach-Pyrzowicach). To możliwe rozszerzenie na później.

---

## 3. Struktura danych

Wszystkie dane wczytujemy do bazy SQL (SQLite) i porządkujemy według daty i godziny. Każdy wiersz odpowiada jednej godzinie i zawiera jak najwięcej wartościowych parametrów:

| czas (UTC) | temperatura [°C] | wilgotność [%] | wysokość Słońca [°] | zachmurzenie [oktanty] | … |
|---|---|---|---|---|---|
| 2005-11-13 07:00 | 8,0 | 93 | 8,3 | 4 | … |

> **Uwagi do struktury:**
> - **Czas zapisujemy w UTC**, jako jedną kolumnę typu timestamp. SYNOP i METAR są w UTC, a czas lokalny ma zmiany czas letni/zimowy, które tworzą dziury i duplikaty. Rok, miesiąc, dzień i godzinę można wyliczyć z timestampu.
> - **Miesiąc zapisujemy liczbą**, nie nazwą (`11`, nie `listopad`).
> - **Zachmurzenie** w SYNOP jest w oktantach (0–8), nie w procentach.
> - **Wysokość Słońca** nie pochodzi z żadnego źródła, wyliczamy ją z daty, godziny i współrzędnych lotniska (np. biblioteką `pvlib` lub `astral`).
> - Układ bazy: **osobna tabela dla każdego źródła** z kluczem czasowym (`ROK`, `MC`, `DZ`, `GG` w UTC), a na nich **widok** (`VIEW`) łączący wszystko w jedną szeroką tabelę cech. Obecnie są tabele `IMGW` i `GIOS_PM10` oraz widok `IMGW_cechy` (rozdział *Jak zacząć*); w etapie 2 dojdzie tabela z METAR. Dzięki temu łatwo dodać nowe źródło bez przebudowy całości.
> - SQLite obsługuje funkcje okna (`LAG`, `AVG(...) OVER`), więc trendy i opóźnienia można liczyć bezpośrednio w SQL.

---

## 4. Okno wejściowe modelu

Do treningu bierzemy **48 kolejnych godzin** wraz ze wszystkimi parametrami dla tych godzin.

Drzewa decyzyjne nie przyjmują sekwencji, tylko płaski wektor cech. Okno 48 h zamieniamy więc na jeden wiersz tabeli: wartości parametrów z wybranych godzin (np. *t*, *t−1*, *t−3*, *t−6*, …), trendy (parametr 22) i proste agregaty z okna (np. minimum, maksimum, średnia). Cały zbiór to macierz o kształcie `(liczba_próbek, liczba_cech)`.

To także pole do eksperymentów: można sprawdzać różne długości okna (np. 24 h, 30 h, 32 h) i porównywać, jak model radzi sobie w zależności od liczby godzin podanych na wejściu.

> **Uwagi:**
> - Okna przesuwamy co godzinę, więc sąsiednie próbki prawie się pokrywają. Przy podziale na zbiory treningowy, walidacyjny i testowy trzeba zostawić **przerwę (≥ 53 h = 48 h wejścia + 5 h horyzontu)** na granicach, żeby żadne okno nie „zaglądało” do innego zbioru.
> - Trzeba zdecydować, co robić z oknami zawierającymi braki danych: odrzucać, uzupełniać czy oznaczać flagą (parametr 27). Gradient boosting (XGBoost, LightGBM) potrafi sam obsłużyć brakujące wartości, więc nie każdą lukę trzeba wypełniać.

---

## 5. Parametry

Priorytet: ★★★ niezbędne · ★★ wyraźnie pomaga · ★ opcjonalne lub do eksperymentów.
W kolumnie „Pole” podane są nazwy z plików IMGW SYNOP lub METAR (IEM).

### Zestaw startowy

Na początek skupiamy się na **najważniejszych parametrach z IMGW**. Pierwsze modele trenujemy tylko na nich, na danych z lat **2001–2025** (podział na zbiory treningowy, walidacyjny i testowy w pułapce 6):

| Lp. | Parametr | Pole IMGW |
|---|---|---|
| 1 | Rok | `ROK` |
| 2 | Miesiąc | `MC` |
| 3 | Dzień | `DZ` |
| 4 | Godzina (UTC) | `GG` |
| 5 | Widzialność [kod] | `WID` |
| 6 | Pogoda bieżąca | `POGB` |
| 7 | Temperatura powietrza | `TEMP` |
| 8 | Temperatura punktu rosy | `TPTR` |
| 9 | Wilgotność względna | `WLGW` |
| 10 | Prędkość wiatru | `FWR` |
| 11 | Kierunek wiatru | `KRWR` |
| 12 | Zachmurzenie ogólne | `NOG` |
| 13 | Zachmurzenie niskie | `CLCM` |
| 14 | Wysokość podstawy chmur [kod] | `HPOD` |
| 15 | Ciśnienie na poziomie morza | `PPPM` |
| 16 | Opad za 6 godzin | `WO6G` |
| 17 | Temperatura gruntu na głębokości 5 cm | `TG05` |
| 18 | Usłonecznienie | `USLN` |
| 19 | Występowanie rosy | `ROSW` |

> **Dlaczego `WID`, a nie `WIDA`:** w plikach IMGW widzialność w metrach (`WIDA` – automat, `WIDO` – obserwator) jest dopiero od 2011 r., a `WIDA` brakuje dodatkowo w 2024 r. i w części 2025 r. Kod `WID` jest wypełniony we wszystkich latach 2001–2025, więc z niego budujemy etykietę i wejście. Porównanie z `WIDO` (2011–2025) potwierdziło, że kody 1–3 oznaczają < 1000 m (patrz pułapka 1).
>
> **Dlaczego `HPOD`:** z tego samego powodu podstawę chmur bierzemy jako kod `HPOD`, a nie wysokość w metrach. Pole w metrach IMGW wypełnia dopiero od 2011 r., a `HPOD` jest dostępne we wszystkich latach 2001–2025 (braki < 1% godzin). Kod według SYNOP:
>
> | `HPOD` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
> |---|---|---|---|---|---|---|---|---|---|---|
> | podstawa [m] | < 50 | 50–100 | 100–200 | 200–300 | 300–600 | 600–1000 | 1000–1500 | 1500–2000 | 2000–2500 | ≥ 2500 lub brak chmur |
>
> Brak wartości (`/` w pliku) występuje dokładnie wtedy, gdy niebo jest niewidoczne (`NOG` = 9), najczęściej z powodu mgły. To sygnał związany z mgłą, a nie zwykły brak danych.

Dopiero w przyszłości można myśleć o rozbudowie modeli o kolejne parametry: pozostałe pola z tabeli 5.1 (np. tendencja ciśnienia, rodzaj opadu, temperatura minimalna przy gruncie, stan gruntu, pokrywa śnieżna) i dane METAR (etap 2).

**PM10 z GIOŚ (5.2) jest już w bazie** – `data_import()` zwraca je jako kolumnę 20 (`PM10`). Zgodnie z planem z rozdziału 1 dokładamy ją jako osobny eksperyment: porównujemy modele bez PM10 i z PM10.

### 5.1 Stacja Kraków-Balice (IMGW SYNOP 12566 + METAR EPKK)

https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/terminowe/synop/

| Nr | Parametr | Pole | Prio | Znaczenie dla mgły |
|---|---|---|---|---|
| 1 | Widzialność | `WID` (kod), `WIDO`/`WIDA` (od 2011), METAR `vsby` | ★★★ | Z niej budujemy etykietę (< 1000 m). Jako wejście daje persystencję i trend: spadająca widzialność (zamglenie) często poprzedza mgłę. Najsilniejszy predyktor dla krótkich horyzontów. |
| 2 | Pogoda bieżąca | `POGB`, METAR `wxcodes` | ★★★ | Odróżnia mgłę (kody 40–49) od zamglenia (10) oraz zmętnienia lub dymu (04–05). Potrzebna do etykiety i jako sygnał, że mgła „już się zaczyna”. |
| 3 | Temperatura powietrza | `TEMP` | ★★★ | Mgła radiacyjna powstaje, gdy powietrze ochłodzi się do punktu rosy. Tempo nocnego spadku temperatury mówi, jak szybko się do niego zbliża. |
| 4 | Temperatura punktu rosy | `TPTR` | ★★★ | Miara zawartości pary wodnej. Razem z temperaturą daje deficyt T − Td, kluczową miarę odległości od nasycenia. |
| 5 | Wilgotność względna | `WLGW` | ★★★ | Bezpośrednia miara nasycenia. Mgła wymaga RH bliskiej 100%. Przydaje się też do odróżnienia mgły od smogu. |
| 6 | Prędkość wiatru | `FWR` | ★★★ | Słaby wiatr (~0,5–3 m/s) sprzyja mgle radiacyjnej. Przy ciszy powstaje raczej rosa, a silniejszy wiatr miesza warstwę przyziemną i nie dopuszcza do nasycenia. |
| 7 | Kierunek wiatru | `KRWR` | ★★★ | Pokazuje, skąd napływa powietrze: wilgotne z doliny Wisły czy Rudawy (adwekcja), czy suche. Kodujemy jako składowe u/v (parametr 26), nie surowe stopnie. |
| 8 | Zachmurzenie ogólne | `NOG` | ★★★ | Czyste niebo w nocy oznacza silne wypromieniowanie długofalowe i szybkie wychładzanie gruntu. Chmury działają jak koc i blokują mgłę radiacyjną. |
| 9 | Zachmurzenie niskie | `CLCM` | ★★ | Niskie chmury najsilniej hamują wychładzanie. Ich obecność to też sygnał wilgotnej warstwy przy ziemi. |
| 10 | Wysokość podstawy chmur | `HPOD` (kod), METAR `skyl1` | ★★ | Obniżający się stratus to osobny mechanizm powstawania mgły (*cloud base lowering*). Ważne przy mgłach niebędących radiacyjnymi. |
| 11 | Ciśnienie na poziomie morza | `PPPM` | ★★ | Wysokie ciśnienie oznacza wyż, a więc osiadanie, inwersję, słaby wiatr i bezchmurne noce: klasyczne warunki mgłowe. |
| 12 | Tendencja ciśnienia | `APP`, `TECH` | ★★ | Rosnące lub stabilne ciśnienie wskazuje na budujący się wyż, a spadające na nadchodzący front, który zwykle rozprasza mgłę. |
| 13 | Opad (6 h) i jego rodzaj | `WO6G`, `ROPT` | ★★ | Mokre podłoże po deszczu dostarcza wilgoci do warstwy przyziemnej. Mgła często pojawia się w pierwszą bezchmurną noc po opadach. |
| 14 | Min. temperatura przy gruncie | `TGMI` | ★★ | Grunt wychładza się szybciej niż powietrze na 2 m, więc pokazuje siłę wychładzania radiacyjnego tuż przy powierzchni. |
| 15 | Temperatura gruntu (5 cm) | `TG05` | ★ | Strumień ciepła z gruntu: ciepły grunt jesienią może opóźniać mgłę, zimny ją przyspiesza. |
| 16 | Stan gruntu | `SGRN` | ★ | Grunt suchy, mokry lub zamarznięty to przybliżenie wilgotności podłoża. |
| 17 | Pokrywa śnieżna | `PKSN` | ★ | Śnieg silnie wypromieniowuje i chłodzi powietrze przy ziemi. Może też sprzyjać mgle przy roztopach i napływie ciepłego, wilgotnego powietrza. |
| 18 | Usłonecznienie | `USLN` | ★ | Słoneczny dzień poprzedzający noc oznacza parowanie i wilgoć przy gruncie wieczorem. W dzień słońce rozprasza mgłę. |
| 19 | Występowanie rosy | `ROSW` | ★ | Rosa oznacza, że przy gruncie osiągnięto nasycenie, co jest blisko progu mgły. |

### 5.2 Jakość powietrza (GIOŚ)

| Nr | Parametr | Prio | Znaczenie dla mgły |
|---|---|---|---|
| 20 | PM10 (`PM10`: średnia z Kraków, Al. Krasińskiego i Kraków, ul. Bulwarowa) | ★ | Aerozol dostarcza jąder kondensacji: wpływa na gęstość mgły i pozwala analizować mgłę vs smog. Jest też wskaźnikiem stagnacji powietrza pod inwersją. W sezonie IX–III średnie PM10 przy mgle wynosi ok. 111 µg/m³, a bez mgły ok. 64 µg/m³. Tylko do osobnego eksperymentu. W latach 2001–2002 GIOŚ ma tylko dane dobowe (`24g`) – nie interpolujemy ich do godzin, więc `PM10` jest tam puste (NaN). Puste są też ok. 1,5% godzin 2003–2025, gdy obie stacje nie mierzyły. Braków nie uzupełniamy – boosting radzi sobie z NaN. |

> **Dlaczego tylko PM10:** dla uproszczenia zbioru danych bierzemy jeden wskaźnik z najdłuższą serią. PM2.5 (fizycznie lepsza miara jąder kondensacji) i SO₂ (prekursor siarczanów, ważny dla długoterminowego trendu mgieł) to możliwe rozszerzenia na później. Pozostałe zanieczyszczenia (CO, benzen, NO₂, O₃, metale) pomijamy, bo wnoszą głównie tę samą informację o stagnacji powietrza co PM10 i dane meteorologiczne.
>
> **Pułapka pomiarowa:** przy bardzo dużej wilgotności i mgle odczyty automatycznych mierników pyłu mogą być zaburzone. Jeśli PM10 okaże się podejrzanie silnym predyktorem, trzeba sprawdzić, czy model nie uczy się artefaktu pomiarowego.

### 5.3 Cechy wyliczane (niczego nie pobieramy, ale są bardzo ważne)

| Nr | Cecha | Prio | Znaczenie dla mgły |
|---|---|---|---|
| 21 | Deficyt punktu rosy T − Td | ★★★ | Ile stopni brakuje do nasycenia. Zwykle najważniejsza pojedyncza cecha. |
| 22 | Trendy: ΔT, ΔTd, ΔRH, Δwidzialności za 1, 3 i 6 h | ★★★ | Model musi wiedzieć, czy powietrze zbliża się do nasycenia, a nie tylko jaki jest stan obecny. |
| 23 | Godzina (sin/cos) i dzień roku (sin/cos) | ★★★ | Silny cykl dobowy (maksimum nad ranem) i roczny (jesień–zima). |
| 24 | Wysokość Słońca w chwili *t* i w godzinie docelowej *t+h* | ★★★ | Po wschodzie Słońca mgła się rozprasza. Bez tej informacji model nie wie, że za 5 h będzie już dzień. |
| 25 | Długość nocy / godziny od zachodu Słońca | ★★ | Im dłużej trwa noc, tym więcej czasu na wychładzanie. Stąd długie jesienne i zimowe noce sprzyjają mgle. |
| 26 | Składowe wiatru u, v | ★★ | Kierunek jako wektor zamiast stopni, bo 359° i 1° to prawie ten sam kierunek. |
| 27 | Flagi braków danych | ★ | Informacja dla modelu, że wartość była uzupełniana, plus kontrola jakości. |

Cechy wyliczane powstają z parametrów zestawu startowego, więc nie wymagają pobierania dodatkowych danych.

> **Do rozważenia:** typ cyrkulacji atmosferycznej według kalendarza Niedźwiedzia. Według pracy Skrzyńskiej (2019) mgła w Balicach najczęściej występuje w sytuacjach bezadwekcyjnych: w centrum wyżu i klinie antycyklonalnym. To gotowa, fizycznie uzasadniona cecha synoptyczna.

---

## 6. Modele

Dane z IMGW z lat 2001–2025 są notowane co 1 godzinę, a z lat wcześniejszych co 3 h. Dlatego pierwsze treningi wykonujemy wyłącznie na danych godzinowych z lat 2001–2025 (etap 1). Lata sprzed 2001 dokładamy w kolejnych podejściach z godzinowych depesz METAR (etap 2, patrz rozdział 1 – *Etapy zbierania danych*). Porównanie modeli z etapu 1 i 2 pokaże, czy dłuższa seria danych poprawia prognozę.

### Metoda: drzewa decyzyjne, nie sieć neuronowa

Nie budujemy sieci neuronowej. Używamy **drzew decyzyjnych w wersji gradient boosting** (np. XGBoost, LightGBM), tak jak grupa z Uniwersytetu w Innsbrucku w projekcie dla lotniska w Wiedniu (Dietz i in., 2018, patrz rozdział 11). Drzewa dobrze radzą sobie z danymi w postaci tabeli, z mieszanką wartości ciągłych i kodów (np. pogoda bieżąca) oraz z brakami danych. Nie wymagają skalowania cech i łatwo z nich odczytać, które cechy są najważniejsze.

### Dwa sposoby prognozy na 1–5 h

Tworzymy łącznie **6 modeli**. Najbardziej zależy nam na **porównaniu tych dwóch sposobów** prognozy wielohoryzontowej.

#### Podejście A: 5 osobnych modeli (modele 1–5)

5 niezależnych modeli, każdy dla innego czasu wyprzedzenia (tak robiła grupa z Innsbrucka dla lotniska w Wiedniu):

- model 1: szansa na mgłę za 1 h,
- model 2: szansa na mgłę za 2 h,
- model 3: szansa na mgłę za 3 h,
- model 4: szansa na mgłę za 4 h,
- model 5: szansa na mgłę za 5 h.

Każdy model ma **jedno wyjście** z prawdopodobieństwem mgły (drugie wyjście 100% − p nie niesie dodatkowej informacji).

#### Podejście B: jeden model z 5 wyjściami (model 6)

Jeden model przyjmuje na wejściu parametry z ostatnich 48 godzin, a na wyjściu ma **5 wyjść**. Każde podaje prawdopodobieństwo mgły w danej godzinie w przód, np.:

| Horyzont | +1 h | +2 h | +3 h | +4 h | +5 h |
|---|---|---|---|---|---|
| Szansa na mgłę | 60% | 55% | 40% | 25% | 10% |

Każde wyjście ma **osobną funkcję logistyczną** (nie wspólny softmax, bo prawdopodobieństwa dla różnych godzin nie muszą sumować się do 100%), a funkcja straty to suma 5 binarnych entropii krzyżowych (*log loss*).

Technicznie drzewa w podstawowej wersji mają jedno wyjście. Model z 5 wyjściami można zbudować tak:
- **XGBoost (od wersji 2.0) z `multi_strategy="multi_output_tree"`**: każde drzewo jest wspólne dla wszystkich 5 horyzontów, a w liściach zapisane jest 5 wartości naraz,
- albo **las losowy / pojedyncze drzewo ze scikit-learn**, które natywnie obsługują wiele wyjść.

> **Uwaga:** `MultiOutputClassifier` ze scikit-learn tylko trenuje osobny model dla każdego wyjścia. To w praktyce podejście A, więc nie nadaje się do porównania.

### Wspólne dla obu podejść

Do modeli podajemy też **aktualną godzinę i wysokość Słońca, również dla godzin docelowych** (parametry 23–24). Dzięki temu model może się nauczyć, że po wschodzie Słońca mgła zanika: promieniowanie słoneczne nagrzewa powierzchnię gruntu, ta ogrzewa powietrze od dołu, temperatura rośnie powyżej punktu rosy i krople parują, a konwekcja rozbija inwersję i miesza warstwę przyziemną.

### Porównanie podejść

| | A: 5 osobnych modeli | B: jeden model, 5 wyjść |
|---|---|---|
| Zalety | każdy horyzont może mieć własne cechy i hiperparametry, standardowe zastosowanie gradient boostingu (LightGBM, XGBoost) | wspólna struktura drzew dla wszystkich horyzontów, gładsze i spójniejsze prognozy, jeden model do utrzymania |
| Wady | prognozy dla kolejnych godzin mogą „skakać”, bo modele nic o sobie nie wiedzą | jeden podział w drzewie musi pasować do wszystkich horyzontów; drzewa wielowyjściowe w XGBoost są nowsze i mniej sprawdzone |

Każde z podejść ma wady i zalety, na które trzeba uważać, i właśnie to porównanie jest głównym wynikiem projektu.

> **Punkt odniesienia:** oba podejścia porównujemy zawsze z dwoma prostymi *baseline'ami*: **persystencją** („będzie tak jak teraz”) i **klimatologią** (częstość mgły dla danej godziny i miesiąca). Patrz pułapka 4.

---

## 7. Ocena modeli

Dobrym sposobem weryfikacji jest sprawdzenie, jak model radzi sobie na różnych horyzontach. Przewidzenie mgły za 1 h jest łatwe, jeśli mgła jest już teraz. Przy prognozie na 5 h w przód skuteczność wyraźnie spadnie i to jest oczekiwane. Ciekawe jest, **jak szybko** spada dla każdego z modeli i o ile lepiej od baseline'ów wypada na dłuższych horyzontach.

Wyniki można porównać z prognozami synoptyków, czyli prognozami lotniskowymi **TAF** dla EPKK.

> **Uwaga:** to porównanie nie jest „łatwe”. Trzeba zdobyć i zdekodować archiwum depesz TAF (np. z serwisu Ogimet, do sprawdzenia), a TAF podaje przedziały czasowe i grupy zmian (`BECMG`, `TEMPO`, `PROB30`), a nie prawdopodobieństwo na każdą godzinę. Trzeba więc ustalić sposób przeliczenia.

---

## 8. Zakres sezonowy

Model prognozuje mgłę w okresie **od początku września do końca marca**. W tym okresie występuje zdecydowana większość mgieł: według Skrzyńskiej (2019) mgła na lotniskach południowej Polski jest najczęstsza jesienią, z maksimum w październiku, a najrzadsza latem.

> **Uwaga implementacyjna:** do bazy wczytujemy dane z całego roku, a ograniczenie do września–marca robimy **według chwili prognozy *t***, a nie przez wycięcie wierszy wejściowych. Kolejność:
> 1. budujemy okna 48 h na pełnej, ciągłej serii godzinowej (po czasie, nie po numerach wierszy),
> 2. dopiero potem zostawiamy próbki, których chwila prognozy *t* wypada między 1 września a 31 marca.
>
> Dzięki temu okno dla 1 września naturalnie sięga do końca sierpnia. Gdyby najpierw odfiltrować wiersze (`WHERE month IN (9,…,3)`), a potem ciąć je na okna po kolejnych wierszach, po 31 marca od razu następowałby 1 września i okno skleiłoby dwie odległe pory roku.

---

## 9. Plan budowy prognozy

1. **Wczytanie danych.** Skrypt w Pythonie pobiera wszystkie dane i wczytuje je do bazy SQLite, układając je w sensowny sposób (osobne tabele dla źródeł, czas w UTC, kontrola braków i statusów pomiaru).
2. **Przygotowanie danych do treningu.** Skrypt wybiera z bazy parametry zestawu startowego, liczy cechy wyliczane i etykiety, zamienia okna 48 h na wiersze cech, dzieli je na zbiory treningowy, walidacyjny i testowy i przygotowuje do podania modelom.
3. **Stworzenie 6 modeli.** Na początku nie zajmujemy się dokładnością, tylko tym, żeby cokolwiek zwracały. Poprawiamy je na końcu. Równolegle liczymy oba baseline'y.
4. **Interfejs do analizy wyników.** Narzędzie analizujące wyniki (metryki dla każdego horyzontu, diagramy wiarygodności, porównanie obu podejść), które ułatwi poprawianie parametrów modeli i innych ustawień.

---

## 10. Pułapki, o których warto wiedzieć od początku

1. **Definicja etykiety.** Przyjmujemy standard WMO:
   > **mgła = widzialność < 1000 m**, czyli kod `WID` ≤ 3

   Kody `WID` odpowiadają przedziałom: 1 = 50–200 m, 2 = 200–500 m, 3 = 500–1000 m, 4 = 1–2 km (sprawdzone na `WIDO` z lat 2011–2025; kod 0 w danych nie występuje).
   **Dlaczego bez dodatkowych warunków:** sprawdziliśmy, czy sam próg widzialności nie łapie smogu lub opadów. W sezonie IX–III (2001–2025) jest 5870 godzin z `WID` ≤ 3, z czego 5837 (99,4%) to mgła według kodu pogody bieżącej (40–49) lub RH ≥ 95%. Pozostałe 33 godziny to głównie intensywne opady śniegu. Dodatkowy warunek (np. „ORAZ RH ≥ 95% LUB kod 40–49”) praktycznie nic by nie zmienił, a komplikowałby etykietę.
   Progu stężenia PM nie używamy: w Krakowie mgła i smog często występują jednocześnie (ta sama inwersja zatrzymuje wilgoć i pył), a pomiary PM z lat 80. praktycznie nie istnieją.
   **Horyzont:** przewidujemy mgłę **dokładnie w godzinie *t+h***, a nie „kiedykolwiek w oknie *t+1…t+h*”. Etykieta dla horyzontu *h* to więc `WID` ≤ 3 w wierszu o *h* godzin późniejszym niż chwila prognozy *t*:
   - modele 1–5 (podejście A): każdy przewiduje jedną taką etykietę, odpowiednio dla *h* = 1, 2, 3, 4 i 5 h,
   - model 6 (podejście B): przewiduje wszystkie 5 etykiet naraz, po jednym wyjściu na każdą godzinę *t+1 … t+5*.

   Wszystkie 6 modeli dostaje te same dane wejściowe i jest oceniane na tych samych etykietach, więc różnica w wynikach wynika tylko z budowy modelu.

   > **Na później: klasy LVP.** Dla lotniska ważniejsza od samej mgły jest procedura ograniczonej widzialności (LVP 0–3), wyznaczana z RVR (widzialności wzdłuż pasa) i pułapu chmur. Tak robiły prace z Innsbrucka dla Wiednia (Kneringer i in., Dietz i in.). Po napisaniu modeli dla mgły można przejść na klasy przybliżające LVP, pamiętając, że:
   > - nie mamy RVR, tylko widzialność meteorologiczną (zwykle mniejszą od RVR), więc klasy będą przybliżeniem,
   > - niski pułap bez mgły też włącza LVP: w sezonie IX–III ok. 4,7% godzin ma podstawę chmur < 100 m przy zachmurzeniu ≥ 5/8, czyli mniej więcej tyle samo co godzin z mgłą,
   > - progi LVP ustala każde lotnisko – dla EPKK trzeba je sprawdzić w AIP Polska (EPKK AD 2.22),
   > - klasy uporządkowane można modelować jako kilka pytań binarnych: P(klasa ≥ 1), P(klasa ≥ 2), P(klasa ≥ 3).
2. **Powstawanie a utrzymywanie się mgły.** Jeśli mgła jest teraz, model łatwo przewidzi, że będzie za godzinę, i metryki wyglądają świetnie. Ciekawe jest powstawanie mgły, więc osobno oceniamy przypadki, w których w chwili *t* mgły nie ma.
3. **Niezbalansowane klasy.** Mgła to kilka procent godzin (w sezonie IX–III 2001–2025: 4,6%). Używamy PR-AUC, Brier score i diagramów wiarygodności (skoro chcemy prawdopodobieństwa, kalibracja jest kluczowa), a nie samej trafności (*accuracy*). Jeśli w funkcji straty damy wagi klas (np. `scale_pos_weight` w XGBoost), kalibracja się psuje i trzeba ją potem poprawić (np. regresją izotoniczną).
4. **Baseline'y.** Zawsze porównujemy z persystencją i klimatologią (częstość mgły dla danej godziny i miesiąca). Wynik bez tego porównania nic nie znaczy.
5. **Niestacjonarność danych 1980–2024.** Częstość mgły w Europie wyraźnie spadła od lat 80., m.in. przez spadek zanieczyszczenia aerozolem. Do tego dochodzi zmiana z widzialności określanej przez obserwatora na pomiar automatyczny, co widać w osobnych polach `WIDO` i `WIDA`.
   W etapie 2 dochodzi zmiana źródła: przed 2001 r. dane stacyjne pochodzą z METAR, a od 2001 r. z IMGW. Trzeba sprawdzić, czy na granicy źródeł nie ma sztucznego skoku, np. w częstości mgły. Najprościej porównać METAR i IMGW w latach, w których dostępne są oba źródła.
   Niestacjonarne jest też PM10 z Krakowa: poziom zanieczyszczeń w Krakowie spadał z przyczyn niezwiązanych z pogodą, m.in. przez zakaz palenia węglem (od 2019 r.) i zmiany w ruchu ulicznym.
6. **Podział danych.** Podział czasowy jest poprawny (żadnego losowego mieszania!), ale potrzebny jest też zbiór walidacyjny do strojenia, a testu nie dotykamy aż do końca. Proponowany podział:

   | Zbiór | Etap 1 (IMGW) | Etap 2 (METAR + IMGW) |
   |---|---|---|
   | treningowy | 2001–2018 | od najstarszego dostępnego roku (np. 1980) do 2018 |
   | walidacyjny | 2019–2020 | 2019–2020 |
   | testowy | 2021–2025 | 2021–2025 |

   W etapie 2 wydłużamy **tylko zbiór treningowy**, a walidacyjny i testowy zostają te same. Dzięki temu wyniki obu etapów są bezpośrednio porównywalne: różnica wynika z dodatkowych danych, a nie z innego okresu testowego.
7. **Sezon chłodny.** Ograniczamy się do okresu wrzesień–marzec, bo wtedy występuje większość zdarzeń (patrz rozdział 8).

---

## 11. Źródła i literatura

### Literatura

1. **Skrzyńska M. (2019).** *Prace Geograficzne*, z. 158, s. 27–44 (tytuł do uzupełnienia ze strony artykułu). DOI: [10.4467/20833113PG.19.014.10918](https://doi.org/10.4467/20833113PG.19.014.10918)
   Najbardziej konkretne źródło o mgłach w rejonie Balic. Analizuje dni z mgłą w latach 1981–2010 na trzech lotniskach: Kraków-Balice, Katowice-Muchowiec i Rzeszów-Jasionka, wraz z typami cyrkulacji. Najwięcej dni z mgłą odnotowano w Balicach.
2. **Dietz S.J., Kneringer P., Mayr G.J., Zeileis A. (2018).** Low visibility forecasts for different flight planning horizons using tree-based boosting models. *Working Papers in Economics and Statistics*, Universität Innsbruck, 2018-11.
   Wzór dla naszego projektu: drzewa decyzyjne z boostingiem i osobne modele dla każdego horyzontu (lotnisko w Wiedniu). Obserwacje dominują do ok. 2 h wyprzedzenia, potem coraz ważniejsze są prognozy modeli numerycznych.
3. **Kneringer P., Dietz S.J., Mayr G.J., Zeileis A. (2017).** Probabilistic nowcasting of low-visibility procedure states at Vienna International Airport during cold season. *Working Papers in Economics and Statistics*, Universität Innsbruck, 2017-21.
4. **Vautard R., Yiou P., van Oldenborgh G.J. (2009).** Decline of fog, mist and haze in Europe over the past 30 years. *Nature Geoscience*, 2, 115–119.
   Źródło do pułapki 5 (spadek częstości mgły w Europie).

### Dane

- IMGW-PIB, dane terminowe SYNOP: <https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/terminowe/synop/>
- Iowa Environmental Mesonet, archiwum METAR: <https://mesonet.agron.iastate.edu/request/download.phtml>
- GIOŚ, bank danych pomiarowych jakości powietrza: <https://powietrze.gios.gov.pl/>
  - archiwum (roczne paczki 2000–2025 i metadane stacji): <https://powietrze.gios.gov.pl/pjp/archives>
