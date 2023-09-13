from enum import Enum     
from app.models.board import Continents
class Player(Enum):
    AZUL = 0
    VERMELHO = 1
    VERDE = 2
    ROXO = 3
    AMARELO = 4
    CINZA = 5

    def __init__(self, value):
        self.index = value
        
        self.objective_card = None  # List to hold ObjectiveCard objects for completed objectives
        self.reserve_armies = 0
        self.reserve_armies_continent_dict = {}
        self.territory_cards = []
        self.can_trade_cards = False
        self.player_excanganble_cards = []

        self.eliminated = False
        self.eliminated_by = None
        self.won = False
        for continent in Continents:
            self.reserve_armies_continent_dict[continent] = 0

    def __str__(self):
         return f"{self._name_} ({self.value})"
