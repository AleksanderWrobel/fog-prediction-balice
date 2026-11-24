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


-- Widok z cechami wyliczanymi z IMGW. Nie przechowuje danych, tylko liczy je przy każdym SELECT.
-- Widok można bezpiecznie usuwać i tworzyć od nowa (DROP + CREATE), bo nic w nim nie jest zapisane.
-- Dzięki temu zmiana definicji widoku zadziała od razu, bez usuwania baza.db.
DROP VIEW IF EXISTS IMGW_cechy;
CREATE VIEW IMGW_cechy AS
SELECT *,
       ROUND(TEMP - TPTR, 1) AS DEFICYT,   --Deficyt punktu rosy T − Td [°C]
       ROUND(TEMP - LAG(TEMP, 3) OVER (ORDER BY ROK, MC, DZ, GG), 1) AS DT_3H   --Zmiana temperatury za 3 h [°C]
FROM IMGW
WHERE ROK >= 2001;   --LAG cofa się o wiersze, nie o godziny; przed 2001 dane są co 3 h

