
import sys
import random
import time
import logging
sys.path.append('../')

from app.controllers.game_controller import GameController, GamePhase
from app.models.board import Territory, Continents, Board
from app.models.player import Player



class gamestate_matrix():
    def __init__(self):
        None
        self.
    #Matriz de OCR possui o formato 6 linhas por 41 colunas     
    def update_gamestate_matrix(self, ocr_matrix):
        self.ocr_matrix = ocr_matrix
        
    def process_ocr_matrix():
        
        return None
        
    # def get_current_player_territories():
        
    #     return None
    # def get_current_player_reserve():
    #     return self.player_reserve
        
    # def get_current_player_all_continent_reserve():
    #     return 0
    # def get_current_player_territory_army_dict():
    #     player_line = self.ocr_matrix[self.player_index]
    #     territory_army_dict = {}
    #     for coluna in player_line:
            
    #     Territory.by_index()
    # def get_adjacent_territory_army_dict
    
    # def get_curr
        

#TODO eliminar o game controller da classe do agent matrix 
class simple_agent_matrix():
    def __init__(self, game_controller, attack_full_dices_chance = 0.5, attack_pass_chance = 0.5, shift_pass_chance = 0.1, log_name = 'agentX', 
                 smart_attack = False, smart_fortify = False, smart_fortify_surplus = 3,
                 smart_shift = False):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #chaces
        self.attack_full_dices_chance = attack_full_dices_chance
        self.attack_pass_chance = attack_pass_chance
        self.shift_pass_chance = shift_pass_chance
        self.smart_attack = smart_attack
        self.smart_fortify = smart_fortify
        self.smart_fortify_surplus = smart_fortify_surplus
        self.smart_shift = smart_shift
        self.game = game_controller

        #OCR Matrix vem com 
        self.game_matrix = gamestate_matrix()
        

        #create a logger for simple_agent
        self.sa_logger = logging.getLogger(log_name)
        self.sa_logger.setLevel(logging.DEBUG)

        #display log in console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self.sa_logger.addHandler(ch)

        #add file log handler
        fh = logging.FileHandler(log_name + '.log')

        fh.setLevel(logging.DEBUG)
        self.sa_logger.addHandler(fh)

        fh.setFormatter(formatter)
        #add simple agent logger to game controller
        #self.game.logger.addHandler(fh)
        #self.game.logger.addHandler(ch)


    def gamestate(self):
        self.game.print_gamestate_matrix()
        self.game.print_gamestate()

    def fortify_to_action_vector(self, territories_troops_dict, exchange_cards):
        result_vector = []
        result_vector.extend([0,255,0,0])
        if (exchange_cards):
            result_vector.append(255)
        else:
            result_vector.append(0)

        for territory in Territory:
            if (territory in territories_troops_dict):
                result_vector.append(territories_troops_dict[territory])
            else:
                result_vector.append(0)
        return result_vector
    
    def get_random_fortify_vector(self, exchange_cards = True, smart_fortify = False,smart_fortify_surplus = 3, dumb_fortify = False):
        start_time = time.time()
        self.sa_logger.info('Fortificar aleatoriamente: ')
        lista_territorios = self.game.get_current_player_territories()
        reserve = self.game.get_current_player_reserve()
        self.sa_logger.info('random fortify player {0} - reserve {1}'.format(Player(self.game.current_player_index), reserve))
        territory_troops_dict = {}
        player_continents_reserve = self.game.get_current_player_all_continent_reserve()

        if (player_continents_reserve > 0):
            self.sa_logger.info('player {0} has {1} continent reserve'.format(Player(self.game.current_player_index), player_continents_reserve))
            player_continent_reserve_army_dict = self.game.get_current_player_continent_reserve_dict()
            player_continents_list = list(player_continent_reserve_army_dict)
            for continent in player_continents_list:
                continent_player_reserve_army = player_continent_reserve_army_dict[continent]
                while(continent_player_reserve_army > 0):
                    for territorio in lista_territorios:
                        if (territorio in continent.territory_list):
                            if(dumb_fortify):
                                reserve_action = 1
                            else:
                                reserve_action = random.randint(1, continent_player_reserve_army)
                            if (continent_player_reserve_army > 0):
                                self.sa_logger.info('Reserva: {0} - Territorio: {1} - Fortificar: {2} - Continente: {3}'.format(continent_player_reserve_army, territorio, reserve_action, continent))
                                continent_player_reserve_army -= reserve_action
                                player_continent_reserve_army_dict[continent] -= reserve_action
                                territory_troops_dict[territorio] = reserve_action
                                return(self.fortify_to_action_vector(territory_troops_dict, exchange_cards))

        elif (reserve > 0):
            self.sa_logger.info('player {0} has {1} reserve'.format(Player(self.game.current_player_index), reserve))
            if (smart_fortify):
                self.sa_logger.info('#### SMART FORTIFY ####')
                player_territories_army_dict = self.game.get_current_player_territory_army_dict()
                player_ter_list = list(player_territories_army_dict)
                for territory, army in player_territories_army_dict.items():
                    #get adjacent territories
                    for adj_ter, adj_ter_army in self.game.get_adjacent_territory_army_dict(territory).items():
                            if(adj_ter not in player_ter_list):
                                    if ( ( reserve + army ) >= ( adj_ter_army + smart_fortify_surplus) ):
                                        reserver_army = adj_ter_army + smart_fortify_surplus - army
                                        if (reserver_army > 0):
                                            territory_troops_dict[territory] = reserver_army
                                            
                                            self.sa_logger.info('Smart surplus - Reserva: {0} - Territorio: {1} - Fortificar: {2}'.format(reserve, territory, reserver_army))
                                            reserve -= reserver_army
                                            if (reserve == 0):
                                                self.sa_logger.info('entrou break reserve for smart fortify')
                                                break
                                    
                                    if ( ( reserve + army ) >= ( adj_ter_army + 3) ):
                                        reserver_army = adj_ter_army + 3 - army
                                        if (reserver_army > 0):
                                            territory_troops_dict[territory] = reserver_army
                                            
                                            self.sa_logger.info('Smart 3 - Reserva: {0} - Territorio: {1} - Fortificar: {2}'.format(reserve, territory, reserver_army))
                                            reserve -= reserver_army
                                            if (reserve == 0):
                                                self.sa_logger.info('entrou break reserve for smart fortify')
                                                break
                    if (reserve == 0):
                        self.sa_logger.info('entrou break reserve for smart fortify 2')
                        break

            while(reserve > 0):
                reserve_random = random.randint(1, reserve)
                reserve_territorio = random.choice(lista_territorios)
                self.sa_logger.info('Reserva: {0} - Territorio: {1} - Fortificar: {2}'.format(reserve, reserve_territorio, reserve_random))
                #self.game.perform_fortify(reserve_territorio, reserve_random, exchange_cards=exchange_cards)
                territory_troops_dict[reserve_territorio] = reserve_random
                reserve -= reserve_random
    
            end_time = time.time()
            self.sa_logger.info('performance perform_fortify {0} ms'.format(round(end_time - start_time, 4) * 1000))
            return(self.fortify_to_action_vector(territory_troops_dict, exchange_cards))
    
    def pass_phase_action_vector(self):
        result_vector = []
        result_vector.extend([0,0,0,255,0])
        #add 42 0 to result_vector
        for i in range(42):
            result_vector.append(0)
        return result_vector
    
    def attack_to_action_vector(self, attack_territory=None, defense_territory=None, pass_phase=False, move_army=None):
        #action vector
        ##attack 1| Fortify 1| Shift 1| Pass 1| Extra_ num army move 1 | Territories (42 columns)
        
        if (pass_phase):
            return(self.pass_phase_action_vector())
        result_vector = []
        result_vector.extend([255,0,0,0])
        result_vector.extend([move_army])

        for territory in Territory:
            if (territory == attack_territory or territory == defense_territory):
                result_vector.append(255)
            else:
                result_vector.append(0)

        return result_vector
    
    def get_random_attack_vector(self, attack_only_full_dices = False, full_dices_chance = 0.5, pass_phase_chance = 0.5, smart_attack = False):
        start_time = time.time()
        pass_phase = False
        random_pass_attack = random.random()
        random_full_dices = random.random()
        attack_only_full_dices = random_full_dices < full_dices_chance
        if ( random_pass_attack < pass_phase_chance ):
            self.sa_logger.info('Attack - Pass phase randoms')
            pass_phase = True
        
        self.sa_logger.debug('perform random chances: \n')
        self.sa_logger.debug('\t -> attack_only_full_dices: {0} < {1} = {2} \n'.format(random_full_dices, full_dices_chance, attack_only_full_dices))
        self.sa_logger.debug('\t -> pass_phase_chance: {0} < {1} = {2} \n'.format(random_pass_attack, pass_phase_chance, pass_phase))

        if(pass_phase):
            return(self.attack_to_action_vector(pass_phase=True))

        
        possible_attack_ter_dict = {}
        #pega o dict do jogador ao qual possui todos seus territorios:num_tropa
        player_ter_army_dict = self.game.get_current_player_territory_army_dict()
        #itera sobre esses territorios:n_trops
        player_ter_list = list(player_ter_army_dict)
        #self.sa_logger.info('player_ter_army_dict: \n')
        for player_territory_enum, territory_army in player_ter_army_dict.items():
                #self.sa_logger.info('\t {0} -> army: {1} \n'.format(player_territory_enum, territory_army))
                if ( (not attack_only_full_dices and territory_army > 1) or (attack_only_full_dices and territory_army > 3) ):
                    enemy_ter = []
                    for adj_ter, adj_ter_army in self.game.get_adjacent_territory_army_dict(player_territory_enum).items():
                        if(adj_ter not in player_ter_list):
                            enemy_ter.append({adj_ter:adj_ter_army})
                            #self.sa_logger.info( '\t ' + str(adj_ter) + ' -> ' + str(adj_ter_army) + '\n' )
                    if (len(enemy_ter) > 0):
                        possible_attack_ter_dict[player_territory_enum] = enemy_ter
        
        if (len(possible_attack_ter_dict) == 0):
            self.sa_logger.info('No attack possible')
            pass_phase = True

        #if (len(value) == 1):
        #    preferable_attack_ter_dict[key] = value
        if(pass_phase):
            return(self.attack_to_action_vector(pass_phase=True))
        else:
            attack_ter = None
            defense_ter = None
            self.sa_logger.info('pass phase false ')
            if (smart_attack):
                self.sa_logger.info('#### SMART ATTACK ####')
                territory_difference_army_dict = {}
                #self.sa_logger.info('SMART ATTACK possible_attack_ter_dict: {0}'.format(possible_attack_ter_dict))
                for key, enemy_territories in possible_attack_ter_dict.items():
                    #self.sa_logger.info('\n attack Territory key: {0} - \n\tenemy_territories: {1}'.format(key, enemy_territories))
                    lowest_army = 10000000
                    lowest_enemy_ter = None
                    attack_ter_army = player_ter_army_dict[key] - 1
                    for enemy_ter in enemy_territories:
                        enemy_ter_army = list(enemy_ter.values())[0]
                        if(enemy_ter_army < lowest_army):
                            lowest_army = enemy_ter_army
                            lowest_enemy_ter = list(enemy_ter)[0]
                    difference_army = attack_ter_army - lowest_army
                    territory_difference_army_dict[difference_army] = {key:lowest_enemy_ter}

                #sort territory_difference_army_dict
                #self.sa_logger.info('SMART ATTACK territory_difference_army_dict: {0}'.format(territory_difference_army_dict))
                highest_diff_terr = sorted(territory_difference_army_dict.items(), key=lambda x: x[0], reverse=True)[0][1]
                #self.sa_logger.info('SMART ATTACK highest_diff_terr: {0}'.format(list(highest_diff_terr)))
                attack_ter = list(highest_diff_terr)[0]
                defense_ter = highest_diff_terr[attack_ter]
                self.sa_logger.info('SMART ATTACK attack_ter: {0} - defense_ter: {1}'.format(attack_ter, defense_ter))
            else:
                attack_ter = random.choice(list(possible_attack_ter_dict))
                defense_ter = list(random.choice(possible_attack_ter_dict[attack_ter]))[0]
            self.sa_logger.info('attack_ter: {0} - defense_ter: {1}'.format(attack_ter, defense_ter))
            #self.game.perform_attack(attack_ter, defense_ter, random.randint(1,3))
            
            end_time = time.time()
            self.sa_logger.info('performance perform_attack {0} ms'.format(round(end_time - start_time, 4) * 1000))
            return(self.attack_to_action_vector(attack_territory=attack_ter, defense_territory=defense_ter, move_army=1))

    def shift_to_action_vector(self, origin_territory=None, destination_territory=None, move_army=None,  pass_phase = False):
        if (pass_phase):
            return(self.pass_phase_action_vector())
        
        result_vector = []
        result_vector.extend([0,0,255,0])
        result_vector.extend([move_army])

        for territory in Territory:
            if (territory == origin_territory):
                result_vector.append(125)
            elif (territory == destination_territory):
                result_vector.append(255)
            else:
                result_vector.append(0)
        return result_vector
    
    def get_random_shift_vector(self, shift_chance = 0.25, smart_shift = False):
        start_time = time.time()
        if ( random.random() < shift_chance ):
            self.sa_logger.info('Shift - Pass phase randoms')
            return(self.pass_phase_action_vector())

        shift_ter = None
        shift_ter_adj = None
        shift_ter_army = None

        player_territory_list = self.game.get_current_player_territories()
        player_mov_army_dict = self.game.get_current_player_movables_armies_dict()
        player_mov_ter_list = list(player_mov_army_dict)
        player_mov_ter_dict = {}
        
        for territory in player_mov_ter_list:
            self.sa_logger.debug('getting adj terr. for territory {0} whith {1} movable armies'.format(territory, player_mov_army_dict[territory]))
            adj_ter_army_list = []
            for adj_ter in self.game.board_controller.board.get_adjacent_Territory(territory):
                self.sa_logger.debug('adj terr. {0}'.format(adj_ter))
                if(adj_ter in player_territory_list):
                    self.sa_logger.debug('adj terr. {0} in player_mov_ter_list. adding...'.format(adj_ter))
                    adj_ter_army_list.append(adj_ter)
            if(len(adj_ter_army_list) > 0 and player_mov_army_dict[territory] > 0):
                player_mov_ter_dict[territory] = adj_ter_army_list

        if (len(player_mov_ter_dict) == 0):
            self.sa_logger.info('No shift possible')
            return(self.pass_phase_action_vector())

        self.sa_logger.debug('player movables territories:')
        for key,value in player_mov_ter_dict.items():
            self.sa_logger.debug(str(key) + ' -> ' + str(value))
        

        if (smart_shift):
            self.sa_logger.info('#### SMART SHIFT ####')
            player_movable_territory_list = list(player_mov_ter_dict)
            for territory in player_movable_territory_list:
                adj_territories = self.game.board_controller.board.get_adjacent_Territory(territory)
                player_own_all_adj_territories = True
                for adj_ter in adj_territories:
                    if(adj_ter not in player_territory_list):
                        player_own_all_adj_territories = False
                
                if (player_own_all_adj_territories):
                    self.sa_logger.info('player own all adj territories of {0}'.format(territory))
                    shift_ter = territory
                    #choose a adj territory from shift that has a adj enemy
                    for adj_ter in adj_territories:
                        adj_territories_from_player_adj_ter = self.game.board_controller.board.get_adjacent_Territory(adj_ter)
                        for territory in adj_territories_from_player_adj_ter:
                            if(territory not in player_territory_list):
                                shift_ter_adj = adj_ter
                                shift_ter_army = player_mov_army_dict[shift_ter]

                                break
                        if (shift_ter_adj != None):
                            break
                    #if there is no adj enemy, get random territory
                    if (shift_ter_adj == None):
                        self.sa_logger.info('no adj enemy, get random territory')
                        shift_ter_adj = random.choice(player_mov_ter_dict[shift_ter])
                        shift_ter_army = player_mov_army_dict[shift_ter]
                    self.sa_logger.info('choosed shift_ter: {0} - shift_ter_adj: {1} - shift_ter_army: {2}'.format(shift_ter, shift_ter_adj, shift_ter_army))
                    return(self.shift_to_action_vector(origin_territory=shift_ter, destination_territory=shift_ter_adj, move_army=shift_ter_army))
            if (shift_ter == None):
                #pass phase
                self.sa_logger.info('No smart shift possible')
                return(self.pass_phase_action_vector())

        if(shift_ter == None or shift_ter_adj == None or shift_ter_army == None):
            shift_ter = random.choice(list(player_mov_ter_dict))
            shift_ter_adj = random.choice(player_mov_ter_dict[shift_ter])
            shift_ter_army = random.randint(1, player_mov_army_dict[shift_ter])
            
        #self.game.perform_shift_troop(shift_ter, shift_ter_adj, shift_ter_army)
            
        end_time = time.time()
        self.sa_logger.info('shift troop from {0} to {1} whith {2} armies'.format(shift_ter, shift_ter_adj, shift_ter_army))
        self.sa_logger.info('performance perform_shift {0} ms'.format(round(end_time - start_time, 4) * 1000))
        return(self.shift_to_action_vector(origin_territory=shift_ter, destination_territory=shift_ter_adj, move_army=shift_ter_army))
        #self.game.perform_shift_troop


    def step(self, ocr_matrix):
        current_turn = self.game.turn_counter
        self.sa_logger.info('doig step for game turn {0} - round {1} - Current phase {2}'.format(current_turn,self.game.round_counter, self.game.current_phase_index))
        action_vector = None
        if(self.game.current_phase_index == GamePhase.FORTIFY.value):
            self.sa_logger.info('Fortificar aleatoriamente: ')
            action_vector = self.get_random_fortify_vector(smart_fortify=self.smart_fortify, smart_fortify_surplus=self.smart_fortify_surplus)
            

        elif(self.game.current_phase_index == GamePhase.ATTACK.value):
            self.sa_logger.info('Atacar aleatoriamente: ')
            #self.perform_random_attack(attack_only_full_dices = False, full_dices_chance = self.attack_full_dices_chance, 
            #                           pass_phase_chance = self.attack_pass_chance, smart_attack = self.smart_attack)
            action_vector = self.get_random_attack_vector(attack_only_full_dices = False, full_dices_chance = self.attack_full_dices_chance,
                                            pass_phase_chance = self.attack_pass_chance, smart_attack = self.smart_attack)
            
        elif(self.game.current_phase_index == GamePhase.SHIFT.value):
            self.sa_logger.info('Fortificar aleatoriamente, random chance: {0}'.format(self.shift_pass_chance))
            #self.perform_random_shift(shift_chance = self.shift_pass_chance)
            action_vector = self.get_random_shift_vector(shift_chance = self.shift_pass_chance, smart_shift=self.smart_shift)
        
        elif(self.game.current_phase_index == GamePhase.NONE):
            self.sa_logger.info('None phase, player dead')
            return None
        
        if(action_vector == None):
            self.sa_logger.error('Action vector none')
            sys.exit(1)

        self.sa_logger.info('performing action vector len {0}'.format(len(action_vector)))
        print('action vector: ')
        print(action_vector)
        ret = self.game.perform_action_vector(action_vector)
        self.sa_logger.info('retorno perform_action_vector {0}'.format(ret))
