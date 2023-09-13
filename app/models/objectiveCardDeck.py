from enum import Enum
import random

# Objetivos https://pt.wikipedia.org/wiki/War
# – Conquistar na totalidade a EUROPA, a OCEANIA e mais um terceiro.
# – Conquistar na totalidade a ÁSIA e a AMÉRICA DO SUL.
# – Conquistar na totalidade a EUROPA, a AMÉRICA DO SUL e mais um terceiro.
# – Conquistar 18 TERRITÓRIOS e ocupar cada um deles com pelo menos dois exércitos.
# – Conquistar na totalidade a ÁSIA e a ÁFRICA.
# – Conquistar na totalidade a AMÉRICA DO NORTE e a ÁFRICA.
# – Conquistar 24 TERRITÓRIOS à sua escolha.
# – Conquistar na totalidade a AMÉRICA DO NORTE e a OCEANIA.
# – Destruir totalmente OS EXÉRCITOS AZUIS.
# – Destruir totalmente OS EXÉRCITOS AMARELOS.
# – Destruir totalmente OS EXÉRCITOS VERMELHOS.
# – Destruir totalmente OS EXÉRCITOS PRETOS.
# – Destruir totalmente OS EXÉRCITOS BRANCO.
# – Destruir totalmente OS EXÉRCITOS VERDES.




class ObjectiveCardDeck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()

    def create_deck(self):
        self.cards = [ObjectiveCard(objective) for objective in Objectives]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        else:
            return None
    
    def add_card(self, card):
        self.cards.append(card)
    
    def remove_card(self, card):
        self.cards.remove(card)

    def get_card_by_territory(self, territory_name):
        for card in self.cards:
            if card.name == territory_name:
                return card
        return None
    
    def __str__(self):
        return ", ".join(str(card) for card in self.cards)



class ObjectiveCard:
    def __init__(self, objective):
        self.objective = objective
        self.index = objective.index
        self.first_objective = objective

    def __str__(self):
        return f"{self.objective.index} - {self.objective.description}"
    
    def get_description(self):
        return self.objective.description
    

class Objectives(Enum):
    OBJ1 = (0, "Objetivo 1", "Conquistar na totalidade a EUROPA, a OCEANIA e mais um terceiro.", True)
    OBJ2 = (1, "Objetivo 2", "Conquistar na totalidade a ÁSIA e a AMÉRICA DO SUL.", True)
    OBJ3 = (2, "Objetivo 3", "Conquistar na totalidade a EUROPA, a AMÉRICA DO SUL e mais um terceiro.", True)
    OBJ4 = (3, "Objetivo 4", "Conquistar 18 TERRITÓRIOS e ocupar cada um deles com pelo menos dois exércitos.", True)
    OBJ5 = (4, "Objetivo 5", "Conquistar na totalidade a ÁSIA e a ÁFRICA.", True)
    OBJ6 = (5, "Objetivo 6", "Conquistar na totalidade a AMÉRICA DO NORTE e a ÁFRICA.", True)
    OBJ7 = (6, "Objetivo 7", "Conquistar 24 TERRITÓRIOS à sua escolha.", True)
    OBJ8 = (7, "Objetivo 8", "Conquistar na totalidade a AMÉRICA DO NORTE e a OCEANIA.", True)
    OBJ9 = (8, "Objetivo 9", "Destruir totalmente OS EXÉRCITOS AZUIS.", False)
    OBJ10 = (9, "Objetivo 10", "Destruir totalmente OS EXÉRCITOS AMARELOS.", False)
    OBJ11 = (10, "Objetivo 11", "Destruir totalmente OS EXÉRCITOS VERMELHOS.", False)
    OBJ12 = (11, "Objetivo 12", "Destruir totalmente OS EXÉRCITOS CINZA.", False)
    OBJ13 = (12, "Objetivo 13", "Destruir totalmente OS EXÉRCITOS ROXO.", False)
    OBJ14 = (13, "Objetivo 14", "Destruir totalmente OS EXÉRCITOS VERDES.", False)

    def __init__(self, index, name, description, conquistar=True):
        self.ext_name = name
        self.index = index
        self.conquistar = conquistar
        self.destruir = not conquistar
        self.description = description

    def __str__(self):
        return self.ext_name

