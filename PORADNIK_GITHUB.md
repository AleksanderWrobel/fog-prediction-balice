# Poradnik dla nowych osób w projekcie

Ten poradnik jest dla osób, które **nigdy nie pracowały z GitHubem**. Prowadzi krok po kroku od założenia konta do wysłania pierwszej własnej zmiany do projektu. Zakłada, że pracujesz na **Windowsie** i w **VS Code**.

O samym projekcie (cel, dane, modele) przeczytasz w [README.md](README.md). Tutaj są narzędzia i sposób pracy.

---

## Spis treści

1. [Co to jest Git i GitHub](#1-co-to-jest-git-i-github)
2. [Konto na GitHubie](#2-konto-na-githubie)
3. [Instalacja programów](#3-instalacja-programów)
4. [Pobranie projektu na komputer](#4-pobranie-projektu-na-komputer)
5. [Środowisko conda](#5-środowisko-conda)
6. [Jak poruszać się po projekcie](#6-jak-poruszać-się-po-projekcie)
7. [Codzienna praca z Gitem](#7-codzienna-praca-z-gitem)
8. [Zasady projektu](#8-zasady-projektu)
9. [Gdy coś pójdzie nie tak](#9-gdy-coś-pójdzie-nie-tak)
10. [Ściągawka](#10-ściągawka)

---

## 1. Co to jest Git i GitHub

- **Git** to program na Twoim komputerze, który zapamiętuje historię zmian w plikach. Każdy zapis to **commit**, czyli coś jak punkt zapisu w grze. Z każdego commita można później odzyskać pliki.
- **GitHub** to strona internetowa, na której leży wspólna kopia projektu (**repozytorium**, w skrócie „repo”). Każdy ma u siebie własną kopię, a GitHub służy do wymieniania się zmianami.

Najważniejsze słowa, które będą się powtarzać:

| Słowo | Co znaczy |
|---|---|
| **repozytorium (repo)** | folder projektu razem z całą historią zmian |
| **clone** | pierwsze pobranie repo z GitHuba na komputer |
| **commit** | zapisanie paczki zmian w historii, z krótkim opisem |
| **push** | wysłanie Twoich commitów na GitHuba |
| **pull** | pobranie z GitHuba zmian innych osób |
| **branch (gałąź)** | osobna „linia” pracy, w której możesz zmieniać pliki bez ruszania głównej wersji |
| **main** | główna gałąź projektu, czyli wersja, z której korzystają wszyscy |
| **pull request (PR)** | prośba o dołączenie Twojej gałęzi do `main`. Opiekun ją przegląda i zatwierdza |

Ważne: **commit zapisuje zmiany tylko u Ciebie.** Inni zobaczą je dopiero po **push**.

---

## 2. Konto na GitHubie

1. Wejdź na <https://github.com/signup> i załóż konto: adres e-mail, hasło, nazwa użytkownika. Nazwa będzie widoczna dla innych, więc najlepiej taka, po której łatwo Cię rozpoznać (np. `jkowalski`).
2. Potwierdź adres e-mail (GitHub wyśle kod).
3. **Włącz weryfikację dwuetapową (2FA).** GitHub i tak jej wymaga od osób, które wysyłają kod. Wejdź w: zdjęcie profilowe (prawy górny róg) → **Settings** → **Password and authentication** → **Enable two-factor authentication**. Najprościej użyć aplikacji w telefonie (GitHub Mobile, Microsoft Authenticator albo Google Authenticator).
   > ⚠️ **Zapisz kody odzyskiwania (recovery codes)** w bezpiecznym miejscu. Bez nich, po zgubieniu telefonu, stracisz dostęp do konta.
4. **Wyślij swoją nazwę użytkownika opiekunowi projektu.** Opiekun doda Cię do repozytorium.
5. **Przyjmij zaproszenie.** Przyjdzie e-mail „… invited you to collaborate”. Kliknij **Accept invitation**. Zaproszenie jest ważne **7 dni**. Jeśli maila nie widać, wejdź na <https://github.com/AleksanderWrobel/fog-prediction-balice/invitations>.

---

## 3. Instalacja programów

Potrzebujesz trzech programów: **Git**, **VS Code** i **Miniforge** (czyli condy). Każdy instalujesz tylko raz.

### 3.1 Git

1. Pobierz instalator z <https://git-scm.com/downloads/win> (**Git for Windows**, wersja 64-bit).
2. W instalatorze wszędzie możesz klikać **Next**, oprócz dwóch ekranów:
   - **Choosing the default editor used by Git** → wybierz **Use Visual Studio Code as Git's default editor**,
   - **Adjusting the name of the initial branch** → wybierz **Override …** i wpisz `main`.
3. Pozostałe ustawienia zostaw domyślne, bo są dobre. Między innymi:
   - końce linii: **Checkout Windows-style, commit Unix-style**,
   - logowanie: **Git Credential Manager**. Dzięki niemu logujesz się do GitHuba przez przeglądarkę i nie musisz wpisywać hasła w konsoli.

### 3.2 VS Code

1. Pobierz z <https://code.visualstudio.com/> i zainstaluj. Zostaw zaznaczone **Add to PATH**. Warto też zaznaczyć opcje **Open with Code** (dodają VS Code do menu prawego przycisku myszy).
2. Uruchom VS Code i zainstaluj rozszerzenia: ikona klocków po lewej (**Extensions**, `Ctrl+Shift+X`) → wyszukaj → **Install**:
   - **Python** (od Microsoft). Instaluje też Pylance i debugger,
   - **Python Environments** (od Microsoft). Ułatwia wybór środowiska conda. Projekt ma już do niego ustawienia w `.vscode/settings.json`,
   - opcjonalnie **Polish Language Pack**, jeśli wolisz menu po polsku. W poradniku nazwy są po angielsku.

### 3.3 Miniforge (conda)

**Conda** instaluje Pythona i biblioteki (pandas, numpy, matplotlib…) w osobnym **środowisku**. Dzięki temu wszyscy w projekcie mają te same wersje i kod, który działa u jednej osoby, działa też u innych. **Miniforge** to darmowa, lekka wersja condy.

1. Wejdź na <https://github.com/conda-forge/miniforge>, w sekcji **Download** pobierz plik **`Miniforge3-Windows-x86_64.exe`**.
2. Uruchom instalator:
   - **Install for: Just Me** (zalecane),
   - **Folder instalacji:** zostaw domyślny (`C:\Users\<nazwa>\miniforge3`).
     > ⚠️ Jeśli Twoja nazwa użytkownika Windows ma **spację albo polskie znaki** (np. `C:\Users\Łukasz Nowak`), zainstaluj do **`C:\miniforge3`**. Conda źle znosi takie ścieżki.
   - Opcji **Add Miniforge3 to my PATH** nie zaznaczaj, tak jak zaleca instalator.
3. Po instalacji w menu Start pojawi się **Miniforge Prompt**. To konsola, w której conda zawsze działa.
4. **Żeby conda działała też w terminalu VS Code**, otwórz **Miniforge Prompt** i wpisz:
   ```
   conda init powershell
   ```
   Potem zamknij i otwórz VS Code. Jeśli terminal VS Code pokaże czerwony błąd o *running scripts is disabled on this system*, otwórz **PowerShell** z menu Start i wpisz (jednorazowo):
   ```
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```
   Potwierdź `T` lub `Y` i uruchom VS Code ponownie.

### 3.4 Przedstaw się Gitowi

Git podpisuje każdy commit imieniem i adresem e-mail. Otwórz terminal w VS Code (**Terminal → New Terminal** albo `` Ctrl+` ``) i wpisz, podając swoje dane:

```
git config --global user.name "Imię Nazwisko"
git config --global user.email "adres@uzywany.na.githubie"
```

Adres e-mail powinien być ten sam co na GitHubie. Wtedy commity będą połączone z Twoim kontem. To robisz raz na komputer.

---

## 4. Pobranie projektu na komputer

### 4.1 Gdzie trzymać projekt

Utwórz folder na projekty, np. **`C:\Projekty`**.

> ⚠️ **Nie trzymaj projektu na OneDrive.** Na wielu komputerach z Windowsem folder **Pulpit** i **Dokumenty** są automatycznie synchronizowane z OneDrive. OneDrive i Git przeszkadzają sobie nawzajem: blokują pliki, tworzą kopie „-Konflikt” i potrafią uszkodzić folder `.git`. Jeśli ścieżka zaczyna się od `C:\Users\<nazwa>\OneDrive\...`, wybierz inne miejsce.

### 4.2 Clone w VS Code

1. Otwórz VS Code.
2. Naciśnij `Ctrl+Shift+P`, wpisz **Git: Clone** i naciśnij Enter.
3. Wklej adres repozytorium:
   ```
   https://github.com/AleksanderWrobel/fog-prediction-balice.git
   ```
4. Wybierz folder `C:\Projekty`. Git utworzy w nim folder **`fog-prediction-balice`**.
5. Gdy pojawi się pytanie o logowanie do GitHuba, zaloguj się w przeglądarce, która się otworzy.
6. Kliknij **Open**, żeby otworzyć projekt. Jeśli VS Code zapyta *Do you trust the authors…?*, kliknij **Yes, I trust the authors**.

To samo w terminalu:
```
cd C:\Projekty
git clone https://github.com/AleksanderWrobel/fog-prediction-balice.git
```

> Clone robisz **tylko raz**. Później projekt otwierasz przez **File → Open Folder…** → `C:\Projekty\fog-prediction-balice`, a zmiany innych pobierasz przez **pull** (rozdział 7).

---

## 5. Środowisko conda

Lista bibliotek projektu jest w pliku **`environment.yml`**. Środowisko nazywa się **`mgla-balice`**.

### 5.1 Utworzenie środowiska (jednorazowo)

W VS Code otwórz terminal (`` Ctrl+` ``). Sprawdź, że jesteś w folderze projektu: ścieżka przed kursorem powinna kończyć się na `fog-prediction-balice`. Wpisz:

```
conda env create -f environment.yml
```

Potrwa to kilka minut, bo conda pobiera Pythona i biblioteki. Potem:

```
conda activate mgla-balice
```

Na początku linii w terminalu pojawi się `(mgla-balice)`. To znaczy, że środowisko jest włączone.

### 5.2 Wybór środowiska w VS Code

VS Code musi wiedzieć, którego Pythona używać do uruchamiania skryptów:

1. `Ctrl+Shift+P` → **Python: Select Interpreter**,
2. wybierz pozycję z **`mgla-balice`** w nazwie.

Wybrane środowisko widać w prawym dolnym rogu okna. Jeśli go tam nie ma, otwórz dowolny plik `.py`.

### 5.3 Sprawdzenie, czy wszystko działa

```
python data_analysis/Instrukcja_do_analizy_danych.py
```

Skrypt powinien wypisać informacje o danych i pokazać wykresy. Okno wykresu trzeba zamknąć, żeby skrypt poszedł dalej. Jeśli zadziałało, wszystko jest gotowe.

### 5.4 Gdy `environment.yml` się zmieni

Jeśli ktoś dodał nową bibliotekę (po `git pull` zmienił się plik `environment.yml`), zaktualizuj środowisko:

```
conda env update -f environment.yml --prune
```

**Nie instaluj bibliotek na własną rękę** (`pip install …`, `conda install …`) do kodu, który wysyłasz do projektu. U innych tej biblioteki nie będzie i ich kod przestanie działać. Jeśli potrzebujesz nowej biblioteki, dopisz ją do `environment.yml` w tej samej zmianie albo zgłoś opiekunowi.

---

## 6. Jak poruszać się po projekcie

### 6.1 Foldery

| Folder / plik | Co tam jest | Czy tu piszesz? |
|---|---|---|
| `README.md` | opis projektu, danych, modeli i pułapek. **Przeczytaj, zanim zaczniesz** | tylko po uzgodnieniu |
| `PORADNIK_GITHUB.md` | ten poradnik | — |
| `environment.yml` | lista bibliotek dla condy | gdy dodajesz bibliotekę |
| `data_scripts/` | baza `baza.db`, jej schemat `schema.sql`, skrypty importu i funkcja `data_import()` | **nie** (zmienia tylko opiekun) |
| `data_analysis/` | analizy i wykresy, `Instrukcja_do_analizy_danych.py` | **tak**, tu dodajesz swoje analizy |
| `prediction/` | przygotowanie danych do treningu, modele, trening, testy | tak, według podziału zadań |
| `raw_data/` | surowe pliki IMGW i GIOŚ. **Nie ma go w repo**, potrzebny tylko opiekunowi | — |

### 6.2 Przydatne miejsca w VS Code

| Gdzie | Skrót | Do czego |
|---|---|---|
| **Explorer** (ikona kartek, lewy pasek) | `Ctrl+Shift+E` | drzewo plików projektu |
| **Search** (lupa) | `Ctrl+Shift+F` | szukanie tekstu we wszystkich plikach |
| **Source Control** (ikona rozgałęzienia) | `Ctrl+Shift+G` | Git: zmienione pliki, commit, push, pull |
| **Terminal** | `` Ctrl+` `` | konsola w folderze projektu |
| **Paleta poleceń** | `Ctrl+Shift+P` | wyszukiwarka wszystkich poleceń VS Code |
| szybkie otwarcie pliku | `Ctrl+P` | wpisz kawałek nazwy pliku |
| przycisk ▷ (prawy górny róg pliku `.py`) | `F5` (z debuggerem) | uruchamia otwarty skrypt |

### 6.3 Wczytywanie danych we własnym skrypcie

Dane z bazy **zawsze** wczytujemy funkcją `data_import()`. Opis każdej kolumny jest na początku pliku `data_scripts/data_import_from_sql.py`. Szablon nowego skryptu w `data_analysis/`:

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))   # folder projektu, żeby Python znalazł data_scripts

from data_scripts.data_import_from_sql import data_import

df = data_import()      # tabela pandas: wszystkie godziny 2001–2025, 20 kolumn

print(df.shape)
print(df.head())
```

Funkcja otwiera bazę **tylko do odczytu**, więc nie da się nią niczego zepsuć.

---

## 7. Codzienna praca z Gitem

### 7.1 Jak to działa

```
 Twój komputer                                          GitHub
 ─────────────────────────────────────────────          ───────────
 zmieniasz pliki → stage (+) → commit  ── push ──▶      repozytorium
                                       ◀── pull ──
```

- **stage** (przycisk `+`) to wybór plików, które mają wejść do commita,
- **commit** zapisuje wybrane zmiany z opisem, na razie tylko u Ciebie,
- **push** wysyła commity na GitHuba,
- **pull** pobiera nowe commity od innych.

### 7.2 Gałęzie i pull requesty: dlaczego tak pracujemy

Nie wysyłamy zmian prosto do `main`. Każde zadanie robisz na **własnej gałęzi** i zgłaszasz ją przez **pull request**:

- `main` zawsze działa, więc nikt nie pobierze cudzego niedokończonego kodu,
- opiekun widzi zmiany przed dołączeniem i może coś podpowiedzieć,
- dwie osoby nie nadpisują sobie nawzajem pracy.

### 7.3 Krok po kroku w VS Code

**Na początku pracy:**

1. Sprawdź w lewym dolnym rogu, na jakiej gałęzi jesteś. Jeśli nie na `main`, kliknij nazwę gałęzi i wybierz `main`.
2. **Pobierz najnowszą wersję:** w panelu **Source Control** (`Ctrl+Shift+G`) kliknij `…` → **Pull**. Możesz też kliknąć ikonę strzałek obok nazwy gałęzi w lewym dolnym rogu.
3. **Utwórz gałąź na swoje zadanie:** kliknij nazwę gałęzi w lewym dolnym rogu → **+ Create new branch…** → wpisz nazwę, np. `analiza-wiatru` albo `etykiety-mgly`. Krótko, małymi literami, bez polskich znaków i spacji.

**W trakcie pracy:**

4. Zmieniaj i zapisuj pliki (`Ctrl+S`). W panelu **Source Control** pojawią się zmienione pliki:
   - **M** (modified) – zmieniony,
   - **U** (untracked) – nowy plik, którego Git jeszcze nie zna,
   - **D** (deleted) – usunięty.

   Kliknij plik, żeby zobaczyć **dokładnie, co się zmieniło**: na czerwono to, co usunięte, na zielono to, co dodane. **Zawsze to przejrzyj przed commitem.**
5. Kliknij **`+`** przy plikach, które mają wejść do commita (stage).
6. W polu **Message** wpisz krótki opis i kliknij **Commit**.
7. Kliknij **Publish Branch** (za pierwszym razem), a później **Sync Changes**. To wysyła commity na GitHuba (push).

**Gdy zadanie jest gotowe:**

8. Wejdź na stronę repo na GitHubie. Pojawi się żółty pasek z przyciskiem **Compare & pull request**. Kliknij go.
   Jeśli paska nie ma: zakładka **Pull requests** → **New pull request** → w polu **compare** wybierz swoją gałąź.
9. Napisz, **co zrobiłeś i dlaczego**. Jeśli to wykres albo analiza, opisz w kilku zdaniach, co z niej wychodzi. Kliknij **Create pull request**.
10. Opiekun przejrzy zmiany. Może poprosić o poprawki: wtedy poprawiasz pliki na **tej samej gałęzi**, robisz commit i push, a pull request zaktualizuje się sam. Gdy wszystko jest dobrze, opiekun kliknie **Merge**.
11. Po scaleniu przełącz się na `main` i zrób **Pull**. Twoje zmiany są już w głównej wersji. Do następnego zadania utwórz nową gałąź (krok 3).

### 7.4 To samo w terminalu

```
git switch main                   # przejdź na main
git pull                          # pobierz najnowsze zmiany
git switch -c analiza-wiatru      # utwórz nową gałąź i przejdź na nią

git status                        # co się zmieniło?
git diff                          # dokładne zmiany w plikach
git add data_analysis/wiatr.py    # stage wybranego pliku
git commit -m "Dodaj analizę kierunku wiatru przy mgle"
git push -u origin analiza-wiatru # pierwszy push nowej gałęzi (później wystarczy: git push)
```

### 7.5 Dobre commity

- **Mały commit = jedna sprawa.** „Dodaj wykres PM10 przy mgle” jest lepsze niż „zmiany” z 10 plikami naraz.
- **Opis mówi, co i po co**, np. „Popraw sezon w analizie temperatury (IX–III zamiast całego roku)”. Opis „poprawki” albo „asdf” po tygodniu nic nikomu nie powie.
- **Rób commit często**, nawet kilka razy w trakcie pracy. Każdy commit to punkt, do którego można wrócić.
- Przed commitem sprawdź, czy skrypt w ogóle się uruchamia.

---

## 8. Zasady projektu

### 8.1 Baza danych `baza.db`

> ⚠️ **Z bazy tylko czytamy.** Szczegóły są w README, w rozdziale *Jak zacząć*.

- Nie uruchamiaj `data_scripts/import_IMGW_to_sql.py` ani `import_GIOS_to_sql.py` i nie edytuj bazy ręcznie (np. programem DB Browser).
- **Nie wysyłaj `baza.db` w swoim commicie.** Jeśli w **Source Control** widzisz `baza.db` ze znakiem **M**, cofnij zmianę: kliknij plik prawym przyciskiem → **Discard Changes**, albo w terminalu:
  ```
  git restore data_scripts/baza.db
  ```
- Potrzebujesz nowej kolumny albo cechy w bazie? Zgłoś to opiekunowi. Po aktualizacji wystarczy `git pull`.

Dlaczego: `baza.db` to plik binarny. Gdy dwie osoby wyślą różne wersje, Git nie potrafi ich połączyć i jedną trzeba wyrzucić.

### 8.2 Czego nie wysyłamy na GitHuba

- **Dużych plików.** GitHub ostrzega przy 50 MB i blokuje pliki powyżej 100 MB. Surowe dane (`raw_data/`) są poza repo celowo i Git je ignoruje (plik `.gitignore`).
- **Wyników, które da się odtworzyć skryptem**: wygenerowanych tabel, wielu obrazków wykresów, zapisanych modeli. Wysyłamy kod, który je tworzy. Jeśli jakiś wykres ma trafić do repo (np. do sprawozdania), uzgodnij to z opiekunem.
- **Haseł, tokenów, kluczy API.** Nigdy, nawet „na chwilę”. Historia Gita pamięta wszystko i usunięcie pliku nie usuwa go z historii.
- **Plików śmieci**: `__pycache__/` i podobnych. `.gitignore` już je pomija.

### 8.3 Praca w zespole

- **Rób pull przed rozpoczęciem pracy.** Im starsza Twoja kopia, tym większa szansa na konflikt.
- **Jedna osoba = jeden plik.** Jeśli dwie osoby zmieniają ten sam plik w tym samym czasie, powstają konflikty. Nowe analizy rób w **nowych plikach** w `data_analysis/`, np. `wind_data_analysis.py`. Nie dopisuj ich do cudzych.
- **Cudzy plik zmieniaj po uzgodnieniu** z jego autorem albo przez pull request z opisem, co i dlaczego zmieniasz.
- **Pytaj.** Lepiej zapytać, niż zgadywać z Gitem. Większość błędów da się naprawić, jeśli nic nie zostało „przepchnięte na siłę”.

### 8.4 Zasady pracy z danymi (ważne dla wyników)

To skrót najważniejszych pułapek. Pełna wersja jest w README, w rozdziale 10.

- **Czas jest w UTC**, a nie w czasie polskim (zimą UTC+1, latem UTC+2). Godzina `GG` = 6 to 7:00 zimą i 8:00 latem.
- **Mgła = `WID` ≤ 3**, czyli widzialność < 1000 m. To etykieta naszych modeli.
- **Kody to nie liczby.** `POGB`, `WID` i `HPOD` to kody, a nie wartości do uśredniania. Średnia z `POGB` nie ma sensu.
- **`NaN` to brak danych**, a nie zero. Zanim coś uzupełnisz, sprawdź w opisie kolumny (`data_import_from_sql.py`), **dlaczego** jest brak.
- **Nie mieszaj danych losowo** przy podziale na zbiory. Dzielimy po latach: trening 2001–2018, walidacja 2019–2023, test 2024–2025.
- **Zbioru testowego (2024–2025) nie oglądamy** przy budowie i strojeniu modeli. Używamy go dopiero na samym końcu. Inaczej wyniki wyjdą zawyżone.

---

## 9. Gdy coś pójdzie nie tak

### 9.1 Częste problemy

| Objaw | Przyczyna i rozwiązanie |
|---|---|
| `conda : The term 'conda' is not recognized…` | Terminal nie zna condy. Wykonaj rozdział 3.3, krok 4 (`conda init powershell`) albo użyj **Miniforge Prompt**. |
| `… running scripts is disabled on this system` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` w PowerShell (rozdział 3.3, krok 4). |
| `ModuleNotFoundError: No module named 'pandas'` | Skrypt uruchamia zły Python. Wybierz `mgla-balice` (punkt 5.2) i włącz środowisko w terminalu: `conda activate mgla-balice`. |
| wpisanie `python` otwiera **Microsoft Store** | Środowisko conda nie jest włączone, więc Windows podsuwa swój skrót. `conda activate mgla-balice`. |
| `ModuleNotFoundError: No module named 'data_scripts'` | W skrypcie brakuje linii `sys.path.append(...)` z szablonu (punkt 6.3). |
| `no such table: IMGW_cechy` albo `unable to open database file` | Brak pliku `data_scripts/baza.db`. Sprawdź, czy projekt jest pobrany w całości (`git pull`), i nie przenoś skryptów `data_scripts/` w inne miejsce. |
| `baza.db` widoczna jako zmieniona (**M**) | `git restore data_scripts/baza.db` (punkt 8.1). |
| push odrzucony: `rejected … fetch first` | Na GitHubie są nowsze zmiany. Zrób **Pull**, potem jeszcze raz **Push**. |
| push: `Permission denied` / `403` | Nie przyjęte zaproszenie do repo (rozdział 2, krok 5) albo logujesz się na inne konto. |
| ostrzeżenie `LF will be replaced by CRLF` | Nieszkodliwe. Git dopasowuje końce linii między Windowsem a Linuksem. |
| skrypt „zawiesza się” po pokazaniu wykresu | Skrypt czeka na zamknięcie okna z wykresem. Zamknij je, a skrypt pójdzie dalej. |

### 9.2 Konflikt (merge conflict)

Konflikt powstaje, gdy Ty i ktoś inny zmieniliście **te same linie** tego samego pliku. Git nie wie, która wersja jest dobra, więc pyta Ciebie.

W VS Code plik z konfliktem ma literę **!** i kolorowe fragmenty:
- **Current Change** – Twoja wersja,
- **Incoming Change** – wersja z GitHuba.

Nad każdym fragmentem są przyciski: **Accept Current**, **Accept Incoming**, **Accept Both**. Wybierz właściwą wersję albo popraw ręcznie, zapisz plik, kliknij `+` (stage), a potem **Commit**.

> Jeśli nie wiesz, którą wersję wybrać, **nie zgaduj**. Zapytaj autora drugiej zmiany albo opiekuna.

### 9.3 Cofanie zmian

| Chcę… | Jak |
|---|---|
| wyrzucić niezapisane w commicie zmiany w jednym pliku | prawy przycisk na pliku w **Source Control** → **Discard Changes**, albo `git restore nazwa_pliku` |
| cofnąć ostatni commit, który **nie** był jeszcze wysłany (zmiany zostaną w plikach) | `git reset --soft HEAD~1` |
| cofnąć commit, który **już** jest na GitHubie | `git revert <numer commita>`. Tworzy nowy commit, który odwraca zmiany, a historia zostaje |

### 9.4 Czego nie robić

- ❌ **`git push --force`.** Nadpisuje historię na GitHubie i może skasować pracę innych.
- ❌ **Usuwanie folderu `.git`.** To cała historia projektu. Folder jest ukryty, więc lepiej go po prostu nie ruszać.
- ❌ **Kopiowanie projektu „na boku”** (`projekt_kopia`, `projekt_nowy`) zamiast tworzenia gałęzi. Po tygodniu nikt nie wie, która wersja jest właściwa.
- ❌ **„Naprawianie” przez usunięcie i ponowne sklonowanie**, gdy masz niewysłane zmiany. Stracisz je. Najpierw zapytaj.

---

## 10. Ściągawka

| Co chcę zrobić | VS Code | Terminal |
|---|---|---|
| pobrać projekt (raz) | `Ctrl+Shift+P` → **Git: Clone** | `git clone https://github.com/AleksanderWrobel/fog-prediction-balice.git` |
| włączyć środowisko | wybór interpretera (punkt 5.2) | `conda activate mgla-balice` |
| pobrać zmiany innych | **Source Control** → `…` → **Pull** | `git pull` |
| nowa gałąź | lewy dolny róg → **Create new branch…** | `git switch -c nazwa-galezi` |
| zmiana gałęzi | lewy dolny róg → nazwa gałęzi | `git switch main` |
| zobaczyć zmiany | **Source Control** → kliknij plik | `git status`, `git diff` |
| commit | `+` przy plikach → opis → **Commit** | `git add plik` → `git commit -m "opis"` |
| wysłać zmiany | **Sync Changes** / **Publish Branch** | `git push` |
| historia projektu | **Source Control** → sekcja **Graph** (albo zakładka **Timeline** w Explorerze dla jednego pliku) | `git log --oneline` |
| zaktualizować środowisko | — | `conda env update -f environment.yml --prune` |

---

Masz pytanie albo coś w tym poradniku jest niejasne? Napisz do opiekuna projektu. Poprawki do poradnika też zgłaszamy przez pull request.
