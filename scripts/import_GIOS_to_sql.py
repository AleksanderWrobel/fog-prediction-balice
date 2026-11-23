# Import godzinowego PM10 GIOŚ (Kraków, Al. Krasińskiego) do bazy SQLite.
# Struktura tabel jest w schema.sql – ten skrypt tylko go uruchamia i wkłada dane.
# Uruchamiać z głównego folderu projektu, w środowisku z openpyxl:
#   conda activate python
#   python scripts/import_GIOS_to_sql.py
#
# Co trzeba wiedzieć o plikach GIOŚ:
# - W każdym pliku jeden arkusz: wiersz "Kod stacji" z kodami stacji w kolumnach,
#   potem kilka wierszy opisu, potem dane (w pierwszej kolumnie data i godzina).
#   Liczba wierszy opisu zmienia się między latami, więc szukamy ich po treści.
# - Al. Krasińskiego ma dwa kody: do 2014 r. "MpKrakowWIOSAKra6117", od 2015 "MpKrakAlKras".
# - Wartości to liczby albo (2016–2018) tekst z przecinkiem, np. "78,3245".
# - W 2015 r. godziny mają "dryf" (np. 03:00:00.005), więc zaokrąglamy do pełnej godziny.
# - Czas w plikach to CET (UTC+1, bez czasu letniego), a godzina oznacza KONIEC
#   okresu uśredniania: "01:00" = średnia z 00:00–01:00 CET.
#   Zapisujemy czas UTC = CET − 1 h (wciąż jako koniec godziny), np. "01:00 CET" -> "00:00 UTC".
#   Dzięki temu wiersz o godzinie t zawiera tylko pomiary sprzed t – nie "zagląda w przyszłość".
# - Pliki *_24g (2001–2002) to średnie dobowe – tabela GIOS jest godzinowa, więc je pomijamy.

import datetime as dt
import sqlite3
import warnings
from pathlib import Path

import openpyxl

DANE = Path("dane/GIOŚ_PM10")
SCHEMA = "schema.sql"
BAZA = "baza.db"
KODY_STACJI = {"MpKrakowWIOSAKra6117", "MpKrakAlKras"}    # stary i nowy kod Al. Krasińskiego

# openpyxl ostrzega o nagłówkach/stopkach wydruku w części plików – nie dotyczy to danych
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def liczba(v):
    """Zamienia komórkę Excela na float albo None (brak pomiaru)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip().replace(",", "."))     # "78,3245" -> 78.3245
    except ValueError:
        return None


def do_pelnej_godziny(t):
    """2015-01-01 03:00:00.005 -> 2015-01-01 03:00:00"""
    return (t + dt.timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)


con = sqlite3.connect(BAZA)
with open(SCHEMA, encoding="utf-8") as f:
    con.executescript(f.read())
con.execute("DELETE FROM GIOS")     # czyścimy tylko swoją tabelę

for plik in sorted(DANE.glob("*_PM10_1g.xlsx")):
    wb = openpyxl.load_workbook(plik, read_only=True)   # read_only = szybciej i mniej pamięci
    arkusz = wb.worksheets[0]

    kolumna = None      # numer kolumny z Al. Krasińskiego
    wiersze = []
    for r in arkusz.iter_rows(values_only=True):
        if r[0] == "Kod stacji":
            for j, kod in enumerate(r):
                if kod in KODY_STACJI:
                    kolumna = j
        elif isinstance(r[0], dt.datetime) and kolumna is not None:
            utc = do_pelnej_godziny(r[0]) - dt.timedelta(hours=1)
            wiersze.append((utc.year, utc.month, utc.day, utc.hour, liczba(r[kolumna])))
    wb.close()

    if kolumna is None:
        print(f"{plik.name}: brak stacji Al. Krasińskiego w pliku – pomijam")
        continue

    con.executemany("INSERT INTO GIOS (ROK, MC, DZ, GG, PM10) VALUES (?, ?, ?, ?, ?)", wiersze)
    braki = sum(w[4] is None for w in wiersze)
    print(f"{plik.name}: {len(wiersze)} godzin, w tym {braki} bez pomiaru")

con.commit()
con.close()
