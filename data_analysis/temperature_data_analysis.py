# Mixing with temperature data


import matplotlib.pyplot as plt
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))   # folder projektu

from data_scripts.data_import_from_sql import data_import

plt.rcParams["toolbar"] = "None" #wyłacza przycisku na wykresie matplotlib, bo mi się linux wywalał cały czas

df = data_import()

dane_do_wykresow = []

srednia_temp_na_przestrzeni_lat = []

for z in range(1, 26, 1):

    temperature = df.loc[df["ROK"] == 2000 + z, "TEMP"].reset_index(drop=True)

    temp_tydzien = [[]]

    j = 0
    for i in range(0, 364*24, 1):
        if len(temp_tydzien[j]) < 24*7:
            temp_tydzien[j].append(temperature[i])
        else:
            temp_tydzien.append([temperature[i]])
            j += 1

    temp_dzien_sredni = [np.mean(temp) for temp in temp_tydzien]

    dane_do_wykresow.append(temp_dzien_sredni)

    
    if z < 10:
        print(f"Średnia temperatura w roku 200{z} wyniosła: {np.mean(temperature):.2f}°C")
    else:
        print(f"Średnia temperatura w roku 20{z} wyniosła: {np.mean(temperature):.2f}°C")

    srednia_temp_na_przestrzeni_lat.append(np.mean(temperature))
    

x = [i for i in range(1, 53 ,1)]     # numery tygodni 1–52 (tak jak w kalendarzu, od 1, a nie od 0)

# Gradient kolorów: 2001 = jasnożółty, 2025 = ciemnoczerwony.
# "YlOrRd" to gotowa mapa kolorów matplotlib (Yellow -> Orange -> Red).
# Bierzemy ją od 0.15, bo sam początek mapy jest prawie biały i linia zlałaby się z tłem.
lata = list(range(2001, 2026))
mapa = plt.get_cmap("YlOrRd")
norma = plt.Normalize(vmin=lata[0], vmax=lata[-1])       # rok -> liczba od 0 do 1


def kolor(rok):
    return mapa(0.15 + 0.85 * norma(rok))


fig, ax = plt.subplots()
for z, rok in enumerate(lata):
    ax.plot(x, dane_do_wykresow[z], color=kolor(rok), linewidth=1.5)

# Pasek kolorów z latami zamiast legendy z 25 pozycjami
pasek = plt.cm.ScalarMappable(
    cmap=plt.matplotlib.colors.ListedColormap([kolor(r) for r in lata]),
    norm=plt.Normalize(vmin=lata[0] - 0.5, vmax=lata[-1] + 0.5),
)
fig.colorbar(pasek, ax=ax, label="Rok", ticks=lata[::4])

ax.set_xlabel("Tydzień roku (1–52)")
ax.set_ylabel("Średnia tygodniowa temperatura [°C]")
ax.set_title("Średnia tygodniowa temperatura powietrza w kolejnych latach\nKraków-Balice (IMGW SYNOP), 2001–2025")
ax.set_xlim(1, 52)
ax.grid(True, alpha=0.3)
plt.show()



fig, ax = plt.subplots()
ax.plot(lata, srednia_temp_na_przestrzeni_lat, color="red", linewidth=1.5, marker="o", markersize=4)   # na osi x prawdziwe lata 2001–2025
ax.set_xlabel("Rok")
ax.set_ylabel("Średnia roczna temperatura [°C]")
ax.set_title("Średnia roczna temperatura powietrza\nKraków-Balice (IMGW SYNOP), 2001–2025")
ax.set_xticks(lata[::4])                                  # podpis co 4 lata, żeby się nie nakładały
ax.grid(True, alpha=0.3)
plt.show()



