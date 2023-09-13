from enum import Enum
import random
import sys
sys.path.append('../')
from app.models.board import Territory

class TerritoryCardDeck:
    def __init__(self, insert_wild_cards = True):
        self.cards = []
        self.used_cards = []
        self.create_deck(insert_wild_cards)
        self.shuffle()

    def create_deck(self, insert_wild_cards = True):
        self.cards = [TerritoryCard(territory) for territory in Territory]
        if(insert_wild_cards):
            self.add_card(WildCard(98))
            self.add_card(WildCard(99))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        #detect if empty
        if self.cards:
            card = self.cards.pop()
            self.used_cards.append(card)
            return card
        else:
            #reinsert used cards inside deck
            self.cards = self.used_cards.copy()
            self.used_cards.clear()
            self.shuffle()
            #draw card
            card = self.cards.pop()
            self.used_cards.append(card)
            return card
    
    def add_card(self, card):
        self.cards.append(card)
    
    def remove_card(self, card):
        self.cards.remove(card)

    def get_deck_length(self):
        return(len(self.cards))
    
    def get_card_by_territory(self, territory_name):
        for card in self.cards:
            if card.name == territory_name:
                return card
        return None
    
    def __str__(self):
        return ", ".join(str(card) for card in self.cards)

class WildCard:
    def __init__(self, index):
        self._name_ = "Coringa"
        self.index = index
        self.symbol = Symbol.WILDCARD
    def __str__(self):
        return f"{self._name_} ({self.symbol.name})"

class TerritoryCard:
    def __init__(self, territory_enum):
        self.territory = territory_enum
        self.name = territory_enum.value[1]
        #self.index = territory_enum.value[0]
        self.symbol = TerritorySymbolDict[territory_enum]
        
    def __str__(self):
        return f"{self.territory.name} ({self.symbol.name})"
    

class Symbol(Enum):
    SQUARE = 0
    TRIANGLE = 1
    CIRCLE = 2
    WILDCARD = 3
TerritorySymbolDict = {
    # América do Sul +2
    Territory.BRASIL : Symbol.CIRCLE,

    Territory.ARGENTINA : Symbol.SQUARE,
    Territory.VENEZUELA : Symbol.TRIANGLE,
    Territory.PERU : Symbol.TRIANGLE,

    #America do Norte +5
    Territory.MEXICO : Symbol.SQUARE,
    Territory.NEW_YORK : Symbol.TRIANGLE,
    Territory.CALIFORNIA :  Symbol.SQUARE,
    Territory.OTTAWA :  Symbol.CIRCLE,
    Territory.VANCOUVER :  Symbol.TRIANGLE,
    Territory.MACKENZIE :  Symbol.CIRCLE,
    Territory.ALASKA :  Symbol.TRIANGLE,
    Territory.LABRADOR :  Symbol.SQUARE,
    Territory.GROELANDIA :  Symbol.CIRCLE,

    #Europa +5
    Territory.ISLANDIA :  Symbol.TRIANGLE,
    Territory.INGLATERRA :  Symbol.CIRCLE,
    Territory.SUECIA :  Symbol.CIRCLE,
    Territory.ALEMANHA :  Symbol.CIRCLE,
    Territory.FRANCA :  Symbol.SQUARE,
    Territory.POLONIA :  Symbol.SQUARE,
    Territory.MOSCOU :  Symbol.TRIANGLE,

    #África +3
    Territory.ARGELIA :  Symbol.CIRCLE,
    Territory.EGITO :  Symbol.TRIANGLE,
    Territory.CONGO :  Symbol.SQUARE,
    Territory.SUDAO :  Symbol.SQUARE,
    Territory.MADAGASCAR : Symbol.CIRCLE,
    Territory.AFRICA_DO_SUL :  Symbol.TRIANGLE,

    #Asia +7
    Territory.ORIENTE_MEDIO :  Symbol.SQUARE,
    Territory.ARAL :  Symbol.TRIANGLE,
    Territory.OMSK :  Symbol.SQUARE,
    Territory.DUDINKA :  Symbol.CIRCLE,
    Territory.SIBERIA :  Symbol.TRIANGLE,
    Territory.TCHITA :  Symbol.TRIANGLE,
    Territory.MONGOLIA :  Symbol.CIRCLE,
    Territory.VLADIVOSTOK :  Symbol.CIRCLE,
    Territory.CHINA : Symbol.CIRCLE,
    Territory.INDIA : Symbol.SQUARE,
    Territory.JAPAO : Symbol.SQUARE,
    Territory.VIETNA : Symbol.TRIANGLE,

    #Oceania +2
    Territory.BORNEU :  Symbol.SQUARE,
    Territory.SUMATRA :  Symbol.SQUARE,
    Territory.NOVA_GUINE : Symbol.CIRCLE,
    Territory.AUSTRALIA : Symbol.TRIANGLE
}

