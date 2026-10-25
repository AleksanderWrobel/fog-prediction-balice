# =====================================================================
# pobierz_era5_pl.py – pobieranie ERA5 "hourly data on pressure levels"
# dla okolic lotniska Kraków-Balice, osobny plik na każdy miesiąc.
#
# Uruchomienie:  python pobierz_era5_pl.py
# Wymaga:        pip install "cdsapi>=0.7.7"  oraz pliku ~/.cdsapirc z tokenem
#
# Skrypt można przerwać (Ctrl+C) i uruchomić ponownie – pominie miesiące,
# które są już pobrane, i zacznie od pierwszego brakującego.
# =====================================================================

from pathlib import Path   # wygodna praca ze ścieżkami plików
import cdsapi

# ---------------------------------------------------------------------
# Ustawienia
# ---------------------------------------------------------------------

# Folder docelowy; Path.home() = /home/aleksander, więc skrypt działa z każdego miejsca
folder = Path.home() / "Studia/semestr_5/Podstawy_fizyki_środowiska/dane/ERA5_Copernicus"
folder.mkdir(parents=True, exist_ok=True)   # utwórz folder, jeśli go nie ma

ROK_OD = 2001   # pierwszy rok (włącznie)
ROK_DO = 2025   # ostatni rok (włącznie)

dataset = "reanalysis-era5-pressure-levels"   # nazwa zbioru w CDS

# Zamówienie – to samo, co w formularzu. "year" i "month" są podmieniane w pętli.
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "specific_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind",
    ],
    "year": [],                                      # uzupełniane w pętli
    "month": [],                                     # uzupełniane w pętli
    "day": [f"{d:02d}" for d in range(1, 32)],       # "01" ... "31" (nieistniejące dni CDS pomija)
    "time": [f"{h:02d}:00" for h in range(24)],      # "00:00" ... "23:00"
    "pressure_level": ["850", "925"],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [50.25, 19.5, 49.75, 20],                # [północ, zachód, południe, wschód]
}

# ---------------------------------------------------------------------
# Pobieranie
# ---------------------------------------------------------------------

client = cdsapi.Client()   # wczytuje url i token z ~/.cdsapirc; tworzymy raz, przed pętlą

nieudane = []   # lista miesięcy, których nie udało się pobrać (wypiszemy ją na końcu)

# range(ROK_OD, ROK_DO + 1) – "+ 1", bo range nie włącza górnej granicy
for rok in range(ROK_OD, ROK_DO + 1):
    for miesiac in range(1, 13):                     # 1, 2, ..., 12

        # "pl" = pressure levels; {miesiac:02d} zapisuje miesiąc na 2 cyfrach: 1 -> "01"
        target = folder / f"era5_pl_{rok}_{miesiac:02d}.nc"

        # Jeśli plik już jest (np. z poprzedniego uruchomienia), pomiń ten miesiąc
        if target.exists():
            print(f"{rok}-{miesiac:02d}: już pobrany, pomijam")
            continue

        # CDS oczekuje wartości jako tekstów w listach, np. ["1976"], ["01"]
        request["year"] = [str(rok)]
        request["month"] = [f"{miesiac:02d}"]

        print(f"{rok}-{miesiac:02d}: wysyłam zamówienie...")

        # try/except – jeśli jedno zamówienie się nie powiedzie (np. chwilowy błąd
        # serwera), zapisz to i idź dalej, zamiast przerywać cały skrypt w nocy
        try:
            # Pobieramy najpierw do pliku tymczasowego ".part" i dopiero po
            # udanym pobraniu zmieniamy nazwę. Dzięki temu przerwane pobieranie
            # nie zostawi niepełnego pliku, który target.exists() uznałby za gotowy.
            tymczasowy = target.with_suffix(".nc.part")
            client.retrieve(dataset, request).download(str(tymczasowy))
            tymczasowy.rename(target)
            print(f"{rok}-{miesiac:02d}: zapisano {target.name}")
        except KeyboardInterrupt:
            # Ctrl+C ma dalej zatrzymywać skrypt, a nie być traktowane jak zwykły błąd
            raise
        except Exception as blad:
            print(f"{rok}-{miesiac:02d}: BŁĄD – {blad}")
            nieudane.append(f"{rok}-{miesiac:02d}")

# ---------------------------------------------------------------------
# Podsumowanie
# ---------------------------------------------------------------------
if nieudane:
    print("\nNie udało się pobrać:", ", ".join(nieudane))
    print("Uruchom skrypt ponownie – spróbuje pobrać tylko brakujące miesiące.")
else:
    print("\nGotowe – wszystkie miesiące pobrane.")
