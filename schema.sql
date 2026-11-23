CREATE TABLE IF NOT EXISTS IMGW(
    ROK INT, --Rok obserwacji IMGW
    MC INT, --Miesiąc obserwacji (1–12) IMGW
    DZ INT, --Dzień miesiąca IMGW
    GG INT, --Godzina terminu obserwacji (0–23) IMGW
    WID INT, --Widzialność [kod 0-9], 0-3 = mgła (<1000 m) IMGW
    WIDA FLOAT, --Widzialność (automat) [m] IMGW
    WIDO FLOAT, --Widzialność (operator) [m] IMGW
    POGB INT, --Pogoda bieżąca [kod] 40–49 mgła, 10 zamglenie IMGW
    TEMP FLOAT, --Temperatura powietrza [°C] IMGW
    TPTR FLOAT, --Temperatura punktu rosy [°C] IMGW
    WLGW FLOAT, --Wilgotność względna [%] IMGW
    FWR FLOAT, --Prędkość wiatru [m/s] IMGW
    KRWR FLOAT, --Kierunek wiatru [°] 999 = wiatr zmienny IMGW
    NOG INT, --Zachmurzenie ogólne [oktanty] IMGW
    CLCM INT, --Zachmurzenie niskie [oktanty] IMGW
    HPON FLOAT, --Wysokość podstawy chmur (niższej) [m] IMGW
    PPPM FLOAT, --Ciśnienie na poziomie morza [hPa] IMGW
    APP FLOAT, --Tendencja ciśnienia – wartość IMGW
    TECH INT, --Tendencja ciśnienia – charakterystyka [kod] IMGW
    WO6G FLOAT, --Opad za 6 godzin [mm] IMGW
    ROPT INT, --Rodzaj opadu za 6 godzin [kod] IMGW
    TGMI FLOAT, --Min. temperatura przy gruncie za 12 h [°C] IMGW
    TG05 FLOAT, --Temperatura gruntu na głębokości 5 cm [°C] IMGW
    SGRN INT, --Stan gruntu [kod] IMGW
    PKSN INT, --Pokrywa śnieżna [cm] 997/998/999 = kody specjalne IMGW
    USLN FLOAT, --Usłonecznienie IMGW
    ROSW INT, --Występowanie rosy [0/1] IMGW
    PRIMARY KEY (ROK, MC, DZ, GG) --to sprawi, że sql nie przyjmie dwóch wierszy z tą samą godziną
);


CREATE TABLE IF NOT EXISTS GIOS(
    ROK INT, --Rok obserwacji IMGW
    MC INT, --Miesiąc obserwacji (1–12) IMGW
    DZ INT, --Dzień miesiąca IMGW
    GG INT, --Godzina terminu obserwacji (0–23) IMGW
    PM10 FLOAT, --Stężenie PM10 [µg/m³] Kraków, Al. Krasińskiego, średnia 1-godzinna GIOŚ
    PRIMARY KEY (ROK, MC, DZ, GG) --czas w UTC, koniec godziny uśredniania
);

CREATE TABLE IF NOT EXISTS ERA5(
    ROK INT, --Rok obserwacji IMGW
    MC INT, --Miesiąc obserwacji (1–12) IMGW
    DZ INT, --Dzień miesiąca IMGW
    GG INT, --Godzina terminu obserwacji (0–23) IMGW
    
    valid_time TIMESTAMP, --Czas (ERA5) ERA5
    latitude FLOAT, --Szerokość geograficzna ERA5
    longitude FLOAT, --Długość geograficzna ERA5
    pressure_level INT, --Poziom ciśnienia ERA5 pressure levels

    blh FLOAT, --Wysokość warstwy granicznej [m] ERA5 single levels
    swvl1 FLOAT, --Wilgotność gleby (warstwa 1) [m³/m³] ERA5 single levels
    str FLOAT, --Promieniowanie długofalowe netto [J/m²] ERA5 single levels
    lcc FLOAT, --Zachmurzenie niskie [0–1] ERA5 single levels
    tcc FLOAT, --Zachmurzenie ogólne [0–1] ERA5 single levels
    t2m FLOAT, --Temperatura na 2 m [K] ERA5 single levels
    d2m FLOAT, --Punkt rosy na 2 m [K] ERA5 single levels
    msl FLOAT, --Ciśnienie na poziomie morza [Pa] ERA5 single levels

    t FLOAT, --Temperatura (850, 925 hPa) [K] ERA5 pressure levels
    q FLOAT, --Wilgotność właściwa (850, 925 hPa) [kg/kg] ERA5 pressure levels
    u FLOAT, --Wiatr – składowa u (850, 925 hPa) [m/s] ERA5 pressure levels
    v FLOAT --Wiatr – składowa v (850, 925 hPa) [m/s] ERA5 pressure levels
);



