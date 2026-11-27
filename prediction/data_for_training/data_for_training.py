# data for training 

import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))   # folder projektu

from data_scripts.data_import_from_sql import data_import

df = data_import()




# Training data, to będą zestawy wyglądające tak: [etykieta (czy mgła tak / nie), dane (na 1 h, 2h, 3h, 4h, 6h, 12h, 24h, 48h)]

def training_data(prediction_hour):

    # prediction_hour, jest to ilość godzin, na ile model potrzebuje danych w przód:
    # prediction_hour = 1, etykieta to czy mgła zajdzie za 1 h
    # prediction_hour = 2, etykieta to czy mgła zajdzie za 2 h
    # prediction_hour = 3, etykieta to czy mgła zajdzie za 3 h
    # prediction_hour = 4, etykieta to czy mgła zajdzie za 4 h
    # prediction_hour = 5, etykieta to czy mgła zajdzie za 5 h
    # prediction_hour = 6, etykieta to tablica, w której mamy przewidywanie mgły w przód na wszystkie pięc godzin [1h, 2h, 3h, 4h, 5h]

    df_training = df.loc[((df["ROK"] < 2019) & (df["MC"] > 8)) | ((df["ROK"] < 2019) & (df["MC"] < 4))].reset_index(drop=True)

    number_rows, number_columns = df_training.shape


    data = []


    for i in range(0, number_rows - (49 + prediction_hour), 1):
        temp_data_box = [[df_training.iloc[i].to_numpy()], []]
        temp_data_box[0].append(df_training.iloc[i].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+24].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+36].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+42].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+44].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+45].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+46].to_numpy())
        temp_data_box[0].append(df_training.iloc[i+47].to_numpy())
        WID = df_training.iloc[i+48+prediction_hour].loc["WID"]
        if WID <= 3:
            temp_data_box[1] = 1
        else:
            temp_data_box[1] = 0

        # trzeba tak podizelić dane, żeby nie wychodziło, że zaraz po marcu pojawiają się dane z września

        # dane trzeba przetasować

        # zamienić na końcu tablicę na tablicę numpy, żeby szybiej działało
        

        if len(data) == 0:
            data = temp_data_box
        else:
            data.append(temp_data_box)


    return data

def validation_data(prediction_hour):
    df_validating = df.loc[((df["ROK"] >= 2019) & (df["ROK"] < 2024) & (df["MC"] > 8)) | ((df["ROK"] >= 2019) & (df["ROK"] < 2024) & (df["MC"] < 4))].reset_index(drop=True)

    number_rows, number_columns = df_validating.shape


    data = 0

    return data
    


def testing_data(prediction_hour):
    df_testing = df.loc[((df["ROK"] >= 2024) & (df["ROK"] < 2026) & (df["MC"] > 8)) | ((df["ROK"] >= 2024) & (df["ROK"] < 2026) & (df["MC"] < 4))].reset_index(drop=True)

    number_rows, number_columns = df_testing.shape


    data = [[]]

    return data


training_data(2)