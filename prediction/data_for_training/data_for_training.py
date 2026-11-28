# data for training 

import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))   # folder projektu

from data_scripts.data_import_from_sql import data_import

df = data_import()


cechy = ["MC", "GG", "WID", "POGB", "TEMP", "TPTR", "WLGW", "FWR", "KRWR", "NOG", "CLCM", "HPOD", "PPPM", "WO6G", "DEFICYT", "DT_3H", "NIEBO_NIEWIDOCZNE", "PM10"]

# Training data, to będą zestawy wyglądające tak: [dane (na 0h (aktualną godzinę), 1 h, 2h, 3h, 4h, 6h, 12h, 24h, 48h)]

# Training data to okres od września 2001 do marca 2019

def training_data(prediction_hour):

    # prediction_hour, jest to ilość godzin, na ile model potrzebuje danych w przód (w celu wyciągnięcia etykiety):
    # prediction_hour = 1, etykieta to czy mgła zajdzie za 1 h
    # prediction_hour = 2, etykieta to czy mgła zajdzie za 2 h
    # prediction_hour = 3, etykieta to czy mgła zajdzie za 3 h
    # prediction_hour = 4, etykieta to czy mgła zajdzie za 4 h
    # prediction_hour = 5, etykieta to czy mgła zajdzie za 5 h
    # prediction_hour = 6, etykieta to tablica, w której mamy przewidywanie mgły w przód na wszystkie pięc godzin [1h, 2h, 3h, 4h, 5h]


    years = [i for i in range(1,19,1)]

    df_training = [df.loc[((df["ROK"] == (2000 + year)) & (df["MC"] > 8)) | ((df["ROK"] == (2001 + year)) & (df["MC"] < 4)), cechy].reset_index(drop=True) for year in years]

    hours = [0, 24, 36, 42, 44, 45, 46, 47, 48]

    Y_data = []
    X_data = []

    for yearly_data in df_training:
        number_rows = len(yearly_data)

        for i in range(0, number_rows - 53, 1):     # bierzemy tutaj 53, żeby każdy model dostawał taki sam zakres próbek i za razem, żeby nie wychodzić poza tablicę
            temp_data_box = []
            for hour in hours:
                temp_data_box.append(yearly_data.iloc[i+hour].to_numpy())
            

            if prediction_hour < 6:
                WID = yearly_data.iloc[i + 48 + prediction_hour].loc["WID"]
                if WID <= 3:
                    Y_data.append(1)
                else:
                    Y_data.append(0)
            else:
                WID = [yearly_data.iloc[i + 48 + z].loc["WID"] for z in range(1,6,1)]
                result = [1 if wid<=3 else 0 for wid in WID]
                Y_data.append(result)

            # X -> o kształcie (liczba próbek, 162), czyli wiersz = dane rzędami, kolumna = nazwa cech,
            # Y -> o kształcie (liczba próbek), czyli same wyniki, co jest przewidziane w przyszłości.
            # W takiej formie dane przyjmują LightGBM, XGBoost i scikit-learn: model.fit(X, y). 

            X_data.append(np.concatenate(temp_data_box))

    nazwy_cech = []

    for hour in hours:
        for cecha in cechy:
            nazwy_cech.append(str(48 - hour) + "-" + cecha)

    X_data = np.array(X_data)
    Y_data = np.array(Y_data)

    np.random.default_rng(42).shuffle(X_data)
    np.random.default_rng(42).shuffle(Y_data)

    return nazwy_cech, X_data, Y_data


# Validation data to okres od września 2019 do marca 2023

def validation_data(prediction_hour):

    years = [i for i in range(19,23,1)]

    df_validating = [df.loc[((df["ROK"] == (2000 + year)) & (df["MC"] > 8)) | ((df["ROK"] == (2001 + year)) & (df["MC"] < 4)), cechy].reset_index(drop=True) for year in years]

    hours = [0, 24, 36, 42, 44, 45, 46, 47, 48]

    Y_data = []
    X_data = []

    for yearly_data in df_validating:
        number_rows = len(yearly_data)

        for i in range(0, number_rows - 53, 1):     # bierzemy tutaj 53, żeby każdy model dostawał taki sam zakres próbek i za razem, żeby nie wychodzić poza tablicę
            temp_data_box = []
            for hour in hours:
                temp_data_box.append(yearly_data.iloc[i+hour].to_numpy())
            

            if prediction_hour < 6:
                WID = yearly_data.iloc[i + 48 + prediction_hour].loc["WID"]
                if WID <= 3:
                    Y_data.append(1)
                else:
                    Y_data.append(0)
            else:
                WID = [yearly_data.iloc[i + 48 + z].loc["WID"] for z in range(1,6,1)]
                result = [1 if wid<=3 else 0 for wid in WID]
                Y_data.append(result)

            # X -> o kształcie (liczba próbek, 162), czyli wiersz = dane rzędami, kolumna = nazwa cech,
            # Y -> o kształcie (liczba próbek), czyli same wyniki, co jest przewidziane w przyszłości.
            # W takiej formie dane przyjmują LightGBM, XGBoost i scikit-learn: model.fit(X, y). 

            X_data.append(np.concatenate(temp_data_box))

    nazwy_cech = []

    for hour in hours:
        for cecha in cechy:
            nazwy_cech.append(str(48 - hour) + "-" + cecha)

    X_data = np.array(X_data)
    Y_data = np.array(Y_data)

    return nazwy_cech, X_data, Y_data
    


# Testing data to okres od września 2023 do marca 2025

def test_data(prediction_hour):

    years = [i for i in range(23,25,1)]

    df_testing = [df.loc[((df["ROK"] == (2000 + year)) & (df["MC"] > 8)) | ((df["ROK"] == (2001 + year)) & (df["MC"] < 4)), cechy].reset_index(drop=True) for year in years]

    hours = [0, 24, 36, 42, 44, 45, 46, 47, 48]

    Y_data = []
    X_data = []

    for yearly_data in df_testing:
        number_rows = len(yearly_data)

        for i in range(0, number_rows - 53, 1):     # bierzemy tutaj 53, żeby każdy model dostawał taki sam zakres próbek i za razem, żeby nie wychodzić poza tablicę
            temp_data_box = []
            for hour in hours:
                temp_data_box.append(yearly_data.iloc[i+hour].to_numpy())
            

            if prediction_hour < 6:
                WID = yearly_data.iloc[i + 48 + prediction_hour].loc["WID"]
                if WID <= 3:
                    Y_data.append(1)
                else:
                    Y_data.append(0)
            else:
                WID = [yearly_data.iloc[i + 48 + z].loc["WID"] for z in range(1,6,1)]
                result = [1 if wid<=3 else 0 for wid in WID]
                Y_data.append(result)

            # X -> o kształcie (liczba próbek, 162), czyli wiersz = dane rzędami, kolumna = nazwa cech,
            # Y -> o kształcie (liczba próbek), czyli same wyniki, co jest przewidziane w przyszłości.
            # W takiej formie dane przyjmują LightGBM, XGBoost i scikit-learn: model.fit(X, y). 

            X_data.append(np.concatenate(temp_data_box))

    nazwy_cech = []

    for hour in hours:
        for cecha in cechy:
            nazwy_cech.append(str(48 - hour) + "-" + cecha)

    X_data = np.array(X_data)
    Y_data = np.array(Y_data)

    return nazwy_cech, X_data, Y_data


if __name__ == "__main__":

    nazwy_cech, x_training_data, y_training_data = training_data(2)



