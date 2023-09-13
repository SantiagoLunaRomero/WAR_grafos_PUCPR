import sys
sys.path.append('../')
from app.models.board import Territory, Continents, Board
from app.models.territoryCardDeck import Symbol
import random

lista_territorios_shift = []

for territory in Territory:
    random_army = random.randint(1, 15)
    lista_territorios_shift.append(random_army)

#iterate over lista_territorios_shift with index
#for index, value in enumerate(lista_territorios_shift):
#    print(Territory(index), value)

for index, value in enumerate(Territory):
    print(value, lista_territorios_shift[index])