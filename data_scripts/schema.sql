CREATE TABLE IF NOT EXISTS IMGW(
    ROK INT, --Rok obserwacji IMGW
    MC INT, --Miesiąc obserwacji (1–12) IMGW
    DZ INT, --Dzień miesiąca IMGW
    GG INT, --Godzina terminu obserwacji (0–23) IMGW
    WID INT, --Widzialność [kod 0-9], 0-3 = mgła (<1000 m) IMGW
    POGB INT, --Pogoda bieżąca [kod] 40–49 mgła, 10 zamglenie IMGW
    TEMP FLOAT, --Temperatura powietrza [°C] IMGW
    TPTR FLOAT, --Temperatura punktu rosy [°C] IMGW
    WLGW FLOAT, --Wilgotność względna [%] IMGW
    FWR FLOAT, --Prędkość wiatru [m/s] IMGW
    KRWR FLOAT, --Kierunek wiatru [°] 999 = wiatr zmienny IMGW
    NOG INT, --Zachmurzenie ogólne [oktanty] IMGW
    CLCM INT, --Zachmurzenie niskie [oktanty] IMGW
    HPOD INT, --Wysokość podstawy chmur [kod 0-9]: 0 <50 m, 1 50-100, 2 100-200, 3 200-300, 4 300-600, 5 600-1000, 6 1000-1500, 7 1500-2000, 8 2000-2500, 9 >=2500 m lub brak chmur; NULL ("/") = niebo niewidoczne (NOG=9) IMGW
    PPPM FLOAT, --Ciśnienie na poziomie morza [hPa] IMGW
    WO6G FLOAT, --Opad za 6 godzin [mm] IMGW
    PRIMARY KEY (ROK, MC, DZ, GG) --to sprawi, że sql nie przyjmie dwóch wierszy z tą samą godziną
);


-- Stężenie PM10 z GIOŚ (Kraków), co 1 h, od 2003 r. Wypełnia je skrypt import_GIOS_to_sql.py.
-- Czas jest przeliczony na UTC (jak w IMGW): wartość z godziny GG to średnia z godziny GG-1 … GG UTC.
CREATE TABLE IF NOT EXISTS GIOS_PM10(
    ROK INT, --Rok (UTC)
    MC INT, --Miesiąc (UTC)
    DZ INT, --Dzień miesiąca (UTC)
    GG INT, --Godzina KOŃCA okresu uśredniania (0–23 UTC)
    PM10_KRAS FLOAT, --PM10 [µg/m³], stacja Kraków, Al. Krasińskiego (brak całego 2022 r.)
    PM10_BULW FLOAT, --PM10 [µg/m³], stacja Kraków, ul. Bulwarowa
    PM10 FLOAT, --PM10 [µg/m³], średnia z dostępnych stacji (Krasińskiego, Bulwarowa); NULL gdy obie bez pomiaru
    PRIMARY KEY (ROK, MC, DZ, GG)
);


-- Widok z cechami wyliczanymi z IMGW i z dołączonym PM10 z GIOŚ. Nie przechowuje danych, tylko liczy je przy każdym SELECT.
-- Widok można bezpiecznie usuwać i tworzyć od nowa (DROP + CREATE), bo nic w nim nie jest zapisane.
-- Dzięki temu zmiana definicji widoku zadziała od razu, bez usuwania baza.db.
-- LEFT JOIN: bierzemy WSZYSTKIE godziny IMGW; gdy GIOŚ nie ma danej godziny (np. 2001–2002), PM10 = NULL.
DROP VIEW IF EXISTS IMGW_cechy;
CREATE VIEW IMGW_cechy AS
SELECT I.*,
       ROUND(I.TEMP - I.TPTR, 1) AS DEFICYT,   --Deficyt punktu rosy T − Td [°C]
       ROUND(I.TEMP - LAG(I.TEMP, 3) OVER (ORDER BY I.ROK, I.MC, I.DZ, I.GG), 1) AS DT_3H,   --Zmiana temperatury za 3 h [°C]
       G.PM10   --Stężenie PM10 [µg/m³] z GIOŚ (średnia Krasińskiego i Bulwarowej)
FROM IMGW AS I
LEFT JOIN GIOS_PM10 AS G USING (ROK, MC, DZ, GG)
WHERE I.ROK >= 2001;   --LAG cofa się o wiersze, nie o godziny; przed 2001 dane są co 3 h
