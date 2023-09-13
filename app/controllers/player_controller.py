from app.models.player import Player
from app.models.objectiveCardDeck import ObjectiveCard, Objectives
from app.models.board import Continents
from app.models.territoryCardDeck import Symbol
import random

class PlayerController:
    def __init__(self):
        self.players = []
        self.current_player_index = 0

        self.eliminated_players = []
        self.eliminated_players_by_dict = {}

    #Player management methods
    def setup_players(self, quantity):
        if ( quantity < 3 or quantity > 6):
            return False
        for i in range(0, quantity):
            self.players.append(Player(i))

    def report_eliminated_player(self, player_enum, eliminated_by):
        self.eliminated_players.append(player_enum)
        self.eliminated_players_by_dict[player_enum] = eliminated_by

        #get eliminated player cards
        player_territory_cards_list = self.get_player_territory_cards(player_enum)

        attack_player_n_territory_cards = len(self.get_player_territory_cards(eliminated_by))
        if (attack_player_n_territory_cards + len(player_territory_cards_list) > 5):
            surplus = attack_player_n_territory_cards + len(player_territory_cards_list) - 5
            random.shuffle(player_territory_cards_list)
            #pop surplus cards
            for i in range(0, surplus):
                player_territory_cards_list.pop()
    
        for card in player_territory_cards_list:
            self.add_territory_card(eliminated_by, card)
        
        self.remove_all_territory_cards(player_enum)

    def get_players_length(self):
        return (len(self.players))

    #Player reserve amry methods
    def set_player_reserve(self, player_enum, army):
        self.players[player_enum.index].reserve_armies = army  
    
    def get_player_reserve(self, player_enum):
        return(self.players[player_enum.index].reserve_armies)
    
    def add_player_reserve(self,player_enum, army):
        self.players[player_enum.index].reserve_armies += army

    def remove_player_reserve(self,player_enum, army):
        self.players[player_enum.index].reserve_armies -= army
    
    def get_player_reserve_continent(self, player_enum, continent_enum):
        return(self.players[player_enum.index].reserve_armies_continent_dict[continent_enum])
    
    def get_all_player_reserve_continent(self, player_enum):
        total_continent_reserve = 0
        for continent in Continents:
            total_continent_reserve += self.players[player_enum.index].reserve_armies_continent_dict[continent]
        return total_continent_reserve

    def remove_player_reserve_continent(self, player_enum, continent_enum, army):
        self.players[player_enum.index].reserve_armies_continent_dict[continent_enum] -= army

    def add_player_reserve_continent(self, player_enum, continent_enum, army):
        self.players[player_enum.index].reserve_armies_continent_dict[continent_enum] += army

    def get_all_player_reserves(self, player_enum):
        return(self.players[player_enum.index].reserve_armies + self.get_all_player_reserve_continent(player_enum))    

    def get_player_reserve_continent_dict(self, player_enum):
        return(self.players[player_enum.index].reserve_armies_continent_dict)

    #Player territory cards methods
    def get_player_territory_cards(self, player_enum):
        return(self.players[player_enum.index].territory_cards)
    
    def add_territory_card(self, player_enum, territory_card):
        if(len(self.players[player_enum.index].territory_cards) == 5):
            return False
        self.players[player_enum.index].territory_cards.append(territory_card)

    def remove_territory_card(self, player_enum, territory_card):
        #print('remove_territory_card: {0} from player {1}'.format(territory_card, player_enum))
        self.players[player_enum.index].territory_cards.remove(territory_card)

    def remove_all_territory_cards(self, player_enum):
        self.players[player_enum.index].territory_cards.clear()

    def player_has_exchangable_cards(self, player_enum):
        self.players[player_enum.index].player_excanganble_cards.clear()
        if(len(self.players[player_enum.index].territory_cards) >= 3):
            symbols_quant_list = [0,0,0,0] #Square, triangle, circle, wild            
            player_territory_cards_list = self.get_player_territory_cards(player_enum)
            
            for card in player_territory_cards_list:
                if(card.symbol == Symbol.SQUARE):
                    symbols_quant_list[0] += 1
                elif(card.symbol == Symbol.TRIANGLE):
                    symbols_quant_list[1] += 1
                elif(card.symbol == Symbol.CIRCLE):
                    symbols_quant_list[2] += 1
                elif(card.symbol == Symbol.WILDCARD):
                    symbols_quant_list[3] += 1

            #Check if got triple of any symbol
            if( any(quant >= 3 for quant in symbols_quant_list) ):
                if (symbols_quant_list[0] >= 3):
                    symbol_to_pin = Symbol.SQUARE
                elif (symbols_quant_list[1] >= 3):
                    symbol_to_pin = Symbol.TRIANGLE
                elif (symbols_quant_list[2] >= 3):
                    symbol_to_pin = Symbol.CIRCLE
                else:
                    symbol_to_pin = Symbol.WILDCARD
                count_append = 0
                for i in range(0, len(player_territory_cards_list)):
                    card = player_territory_cards_list[i]
                    if(card.symbol == symbol_to_pin):
                        count_append += 1
                        self.players[player_enum.index].player_excanganble_cards.append(card)
                        if(count_append == 3):
                            break

                self.players[player_enum.index].can_trade_cards = True
                return True
            
            #Check if got one of each symbol
            elif (symbols_quant_list[0] >= 1 and symbols_quant_list[1] >= 1 and symbols_quant_list[2] >= 1):
                done_square = False
                done_triangle = False
                done_circle = False

                count_append = 0
                for i in range(0, len(player_territory_cards_list)):
                    card = player_territory_cards_list[i]
                    if (card.symbol == Symbol.SQUARE and not done_square):
                        count_append += 1
                        self.players[player_enum.index].player_excanganble_cards.append(card)
                        done_square = True
                    elif (card.symbol == Symbol.TRIANGLE and not done_triangle):
                        count_append += 1
                        self.players[player_enum.index].player_excanganble_cards.append(card)
                        done_triangle = True
                    elif (card.symbol == Symbol.CIRCLE and not done_circle):
                        count_append += 1
                        self.players[player_enum.index].player_excanganble_cards.append(card)
                        done_circle = True
                    if(count_append == 3):
                        break
                self.players[player_enum.index].can_trade_cards = True
                return True
            
            #Check if got two of any symbol
            elif(symbols_quant_list[3] == 1):
                if (symbols_quant_list[3] == 1 and symbols_quant_list[0] >= 1 and symbols_quant_list[1] >= 1):
                    pin_symbols = [Symbol.SQUARE, Symbol.TRIANGLE, Symbol.WILDCARD]
                    self.players[player_enum.index].can_trade_cards = True                                
                elif (symbols_quant_list[3] == 1 and symbols_quant_list[0] >= 1 and symbols_quant_list[2] >= 1):
                    pin_symbols = [Symbol.SQUARE, Symbol.CIRCLE, Symbol.WILDCARD]
                    self.players[player_enum.index].can_trade_cards = True
                elif (symbols_quant_list[3] == 1 and symbols_quant_list[1] >= 1 and symbols_quant_list[2] >= 1):
                    pin_symbols = [Symbol.TRIANGLE, Symbol.CIRCLE, Symbol.WILDCARD]
                    self.players[player_enum.index].can_trade_cards = True

            elif(symbols_quant_list[3] == 2):
                if (symbols_quant_list[3] == 2 and symbols_quant_list[0] >= 1):
                    pin_symbols = [Symbol.SQUARE, Symbol.WILDCARD]
                    self.players[player_enum.index].can_trade_cards = True                  
                elif (symbols_quant_list[3] == 2 and symbols_quant_list[1] >= 1):
                    pin_symbols = [Symbol.TRIANGLE, Symbol.WILDCARD]
                    self.players[player_enum.index].can_trade_cards = True
                elif (symbols_quant_list[3] == 2 and symbols_quant_list[2] >= 1):
                    pin_symbols = [Symbol.CIRCLE, Symbol.WILDCARD]
                    self.players[player_enum.index].can_trade_cards = True
            
            if (self.players[player_enum.index].can_trade_cards):
                count_append = 0
                for i in range(0, len(player_territory_cards_list)):
                    card = player_territory_cards_list[i]
                    if(card.symbol in pin_symbols):
                        count_append += 1
                        self.players[player_enum.index].player_excanganble_cards.append(card)
                        if(count_append == 3):
                            break
                return True
        return False


    def remove_player_exchangable_cards(self, player_enum):
        #print territory cards
        #print('territory cards player {0} len {1} -> \n'.format(player_enum, len(self.players[player_enum.index].territory_cards)))
        #for card in self.players[player_enum.index].territory_cards:
        #    print(str(card) + " ")
        #print('exchangable cards {0}: \n'.format(len(self.players[player_enum.index].player_excanganble_cards)))
        #for card in self.players[player_enum.index].player_excanganble_cards:
        #    print(str(card) + " ")

        if(self.players[player_enum.index].can_trade_cards):
            self.players[player_enum.index].can_trade_cards = False
            for card in self.players[player_enum.index].player_excanganble_cards:
                self.remove_territory_card(player_enum, card)
            self.players[player_enum.index].player_excanganble_cards.clear()

    #Players objective methods
    def set_player_objective_card(self, player_enum:Player, objective_card):
        self.players[player_enum.index].objective_card = objective_card

    def get_player_objective_card(self, player_enum):
        return(self.players[player_enum.index].objective_card)

    def remove_objective(self, player_enum):
        # Remove a completed objective from the player's objectives
        self.players[player_enum.index].objective_card = None

    def change_to_alternative_objective(self, player_enum, objective):
        self.players[player_enum.index].objective_card.objective = objective



    #Information methods
    def get_player_objective_str(self, player_enum):
        objective_card:ObjectiveCard = self.get_player_objective_card(player_enum)
        return objective_card.get_description()
    
    def get_players_objectives_str(self):
        res = "\n\nPlayers objectives:"
        for player in self.players:
               res += "\n\t" + player.name + " -> " + self.get_player_objective_str(player)

        return (res)

    def get_players_info(self):
        res = str(self.get_players_length()) + " Players -> \n"
        for player in self.players:
            res += str(player) +  " \n"
        return(res)
    def get_player_territory_cards_str(self, player_enum):
        territoy_cards_list = self.get_player_territory_cards(player_enum)
        res = "Territory cards {0} -> ".format(len(territoy_cards_list))
        for card in territoy_cards_list:
            res += str(card) + " | "
        return(res)
    #Vetor dado pelo player controller
    #N_cartas 1 | troca disponivel 1 | Free Armie 7 cols | Objetivo 13 cols = 22 cols
    def get_player_gamestate_vector(self, player_enum):
        res = []
        res.append(len(self.players[player_enum.index].territory_cards))

        if(self.player_has_exchangable_cards(player_enum)):
           res.append(1)
        else:
            res.append(0)
        #Reserve armies
        res.append(self.players[player_enum.index].reserve_armies)
        for continent in Continents:
            res.append(self.players[player_enum.index].reserve_armies_continent_dict[continent])
        #Objective
        for objective in Objectives:
            if(self.players[player_enum.index].objective_card.objective == objective):
                res.append(255)
            else:
                res.append(0)
        return(res)

    

    def __str__(self):
        return f"Player Controller"