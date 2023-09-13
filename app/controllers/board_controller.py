from app.models.board import Board, Territory, Continents
from app.models.player import Player
from app.models.objectiveCardDeck import Objectives

class BoardController: 
    def __init__(self, logger):
        self.board = Board()
        self.territory_player_dict = {}
        self.territory_army_dict = {}
        self.continent_player_dict = {}
        self.player_movable_armies_dict = {}
        self.logger = logger
    
    #Territory Methods
    def player_own_territory(self, player_enum, territory_enum):
        if (territory_enum == None):
            self.logger.error("territory_enum is None")
            return False
        if(territory_enum in self.territory_player_dict):
            if(self.territory_player_dict[territory_enum] == player_enum):
                return True
        return False

    def add_player_territory(self, player_enum, territory_enum, army_quant):
        self.territory_player_dict[territory_enum] = player_enum
        self.territory_army_dict[territory_enum] = army_quant
    
    def remove_player_territory(self, territory_enum):
        if territory_enum in self.territory_player_dict:
            del self.territory_player_dict[territory_enum]
        if territory_enum in self.territory_army_dict:
            del self.territory_army_dict[territory_enum]
    
    def get_player_n_territories(self, player_enum):
            return len([key for key, val in self.territory_player_dict.items() if val.index == player_enum.index])
    
    def get_player_territories(self, player_enum):
        return [key for key, val in self.territory_player_dict.items() if val.index == player_enum.index]
    
    #Continent methods
    def add_player_continent(self, player_enum, continent_enum):
        self.continent_player_dict[continent_enum] = player_enum

    def remove_player_continent(self, continent_enum):
        #verify if continent is in dict
        if(continent_enum in self.continent_player_dict):
            del self.continent_player_dict[continent_enum]

    def get_territory_continent(self, territory_enum):
        return self.board.get_territory_continent(territory_enum)
   
    def get_player_n_continents(self, player_enum):
        return len([key for key, val in self.continent_player_dict.items() if val.index == player_enum.index])
    
    def get_player_continents_list(self, player_enum):
        return [key for key, val in self.continent_player_dict.items() if val.index == player_enum.index]
   
    def update_player_continents(self, player_enum):
        self.logger.debug('update continents')
        has_continent = False
        for continent in Continents:
            player_owns_continent = True
            #self.logger.debug('continent: {0}:\n'.format(continent))
            for territory in continent.territory_list:
                #self.logger.debug('\t {0} -> '.format(territory))
                if(not self.player_own_territory(player_enum, territory)):
                    #self.logger.debug('player does not own territory \n'.format(territory))
                    player_owns_continent = False
                    break
                #else:
                    #self.logger.debug('player owns territory \n'.format(territory))
            if(player_owns_continent):
                self.logger.info("Player {0} owns continent {1}".format(player_enum, continent))
                self.add_player_continent(player_enum, continent)
                has_continent = True
            else:
                #self.logger.info("Player {0} does not own continent {1}".format(player_enum, continent))
                self.remove_player_continent(continent)
        if(not has_continent):
            self.logger.info("Player {0} does not own any continent".format(player_enum))
        return has_continent
    def update_players_continents(self):
        for player in Player:
            self.update_player_continents(player)
    #Arm methods
    def add_arm_territory(self, territory_enum, army_quant):
        self.territory_army_dict[territory_enum] += army_quant

    def remove_arm_territory(self, territory_enum, army_quant):
        self.territory_army_dict[territory_enum] -= army_quant

    def get_territory_army(self, territory_enum):
        return self.territory_army_dict[territory_enum]

    #Attack methods
    def allow_attack(self, player_enum, attack_territory_enum, defending_territory_enum):
        if(self.get_territory_army(attack_territory_enum) > 1):
            if self.player_own_territory(player_enum, attack_territory_enum) :
                adj_ter_list = self.board.get_adjacent_Territory(attack_territory_enum)
                if(defending_territory_enum in adj_ter_list):
                    self.logger.debug("territory {0} is adjacent to {1}".format(defending_territory_enum, attack_territory_enum))
                    return True
                else:
                    self.logger.debug("territory {0} is not adjacent to {1}".format(defending_territory_enum, attack_territory_enum))
                    return False
            else:
                self.logger.debug("Player {0} does not own territory {1} or {2} is not adjacent to {1}".format(player_enum, attack_territory_enum, defending_territory_enum))
                return False
        else:
            self.logger.debug("Player {0} does not have enough armies in territory {1}".format(player_enum, attack_territory_enum))
            return False

    #Shift troops methods
    def initialize_player_movable_armies_dict(self, player_enum):
        #reset dictionary
        self.player_movable_armies_dict = {}
        self.movable_army_sum = 0
        #for each territory owned by player, add armies - 1 to movable armies dict
        for territory in self.get_player_territories(player_enum):
            self.player_movable_armies_dict[territory] = self.territory_army_dict[territory] - 1
            self.movable_army_sum += self.territory_army_dict[territory] - 1
            if(self.player_movable_armies_dict[territory] <= 0):
                del self.player_movable_armies_dict[territory]
    
    def remove_movable_army(self, territory_enum, army_quant):
        if (self.player_movable_armies_dict[territory_enum]):
            self.player_movable_armies_dict[territory_enum] -= army_quant
            return True
        else:
            return False
        
    def allow_shift_troop(self, player_enum, origin_territory_enum, destination_territory_enum, army_quant):

        if (origin_territory_enum == destination_territory_enum):
            self.logger.info("Origin and destination territories are the same")
            return False
        if(not self.player_own_territory(player_enum, origin_territory_enum)):
            self.logger.info("Player does not own territory origin {0}".format(origin_territory_enum))
            return False
        elif(not self.player_own_territory(player_enum, destination_territory_enum)):
            self.logger.info("Player does not own territory destination{0}".format(destination_territory_enum))
            return False
        if (origin_territory_enum not in self.player_movable_armies_dict):
            self.logger.info("Player does not have movable armies in territory {0}".format(origin_territory_enum))
            return False
        if(army_quant <= self.player_movable_armies_dict[origin_territory_enum]):
            if(origin_territory_enum in self.board.get_adjacent_Territory(destination_territory_enum)):
                return True
            else:
                self.logger.info("territory {0} is not adjacent to {1}".format(destination_territory_enum, origin_territory_enum))
                return False
        else:
            self.logger.info("Player does not have enough movable armies in territory {0}".format(origin_territory_enum))
            return False

    def get_player_movables_armies_dict(self):
        return self.player_movable_armies_dict

    
    #Status methods
    
    def get_player_status_board_str(self, player_enum:Player):
        #iterate over player enum on BoardTerritory player list
        res = ''
        res += "\n Player {0} ({1}) status board: ".format(player_enum.name, player_enum.value)
        res += "Territories: (Territory - ArmyQuant.)\n"
        territories_list = self.get_player_territories(player_enum)
        for territory in territories_list:
            res += "\t " + territory.name + " - " + str(self.territory_army_dict[territory]) + " \n"
        # for boardTerritory in self.player_bterritories_dict[player_enum]:
        #     res += boardTerritory.name + ", " #TODO arrumar essa str usando o join list
        res  += " \n"
        return res
    
    def get_player_territories_army_vector(self, player_enum):
        res = []
        for territory in Territory:
            if(self.player_own_territory(player_enum, territory)):
                res.append(self.territory_army_dict[territory])
            else:
                res.append(0)
        return res
    
    def get_player_territory_army_dict(self, player_enum):
        ret_dict = {}
        for key,val in self.territory_player_dict.items():
            if(val.index == player_enum.index):
                ret_dict[key] = self.territory_army_dict[key]
        
        return(ret_dict)
    
    def get_adjacent_territory_army_dict(self, territory_enum):
        ret_dict = {}
        for territory in self.board.get_adjacent_Territory(territory_enum):
            ret_dict[territory] = self.territory_army_dict[territory]
        return(ret_dict)
    

    


    # def get_player_adj_territory_army_dict(self, player_enum):
    #     return_dict = {}






