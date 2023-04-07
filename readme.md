### Jakub Poćwiardowski 184827
# Instrukcja
Lewy dolny róg: wskazanie gracza, który aktualnie ma ruch
- kolor czerwony - aktualny gracz
- kolor biały - reszta graczy 

Zasady Rummikuba są zachowane, więc przy pierwszym ruchu trzeba wyłożyć kafelki o łącznej wartości >= 30 (bez użycia kafelków obecnych na planszy). Warto to wziąć pod uwagę, gdyż czasami może się wydawać że sprawdzanie ruchu lub podświetlanie nie działa poprawnie, jednak wówczas najprawdopodobniej znaczy to że jest to nadal pierwszy ruch danego gracza.

Wykonane wszystko z podstawowych + logger

- QGraphicsScene - klasa Board (plik main)
- QGraphicsItem - klasa Tile (plik tile)
- Drag and drop - funkcje mousePress, mouseRelease itd. na końcu klasy Board
- Autosortowanie po kolorze i po liczbach - przyciski w prawym górnym rogu
- Timer Analogowy - klasa timer
- Podświetlanie możliwości ruchu - czerwony prostąkąt po kliknięciu klocka (przy 2+elementach w grupie na planszy)
- Sprawdzanie poprawności ruchu - po kliknięciu przycisku accept move lub dobraniu klocka, bądź upływie czasu. W dwóch ostatnich przypadkach ruch zostaje cofnięty jeśli jest niepoprawny. W pierwszym wyświetlone zostaje ostrzeżenie w loggerze.
- Grafiki zewnętrzne - plik graphics.qrc oraz skompilowany z niego graphics_rc.py
- Dociąganie płytek do siatki - metoda snap_to_grid w klasie Board. Metoda uwzględnia również próby umieszczenia jednego klocka na drugim oraz wyniesienie go poza planszę
- Multiselect realizowany jest poprzez kliknięcie myszką na puste pole i przeciągnięcie celem narysowania obszaru zaznaczenia. Przy przeciągnięciu któregoś z zaznaczonych klocków, przeciągnięte zostaną wszystkie zaznaczone klocki.
- Logger - QTextEdit w prawym dolnym rogu + printowanie na ekran + do pliku logfile.log
## Biblioteki
- PySide2
- Numpy
- logging + standardowe
### Python 3.8

