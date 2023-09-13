from app.controllers.game_controller import GameController, GamePhase
from app.models.board import Territory, Continents, Board
from app.models.player import Player
import logging
from agents.simple_agent import simple_agent
from agents.simple_agent_vector import simple_agent_vector
from agents.dumb_agent_vector import dumb_agent_vector
from Jugadores.jugadorGrafoOptimizado_2Cambios import JugadorGrafoOptimizado
import sys

formatter = logging.Formatter('%(asctime)s - %(name)s - (%(funcName)s) - %(levelname)s - %(message)s')
game = GameController()

game_logger = logging.getLogger('game_logger')
#create a logger for simple_agent
game_logger.setLevel(logging.DEBUG)

#display log in console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
game.logger.addHandler(ch)

game.start_game(6)

def print_gamestate():
    for linha in game.get_gamestate_matrix():
        print(linha)


def print_gamestatus():
    print(game.get_game_info())

#print_gamestate()
print_gamestatus()


agents_list = []
#Azul
agent = simple_agent_vector(game, 0.8, 0.0, 0.0, f'playerAzul', 
                            smart_attack=True, smart_fortify=True, smart_fortify_surplus=6, smart_shift=True)
agents_list.append(agent)
#Vermelho
agent = dumb_agent_vector(game, 0.1, 0.0, 0.2, f'playerVermelho')
agents_list.append(agent)
#Verde
agent = dumb_agent_vector(game, 0.1, 0.0, 0.8, f'playerVerde') #0.1, 0.0, 0.8 boa config
agents_list.append(agent)
#Roxo
agent = dumb_agent_vector(game, 0.1, 0.0, 0.9, f'playerRoxo')
agents_list.append(agent)
#Amarelo
agent = dumb_agent_vector(game, 0.05, 0.0, 0.9, f'playerAmarelo')
agents_list.append(agent)
#Cinza
matriz = game.get_gamestate_matrix()
print(matriz[5])
cinza_objectivos = matriz[5][-17:-3]
print(cinza_objectivos)
#Jugador_puc = JugadorGrafoOptimizado("JOGADOR_PUCPR_IA", colores[5], misiones[np.argmax(matriz[5][-14:])])
#agent = JugadorGrafoOptimizado()
agents_list.append(agent)

game.print_gamestate_matrix()
game.print_gamestate()

steps = 0


while True:
    previous_game_phase = game.current_phase_index
    agents_list[game.current_player_index].step()
    steps += 1

    if(game.current_phase_index == GamePhase.NONE.value and game.winner != None):
        break
    
    if(previous_game_phase != game.current_phase_index):
        game.print_gamestate_matrix()
        game.print_gamestate()
    


    if(steps > 10000):
        print("Game ended due to too many steps")
        break
    input("Press Enter to continue...")

if(game.winner != None):
    game.print_gamestate()
    print(f'Winner: {game.winner}')
    game.logger.info(f'Winner: {game.winner}')



