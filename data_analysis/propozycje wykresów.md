# Propozycje wykresów, testów i obliczeń

Lista pomysłów na analizy, które można zrobić na danych z `baza.db` (IMGW 2001–2025 + PM10 z GIOŚ 2003–2025).
Każdy punkt jest osobnym, małym zadaniem – można wziąć jeden i zrobić z niego skrypt w `data_analysis/`.

Dane wczytujemy jak zwykle (patrz `Instrukcja_do_analizy_danych.py`):

```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_scripts.data_import_from_sql import data_import

df = data_import()
df["MGLA"] = (df["WID"] <= 3).astype(int)      # 1 = mgła (widzialność < 1000 m), 0 = brak
```

**Legenda:** ⭐ = szczególnie polecane (szybkie i dużo mówią o mgle) · 🧪 = test statystyczny · 🔢 = obliczenie / nowa cecha · 🛠️ = przydaje się bezpośrednio przy budowie modeli.

---

## Liczby na rozgrzewkę

Policzone wstępnie na `df` z `data_import()`, żeby było wiadomo, czego się spodziewać. „Dzień z mgłą” = dzień, w którym przynajmniej jedna godzina ma `WID` ≤ 3.

| Co | Wynik |
|---|---|
| Dni z mgłą w roku | średnio ok. 54; najmniej 39 (2018), najwięcej 69 (2014) |
| Trend dni z mgłą (prosta regresja) | ok. −5 dni na dekadę – **do sprawdzenia testem** (punkt C1) |
| Dni z mgłą w listopadzie | od 1 do 17, średnio ok. 10,5 |
| Najbardziej mglisty miesiąc | listopad (9,2% godzin), potem grudzień (7,2%) i październik (5,7%) |
| Najbardziej mglista godzina (sezon IX–III) | 05 UTC (9,2% godzin); najmniej mglista: 13 UTC (0,7%) |
| Mgła teraz → mgła za 1 / 3 / 5 h | 78% / 54% / 38% |
| Brak mgły teraz → mgła za 1 h | 0,7% |
| Epizody mgły | ok. 1400; mediana długości 3 h, najdłuższy 44 h; 28% trwa tylko 1 h |
| Średnie roczne PM10 | spadek z ok. 70 µg/m³ (2003–2011) do ok. 30 µg/m³ (2022–2025) |
| Mgła przy `DEFICYT` ≤ 0,5 °C / > 3 °C (sezon) | 26,5% / ok. 0% godzin |

---

## 1. Propozycje z pierwotnej listy (doprecyzowane)

1. ⭐ **Liczba dni z mgłą w listopadzie w kolejnych latach** – wykres słupkowy (oś x: rok 2001–2025). Można dorysować linię trendu i średnią z całego okresu.
2. ⭐ **Liczba dni z mgłą w roku w kolejnych latach** – jak wyżej. Lepiej liczyć „rok sezonowy” (wrzesień roku N – marzec roku N+1), bo inaczej jeden sezon mgłowy jest rozcięty między dwa lata kalendarzowe.
   - Warto sprawdzić, jak wynik zależy od definicji „dnia z mgłą”: ≥ 1 h mgły, ≥ 3 h mgły, mgła o konkretnej godzinie (np. 06 UTC). Jeśli trend znika przy innej definicji, to nie jest „mocny” trend.
3. **Średnia roczna temperatura w kolejnych latach (trend ocieplenia)** – częściowo zrobione w `temperature_data_analysis.py`. Do dodania: trend testem Manna-Kendalla (C1) i porównanie trendu osobno dla lata i dla sezonu IX–III.
4. **Prędkość wiatru a ciśnienie** – wykres punktowy `PPPM` × `FWR`. Przy 200 tys. godzin zwykły scatter będzie czarną plamą, lepiej `plt.hexbin` albo średnia prędkość wiatru w przedziałach ciśnienia co 5 hPa.
   - Fizycznie wiatr zależy od **różnicy** ciśnień między miejscami (gradientu), a nie od samego ciśnienia. Jedna stacja tego nie pokaże, ale wysokie ciśnienie = środek wyżu = słaby wiatr, więc zależność powinna być widoczna. Ciekawsze może być `FWR` w zależności od **zmiany** ciśnienia za 3 h (szybki spadek = nadchodzi front = silny wiatr).

---

## A. Klimatologia mgły – kiedy i jak długo

| Nr | Wykres | Po co |
|---|---|---|
| A1 ⭐ | **Mapa ciepła godzina (0–23) × miesiąc (1–12)**, kolor = % godzin z mgłą | Jeden obrazek pokazuje cały cykl dobowy i roczny. Spodziewamy się maksimum jesienią nad ranem. |
| A2 ⭐ | **Cykl dobowy mgły** osobno dla każdego miesiąca sezonu (7 linii na jednym wykresie) | Pokazuje, jak maksimum przesuwa się z porą roku (późniejszy wschód Słońca zimą). |
| A3 | **„Kalendarz mgły”**: mapa ciepła dzień sezonu × rok, kolor = liczba godzin z mgłą w danym dniu | Widać serie mglistych dni, „dziury” w danych i lata wyjątkowe. |
| A4 ⭐ | **Rozkład długości epizodów mgły** (histogram, oś y logarytmiczna) | Ile mgieł trwa 1 h, a ile cały dzień. Ważne przy ocenie modelu: krótkie epizody są najtrudniejsze. |
| A5 | **Godzina początku i godzina końca epizodu** (dwa histogramy) | Mgła radiacyjna powinna zaczynać się w nocy i kończyć 1–3 h po wschodzie Słońca. |
| A6 | **Koniec mgły względem wschodu Słońca** (histogram „ile godzin po wschodzie”) | Wymaga policzenia wschodu Słońca (D1). Pokazuje, czy to Słońce „rozpuszcza” mgłę. |
| A7 | **Rozkład kodów `WID`** w sezonie, osobno dla nocy i dnia | Jak często jest bardzo gęsta mgła (kod 1, < 200 m) w porównaniu z kodem 3. |
| A8 | **Częstość mgły w kolejnych sezonach osobno dla każdego miesiąca** (mała mapa ciepła rok × miesiąc) | Czy spadek dotyczy całego sezonu, czy np. tylko listopada. |

---

## B. Fizyka mgły – w jakich warunkach powstaje

| Nr | Wykres | Po co |
|---|---|---|
| B1 ⭐ | **Prawdopodobieństwo mgły w funkcji `DEFICYT`** (przedziały co 0,2 °C, oś y: % godzin z mgłą) | Najważniejsza zależność fizyczna. Spodziewamy się gwałtownego wzrostu poniżej ok. 1 °C. |
| B2 | To samo dla `WLGW`, `FWR`, `NOG`, `PPPM` (siatka 2×2 wykresów) | Szybki przegląd, które zmienne „coś mówią”. Dobre do porównania z ważnością cech w modelu. |
| B3 ⭐ | **Analiza złożona (composite) przed początkiem mgły**: średni przebieg `TEMP`, `TPTR`, `DEFICYT`, `FWR`, `NOG` od 12 h przed do 6 h po początku każdego epizodu (oś x: godziny względem początku, 0 = start mgły) | Pokazuje, *jak* atmosfera dochodzi do mgły – dokładnie to, czego model ma się nauczyć. Warto dorysować przedział ±1 odchylenie standardowe. |
| B4 | To samo względem **końca** epizodu | Co rozprasza mgłę: wzrost wiatru, wzrost temperatury po wschodzie Słońca, napływ chmur? |
| B5 | **Róża wiatrów**: wszystkie godziny vs. godziny z mgłą (dwa wykresy biegunowe, `plt.subplot(projection="polar")`) | Czy mgła przychodzi z konkretnego kierunku (np. z doliny Wisły lub Rudawy)? Pamiętaj: `KRWR` 0 = cisza, 999 = zmienny – osobno. |
| B6 | **Mgła a opad z ostatnich 6–24 h** (częstość mgły po nocy z opadem vs. bez) | Sprawdza zasadę „mgła w pierwszą pogodną noc po deszczu”. |
| B7 | **Tempo nocnego wychładzania** (spadek `TEMP` od 18 do 03 UTC) w nocach z mgłą rano i bez | Mgła radiacyjna potrzebuje silnego wychładzania – powinno być widać różnicę. |
| B8 | **Typy mgły**: podział epizodów na radiacyjne (bezchmurna noc, wiatr ≤ 2 m/s, start w nocy) i pozostałe (np. adwekcyjne, z opadającego stratusa – niski `HPOD` przed startem), wzorem algorytmu Tardif i Rasmussen (2007) | Różne typy mgły mają różną przewidywalność. Można potem sprawdzić, który typ model przewiduje najgorzej. |

### PM10 i mgła

| Nr | Wykres | Po co |
|---|---|---|
| B9 ⭐ | **Rozkład PM10 przy mgle i bez mgły** (dwa histogramy lub wykres pudełkowy, sezon IX–III) | Wstępnie: średnio ok. 111 vs. 64 µg/m³. Czy to tylko efekt tego, że i smog, i mgła lubią zimę i noc? → porównać w obrębie tego samego miesiąca i godziny. |
| B10 | **Cykl dobowy PM10** w sezonie (średnia dla każdej godziny UTC) | Maksimum wieczorem (ogrzewanie domów, inwersja). Warto nałożyć na cykl dobowy mgły (A2). |
| B11 | **PM10 rok po roku** (średnia sezonowa, słupki) | Wyraźny spadek (zakaz palenia węglem w Krakowie od września 2019). Uwaga: 2022 to tylko stacja Bulwarowa. |
| B12 | **PM10 w trakcie epizodu mgły** (composite jak B3) | Pułapka z README (5.2): mierniki pyłu mogą zawyżać odczyt przy bardzo dużej wilgotności. Gwałtowny skok PM10 dokładnie w chwili startu mgły sugerowałby artefakt pomiarowy. |
| B13 | **Mgła vs. zamglenie vs. zmętnienie** (`POGB` 40–49 / 10 / 04–05) w zależności od PM10 i `WLGW` | Przy dużym PM10 i niższej wilgotności widzialność spada przez smog, a nie przez mgłę. Pokazuje, czy etykieta `WID` ≤ 3 łapie też smog. |

---

## C. Testy statystyczne

> **Ważne przed wszystkimi testami:** godziny nie są od siebie niezależne – mgła o 05 UTC prawie na pewno oznacza mgłę o 06 UTC. Testy zakładające niezależne obserwacje (t-Student, chi-kwadrat na godzinach) dadzą wtedy **zbyt małe p-value**, czyli „istotne” wyniki, które wcale nie są istotne. Bezpieczniej testować na **dniach lub sezonach** albo używać bootstrapu blokowego (C9).

| Nr | Test | Na czym | Co sprawdza |
|---|---|---|---|
| C1 ⭐🧪 | **Test Manna-Kendalla + estymator nachylenia Sena** | roczna liczba dni z mgłą, średnia temperatura, średnie PM10 | Czy trend jest istotny. Lepszy od zwykłej regresji liniowej: nie zakłada rozkładu normalnego i jest odporny na pojedyncze nietypowe lata. Wynik: „zmiana o X dni na dekadę, p = …”. Pakiet `pymannkendall` lub `scipy.stats.kendalltau` (rok × wartość). |
| C2 🧪 | **Test Pettitta** (punkt zmiany) | roczna liczba dni z mgłą, częstość kodów `WID` | Czy w serii jest nagły skok. Szczególnie ciekawe: czy coś zmieniło się ok. 2011 r., gdy IMGW zaczęło zapisywać widzialność z automatu (`WIDA`)? Skok przy zmianie sprzętu to niejednorodność danych, a nie zmiana klimatu. Pakiet `pyhomogeneity`. |
| C3 ⭐🧪 | **Korelacja po usunięciu trendu** | roczne dni z mgłą vs. roczne PM10 | Wstępnie korelacja wynosi 0,66 – ale **obie serie maleją w czasie**, więc korelacja może być pozorna (każde dwie malejące serie są skorelowane). Trzeba ją policzyć na **różnicach rok do roku** (`.diff()`) albo na resztach po usunięciu trendu. Dopiero to mówi, czy w latach z większym PM10 jest więcej mgły. Świetny przykład pułapki statystycznej. |
| C4 🧪 | **Test U Manna-Whitneya** | PM10, `DEFICYT`, `FWR` przy mgle vs. bez (na wartościach dziennych) | Czy rozkłady różnią się istotnie. Nieparametryczny, bo PM10 i `FWR` nie mają rozkładu normalnego. |
| C5 🧪 | **Test chi-kwadrat niezależności** | sektor wiatru (8 kierunków + cisza) × mgła tak/nie | Czy kierunek wiatru wiąże się z mgłą (B5). Na dniach lub z poprawką na zależność godzin. |
| C6 🧪 | **Test Kołmogorowa-Smirnowa** | rozkład długości epizodów mgły: 2001–2012 vs. 2013–2025 | Czy mgły stały się nie tylko rzadsze, ale też krótsze. |
| C7 🧪 | **Rozkład geometryczny długości epizodów** | długości epizodów (A4) | Jeśli prawdopodobieństwo „mgła trwa dalej” jest stałe (78% co godzinę), długości mają rozkład geometryczny. Odstępstwo pokazuje, że mgła ma „pamięć” – np. mgła, która przetrwała noc, rozpada się po wschodzie Słońca. |
| C8 🧪 | **Autokorelacja (ACF) serii mgły** | godzinowa seria 0/1 w sezonie | Jak szybko mgła „zapomina” swój stan. Uzasadnia, ile godzin wstecz warto podawać modelowi (okno 48 h z README). `statsmodels.graphics.tsaplots.plot_acf`. |
| C9 🧪 | **Bootstrap blokowy** (losowanie całych sezonów lub tygodni zamiast pojedynczych godzin) | dowolna statystyka, np. różnica częstości mgły między dekadami, Brier score modelu | Przedziały ufności, które uwzględniają zależność godzin. Przyda się też na końcu do porównania 6 modeli: czy różnica wyników jest większa niż przypadkowa. |
| C10 🧪 | **Regresja logistyczna** mgła ~ `DEFICYT` + `FWR` + `NOG` + … | godziny sezonu | Prosty model z interpretacją: iloraz szans (*odds ratio*) mówi np. „każdy 1 °C deficytu mniej zwiększa szanse mgły X razy”. Dobry punkt odniesienia dla boostingu (`statsmodels.Logit`). |

> **Uwaga o wielu testach naraz:** jeśli przetestujemy 20 zmiennych na poziomie 0,05, średnio jedna wyjdzie „istotna” przez przypadek. Przy wielu testach warto użyć poprawki Bonferroniego (dzielimy 0,05 przez liczbę testów) albo Holma.

---

## D. Obliczenia i nowe cechy

| Nr | Obliczenie | Po co |
|---|---|---|
| D1 ⭐🔢 | **Wysokość Słońca, godzina wschodu i zachodu** dla Balic (50,08° N, 19,80° E), dla każdej godziny | Parametr 24 i 25 z README. Biblioteka `astral` lub `pvlib`. Bez tego model nie wie, że za 3 h wzejdzie Słońce. |
| D2 🔢 | **Godziny od zachodu Słońca** i **długość nocy** | Im dłuższa noc, tym więcej czasu na wychładzanie (parametr 25). |
| D3 🔢 | **Wilgotność względna z `TEMP` i `TPTR`** (wzór Magnusa) i porównanie z `WLGW` | Kontrola jakości danych: obie wartości powinny się zgadzać z dokładnością do kilku %. Duże różnice = błędy w danych. |
| D4 🔢 | **Wilgotność bezwzględna / właściwa** (g wody na kg powietrza) z `TPTR` i `PPPM` | Mówi, ile wody jest w powietrzu niezależnie od temperatury. Czy przed mgłą wilgoci przybywa (adwekcja), czy tylko spada temperatura (radiacja)? |
| D5 🔢 | **Wysokość poziomu kondensacji (LCL)** ≈ 125 m × (`TEMP` − `TPTR`) | Na jakiej wysokości powietrze unoszone z ziemi zaczyna się skraplać. LCL bliski 0 m = mgła. Ciekawe porównanie z kodem `HPOD`. |
| D6 🔢 | **Składowe wiatru u, v** z `FWR` i `KRWR` | Parametr 26. `u = −FWR·sin(KRWR)`, `v = −FWR·cos(KRWR)` (kąt w radianach); cisza (0) i wiatr zmienny (999) → u = v = 0. |
| D7 🔢 | **Godzina i dzień roku jako sin/cos** | Parametr 23: godzina 23 i 0 są obok siebie, a zwykła liczba tego nie pokazuje. |
| D8 🔢 | **Trendy za 1, 3, 6 h** dla `TPTR`, `WLGW`, `WID`, `PPPM` (wzorem `DT_3H`) | Parametr 22. Model musi wiedzieć, czy powietrze *zbliża się* do nasycenia. |
| D9 🔢 | **PM10 – średnia z ostatnich 24 h** i zmiana za 3 h | Smog narasta przez kilka dni; pojedyncza godzina jest „hałaśliwa”. |
| D10 🔢 | **Kontrola jakości danych**: czy `TPTR` ≤ `TEMP` zawsze, czy są skoki temperatury > 5 °C w 1 h, czy brakuje godzin, ile jest wartości specjalnych (999, 9) | Lepiej znaleźć błędy w danych teraz niż po wytrenowaniu modelu. |

---

## E. Analizy, które od razu pomagają przy modelach 🛠️

| Nr | Analiza | Po co |
|---|---|---|
| E1 ⭐🛠️ | **Wyniki baseline'ów**: Brier score i PR-AUC dla persystencji („za *h* godzin będzie tak jak teraz”) i klimatologii („częstość mgły dla tej godziny i miesiąca”), dla *h* = 1…5 | README, pułapka 4: bez tego nie wiadomo, czy model jest dobry. To pierwsza liczba, którą modele muszą pobić. |
| E2 ⭐🛠️ | **Częstość mgły w podziale na zbiory**: treningowy 2001–2018, walidacyjny 2019–2020, testowy 2021–2025 | Jeśli w zbiorze testowym mgły jest wyraźnie mniej (trend!), wyniki na nim będą inne niż na walidacji. Lepiej wiedzieć to przed treningiem. |
| E3 🛠️ | **Korelacje cech z mgłą za *h* godzin** dla różnych opóźnień (np. `DEFICYT` z chwili *t*, *t−3*, *t−6* vs. mgła w *t+1…t+5*) | Które godziny z okna 48 h niosą najwięcej informacji – podpowiedź, jakie opóźnienia brać do cech. |
| E4 🛠️ | **Informacja wzajemna (mutual information)** każdej cechy z etykietą | Jak korelacja, ale łapie też zależności nieliniowe (np. wiatr: za słaby i za silny przeszkadza mgle). `sklearn.feature_selection.mutual_info_classif`. |
| E5 🛠️ | **Ile jest „przejść”**: godziny, w których mgły nie ma w *t*, a jest w *t+h* (powstawanie) i odwrotnie (zanik), dla *h* = 1…5 | README, pułapka 2: to są przypadki, które naprawdę testują model. Warto znać ich liczbę w każdym zbiorze. |
| E6 🛠️ | **Macierz korelacji wszystkich cech** (mapa ciepła) | Silnie skorelowane cechy (np. `WLGW` i `DEFICYT`) – drzewom to nie szkodzi, ale utrudnia odczytanie ważności cech. |

---

## Od czego zacząć

Jeśli czasu jest mało, największy pożytek przy najmniejszej pracy dadzą:

1. **A1** – mapa ciepła godzina × miesiąc,
2. **B1** – prawdopodobieństwo mgły w funkcji deficytu punktu rosy,
3. **B3** – analiza złożona przed początkiem mgły,
4. **C1 + C3** – trend dni z mgłą i pułapka korelacji z PM10,
5. **E1** – wyniki baseline'ów (będą potrzebne i tak).

---

## Uwagi techniczne

- **Sezon:** do większości analiz bierzemy tylko wrzesień–marzec: `df[df["MC"].isin([9, 10, 11, 12, 1, 2, 3])]`.
- **Czas jest w UTC.** Wschód Słońca zimą to ok. 06–07 UTC (07–08 czasu polskiego).
- **PM10** jest puste (NaN) w 2001–2002 i w ok. 1,5% godzin później; w 2022 r. pochodzi tylko ze stacji Bulwarowa.
- **Biblioteki:** `scipy`, `statsmodels`, `scikit-learn`, `astral`, `pymannkendall` nie są jeszcze w `environment.yml`. Kto będzie ich potrzebował, zgłasza opiekunowi projektu, żeby dopisał je do pliku – wtedy wszyscy mają to samo środowisko.
- **Literatura:** Tardif R., Rasmussen R.M. (2007). Event-based climatology and typology of fog in the New York City region. *Journal of Applied Meteorology and Climatology*, 46, 1141–1168 – klasyczny algorytm podziału mgieł na typy (B8).
