# Mixing with data

# Data import

# Najważniejsze dane, które należy zgrać do trenowania pierwszych modeli (lata 2001–2025) to:
# IMGW:
#
# Nr kolumny = numer kolumny w plikach s_t_566_*.csv, liczony od 1 (tak jak w Excelu: A = 1).
# W Pythonie/pandas indeks jest o 1 mniejszy (usecols=[nr - 1]).
# Status = kolumna ze statusem pomiaru ("8" brak pomiaru, "9" brak zjawiska); "-" = pole nie ma statusu.
#
#  Lp. | Parametr                              | Skrót | Nr kolumny | Status (nr kolumny)
#  ----+---------------------------------------+-------+------------+--------------------
#   1. | Rok                                   | ROK   |   2        | -
#   2. | Miesiąc                               | MC    |   3        | -
#   3. | Dzień                                 | DZ    |   4        | -
#   4. | Godzina (UTC)                         | GG    |   5        | -
#   5. | Widzialność [kod]                     | WID   |  15        | WWID   (16)
#   6. | Pogoda bieżąca                        | POGB  |  52        | -
#   7. | Temperatura powietrza                 | TEMP  |  29        | WTEMP  (30)
#   8. | Temperatura punktu rosy               | TPTR  |  39        | WTPTR  (40)
#   9. | Wilgotność względna                   | WLGW  |  37        | WWLGW  (38)
#  10. | Prędkość wiatru                       | FWR   |  25        | WFWR   (26)
#  11. | Kierunek wiatru                       | KRWR  |  23        | WKRWR  (24)
#  12. | Zachmurzenie ogólne                   | NOG   |  21        | WNOG   (22)
#  13. | Zachmurzenie niskie                   | CLCM  |  54        | WCLCM  (55)
#  14. | Wysokość podstawy chmur (niższej)     | HPON  |   8        | WHPON  (9)
#  15. | Ciśnienie na poziomie morza           | PPPM  |  43        | WPPPM  (44)
#  16. | Opad za 6 godzin                      | WO6G  |  48        | WWO6G  (49)
#  17. | Temperatura gruntu na głębokości 5 cm | TG05  |  77        | WTG05  (78)
#  18. | Usłonecznienie                        | USLN  |  69        | WUSLN  (70)
#  19. | Występowanie rosy                     | ROSW  |  71        | WROSW  (72)
#
# Widzialność: bierzemy WID (kod), a nie WIDA (automat, kolumna 20) ani WIDO (operator, kolumna 18).
# WID jest wypełnione we wszystkich latach 2001–2025, a WIDA/WIDO dopiero od 2011 r.
# (WIDA brak w 2024 r. i w części 2025 r.).


from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["toolbar"] = "None" #wyłacza przycisku na wykresie matplotlib, bo mi się linux wywalał cały czas

dane_do_wykresow = []

srednia_temp_na_przestrzeni_lat = []

for z in range(1, 26, 1):
    if z < 10:
        path = Path(f"dane/IMGW_PIB_dane_terminowe_SYNOP/s_t_566_200{z}.csv")
    else:
        path = Path(f"dane/IMGW_PIB_dane_terminowe_SYNOP/s_t_566_20{z}.csv")

    df = pd.read_csv(path, encoding = "cp1250", header = None)

    temperature = df.iloc[:,29]   # [wiersze, kolumny]

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
        print(f"Średnia temperatura w roku 200{z} wyniosła{np.mean(temperature):.2f}")
    else:
        print(f"Średnia temperatura w roku 20{z} wyniosła{np.mean(temperature):.2f}")

    srednia_temp_na_przestrzeni_lat.append(np.mean(temperature))
    

x = [i for i in range(0, 52 ,1)]

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

ax.set_xlabel("Tydzień roku")
ax.set_ylabel("Średnia tygodniowa temperatura [°C]")
ax.set_title("Kraków-Balice, 2001–2025")
ax.grid(True, alpha=0.3)
plt.show()



fig, ax = plt.subplots()
ax.plot([i for i in range(0,25,1)], srednia_temp_na_przestrzeni_lat, color="red", linewidth=1.5)
ax.set_xlabel("Rok 20x")
ax.set_ylabel("Średniaroczna temperatura [°C]")
ax.set_title("Kraków-Balice, 2001–2025")
ax.grid(True, alpha=0.3)
plt.show()



