# training file


import time
start = time.perf_counter()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))   # folder projektu

from data_for_training.data_for_training import training_data, validation_data, test_data


df_training = training_data(1)
df_validation = validation_data(1)
df_testing = test_data(1)


koniec = time.perf_counter()
print(f"Czas: {koniec - start:.2f} s")


