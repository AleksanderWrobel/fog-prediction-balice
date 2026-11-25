# data for training 


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))   # folder projektu

from data_scripts.data_import_from_sql import data_import

df = data_import()


def training_data(i):
    df_training = df.loc[df["ROK"] < 2019].reset_index(drop=True)

    df_training = df_training.loc[(df_training["MC"] > 8) | (df_training["MC"] < 4)].reset_index(drop=True)

    data = [[]]

    return data

def validation_data(i):
    df_validating = df.loc[(df["ROK"] >= 2019) & (df["ROK"] < 2024)].reset_index(drop=True)
    
    data = 0

    return data
    




df_testing = df.loc[(df["ROK"] >= 2024) & (df["ROK"] <= 2025)].reset_index(drop=True)



