# Prognozowanie mgły w rejonie lotniska Kraków-Balice

> Projekt w ramach przedmiotu **Podstawy fizyki środowiska**.
> Cel: model uczenia maszynowego, który na podstawie danych meteorologicznych z ostatnich godzin podaje prawdopodobieństwo wystąpienia mgły na lotnisku Kraków-Balice (EPKK) w kolejnych 1–10 godzinach.

---

## Spis treści

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
| **ERA5 (Copernicus)** | Reanaliza: profil pionowy atmosfery, warstwa graniczna, wilgotność gleby, promieniowanie | godzinowa, siatka 0,25° | Dostępna od 1940 r. |
| **GIOŚ – jakość powietrza** | **tylko PM10**, stacja Kraków, Al. Krasińskiego | godzinowa (`1g`); w części lat może być tylko dobowa (`24g`) | Archiwum od 2000 r. Czas w **CET** – przy imporcie przesunąć na UTC. |

IMGW-PIB - dane terminowe SYNOP (Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy - dane terminowe surface synoptic observations)

METAR - Iowa Environmental Mesonet (IEM) (Meteorological Aerodrome Report)

ERA5 (Copernicus) - (to ECMWF Reanalysis v5, czyli piąta generacja reanalizy klimatycznej przygotowywanej przez ECMWF (European Centre for Medium-Range Weather Forecasts, Europejskie Centrum Prognoz Średnioterminowych))

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
- ERA5 i GIOŚ dokładamy jako **osobne eksperymenty** i mierzymy, o ile poprawiają wynik względem modelu na samym IMGW.

---

## 2. Zakres przestrzenny

Dane stacyjne bierzemy **tylko z lotniska w Balicach**. Pozostałe stacje synoptyczne są dość rozrzucone po mapie, a różnice w ukształtowaniu terenu (lotnisko leży w obniżeniu, w pobliżu dolin Wisły i Rudawy) sprawiają, że przenoszenie ich wartości na Balice ma niewielki sens.

> **Doprecyzowanie:** nie wszystkie źródła są punktowe.
> - **ERA5** to siatka o oczku ok. 0,25° (ok. 28 × 18 km w naszej szerokości geograficznej). Bierzemy **punkt siatki najbliższy Balicom**, pamiętając, że reprezentuje on średnią z obszaru, a rzeźba terenu jest w nim wygładzona.
> - **GIOŚ** nie ma stacji na lotnisku. Bierzemy **tylko PM10 ze stacji Kraków, Al. Krasińskiego**, około 13 km od Balic.
>   - **Dlaczego ta stacja:** ma najdłuższą ciągłą serię (działa od początku lat 2000.). Bliższa stacja w Zabierzowie (`MpZabieWapie`) powstała później i nie pokrywa etapu 1 (2001–2025).
>   - **Ograniczenie:** to **stacja komunikacyjna** przy ruchliwej ulicy, a nie stacja tła. Bezwzględne stężenia są wyższe niż przy lotnisku, a cykl dobowy częściowo wynika z ruchu ulicznego. Zakładamy, że epizody smogowe przy inwersji mają w Krakowie charakter regionalny, więc **zmienność w czasie** jest podobna jak przy Balicach.
>   - **Do sprawdzenia:** korelacja PM10 z Krasińskiego i z Zabierzowa w latach, w których działają obie stacje. Wysoka korelacja uzasadnia ten wybór.
>   - **Kody stacji:** w starszych plikach Krasińskiego występuje jako `MpKrakowWIOSAKra6117`, w nowszych pod nowym kodem. Powiązanie kodów jest w pliku metadanych GIOŚ (kolumna ze starym kodem). Przy imporcie oba kody łączymy w jedną serię.
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
> - Wygodny układ bazy: **osobna tabela dla każdego źródła** (`synop`, `metar`, `era5`, `gios`) z kluczem czasowym, a na nich **widok** (`VIEW`) łączący wszystko w jedną szeroką tabelę cech. Dzięki temu łatwo dodać nowe źródło bez przebudowy całości.
> - SQLite obsługuje funkcje okna (`LAG`, `AVG(...) OVER`), więc trendy i opóźnienia można liczyć bezpośrednio w SQL.

---

## 4. Okno wejściowe modelu

Do treningu bierzemy **48 kolejnych godzin** wraz ze wszystkimi parametrami dla tych godzin. Jedna próbka to więc tensor o kształcie `(48, liczba_cech)`, a cały zbiór: `(liczba_próbek, 48, liczba_cech)`.

To także pole do eksperymentów: można sprawdzać różne długości okna (np. 24 h, 30 h, 32 h) i porównywać, jak model radzi sobie w zależności od liczby godzin podanych na wejściu.

> **Uwagi:**
> - Okna przesuwamy co godzinę, więc sąsiednie próbki prawie się pokrywają. Przy podziale na zbiory treningowy, walidacyjny i testowy trzeba zostawić **przerwę (≥ 58 h = 48 h wejścia + 10 h horyzontu)** na granicach, żeby żadne okno nie „zaglądało” do innego zbioru.
> - Trzeba zdecydować, co robić z oknami zawierającymi braki danych: odrzucać, uzupełniać (np. z ERA5) czy oznaczać flagą (parametr 37).

---

## 5. Parametry

Priorytet: ★★★ niezbędne · ★★ wyraźnie pomaga · ★ opcjonalne lub do eksperymentów.
W kolumnie „Pole” podane są nazwy z plików IMGW SYNOP, METAR (IEM) lub ERA5.

### 5.1 Stacja Kraków-Balice (IMGW SYNOP 12566 + METAR EPKK)

https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/terminowe/synop/

| Nr | Parametr | Pole | Prio | Znaczenie dla mgły |
|---|---|---|---|---|
| 1 | Widzialność | `WIDO`/`WIDA`, METAR `vsby` | ★★★ | Z niej budujemy etykietę (< 1000 m). Jako wejście daje persystencję i trend: spadająca widzialność (zamglenie) często poprzedza mgłę. Najsilniejszy predyktor dla krótkich horyzontów. |
| 2 | Pogoda bieżąca | `POGB`, METAR `wxcodes` | ★★★ | Odróżnia mgłę (kody 40–49) od zamglenia (10) oraz zmętnienia lub dymu (04–05). Potrzebna do etykiety i jako sygnał, że mgła „już się zaczyna”. |
| 3 | Temperatura powietrza | `TEMP` | ★★★ | Mgła radiacyjna powstaje, gdy powietrze ochłodzi się do punktu rosy. Tempo nocnego spadku temperatury mówi, jak szybko się do niego zbliża. |
| 4 | Temperatura punktu rosy | `TPTR` | ★★★ | Miara zawartości pary wodnej. Razem z temperaturą daje deficyt T − Td, kluczową miarę odległości od nasycenia. |
| 5 | Wilgotność względna | `WLGW` | ★★★ | Bezpośrednia miara nasycenia. Mgła wymaga RH bliskiej 100%. Przydaje się też do odróżnienia mgły od smogu. |
| 6 | Prędkość wiatru | `FWR` | ★★★ | Słaby wiatr (~0,5–3 m/s) sprzyja mgle radiacyjnej. Przy ciszy powstaje raczej rosa, a silniejszy wiatr miesza warstwę przyziemną i nie dopuszcza do nasycenia. |
| 7 | Kierunek wiatru | `KRWR` | ★★★ | Pokazuje, skąd napływa powietrze: wilgotne z doliny Wisły czy Rudawy (adwekcja), czy suche. Kodujemy jako składowe u/v (parametr 34), nie surowe stopnie. |
| 8 | Zachmurzenie ogólne | `NOG` | ★★★ | Czyste niebo w nocy oznacza silne wypromieniowanie długofalowe i szybkie wychładzanie gruntu. Chmury działają jak koc i blokują mgłę radiacyjną. |
| 9 | Zachmurzenie niskie | `CLCM` | ★★ | Niskie chmury najsilniej hamują wychładzanie. Ich obecność to też sygnał wilgotnej warstwy przy ziemi. |
| 10 | Wysokość podstawy chmur | `HPON`/`HPOD`, METAR `skyl1` | ★★ | Obniżający się stratus to osobny mechanizm powstawania mgły (*cloud base lowering*). Ważne przy mgłach niebędących radiacyjnymi. |
| 11 | Ciśnienie na poziomie morza | `PPPM` | ★★ | Wysokie ciśnienie oznacza wyż, a więc osiadanie, inwersję, słaby wiatr i bezchmurne noce: klasyczne warunki mgłowe. |
| 12 | Tendencja ciśnienia | `APP`, `TECH` | ★★ | Rosnące lub stabilne ciśnienie wskazuje na budujący się wyż, a spadające na nadchodzący front, który zwykle rozprasza mgłę. |
| 13 | Opad (6 h) i jego rodzaj | `WO6G`, `ROPT` | ★★ | Mokre podłoże po deszczu dostarcza wilgoci do warstwy przyziemnej. Mgła często pojawia się w pierwszą bezchmurną noc po opadach. |
| 14 | Min. temperatura przy gruncie | `TGMI` | ★★ | Grunt wychładza się szybciej niż powietrze na 2 m, więc pokazuje siłę wychładzania radiacyjnego tuż przy powierzchni. |
| 15 | Temperatura gruntu (5 cm) | `TG05` | ★ | Strumień ciepła z gruntu: ciepły grunt jesienią może opóźniać mgłę, zimny ją przyspiesza. |
| 16 | Stan gruntu | `SGRN` | ★ | Grunt suchy, mokry lub zamarznięty to przybliżenie wilgotności podłoża. |
| 17 | Pokrywa śnieżna | `PKSN` | ★ | Śnieg silnie wypromieniowuje i chłodzi powietrze przy ziemi. Może też sprzyjać mgle przy roztopach i napływie ciepłego, wilgotnego powietrza. |
| 18 | Usłonecznienie | `USLN` | ★ | Słoneczny dzień poprzedzający noc oznacza parowanie i wilgoć przy gruncie wieczorem. W dzień słońce rozprasza mgłę. |
| 19 | Występowanie rosy | `ROSW` | ★ | Rosa oznacza, że przy gruncie osiągnięto nasycenie, co jest blisko progu mgły. |

### 5.2 ERA5 (reanaliza Copernicus, godzinowa)

| Nr | Parametr | Zmienna | Prio | Znaczenie dla mgły |
|---|---|---|---|---|
| 20 | Temperatura na 925 i 850 hPa | `t` | ★★★ | W połączeniu z temperaturą przy ziemi daje siłę inwersji. Silna inwersja zatrzymuje wilgoć i chłód przy gruncie, co jest głównym warunkiem mgieł zimowych. |
| 21 | Wysokość warstwy granicznej | `blh` | ★★★ | Płytka warstwa graniczna to słabe mieszanie, więc wilgoć i ochłodzenie koncentrują się przy ziemi. |
| 22 | Wiatr na 925 hPa | `u`, `v` | ★★ | Silny wiatr tuż nad warstwą przyziemną może „zdrapać” mgłę przez turbulencję, nawet gdy przy ziemi jest cisza. |
| 23 | Wilgotność właściwa na 925/850 hPa | `q` | ★★ | Suche powietrze nad warstwą przyziemną sprzyja wypromieniowaniu, a gruba wilgotna warstwa sprzyja raczej niskim chmurom niż mgle. |
| 24 | Wilgotność gleby (warstwa wierzchnia) | `swvl1` | ★★ | Źródło pary wodnej z podłoża. Ciągła seria, w przeciwieństwie do opisowego „stanu gruntu”. |
| 25 | Promieniowanie długofalowe netto | `str` | ★★ | Bezpośrednia miara wypromieniowania energii przez powierzchnię nocą, czyli tempa wychładzania radiacyjnego. |
| 26 | Zachmurzenie niskie / ogólne | `lcc`, `tcc` | ★ | Uzupełnienie braków w danych stacyjnych i wartość ciągła zamiast oktantów. |
| 27 | T i Td na 2 m, ciśnienie | `t2m`, `d2m`, `msl` | ★ | Wypełnianie luk w danych stacyjnych. |

### 5.3 Jakość powietrza (GIOŚ)

| Nr | Parametr | Prio | Znaczenie dla mgły |
|---|---|---|---|
| 28 | PM10 (Kraków, Al. Krasińskiego) | ★ | Aerozol dostarcza jąder kondensacji: wpływa na gęstość mgły i pozwala analizować mgłę vs smog. Jest też wskaźnikiem stagnacji powietrza pod inwersją. Tylko do osobnego eksperymentu. Dane `24g` nie są interpolowane do godzin – co najwyżej jako cecha „średnie PM10 z poprzedniej doby” (nie z bieżącej, bo zawiera ona godziny z przyszłości). |

> **Dlaczego tylko PM10:** dla uproszczenia zbioru danych bierzemy jeden wskaźnik z najdłuższą serią. PM2.5 (fizycznie lepsza miara jąder kondensacji) i SO₂ (prekursor siarczanów, ważny dla długoterminowego trendu mgieł) to możliwe rozszerzenia na później. Pozostałe zanieczyszczenia (CO, benzen, NO₂, O₃, metale) pomijamy, bo wnoszą głównie tę samą informację o stagnacji powietrza co PM10 i dane meteorologiczne.
>
> **Pułapka pomiarowa:** przy bardzo dużej wilgotności i mgle odczyty automatycznych mierników pyłu mogą być zaburzone. Jeśli PM10 okaże się podejrzanie silnym predyktorem, trzeba sprawdzić, czy model nie uczy się artefaktu pomiarowego.

### 5.4 Cechy wyliczane (niczego nie pobieramy, ale są bardzo ważne)

| Nr | Cecha | Prio | Znaczenie dla mgły |
|---|---|---|---|
| 29 | Deficyt punktu rosy T − Td | ★★★ | Ile stopni brakuje do nasycenia. Zwykle najważniejsza pojedyncza cecha. |
| 30 | Trendy: ΔT, ΔTd, ΔRH, Δwidzialności za 1, 3 i 6 h | ★★★ | Model musi wiedzieć, czy powietrze zbliża się do nasycenia, a nie tylko jaki jest stan obecny. |
| 31 | Godzina (sin/cos) i dzień roku (sin/cos) | ★★★ | Silny cykl dobowy (maksimum nad ranem) i roczny (jesień–zima). |
| 32 | Wysokość Słońca w chwili *t* i w godzinie docelowej *t+h* | ★★★ | Po wschodzie Słońca mgła się rozprasza. Bez tej informacji model nie wie, że za 6 h będzie już dzień. |
| 33 | Długość nocy / godziny od zachodu Słońca | ★★ | Im dłużej trwa noc, tym więcej czasu na wychładzanie. Stąd długie jesienne i zimowe noce sprzyjają mgle. |
| 34 | Składowe wiatru u, v | ★★ | Kierunek jako wektor zamiast stopni, bo 359° i 1° to prawie ten sam kierunek. |
| 35 | Siła inwersji (T₉₂₅ − T₂ₘ) | ★★ | Wyliczana z ERA5 i stacji. Bezpośrednia miara stabilności warstwy przyziemnej. |
| 36 | Gradient ciśnienia | ★ | Przybliżony wiatr synoptyczny. Przy danych stacyjnych tylko z Balic liczymy go z pola ciśnienia ERA5 (`msl`) wokół lotniska, a nie między stacjami. |
| 37 | Flagi braków danych | ★ | Informacja dla modelu, że wartość była uzupełniana, plus kontrola jakości. |

> **Do rozważenia:** typ cyrkulacji atmosferycznej według kalendarza Niedźwiedzia. Według pracy Skrzyńskiej (2019) mgła w Balicach najczęściej występuje w sytuacjach bezadwekcyjnych: w centrum wyżu i klinie antycyklonalnym. To gotowa, fizycznie uzasadniona cecha synoptyczna.

---

## 6. Modele

Dane z IMGW z lat 2001–2025 są notowane co 1 godzinę, a z lat wcześniejszych co 3 h. Dlatego pierwsze treningi wykonujemy wyłącznie na danych godzinowych z lat 2001–2025 (etap 1). Lata sprzed 2001 dokładamy w kolejnych podejściach z godzinowych depesz METAR (etap 2, patrz rozdział 1 – *Etapy zbierania danych*). Porównanie modeli z etapu 1 i 2 pokaże, czy dłuższa seria danych poprawia prognozę.

Tworzymy łącznie **11 modeli** i porównujemy dwa podejścia do prognozy wielohoryzontowej.

### Podejście A: jeden model z 10 wyjściami

Jeden duży model przyjmuje na wejściu parametry z ostatnich 48 godzin, a na wyjściu ma **10 niezależnych wyjść**. Każde podaje prawdopodobieństwo mgły w danej godzinie w przód, np.:

| Horyzont | +1 h | +2 h | … | +10 h |
|---|---|---|---|---|
| Szansa na mgłę | 60% | 55% | … | 2% |

Technicznie: każde wyjście ma **osobną sigmoidę** (nie wspólny softmax, bo prawdopodobieństwa dla różnych godzin nie muszą sumować się do 100%), a funkcja straty to suma 10 binarnych entropii krzyżowych.

Do modelu podajemy też **aktualną godzinę i wysokość Słońca, również dla godzin docelowych** (parametry 31–32). Dzięki temu model może się nauczyć, że po wschodzie Słońca mgła zanika: promieniowanie słoneczne nagrzewa powierzchnię gruntu, ta ogrzewa powietrze od dołu, temperatura rośnie powyżej punktu rosy i krople parują, a konwekcja rozbija inwersję i miesza warstwę przyziemną.

### Podejście B: 10 osobnych modeli

10 niezależnych modeli, każdy dla innego czasu wyprzedzenia (tak robiła grupa z Uniwersytetu w Innsbrucku dla lotniska w Wiedniu):

- model 1: szansa na mgłę za 1 h,
- model 2: szansa na mgłę za 2 h,
- …
- model 10: szansa na mgłę za 10 h.

Każdy model ma **jedno wyjście** z prawdopodobieństwem mgły (drugie wyjście 100% − p nie niesie dodatkowej informacji).
https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/terminowe/synop/1996_2000/
### Porównanie podejść

| | A: jeden model, 10 wyjść | B: 10 osobnych modeli |
|---|---|---|
| Zalety | wspólna reprezentacja dla wszystkich horyzontów, gładsze i spójniejsze prognozy, jeden model do utrzymania | każdy horyzont może mieć własne cechy i hiperparametry, naturalne dla gradient boostingu (LightGBM, XGBoost) |
| Wady | jedna architektura musi pasować do wszystkich horyzontów | prognozy dla kolejnych godzin mogą „skakać”, bo modele nic o sobie nie wiedzą |

To dobra okazja, żeby porównać oba podejścia, bo każde ma wady i zalety, na które trzeba uważać.

> **Punkt odniesienia:** oba podejścia porównujemy zawsze z dwoma prostymi *baseline'ami*: **persystencją** („będzie tak jak teraz”) i **klimatologią** (częstość mgły dla danej godziny i miesiąca). Patrz pułapka 4.

---

## 7. Ocena modeli

Dobrym sposobem weryfikacji jest sprawdzenie, jak model radzi sobie na różnych horyzontach. Przewidzenie mgły za 1 h jest łatwe, jeśli mgła jest już teraz. Przy prognozie na 10 h w przód skuteczność wyraźnie spadnie i to jest oczekiwane. Ciekawe jest, **jak szybko** spada dla każdego z modeli i o ile lepiej od baseline'ów wypada na dłuższych horyzontach.

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
2. **Przygotowanie danych do treningu.** Skrypt wybiera dane z bazy, liczy cechy wyliczane i etykiety, tnie dane na okna 48 h, dzieli je na zbiory treningowy, walidacyjny i testowy, zamienia na tensory i przygotowuje do podania modelom.
3. **Stworzenie 11 modeli.** Na początku nie zajmujemy się dokładnością, tylko tym, żeby cokolwiek zwracały. Poprawiamy je na końcu. Równolegle liczymy oba baseline'y.
4. **Interfejs do analizy wyników.** Narzędzie analizujące wyniki (metryki dla każdego horyzontu, diagramy wiarygodności, porównanie modeli), które ułatwi poprawianie parametrów modeli i innych ustawień.

---

## 10. Pułapki, o których warto wiedzieć od początku

1. **Definicja etykiety.** Standard WMO to widzialność < 1000 m. Można też użyć kodów pogody bieżącej 40–49 (mgła). Trzeba zdecydować, czy przewidujemy „mgłę w godzinie *t+h*”, czy „mgłę kiedykolwiek w oknie *t+1…t+h*”.
   Proponowana definicja, odróżniająca mgłę od smogu:
   > **mgła = widzialność < 1000 m ORAZ (RH ≥ 95% LUB kod pogody bieżącej 40–49)**

   Progu stężenia PM nie używamy: w Krakowie mgła i smog często występują jednocześnie (ta sama inwersja zatrzymuje wilgoć i pył), a pomiary PM z lat 80. praktycznie nie istnieją.
2. **Powstawanie a utrzymywanie się mgły.** Jeśli mgła jest teraz, model łatwo przewidzi, że będzie za godzinę, i metryki wyglądają świetnie. Ciekawe jest powstawanie mgły, więc osobno oceniamy przypadki, w których w chwili *t* mgły nie ma.
3. **Niezbalansowane klasy.** Mgła to kilka procent godzin. Używamy PR-AUC, Brier score i diagramów wiarygodności (skoro chcemy prawdopodobieństwa, kalibracja jest kluczowa), a nie samej trafności (*accuracy*). Jeśli w funkcji straty damy wagi klas, kalibracja się psuje i trzeba ją potem poprawić (np. regresją izotoniczną).
4. **Baseline'y.** Zawsze porównujemy z persystencją i klimatologią (częstość mgły dla danej godziny i miesiąca). Wynik bez tego porównania nic nie znaczy.
5. **Niestacjonarność danych 1980–2024.** Częstość mgły w Europie wyraźnie spadła od lat 80., m.in. przez spadek zanieczyszczenia aerozolem. Do tego dochodzi zmiana z widzialności określanej przez obserwatora na pomiar automatyczny, co widać w osobnych polach `WIDO` i `WIDA`.
   W etapie 2 dochodzi zmiana źródła: przed 2001 r. dane stacyjne pochodzą z METAR, a od 2001 r. z IMGW. Trzeba sprawdzić, czy na granicy źródeł nie ma sztucznego skoku, np. w częstości mgły. Najprościej porównać METAR i IMGW w latach, w których dostępne są oba źródła.
   Niestacjonarne jest też PM10 z Al. Krasińskiego: poziom zanieczyszczeń w Krakowie spadał z przyczyn niezwiązanych z pogodą, m.in. przez zakaz palenia węglem (od 2019 r.) i zmiany w ruchu ulicznym.
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
   Osobne modele dla każdego horyzontu (lotnisko w Wiedniu). Obserwacje dominują do ok. 2 h wyprzedzenia, potem coraz ważniejsze są prognozy modeli numerycznych.
3. **Kneringer P., Dietz S.J., Mayr G.J., Zeileis A. (2017).** Probabilistic nowcasting of low-visibility procedure states at Vienna International Airport during cold season. *Working Papers in Economics and Statistics*, Universität Innsbruck, 2017-21.
4. **Vautard R., Yiou P., van Oldenborgh G.J. (2009).** Decline of fog, mist and haze in Europe over the past 30 years. *Nature Geoscience*, 2, 115–119.
   Źródło do pułapki 5 (spadek częstości mgły w Europie).

### Dane

- IMGW-PIB, dane terminowe SYNOP: <https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/terminowe/synop/>
- Iowa Environmental Mesonet, archiwum METAR: <https://mesonet.agron.iastate.edu/request/download.phtml>
- ERA5, Copernicus Climate Data Store: <https://cds.climate.copernicus.eu/>
- GIOŚ, bank danych pomiarowych jakości powietrza: <https://powietrze.gios.gov.pl/>
  - archiwum (roczne paczki 2000–2025 i metadane stacji): <https://powietrze.gios.gov.pl/pjp/archives>
