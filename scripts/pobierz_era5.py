from pathlib import Path   # wygodna praca ze ścieżkami plików
import cdsapi

# Folder docelowy (ten, w którym teraz jesteś); utworzy go, jeśli nie istnieje
folder = Path.home() / "Studia/semestr_5/Podstawy_fizyki_środowiska/dane/ERA5_Copernicus"
folder.mkdir(parents=True, exist_ok=True)

dataset = "reanalysis-era5-single-levels"
request = {
    "product_type": ["reanalysis"],
    "year": ["2001"],
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
    "day": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12",
        "13", "14", "15",
        "16", "17", "18",
        "19", "20", "21",
        "22", "23", "24",
        "25", "26", "27",
        "28", "29", "30",
        "31"
    ],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "variable": [
        "boundary_layer_height",
        "volumetric_soil_water_layer_1",
        "surface_net_thermal_radiation",
        "low_cloud_cover",
        "total_cloud_cover",
        "2m_temperature",
        "2m_dewpoint_temperature",
        "mean_sea_level_pressure"
    ],
    "area": [50.25, 19.5, 49.75, 20]
}

client = cdsapi.Client()   # tworzymy raz, przed pętlą – nie trzeba w każdym obrocie


for rok in range(2001, 2026):
    for miesiac in range(1, 13):       # 1, 2, ..., 12 (13 nie jest włączane)

        # {miesiac:02d} – liczba zapisana na 2 cyfrach z zerem z przodu: 1 -> "01"
        # dzięki temu pliki sortują się poprawnie: _01, _02, ..., _12
        target = folder / f"era5_sl_{rok}_{miesiac:02d}.nc"

        if target.exists():
            print(f"{rok}-{miesiac:02d}: już pobrany, pomijam")
            continue

        request["year"] = [str(rok)]
        request["month"] = [f"{miesiac:02d}"]   # NOWE: tylko jeden miesiąc w zamówieniu

        print(f"{rok}-{miesiac:02d}: wysyłam zamówienie...")
        client.retrieve(dataset, request).download(str(target))