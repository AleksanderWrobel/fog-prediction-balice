# W tym pliku będzie się znajdować cały plan odnośnie modeli predykcyjnych


## Krok 1:
Przygotowanie danych treningowych, walidacyjnych oraz testowych. 
W tym celu należy się skupić na:
 - dane muszą być podzielone na pakiety w których mamy wiadomości o godzinach: [1, 2, 3, 4, 6, 12, 24, 48] w przód. Nie bierzemy wszystkich godzin, bo model mógłby się wtedy pogubić i nie wiedziałby, jakie pytania zadawać.
 - Do danych należy przypasować etykiety, jaka była widoczność na 1, 2, 3, 4 i 5 h w przód (liczy się dla nas wartość WID)
 - po zrobieniu pakietów z odpowiednimi godzinami w przód, należy dane treningowe wymieszać
 - Takie przygotowane dane, należy wrzucić w odpowiednie pliki treningowe do odpowiednich modeli

## Krok 2:
Zbudowanie modeli, razem 6 modeli i najlepiej kilku różnych kombinacji z róznymi parametrami, żeby wybrać ostatecznie te najlepsze (Robimy modele gradient boosted decision trees)


## Krok 3:
Zbudowanie training pipelinu, w którym modele będą feedowane danymi treningowymi i walidowane

## Krok 4:
Przeprowadzenie testów różnych wytrenowanych modeli w celu wybrania, bądź późniejszego podrasowania tych najlepszych


