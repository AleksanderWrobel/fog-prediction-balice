# Import danych terminowych SYNOP IMGW (Kraków-Balice) do bazy SQLite.
# Struktura tabel jest w schema.sql – ten skrypt tylko go uruchamia i wkłada dane.
# Uruchamiać z głównego folderu projektu:  python scripts/import_IMGW_to_sql.py

import csv
import sqlite3
from pathlib import Path

DANE = Path("dane/IMGW_PIB_dane_terminowe_SYNOP")
SCHEMA = "schema.sql"
BAZA = "baza.db"

# 1. Nazwy 107 kolumn CSV z s_t_format.txt (pliki CSV nie mają nagłówka)
KOLUMNY = []        # lista na nazwy kolumn, w tej samej kolejności co w plikach CSV
with open(DANE / "s_t_format.txt", encoding="cp1250") as f:
    for linia in f:
        if linia.strip():                       # pomijamy puste linie
            KOLUMNY.append(linia.split()[0])    # pierwsze słowo linii = skrót kolumny
            if KOLUMNY[-1] == "WCIPR":          # ostatnia kolumna, dalej są już tylko opisy
                break
assert len(KOLUMNY) == 107

# 2. Otwieramy bazę (jeśli nie istnieje, SQLite ją utworzy)
con = sqlite3.connect(BAZA)

# 3. Usuwamy starą tabelę IMGW i tworzymy ją od nowa według schema.sql.
#    Samo CREATE TABLE IF NOT EXISTS nie zmienia istniejącej tabeli, więc bez DROP
#    zmiany kolumn w schema.sql (np. HPON -> HPOD) nie trafiłyby do bazy.
#    Tabela IMGW i tak jest w całości wczytywana od nowa z plików CSV, więc nic nie tracimy.
#    Inne tabele (gdyby się pojawiły) zostają nietknięte.
con.execute("DROP TABLE IF EXISTS IMGW")
with open(SCHEMA, encoding="utf-8") as f:
    con.executescript(f.read())

# 4. Pytamy bazę, jakie kolumny ma tabela IMGW -> ['ROK', 'MC', 'DZ', 'GG', 'WID', ...]
POLA = [kol[1] for kol in con.execute("PRAGMA table_info(IMGW)")]


def liczba(tekst):
    try:
        return float(tekst)
    except ValueError:      # "" albo tekst, np. "/"
        return None


sql = f"INSERT INTO IMGW ({', '.join(POLA)}) VALUES ({', '.join('?' * len(POLA))})"

# 5. Wczytujemy po kolei wszystkie pliki
for plik in sorted(DANE.glob("s_t_566_*.csv")):
    wiersze = []
    with open(plik, encoding="cp1250", newline="") as f:
        for r in csv.reader(f):
            w = dict(zip(KOLUMNY, r))           # {'ROK': '2010', 'TEMP': '-.3', ...}
            wartosci = []
            for p in POLA:
                v = liczba(w[p])
                status = w.get("W" + p, "").strip()     # np. WTEMP; nie każde pole ma status
                if status == "8":
                    v = None        # brak pomiaru
                elif status == "9":
                    v = 0.0         # brak zjawiska
                wartosci.append(v)
            wiersze.append(wartosci)
    con.executemany(sql, wiersze)
    print(plik.name, len(wiersze))

con.commit()
con.close()
