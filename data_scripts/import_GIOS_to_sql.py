# Import godzinowych stężeń PM10 z GIOŚ (Kraków) do bazy SQLite – tabela GIOS_PM10.
# Struktura tabeli jest w schema.sql – ten skrypt tylko go uruchamia i wkłada dane.
# Uruchamianie (z dowolnego folderu, np. z głównego folderu projektu):  python data_scripts/import_GIOS_to_sql.py
# Wymaga biblioteki openpyxl (do czytania plików .xlsx) – jest w environment.yml.
# Czas działania: ok. 2 minuty (pliki .xlsx czyta się wolno).
#
# UWAGA: ten skrypt ZMIENIA baza.db – uruchamia go tylko opiekun projektu (zasada z README).
#
# -------------------------------------------------------------------------------------
#  SKĄD SĄ DANE I CO ROBI SKRYPT
# -------------------------------------------------------------------------------------
# Pliki raw_data/GIOŚ_PM10/RRRR_PM10_1g.xlsx z banku danych pomiarowych GIOŚ
# (https://powietrze.gios.gov.pl/pjp/archives). Jeden plik = jeden rok.
# Plik to tabela "szeroka": wiersz = godzina, kolumna = jedna stacja pomiarowa z całej Polski.
#
# Bierzemy dwie krakowskie stacje, które mierzą PM10 co godzinę przez cały okres 2003–2025:
#   - Kraków, Al. Krasińskiego (stacja przy ruchliwej ulicy, centrum) – brak całego 2022 r.,
#   - Kraków, ul. Bulwarowa (Nowa Huta, wschód miasta).
# PM10 w bazie = średnia z tych stacji, które w danej godzinie mają pomiar
# (gdy działa tylko jedna – jej wartość; gdy żadna – NULL).
#
# Na co trzeba uważać (i co skrypt poprawia):
#   1. 2001–2002: GIOŚ ma tylko średnie DOBOWE (pliki *_24g.xlsx) – pomijamy je, PM10 = NULL.
#   2. Czas: GIOŚ podaje czas CET = UTC+1 przez cały rok (bez czasu letniego; każdy rok ma
#      ciągłe 8760/8784 godzin), a godzina oznacza KONIEC okresu uśredniania
#      ("01:00" = średnia z 00:00–01:00 CET). IMGW podaje czas UTC.
#      Odejmujemy 1 h -> godzina UTC końca uśredniania. Wartość przypisana do godziny GG UTC
#      to średnia z godziny tuż PRZED obserwacją IMGW, więc nie zaglądamy w przyszłość.
#   3. Znaczniki czasu mają czasem "ułamki sekund" (np. 03:00:00.005) – zaokrąglamy do pełnej godziny.
#   4. Nagłówek ma 3 wiersze (do 2015 r.) albo 6 wierszy (od 2016 r.) – szukamy wiersza "Kod stacji".
#   5. Kody stacji zmieniły się w 2015 r. – niżej jest lista obu wersji kodu dla każdej stacji.
#   6. W niektórych latach liczby są tekstem z przecinkiem ("78,3245") – zamieniamy przecinek na kropkę.

import sqlite3
from pathlib import Path

import pandas as pd

# Ścieżki liczymy od położenia TEGO pliku (jak w import_IMGW_to_sql.py).
FOLDER = Path(__file__).resolve().parent                    # = data_scripts/
DANE = FOLDER.parent / "raw_data" / "GIOŚ_PM10"             # = <projekt>/raw_data/GIOŚ_PM10
SCHEMA = FOLDER / "schema.sql"
BAZA = FOLDER / "baza.db"

# Kody stacji: stary kod (do 2014 r.) i nowy kod (od 2015 r.) to ta sama stacja.
STACJE = {
    "PM10_KRAS": ["MpKrakowWIOSAKra6117", "MpKrakAlKras"],   # Al. Krasińskiego
    "PM10_BULW": ["MpKrakowWIOSBulw6118", "MpKrakBulwar"],   # ul. Bulwarowa
}
ROK_OD = 2003          # od tego roku GIOŚ ma dane godzinowe


def wczytaj_rok(plik):
    """Zwraca tabelę z kolumnami CZAS_UTC, PM10_KRAS, PM10_BULW dla jednego pliku .xlsx."""
    surowe = pd.read_excel(plik, header=None)

    # Wiersz z kodami stacji (w kolumnie 0 jest napis "Kod stacji")
    wiersz_kodow = surowe.index[surowe[0].astype(str).str.strip() == "Kod stacji"][0]
    kody = surowe.iloc[wiersz_kodow].astype(str).str.strip()

    # Wiersze z danymi = te, w których kolumna 0 jest datą (pomija wszystkie wiersze nagłówka)
    czas = pd.to_datetime(surowe[0], errors="coerce", format="mixed")
    dane = surowe.loc[czas.notna()]
    czas = czas[czas.notna()]

    wynik = pd.DataFrame({
        # CET (UTC+1) -> UTC; round("h") usuwa ułamki sekund ze znaczników czasu
        "CZAS_UTC": czas.dt.round("h") - pd.Timedelta(hours=1),
    })
    for nazwa, warianty_kodu in STACJE.items():
        kolumny = kody.index[kody.isin(warianty_kodu)]
        if len(kolumny) == 0:          # stacja nie mierzyła w tym roku (np. Al. Krasińskiego w 2022)
            wynik[nazwa] = float("nan")
            continue
        tekst = dane[kolumny[0]].astype(str).str.replace(",", ".")
        wynik[nazwa] = pd.to_numeric(tekst, errors="coerce")   # puste / "nan" -> NaN
    return wynik


# 1. Wczytujemy wszystkie lata z danymi godzinowymi
lata = []
for plik in sorted(DANE.glob("*_PM10_1g.xlsx")):
    if int(plik.name[:4]) < ROK_OD:
        continue
    rok = wczytaj_rok(plik)
    lata.append(rok)
    print(plik.name, len(rok), "godzin,",
          "braki: Krasińskiego", rok["PM10_KRAS"].isna().sum(), "| Bulwarowa", rok["PM10_BULW"].isna().sum())

df = pd.concat(lata, ignore_index=True)
df = df.drop_duplicates("CZAS_UTC").sort_values("CZAS_UTC")

# 2. Średnia z dostępnych stacji (mean pomija NaN; gdy obie są NaN, wynik też jest NaN)
df["PM10"] = df[["PM10_KRAS", "PM10_BULW"]].mean(axis=1).round(1)

# 3. Rozbijamy czas na ROK, MC, DZ, GG – tak jak w tabeli IMGW, żeby dało się je połączyć
df["ROK"] = df["CZAS_UTC"].dt.year
df["MC"] = df["CZAS_UTC"].dt.month
df["DZ"] = df["CZAS_UTC"].dt.day
df["GG"] = df["CZAS_UTC"].dt.hour
df = df[["ROK", "MC", "DZ", "GG", "PM10_KRAS", "PM10_BULW", "PM10"]]
df = df.astype(object).where(df.notna(), None)      # NaN -> None, żeby SQLite zapisał NULL

# 4. Zapis do bazy: usuwamy starą tabelę GIOS_PM10 i tworzymy ją od nowa według schema.sql.
#    Tabela IMGW zostaje nietknięta (w schema.sql jest CREATE TABLE IF NOT EXISTS).
con = sqlite3.connect(BAZA)
con.execute("DROP TABLE IF EXISTS GIOS_PM10")
with open(SCHEMA, encoding="utf-8") as f:
    con.executescript(f.read())
con.executemany(
    "INSERT INTO GIOS_PM10 (ROK, MC, DZ, GG, PM10_KRAS, PM10_BULW, PM10) VALUES (?, ?, ?, ?, ?, ?, ?)",
    df.itertuples(index=False, name=None),
)
con.commit()
print("Zapisano", con.execute("SELECT COUNT(*) FROM GIOS_PM10").fetchone()[0], "godzin do tabeli GIOS_PM10")
con.close()
