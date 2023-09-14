import sys
import logging

sys.path.append('../')

from app.models.player import Player
from app.models.board import Territory, Continents
from app.models.territoryCardDeck import TerritoryCard, TerritoryCardDeck
from app.models.objectiveCardDeck import ObjectiveCardDeck, Objectives, ObjectiveCard
from app.controllers.player_controller import PlayerController
from app.controllers.board_controller import BoardController
import random
from enum import Enum
import app.views.visualize_cli_game_state as visualize_cli_game_state
import collections
#TODO validar se a acao do perform fortify, attack ou shift é valida para aquela fase do jogo
#TODO alterar objetivo quando for o caso das cartas de destruir um jogador
#   quando por exemplo ele é o proprio jogador ou o objetivo ja foi cumprido
#TODO implementar fast_attack
#TODO adicionar a regra-> no caso do n jogadores ser inferior a 6, os objetivos relacionados a cor nao participante, deve ser retirada
#TODO arrumar retornos das funcoes para facilitar a api final

class GamePhase(Enum):
    NONE = 0
    FORTIFY = 1
    ATTACK = 2
    SHIFT = 3


class GameController:
    def __init__(self):
        # Initialize the game components
        
        self.territory_card_deck = TerritoryCardDeck()
        self.objective_card_deck = ObjectiveCardDeck()
        self.player_controller = PlayerController()
        self.players_length = None
        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(logging.DEBUG)
        self.current_phase_index = GamePhase.NONE.value

        self.turn_counter = 0
        self.round_counter = 1
        self.board_controller = BoardController(self.logger)
        self.gamestate_matrix = None
        self.player_n_territories_before_attack_dict = {}
        
        self.exchange_cards_turn = 1
        self.gamestates_deque = collections.deque(maxlen=100)
        self.fast_attack = False
        self.winner = None
        #Add a console handler to display logs in the console
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.DEBUG)
        # ch.setFormatter(formatter)
        # self.logger.addHandler(ch)
        
        #  # Add a file handler to save logs to a file
        # fh = logging.FileHandler('game.log')  # Specify the log file name here
        # fh.setLevel(logging.INFO)
        # fh.setFormatter(formatter)
        # self.logger.addHandler(fh)

    def setup_players(self, quantity):
        #TODO bloquear para apenas conseguir mudar comeco do jogo
        self.player_controller.setup_players(quantity)
        self.players_length = self.player_controller.get_players_length()
        for player in self.player_controller.players:
            self.player_n_territories_before_attack_dict[player] = 0

    def get_player_info(self, player_index):
        res = self.board_controller.get_player_status_board_str(Player(player_index))
        return res

    def get_players_info(self):
        for index in range(0, self.players_length):
            self.logger.debug(self.get_player_info(index))
        self.logger.info(self.player_controller.get_players_objectives_str())

    def get_game_info(self):
        res = 'Player ' + str(Player(self.current_player_index)) + ' turn \n'
        res += 'Phase ' + str(GamePhase(self.current_phase_index)) + '\n'
        if(self.current_phase_index == GamePhase.FORTIFY.value):
            res += 'Reserve armies: ' + str(self.player_controller.get_player_reserve(Player(self.current_player_index))) + ' \n'
        res += 'Board status: \n ' + self.board_controller.get_player_status_board_str(Player(self.current_player_index)) + '\n'
        if(self.current_phase_index == GamePhase.ATTACK.value):
            res += 'Attack status: '
        return res

    def get_current_player_info(self):
        res = '---------------- Current player info ---------------- \n'
        res += 'Player ' + str(Player(self.current_player_index)) + ' turn \n'
        res += 'Phase ' + str(GamePhase(self.current_phase_index)) + '\n'
        res += 'Reserve armies: ' + str(self.player_controller.get_player_reserve(Player(self.current_player_index))) + ' \n'
        res += 'Reserve continent armies: ' + str(self.player_controller.get_all_player_reserve_continent(Player(self.current_player_index))) + ' \n'
        res += self.board_controller.get_player_status_board_str(Player(self.current_player_index))
        res += 'Objective: ' + self.player_controller.get_player_objective_str(Player(self.current_player_index)) + '\n'
        res += str(self.player_controller.get_player_territory_cards_str(Player(self.current_player_index))) + '\n'
        return res

    def get_current_phase(self):
        return self.current_phase_index

    def get_gamestate_matrix(self):
        return(self.update_gamestate_matrix())

    def update_gamestate_matrix(self):
        gamestate_matrix = []
        self.logger.debug('updating matrix...')
        for player in Player:
            #adiciona as informacoes de territorio
            if (player not in self.player_controller.players):
                empty_player_vector = [0] * 69
                gamestate_matrix.append(empty_player_vector)
            else:
                player_vector = []
                if(player == Player.CINZA):
                    self.logger.debug('Player cinza army {0}'.format(self.board_controller.get_player_territories_army_vector(player)))
                player_vector.extend(self.board_controller.get_player_territories_army_vector(player))
                player_vector.extend(self.player_controller.get_player_gamestate_vector(player))
                #adiciona informacao fase do jogo
                for phase in GamePhase:
                    if(phase.value == self.current_phase_index and player.value == self.current_player_index):
                        player_vector.append(255)
                    else:
                        player_vector.append(0)
                gamestate_matrix.append(player_vector)
        self.gamestate_matrix = gamestate_matrix
        return gamestate_matrix
    def print_gamestate_matrix(self):
        self.update_gamestate_matrix()
        self.logger.debug('Gamestate matrix: \n')
        self.logger.debug('Gamestate matrix len {0} \n'.format(len(self.gamestate_matrix)))
        for i in range(0, len(self.gamestate_matrix)):
            self.logger.debug('Player {0} len: {1} \n'.format(Player(i), len(self.gamestate_matrix[i])))
            self.logger.debug('Territorios: \n {0} \n'.format(self.gamestate_matrix[i][0:42]))
            self.logger.debug('Cartas territorio: \n {0} \n'.format(self.gamestate_matrix[i][42:44]))
            self.logger.debug('Reserva: \n {0} \n'.format(self.gamestate_matrix[i][44:51]))
            self.logger.debug('Objetivos: \n {0} \n'.format(self.gamestate_matrix[i][51:65]))
            self.logger.debug('Fase: \n {0}'.format(self.gamestate_matrix[i][65:69]))
            self.logger.debug('-' * 50)

    def print_gamestate(self):
        self.update_gamestate_matrix()
        self.logger.info(visualize_cli_game_state.get_str_map(self.gamestate_matrix))
        self.logger.info(self.get_current_player_info())
        self.logger.info(self.get_player_objective_progess_str(Player(self.current_player_index)))
        #visualize_cli_game_state.print_map(self.gamestate_matrix)

    def print_gamestate_color(self):
        self.update_gamestate_matrix()
        visualize_cli_game_state.print_map(self.gamestate_matrix)

    def get_current_player_territories(self):
        return(self.board_controller.get_player_territories(Player(self.current_player_index)))
    
    def get_current_player_reserve(self):
        return(self.player_controller.get_player_reserve(Player(self.current_player_index)))
    
    def get_current_player_all_continent_reserve(self):
        return(self.player_controller.get_all_player_reserve_continent(Player(self.current_player_index)))
    
    def get_current_player_continent_reserve(self, continent_enum):
        return(self.player_controller.get_player_reserve_continent(Player(self.current_player_index), continent_enum))
    
    def get_current_player_continent_reserve_dict(self):
        return(self.player_controller.get_player_reserve_continent_dict(Player(self.current_player_index)))


    def get_current_player_territory_army_dict(self):
        return(self.board_controller.get_player_territory_army_dict(Player(self.current_player_index)))
    
    def get_adjacent_territory_army_dict(self, territory_enum):
        return(self.board_controller.get_adjacent_territory_army_dict(territory_enum))

    def get_current_player_movables_armies_dict(self):
        return(self.board_controller.get_player_movables_armies_dict())




    ###-------------------------------------------------------------------------------
    ### ------------------- Phase game methods ---------------------------------------
    ###-------------------------------------------------------------------------------

    def init_phase(self):
        if (self.current_phase_index == GamePhase.FORTIFY.value):
            #TODO verificar cartas territorios, edit, ja verificado dentro do fortify
            #TODO Atribuir verificar continente completo
            player_n_territories = self.board_controller.get_player_n_territories(Player(self.current_player_index))
            new_troop = int(player_n_territories/2)
            given_reserve = 3 if new_troop < 3 else new_troop
            self.logger.debug('init_phase {0} reserve {1}'.format(Player(self.current_player_index), given_reserve))
            self.player_controller.set_player_reserve(Player(self.current_player_index), given_reserve)
            self.board_controller.update_player_continents(Player(self.current_player_index))
            # if(self.board_controller.update_player_continents(Player(self.current_player_index))):
            #     self.logger.info('Player {0} conquered a continent, getting reserve... '.format(Player(self.current_player_index)))
            #     player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            #     for continent in Continents:
            #         if continent in player_continent_list:
            #             self.player_controller.add_player_reserve_continent(Player(self.current_player_index), continent, continent.extra_soldiers)
            #             self.logger.info('init_phase - Player {0} conquered continent {1}, getting {2} armies'.format(Player(self.current_player_index), continent, continent.extra_soldiers))
        
        elif (self.current_phase_index == GamePhase.ATTACK.value):
            self.logger.debug('init_phase ' + str(Player(self.current_player_index)) + ' attack phase ')
        elif(self.current_phase_index == GamePhase.SHIFT.value):
            self.board_controller.initialize_player_movable_armies_dict(Player(self.current_player_index))
            self.logger.debug('init_phase ' + str(Player(self.current_player_index)) + ' shift phase ')

    def next_phase(self):
        self.logger.info('next phase -> turn counter {0} and players length {1}'.format(self.turn_counter, self.players_length))
        #verifica as rodadas de apenas fortificar

        #primeira rodada de fortificacao
        if ( self.turn_counter <= self.players_length ):
            self.current_player_index = (self.current_player_index + 1) % self.players_length
            self.current_phase_index = GamePhase.FORTIFY.value
        
        elif (self.current_phase_index == GamePhase.FORTIFY.value):
            self.player_n_territories_before_attack_dict[Player(self.current_player_index)] = self.board_controller.get_player_n_territories(Player(self.current_player_index))
            self.current_phase_index = GamePhase.ATTACK.value
            if ( self.check_objective_accoplished() ):
                self.logger.debug('Player {0} won the game'.format(Player(self.current_player_index)))
                self.winner = Player(self.current_player_index)
                self.current_phase_index = GamePhase.NONE.value
                return True
                
        elif (self.current_phase_index == GamePhase.ATTACK.value):
            if(self.board_controller.get_player_n_territories(Player(self.current_player_index)) > self.player_n_territories_before_attack_dict[Player(self.current_player_index)]):
                self.round_counter += 1
                self.logger.info('Player {0} conquistou mais que um territorio, ganhou carta territorio'.format(Player(self.current_player_index)))
                self.player_controller.add_territory_card(Player(self.current_player_index), self.territory_card_deck.draw_card())
            self.current_phase_index = GamePhase.SHIFT.value
        
        elif (self.current_phase_index == GamePhase.SHIFT.value):
            if ( self.check_objective_accoplished() ):
                self.logger.debug('Player {0} won the game'.format(Player(self.current_player_index)))
                self.winner = Player(self.current_player_index)
                self.current_phase_index = GamePhase.NONE.value
                return True
            
            self.current_player_index = (self.current_player_index + 1) % self.players_length
            if (Player(self.current_player_index) in self.player_controller.eliminated_players):
                self.logger.info('Player {0} esta eliminado, avancando proximo jogador...'.format(Player(self.current_player_index)))
                for i in range(0, self.players_length):
                    self.current_player_index = (self.current_player_index + 1) % self.players_length
                    if (Player(self.current_player_index) not in self.player_controller.eliminated_players):
                        break
                    else:
                        self.logger.info('Player {0} esta eliminado, avancando proximo jogador...'.format(Player(self.current_player_index)))
        
            self.current_phase_index = GamePhase.FORTIFY.value            

        self.turn_counter += 1
        self.gamestates_deque.append(self.get_gamestate_matrix())
        self.logger.info(f"Next turn: Player number {self.current_player_index}")
        self.logger.info(f"Next phase is {GamePhase(self.current_phase_index)} for player {Player(self.current_player_index)}")
        self.init_phase()

    def perform_attack(self, attacking_territory_enum=None, defending_territory_enum=None, num_armies_move=1, pass_phase=False):
        if (pass_phase):
            self.logger.debug('Attack --- Passing phase')
            self.next_phase()
            return 
        #verifing if its a valid attack
        self.logger.info('---------------- Attack ----------------')
        self.logger.debug('Attack --- Player {0} attacking territory {1} from territory {2}'.format(Player(self.current_player_index), defending_territory_enum, attacking_territory_enum))
        if (not self.board_controller.allow_attack(Player(self.current_player_index), attacking_territory_enum, defending_territory_enum)):
            self.logger.info('Player {0} cannot attack territory {1} from territory {2}'.format(Player(self.current_player_index), defending_territory_enum, attacking_territory_enum))
            return False
        #perform combat, get number of armies in each territory
        attack_territory_army = self.board_controller.get_territory_army(attacking_territory_enum) - 1 
        defend_territory_army = self.board_controller.get_territory_army(defending_territory_enum)

        attack_territory_army = 3 if attack_territory_army > 3 else attack_territory_army
        defend_territory_army = 3 if defend_territory_army > 3 else defend_territory_army
        #roll dices
        attack_dices = []
        defend_dices = []
        #TODO alterar funcoes random para o estudo realizado anteriormente
        for i in range(0, attack_territory_army):
            attack_dices.append(random.randint(1, 6))
        for i in range(0, defend_territory_army):
            defend_dices.append(random.randint(1, 6))
        
        defending_territory_player = self.board_controller.territory_player_dict[defending_territory_enum]
        self.logger.info('Player {0} territory {1} with {2} army attacking player {3} territory {4} with {5} army(es)'.format(Player(self.current_player_index), attacking_territory_enum, attack_territory_army, defending_territory_player, defending_territory_enum, defend_territory_army))
        self.logger.info(' with dices {0} and {1}'.format(attack_dices, defend_dices))

        #sort dices
        attack_dices.sort(reverse=True)
        defend_dices.sort(reverse=True)
        defending_territory_lost_army = 0
        attacking_territory_lost_army = 0
        #compare dices
        for i in range(0, min(len(attack_dices), len(defend_dices))):
            if(attack_dices[i] > defend_dices[i]):
                self.board_controller.remove_arm_territory(defending_territory_enum, 1)
                defending_territory_lost_army += 1
            else:
                self.board_controller.remove_arm_territory(attacking_territory_enum, 1)
                attacking_territory_lost_army += 1
        self.logger.info('Player {0} attack - lost {1} army(es) in territory {2}'.format(Player(self.current_player_index), attacking_territory_lost_army, attacking_territory_enum))
        self.logger.info('Player {0} defens - lost {1} army(es) in territory {2}'.format(defending_territory_player, defending_territory_lost_army, defending_territory_enum))
       
        #check if territory was conquered
        if ( self.board_controller.get_territory_army(defending_territory_enum) == 0 ):
            self.logger.info('CONQUERED - Player {0}  territory {1}'.format(Player(self.current_player_index), defending_territory_enum))
            self.board_controller.remove_player_territory(defending_territory_enum)
            get_n_movable_army_attack_territory = attack_territory_army - attacking_territory_lost_army

            if (num_armies_move == None or num_armies_move <= 0):
                num_armies_move = 1
            elif(num_armies_move > get_n_movable_army_attack_territory):
                num_armies_move = get_n_movable_army_attack_territory
            
            self.board_controller.add_player_territory(Player(self.current_player_index), defending_territory_enum, num_armies_move)
            self.board_controller.remove_arm_territory(attacking_territory_enum, num_armies_move)
            
            defending_player_n_territories = self.board_controller.get_player_n_territories(defending_territory_player)
            if (defending_player_n_territories == 0):
                self.player_controller.report_eliminated_player(defending_territory_player, Player(self.current_player_index))
                self.logger.info('ELIMINATED - Player {0} was eliminated by player {1}, getting cards from player ....'.format(defending_territory_player, Player(self.current_player_index)))
                #get territory from eliminated player

            self.board_controller.update_player_continents(Player(self.current_player_index))
            self.board_controller.update_player_continents(defending_territory_player)
            #check objective
            if( self.check_objective_accoplished() ):
                self.logger.debug('Player {0} won the game'.format(Player(self.current_player_index)))
                self.winner = Player(self.current_player_index)
                self.current_phase_index = GamePhase.NONE.value
                return True
        #self.update_gamestate_matrix() #TODO generalizar para pre_camada antes de fazer perform_acao e colocar essa linha no final do metodo
    
    def check_objective_accoplished(self):
        self.board_controller.update_player_continents(Player(self.current_player_index))
        current_player_objective:ObjectiveCard = self.player_controller.get_player_objective_card(Player(self.current_player_index))
        self.logger.info('HEAD - Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
        #Conquistar na totalidade a EUROPA, a OCEANIA e mais um terceiro.
        if(current_player_objective.objective == Objectives.OBJ1):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if(self.board_controller.get_player_n_continents(Player(self.current_player_index)) < 3):
                self.logger.info('Player {0} nao possui 3 continentes'.format(Player(self.current_player_index)))                      
                return False
            player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            if(Continents.EUROPA in player_continent_list and Continents.OCEANIA in player_continent_list):
                self.logger.info('Player {0} possui a EUROPA e a OCEANIA'.format(Player(self.current_player_index)))
                return True
            
        #Conquistar na totalidade a ÁSIA e a AMÉRICA DO SUL
        elif(current_player_objective.objective == Objectives.OBJ2):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (self.board_controller.get_player_n_continents(Player(self.current_player_index)) < 2):
                self.logger.info('Player {0} nao possui 2 continentes'.format(Player(self.current_player_index)))
                return False
            player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            if(Continents.ASIA in player_continent_list and Continents.AMERICA_DO_SUL in player_continent_list):
                self.logger.info('Player {0} possui a ASIA e a AMERICA DO SUL'.format(Player(self.current_player_index)))
                return True
            
        #Conquistar na totalidade a EUROPA, a AMÉRICA DO SUL e mais um terceiro
        elif(current_player_objective.objective == Objectives.OBJ3):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (self.board_controller.get_player_n_continents(Player(self.current_player_index)) < 3):
                self.logger.info('Player {0} nao possui 3 continentes'.format(Player(self.current_player_index)))
                return False
            
            player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            if(Continents.EUROPA in player_continent_list and Continents.AMERICA_DO_SUL in player_continent_list):
                self.logger.info('Player {0} possui a EUROPA e a AMERICA DO SUL'.format(Player(self.current_player_index)))
                return True
            
        #Conquistar 18 TERRITÓRIOS e ocupar cada um deles com pelo menos dois exércitos.
        elif(current_player_objective.objective == Objectives.OBJ4):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (self.board_controller.get_player_n_territories(Player(self.current_player_index)) < 18):
                self.logger.info('Player {0} nao possui 18 territorios'.format(Player(self.current_player_index)))
                return False
            else:
                army_plus_2_territories_quantity = 0
                self.logger.info('Player {0} possui 18 territorios ou mais, verificando 2 armies em cada territorio...'.format(Player(self.current_player_index)))
                for territory in self.board_controller.get_player_territories(Player(self.current_player_index)):
                    if(self.board_controller.get_territory_army(territory) >= 2):
                        army_plus_2_territories_quantity += 1
                if(army_plus_2_territories_quantity >= 18):
                    self.logger.info('Player {0} possui 18 territorios com 2 armies'.format(Player(self.current_player_index)))
                    return True
                else:
                    self.logger.info('Player {0} nao possui 18 territorios com 2 armies'.format(Player(self.current_player_index)))
                    return False
            
        #Conquistar na totalidade a ÁSIA e a ÁFRICA.
        elif(current_player_objective.objective == Objectives.OBJ5):
            self.logger.debug('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (self.board_controller.get_player_n_continents(Player(self.current_player_index)) < 2):
                self.logger.info('Player {0} nao possui 2 continentes'.format(Player(self.current_player_index)))
                return False
            player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            if(Continents.ASIA in player_continent_list and Continents.AFRICA in player_continent_list):
                self.logger.info('Player {0} possui a ASIA e a AFRICA'.format(Player(self.current_player_index)))
                return True
        
        #Conquistar na totalidade a AMÉRICA DO NORTE e a ÁFRICA.
        elif(current_player_objective.objective == Objectives.OBJ6):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (self.board_controller.get_player_n_continents(Player(self.current_player_index)) < 2):
                self.logger.info('Player {0} nao possui 2 continentes'.format(Player(self.current_player_index)))
                return False
            player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            if(Continents.AMERICA_DO_NORTE in player_continent_list and Continents.AFRICA in player_continent_list):
                self.logger.info('Player {0} possui a AMERICA DO NORTE e a AFRICA'.format(Player(self.current_player_index)))
                return True
            
        #Conquistar 24 TERRITÓRIOS à sua escolha.
        elif(current_player_objective.objective == Objectives.OBJ7):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            player_n_territories = self.board_controller.get_player_n_territories(Player(self.current_player_index))
            if (player_n_territories < 24):
                self.logger.info('Player {0} nao possui 24 territorios'.format(Player(self.current_player_index)))
                return False
            else:
                self.logger.info('Player {0} possui 24 territorios ou mais. player possui {1} territorios'.format(Player(self.current_player_index), player_n_territories))
                return True
            
        #Conquistar na totalidade a AMÉRICA DO NORTE e a OCEANIA.
        elif(current_player_objective.objective == Objectives.OBJ8):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (self.board_controller.get_player_n_continents(Player(self.current_player_index)) < 2):
                self.logger.info('Player {0} nao possui 2 continentes'.format(Player(self.current_player_index)))
                return False
            player_continent_list = self.board_controller.get_player_continents_list(Player(self.current_player_index))
            if(Continents.AMERICA_DO_NORTE in player_continent_list and Continents.OCEANIA in player_continent_list):
                self.logger.info('Player {0} possui a AMERICA DO NORTE e a OCEANIA'.format(Player(self.current_player_index)))
                return True
            
        #Destruir totalmente OS EXÉRCITOS AZUIS.
        elif(current_player_objective.objective == Objectives.OBJ9):

            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            
            if (Player(self.current_player_index) == Player.AZUL):
                self.logger.info('Player AZUL nao pode ter o objetivo de destruir o player AZUL, trocando objetivo....')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
            
            if (Player.AZUL not in self.player_controller.eliminated_players):
                self.logger.info('Player AZUL nao foi eliminado na partida')
                return False

            if (self.player_controller.eliminated_players_by_dict[Player.AZUL] == Player(self.current_player_index)):
                self.logger.info('Player {0} possui o objetivo de destruir o player {1}'.format(Player(self.current_player_index), Player.AZUL))
                return True
            else:
                self.logger.info('Player Azul já eliminado por outro player {0}'.format(self.player_controller.eliminated_players_by_dict[Player.AZUL]))
                self.logger.info('trocando objetivo para OBJ7, destruir 24 territorios....')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
            
        #Destruir totalmente OS EXÉRCITOS AMARELOS
        elif(current_player_objective.objective == Objectives.OBJ10):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if(Player(self.current_player_index) == Player.AMARELO):
                self.logger.info('Player AMARELO nao pode ter o objetivo de destruir o player AMARELO, trocando objetivo...')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
            
            if (Player.AMARELO not in self.player_controller.eliminated_players):
                self.logger.info('Player AMARELO nao foi eliminado na partida')
                return False
            
            if (self.player_controller.eliminated_players_by_dict[Player.AMARELO] == Player(self.current_player_index)):
                self.logger.info('Player {0} possui o objetivo de destruir o player {1}'.format(Player(self.current_player_index), Player.AMARELO))
                return True
            else:
                self.logger.info('Player Amarelo já eliminado por outro player {0}'.format(self.player_controller.eliminated_players_by_dict[Player.AMARELO]))
                self.logger.info('trocando objetivo para OBJ7, destruir 24 territorios')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
            
        #Destruir totalmente OS EXÉRCITOS VERMELHOS.
        elif(current_player_objective.objective == Objectives.OBJ11):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (Player(self.current_player_index) == Player.VERMELHO):
                self.logger.info('Player VERMELHO nao pode ter o objetivo de destruir o player VERMELHO, trocando objetivo....')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
        
            if (Player.VERMELHO not in self.player_controller.eliminated_players):
                self.logger.info('Player VERMELHO nao foi eliminado na partida')
                return False
            if (self.player_controller.eliminated_players_by_dict[Player.VERMELHO] == Player(self.current_player_index)):
                self.logger.info('Player {0} possui o objetivo de destruir o player {1}'.format(Player(self.current_player_index), Player.VERMELHO))
                return True
            else:
                self.logger.info('Player Vermelho já eliminado por outro player {0}'.format(self.player_controller.eliminated_players_by_dict[Player.VERMELHO]))
                self.logger.info('trocando objetivo para OBJ7, destruir 24 territorios')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
        
        #Destruir totalmente OS EXÉRCITOS CINZA
        elif(current_player_objective.objective == Objectives.OBJ12):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (Player(self.current_player_index) == Player.CINZA):
                self.logger.info('Player CINZA nao pode ter o objetivo de destruir o player CINZA, trocando objetivo....')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False

            if (Player.CINZA not in self.player_controller.eliminated_players):
                self.logger.info('Player CINZA nao foi eliminado na partida')
                return False
            if (self.player_controller.eliminated_players_by_dict[Player.CINZA] == Player(self.current_player_index)):
                self.logger.info('Player {0} possui o objetivo de destruir o player {1}'.format(Player(self.current_player_index), Player.CINZA))
                return True
            else:
                self.logger.info('Player Cinza já eliminado por outro player {0}'.format(self.player_controller.eliminated_players_by_dict[Player.CINZA]))
                self.logger.info('trocando objetivo para OBJ7, destruir 24 territorios...')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
        
        #Destruir totalmente OS EXÉRCITOS Roxo
        elif(current_player_objective.objective == Objectives.OBJ13):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (Player(self.current_player_index) == Player.ROXO):
                self.logger.info('Player ROXO nao pode ter o objetivo de destruir o player ROXO, trocando objetivo....')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
            if (Player.ROXO not in self.player_controller.eliminated_players):
                self.logger.info('Player ROXO nao foi eliminado na partida')
                return False
            if (self.player_controller.eliminated_players_by_dict[Player.ROXO] == Player(self.current_player_index)):
                self.logger.info('Player {0} possui o objetivo de destruir o player {1}'.format(Player(self.current_player_index), Player.ROXO))
                return True
            else:
                self.logger.info('Player Roxo já eliminado por outro player {0}'.format(self.player_controller.eliminated_players_by_dict[Player.ROXO]))
                self.logger.info('trocando objetivo para OBJ7, destruir 24 territorios...')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
    
        #Destruir totalmente OS EXÉRCITOS VERDES.
        elif(current_player_objective.objective == Objectives.OBJ14):
            self.logger.info('Verificando objetivo {0} para o player {1}'.format(current_player_objective, Player(self.current_player_index)))
            if (Player(self.current_player_index) == Player.VERDE):
                self.logger.debug('Player VERDE nao pode ter o objetivo de destruir o player VERDE, trocando objetivo...')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
            
            if (Player.VERDE not in self.player_controller.eliminated_players):
                self.logger.info('Player VERDE nao foi eliminado na partida')
                return False
            if (self.player_controller.eliminated_players_by_dict[Player.VERDE] == Player(self.current_player_index)):
                self.logger.info('Player {0} possui o objetivo de destruir o player {1}'.format(Player(self.current_player_index), Player.VERDE))
                return True
            else:
                self.logger.info('Player Verde já eliminado por outro player {0}'.format(self.player_controller.eliminated_players_by_dict[Player.VERDE]))
                self.logger.info('trocando objetivo para OBJ7, destruir 24 territorios')
                self.player_controller.change_to_alternative_objective(Player(self.current_player_index), Objectives.OBJ7)
                return False
        self.logger.info('Player {0} nao possui nenhum objetivo'.format(Player(self.current_player_index)))
        return False
    
    def get_player_objective_progess_str(self, player_enum):
        res = ""
        objective_card:ObjectiveCard = self.player_controller.get_player_objective_card(player_enum)
        if ( objective_card.objective.conquistar ):
            if (objective_card.objective == Objectives.OBJ4 or objective_card.objective == Objectives.OBJ7):
                player_n_territorios = self.board_controller.get_player_n_territories(player_enum)
                res += "Player possui {0} territorios".format(player_n_territorios)
                if (player_n_territorios >= 18 and objective_card.objective == Objectives.OBJ4):
                    army_plus_2_territories_quantity = 0
                    self.logger.info('Player {0} possui 18 territorios ou mais, verificando 2 armies em cada territorio...'.format(Player(self.current_player_index)))
                    for territory in self.board_controller.get_player_territories(Player(self.current_player_index)):
                        if(self.board_controller.get_territory_army(territory) >= 2):
                            army_plus_2_territories_quantity += 1
                    self.logger.info('Player {0} possui {1} territorios com 2 armies'.format(Player(self.current_player_index), army_plus_2_territories_quantity))
            else:
                player_n_continents = self.board_controller.get_player_n_continents(player_enum)
                res += "Player possui {0} continentes: ".format(player_n_continents)
                player_continents = self.board_controller.get_player_continents_list(player_enum)
                for continent in player_continents:
                    res += " " + str(continent) + " "

        elif ( objective_card.objective.destruir ):
            #iterate over eliminated players by dict and put into res +=
            eliminated_players_list = self.player_controller.eliminated_players
            res += ("Players eliminated: {0} ->".format(len(eliminated_players_list)))
            for item in eliminated_players_list:
                res += str(item) + " "
            res += "\n eliminated players ->"
            for player, eliminated_player in self.player_controller.eliminated_players_by_dict.items():
                res += str(player) + " eliminated by" + str(eliminated_player) + " \n"
        return res
        #if objective is conquistar
        # return objective_card.get_progress_description(player_enum)


    def get_extra_army_next_exchange_territory_cards(self):
        if (self.exchange_cards_turn == 1):
            return 4
        elif (self.exchange_cards_turn == 2):
            return 6
        elif (self.exchange_cards_turn == 3):
            return 8
        elif (self.exchange_cards_turn == 4):
            return 10
        elif (self.exchange_cards_turn == 5):
            return 12
        elif (self.exchange_cards_turn == 6):
            return 15
        elif (self.exchange_cards_turn == 7):
            return 20
        else:
            return ((self.exchange_cards_turn - 7) * 5 + 20)

    def perform_fortify(self, territory_enum, num_armies, exchange_cards=False):
        player_enum = Player(self.current_player_index)
        
        if (exchange_cards):
            #TODO - PERFORMANCE retirar essa verificacao a todo momento q for chamado perform fortify
            #colocar apenas quando mudar de fase, colocar apenas a verificao se o player tem o atributo .can_trade_cards == True
            if (self.player_controller.player_has_exchangable_cards(player_enum)): 
                self.player_controller.remove_player_exchangable_cards(player_enum)
                self.logger.debug('Fortify --- Exchanging cards....')
                self.player_controller.add_player_reserve(player_enum, self.get_extra_army_next_exchange_territory_cards())
                self.logger.info('Player {0} exchanged cards and got {1} armies'.format(player_enum, self.get_extra_army_next_exchange_territory_cards()))
                self.exchange_cards_turn += 1
                return True
        
        player_continents_reserve = self.player_controller.get_all_player_reserve_continent(player_enum)
        player_normal_reserve = self.player_controller.get_player_reserve(player_enum)
        
        if (player_continents_reserve > 0):
            self.logger.info('jogador possui reserva de continente completo a gastar {0}'.format(player_continents_reserve))
            player_continent_list = self.board_controller.get_player_continents_list(player_enum)
            if (player_continents_reserve >= num_armies):
                for continent in player_continent_list:
                    if (territory_enum in continent.territory_list and self.board_controller.player_own_territory(player_enum, territory_enum)):
                        player_continent_army = self.player_controller.get_player_reserve_continent(player_enum, continent)
                        if (player_continent_army >= num_armies):
                            self.board_controller.add_arm_territory(territory_enum, num_armies)
                            self.player_controller.remove_player_reserve_continent(player_enum, continent, num_armies)

        elif( player_normal_reserve > 0 ):
            if( (player_normal_reserve >= num_armies) and self.board_controller.player_own_territory(player_enum, territory_enum) ):
                self.board_controller.add_arm_territory(territory_enum, num_armies )
                self.player_controller.remove_player_reserve(player_enum, num_armies)
            else:
                self.logger.error('Player {0} does not have enough armies {1} (reserve: {2}) to fortify territory {3}'.format(player_enum, num_armies, self.player_controller.get_player_reserve(player_enum), territory_enum))
                return False

        if (self.player_controller.get_all_player_reserves(player_enum) == 0):
            self.logger.info('Player {0} has no more armies to fortify... going to next phase'.format(player_enum))
            self.next_phase()
            return True

    def perform_shift_troop(self, origin_territory_enum=None, destination_territory_enum=None, num_armies=None, pass_phase=False):
        if (pass_phase):
            self.logger.info('Shift --- Passing phase')
            self.next_phase()
            return True
        
        if (self.board_controller.allow_shift_troop(Player(self.current_player_index), origin_territory_enum, destination_territory_enum, num_armies)):
            self.board_controller.remove_movable_army(origin_territory_enum, num_armies)
            self.board_controller.remove_arm_territory(origin_territory_enum, num_armies)
            self.board_controller.add_arm_territory(destination_territory_enum, num_armies)
            self.logger.info('Player {0} shifted {1} armies from {2} to {3}'.format(Player(self.current_player_index), num_armies, origin_territory_enum, destination_territory_enum))
            return True
        else:
            self.logger.info('Player {0} cannot shift troops'.format(Player(self.current_player_index)))
            return False

    def perform_fortify_vector(self, fortify_vector_territories, exchange_card=False):
        if (len (fortify_vector_territories) != 42):
            self.logger.debug('perform_fortify_vector: Invalid number of territories {0}'.format(len(fortify_vector_territories)))
            return False
        
        #get fortify_vetor_territories indexes that are > 0
        fortify_vector_territories_indexes = [i for i, x in enumerate(fortify_vector_territories) if x > 0]
        if (len(fortify_vector_territories_indexes) > 0):
            for territory_index in fortify_vector_territories_indexes:
                self.logger.debug('perform_fortify_vector: Performing fortify in territory index {0} with {1} armies'.format(territory_index, fortify_vector_territories[territory_index]))
                territory_index_ter = Territory.get_territory_by_index(territory_index)
                self.logger.debug('perform_fortify_vector: Performing fortify in territory {0} with {1} armies'.format(territory_index_ter, fortify_vector_territories[territory_index]))
                
                if ( self.board_controller.player_own_territory(Player(self.current_player_index), territory_index_ter) ):
                    self.logger.debug('perform_fortify_vector: Performing fortify in territory {0} with {1} armies'.format(territory_index_ter, fortify_vector_territories[territory_index]))
                    self.perform_fortify(territory_index_ter, fortify_vector_territories[territory_index], exchange_card)
        else:
            self.logger.debug('perform_fortify_vector: Invalid number of territories {0}'.format(len(fortify_vector_territories_indexes)))
            return False


    def perform_troop_shift_vector(self, shift_vector_territories, num_armies_move):
        if (len (shift_vector_territories) != 42):
            self.logger.debug('perform_troop_shift_vector: Invalid number of territories {0}'.format(len(shift_vector_territories)))
            return False
        
        #get shift_vetor_territories indexes that are > 0
        shift_vector_territories_indexes = [i for i, x in enumerate(shift_vector_territories) if x > 0]
        if (len(shift_vector_territories_indexes) % 2 != 0):
            self.logger.debug('perform_troop_shift_vector: Invalid number of territories {0}'.format(len(shift_vector_territories_indexes)))
            return False
        current_player_enum = Player(self.current_player_index)
        territory_one = Territory.get_territory_by_index(shift_vector_territories_indexes[0])
        territory_two = Territory.get_territory_by_index(shift_vector_territories_indexes[1])

        territory_one_value = shift_vector_territories[shift_vector_territories_indexes[0]]
        territory_two_value = shift_vector_territories[shift_vector_territories_indexes[1]]

        current_player_own_territory_one = self.board_controller.player_own_territory(current_player_enum, territory_one)
        current_player_own_territory_two = self.board_controller.player_own_territory(current_player_enum, territory_two)
        
        if (current_player_own_territory_one and current_player_own_territory_two):
            self.logger.debug('current player owns both territories')
            
            if (territory_one_value <= 128 and territory_two_value == 255):
                self.logger.debug('performing shift vector {0} -> {1}'.format(territory_one, territory_two))
                self.perform_shift_troop(territory_one, territory_two, num_armies_move)
            
            elif (territory_one_value == 255 and territory_two_value <= 128):
                self.logger.debug('performing shift vector {0} -> {1}'.format(territory_two, territory_one))
                self.perform_shift_troop(territory_two, territory_one, num_armies_move)
            
            return True
        else:
            self.logger.debug('current player does not own both territories')
            return False


    def perform_attack_vector(self, attack_vector_territories, num_armies_move):
        
        if (len (attack_vector_territories) != 42):
            self.logger.debug('perform_attack_vector: Invalid number of territories {0}'.format(len(attack_vector_territories)))
            return False
        
        #get attack_vetor_territories indexes that are > 0
        attack_vector_territories_indexes = [i for i, x in enumerate(attack_vector_territories) if x > 0]
        if ( len(attack_vector_territories_indexes) % 2 != 0 ):
            self.logger.debug('perform_attack_vector: Invalid number of territories {0}'.format(len(attack_vector_territories_indexes)))
            return False
        current_player_enum = Player(self.current_player_index)
        territory_one = Territory.get_territory_by_index(attack_vector_territories_indexes[0])
        territory_two = Territory.get_territory_by_index(attack_vector_territories_indexes[1])
        current_player_own_territory_one = self.board_controller.player_own_territory(current_player_enum, territory_one)
        current_player_own_territory_two = self.board_controller.player_own_territory(current_player_enum, territory_two)
        if (current_player_own_territory_one and current_player_own_territory_two):
            self.logger.debug('current player owns both territories')
            return False
        elif (not current_player_own_territory_one and not current_player_own_territory_two):
            self.logger.debug('current player does not own any of the territories')
            return False
        elif (current_player_own_territory_one and not current_player_own_territory_two):
            self.logger.debug('performing attack vector {0} -> {1}'.format(territory_one, territory_two))
            self.perform_attack(territory_one, territory_two, num_armies_move)
            return True
        elif (not current_player_own_territory_one and current_player_own_territory_two):
            self.logger.debug('performing attack vector {0} -> {1}'.format(territory_two, territory_one))
            self.perform_attack(territory_two, territory_one, num_armies_move)
            return True
        self.logger.error('perform_attack_vector: None action performed')
        return False
    
    #def get_
    #Action vector
    #attack 1| Fortify 1| Shift 1| Pass 1| Extra_ num army move 1 | Territories (42 columns)
    def perform_action_vector(self, action_vector):
        attack = action_vector[0]
        fortify = action_vector[1]
        shift = action_vector[2]
        pass_phase = action_vector[3]
        extra = action_vector[4]
                
        if (len (action_vector) != 47):
            self.logger.debug('perform_action_vector: Invalid number of columns {0}'.format(len(action_vector)))
            return False
        self.logger.debug('perform_action_vector: attack {0} fortify {1} shift {2} pass {3} extra {4}'.format(attack, fortify, shift, pass_phase, extra))

        if (pass_phase):
            self.logger.debug('perform_action_vector: Pass phase')
            self.next_phase()
            self.update_gamestate_matrix()
            return True
        
        if (attack):
            attack_vector = action_vector[5:47]
            num_armies_move = extra
            self.logger.debug('perform_action_vector: attack vector {0}'.format(attack_vector))
            action_ret = self.perform_attack_vector(attack_vector, num_armies_move)
            self.update_gamestate_matrix()
            return (action_ret)
        
        elif (fortify):
            fortify_vector = action_vector[5:47]
            exchange_card = extra
            self.logger.debug('perform_action_vector: fortify vector {0}'.format(fortify_vector))
            action_ret = self.perform_fortify_vector(fortify_vector, exchange_card)
            self.update_gamestate_matrix()
            return (action_ret)
        
        elif (shift):
            shift_vector = action_vector[5:47]
            num_armies_move = extra
            self.logger.debug('perform_action_vector: shift vector {0}'.format(shift_vector))
            action_ret = self.perform_troop_shift_vector(shift_vector, num_armies_move)
            self.update_gamestate_matrix()
            return (action_ret)
        
        else:
            self.logger.error('perform_action_vector: None action performed')
            return False



    ###-------------------------------------------------------------------------------
    ### ------------------- Start game methods ---------------------------------------
    ###-------------------------------------------------------------------------------

    def set_start_territories(self):
        territories_deck = TerritoryCardDeck(insert_wild_cards=False)
        player_index = random.randint(0, self.players_length - 1)
        self.logger.debug('Setting territories')
        self.logger.debug('Comecou distribuir territorios index: {0} -> {1}'.format(player_index, Player(player_index)))
        #distribuidor pega as cartas e distribui sentido horario, comecando pelo jogador a sua esquerda
        for i in range(0, territories_deck.get_deck_length()):
            player_index = (player_index + 1) % self.players_length
            self.player_controller.players[player_index]
            
            territory_card = territories_deck.draw_card()
            #atribui o territorio da carta ao jogador, adiciona uma tropa a cada territorio
            self.board_controller.add_player_territory(Player(player_index), territory_card.territory, 1)
            
           
           # self.logger.debug('carta {0} -> {1} '.format(territory_card, Player(player_index)))
        #for every player update continents
        for index in range(0, self.players_length):
            self.board_controller.update_player_continents(Player(index))


        #jogo tem comeco com o jogador seguinte do qual recebeu a ultima carta
        self.current_player_index = player_index
        self.logger.debug('Jogador {0}:{1} ultimo a receber a carta território'.format(self.current_player_index, Player(self.current_player_index)))

        return None
        
    def set_start_objectives(self):
        self.logger.debug('Setting objectives')
        for index in range (0, self.players_length):
            objective_card = self.objective_card_deck.draw_card()
            self.logger.info('Jogador {0} -> {1}'.format(Player(index), str(objective_card)))
            self.player_controller.set_player_objective_card(Player(index), objective_card)
        

    
    def start_game(self, n_players):
        self.logger.info('Game started.')
        self.setup_players(n_players)
        self.logger.info('Distribuindo territorios')
        self.set_start_territories()
        self.logger.info('Distribuindo cartas objetivos')
        self.set_start_objectives()
        self.next_phase()

        #self.get_players_info()
        #Primeira rodada apenas fortificar
        #var = True
        #while(var)
        #{
        #    self.logger.info('Player ' + self.current_player_index + ' -> ' + )
        #    var = False
        #}
        #Colocar etapas do jogo
        # 1 - fortificar -> recompensa /2 min 3. , troca cartas, 
        # 2 - ataque -> iterativo, invadir.
        # 3 - deslocar.
        # 4 - recebe carta territorio


