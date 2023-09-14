from app.controllers.game_controller import GameController, GamePhase
from app.models.board import Territory, Continents, Board
from app.models.player import Player
import logging
from agents.simple_agent import simple_agent
from agents.simple_agent_vector import simple_agent_vector
from agents.dumb_agent_vector import dumb_agent_vector
from Jugadores.jugadorGrafoOptimizado_2Cambios import JugadorGrafoOptimizado
import sys
import numpy as np
from misiones import misiones
from tablero_jugador import Tablero
from Jugadores.jugador import Jugador

#TODO verificar troca de missao do JugadorGrafoOptimizado dinamica
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

fh = logging.FileHandler('game.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
game.logger.addHandler(fh)


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
cinza_objectivo = np.argmax(matriz[5][-18:-4])
print(cinza_objectivo)
colores = ["blue","red","green","purple","yellow","black"]
Jugador_puc = JugadorGrafoOptimizado("JOGADOR_PUCPR_IA", colores[5], misiones[cinza_objectivo])

agents_list.append(agent)

game.print_gamestate_matrix()
game.print_gamestate()

mision_desconocida = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
jugador1 = Jugador("1",colores[0],mision_desconocida)
jugador2 = Jugador("2",colores[1],mision_desconocida)
jugador3 = Jugador("3",colores[2],mision_desconocida)
jugador4 = Jugador("4",colores[3],mision_desconocida)
jugador5 = Jugador("5",colores[4],mision_desconocida)

jugadores = [Jugador_puc,jugador1,jugador2,jugador3,jugador4,jugador5]
tablero = Tablero(jugadores)


steps = 0

while True:
    previous_game_phase = game.current_phase_index
    gamestate_matrix = game.get_gamestate_matrix()
    tablero.actualizarmatriz(gamestate_matrix)

    if(game.current_player_index == 5):
        print('gamestate matrix', gamestate_matrix[5])

        matriz = game.get_gamestate_matrix()
        cinza_objectivo = np.argmax(matriz[5][-18:-4])
        Jugador_puc.interpretar_mision(misiones[cinza_objectivo])
        Jugador_puc.mision = misiones[cinza_objectivo]
        Jugador_puc.descripcion = misiones[cinza_objectivo].descripcion

        action_vector = Jugador_puc.step(gamestate_matrix, player_index=5, tablero=tablero)
        print('phase index ', game.current_phase_index)
        #pulando fase de ataque
        
        if (game.current_phase_index == GamePhase.SHIFT.value):
            print('varios vetores de acao retorna pelo deslocar do Jugador')
            for action in action_vector:
                
                game.perform_action_vector(action)
        else:
            game.perform_action_vector(action_vector)
        input("Press Enter to continue...")
    else:
       
       agents_list[game.current_player_index].step()
    steps += 1

    if(game.current_phase_index == GamePhase.NONE.value and game.winner != None):
        break
    
    if(previous_game_phase != game.current_phase_index): #detecta mudanca de fase, apenas para debug
        game.print_gamestate_matrix()
        game.print_gamestate()
    


    if(steps > 10000):
        print("Game ended due to too many steps")
        break


if(game.winner != None):
    game.print_gamestate()
    print(f'Winner: {game.winner}')
    game.logger.info(f'Winner: {game.winner}')



