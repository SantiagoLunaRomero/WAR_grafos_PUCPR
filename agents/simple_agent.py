
import sys
import random
import time
import logging
sys.path.append('../')

from app.controllers.game_controller import GameController, GamePhase
from app.models.board import Territory, Continents, Board
from app.models.player import Player


class simple_agent():
    def __init__(self, game_controller, attack_full_dices_chance = 0.5, attack_pass_chance = 0.5, shift_pass_chance = 0.1, log_name = 'agentX', smart_attack = False):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #chaces
        self.attack_full_dices_chance = attack_full_dices_chance
        self.attack_pass_chance = attack_pass_chance
        self.shift_pass_chance = shift_pass_chance
        self.smart_attack = smart_attack
        self.game = game_controller

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


    def perform_random_fortify(self, exchange_cards = True):
        start_time = time.time()
        self.sa_logger.info('Fortificar aleatoriamente: ')
        lista_territorios = self.game.get_current_player_territories()
        reserve = self.game.get_current_player_reserve()
        self.sa_logger.info('random fortify player {0} - reserve {1}'.format(Player(self.game.current_player_index), reserve))
        while(reserve > 0):
            reserve_random = random.randint(1, reserve)
            reserve_territorio = random.choice(lista_territorios)
            self.sa_logger.info('Reserva: {0} - Territorio: {1} - Fortificar: {2}'.format(reserve, reserve_territorio, reserve_random))
            self.game.perform_fortify(reserve_territorio, reserve_random, exchange_cards=exchange_cards)
            reserve -= reserve_random
        end_time = time.time()
        self.sa_logger.info('performance perform_fortify {0} ms'.format(round(end_time - start_time, 4) * 1000))

    def perform_random_attack(self, attack_only_full_dices = False, full_dices_chance = 0.5, pass_phase_chance = 0.5, smart_attack = False):
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
            self.game.perform_attack(pass_phase=True)
            return True
        
        possible_attack_ter_dict = {}
        #pega o dict do jogador ao qual possui todos seus territorios:num_tropa
        player_ter_army_dict = self.game.get_current_player_territory_army_dict()
        #itera sobre esses territorios:n_trops
        player_ter_list = list(player_ter_army_dict)

        for player_territory_enum, territory_army in player_ter_army_dict.items():
                self.sa_logger.debug('{0} -> army: {1}'.format(player_territory_enum, territory_army))
                if ( (not attack_only_full_dices and territory_army > 1) or (attack_only_full_dices and territory_army > 3) ):
                    enemy_ter = []
                    for adj_ter, adj_ter_army in self.game.get_adjacent_territory_army_dict(player_territory_enum).items():
                        if(adj_ter not in player_ter_list):
                            enemy_ter.append({adj_ter:adj_ter_army})
                            self.sa_logger.debug( '\t ' + str(adj_ter) + ' -> ' + str(adj_ter_army) )
                    if (len(enemy_ter) > 0):
                        possible_attack_ter_dict[player_territory_enum] = enemy_ter
        
        if (len(possible_attack_ter_dict) == 0):
            self.sa_logger.info('No attack possible')
            pass_phase = True

        #if (len(value) == 1):
        #    preferable_attack_ter_dict[key] = value
        if(pass_phase):
            self.game.perform_attack(pass_phase=True)
        else:
            attack_ter = None
            defense_ter = None
            self.sa_logger.info('pass phase false ')
            if (smart_attack):
                self.sa_logger.debug('#### SMART ATTACK ####')
                territory_difference_army_dict = {}
                for key, enemy_territories in possible_attack_ter_dict.items():
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
                self.sa_logger.info('SMART ATTACK territory_difference_army_dict: {0}'.format(territory_difference_army_dict))
                highest_diff_terr = sorted(territory_difference_army_dict.items(), key=lambda x: x[0], reverse=True)[0][1]
                self.sa_logger.info('SMART ATTACK highest_diff_terr: {0}'.format(list(highest_diff_terr)))
                attack_ter = list(highest_diff_terr)[0]
                defense_ter = highest_diff_terr[attack_ter]
                self.sa_logger.info('SMART ATTACK attack_ter: {0} - defense_ter: {1}'.format(attack_ter, defense_ter))
            else:
                attack_ter = random.choice(list(possible_attack_ter_dict))
                defense_ter = list(random.choice(possible_attack_ter_dict[attack_ter]))[0]
            self.sa_logger.info('attack_ter: {0} - defense_ter: {1}'.format(attack_ter, defense_ter))
            self.game.perform_attack(attack_ter, defense_ter, random.randint(1,3))
            end_time = time.time()
            self.sa_logger.info('performance perform_attack {0} ms'.format(round(end_time - start_time, 4) * 1000))


    def perform_random_shift(self, shift_chance = 0.25):
        start_time = time.time()
        if ( random.random() < shift_chance ):
            self.sa_logger.info('Shift - Pass phase randoms')
            self.game.perform_shift_troop(pass_phase=True)
            return

        
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
            self.game.perform_shift_troop(pass_phase=True)
            return
        else:
            self.sa_logger.debug('player movables territories:')
            for key,value in player_mov_ter_dict.items():
                self.sa_logger.debug(str(key) + ' -> ' + str(value))
            
            shift_ter = random.choice(list(player_mov_ter_dict))
            shift_ter_adj = random.choice(player_mov_ter_dict[shift_ter])
            shift_ter_army = random.randint(1, player_mov_army_dict[shift_ter])
            self.sa_logger.info('shift troop from {0} to {1} whith {2} armies'.format(shift_ter, shift_ter_adj, shift_ter_army))
            self.game.perform_shift_troop(shift_ter, shift_ter_adj, shift_ter_army)

        end_time = time.time()
        self.sa_logger.info('performance perform_shift {0} ms'.format(round(end_time - start_time, 4) * 1000))

        #self.game.perform_shift_troop

    def step(self):
        current_turn = self.game.turn_counter
        self.sa_logger.info('doig step for game turn {0} - round {1} - Current phase {2}'.format(current_turn,self.game.round_counter, self.game.current_phase_index))
        
        if(self.game.current_phase_index == GamePhase.FORTIFY.value):
            self.sa_logger.info('step - Fortificar aleatoriamente: ')
            self.perform_random_fortify()

        elif(self.game.current_phase_index == GamePhase.ATTACK.value):
            self.sa_logger.info('step - Atacar aleatoriamente: ')
            self.perform_random_attack(attack_only_full_dices = False, full_dices_chance = self.attack_full_dices_chance, 
                                       pass_phase_chance = self.attack_pass_chance, smart_attack = self.smart_attack)
        
        elif(self.game.current_phase_index == GamePhase.SHIFT.value):
            self.sa_logger.info('step - Shift aleatoriamente, random chance: {0}'.format(self.shift_pass_chance))
            self.perform_random_shift(shift_chance = self.shift_pass_chance)
        
        elif(self.game.current_phase_index == GamePhase.NONE):
            self.sa_logger.info('None phase, player dead')


