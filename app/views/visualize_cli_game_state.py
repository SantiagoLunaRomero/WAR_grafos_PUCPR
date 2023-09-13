import sys
sys.path.append('../../')
#print sys path appended
from app.models.board import Board, Territory, Continents
from app.models.player import Player
import random
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

#from app.models.board import Board, Territory, Continents
#from app.models.player import Player

def print_territory(territory_enum, underlines_times=0, spaces=0):
    #get territory name and truncate to 5 caracters
    territory_name = str(territory_enum.name)[:6]
    #get army quant, transform to str and add 0 left, maximum 3 characters

    if (territory_name == Territory.OMSK.name):
        territory_name += "  "
    elif (territory_name == Territory.ARAL.name):
        territory_name += "  "
    elif (territory_name == Territory.CHINA.name):
        territory_name += " "
    elif (territory_name == Territory.EGITO.name):
        territory_name += " "
    elif (territory_name == Territory.INDIA.name):
        territory_name += " "
    elif (territory_name == Territory.JAPAO.name):
        territory_name += " "
    elif (territory_name == Territory.CONGO.name):
        territory_name += " "
    elif (territory_name == Territory.SUDAO.name):
        territory_name += " "
    elif (territory_name == Territory.PERU.name):
        territory_name += "  "
    sys.stdout.write("| {0}  |".format(territory_name))

    sys.stdout.write(" _ " * underlines_times)
    sys.stdout.write(" " * spaces)

def str_territory(territory_enum, underlines_times=0, spaces=0):
    res = ""
    #get territory name and truncate to 5 caracters
    territory_name = str(territory_enum.name)[:6]
    #get army quant, transform to str and add 0 left, maximum 3 characters

    if (territory_name == Territory.OMSK.name):
        territory_name += "  "
    elif (territory_name == Territory.ARAL.name):
        territory_name += "  "
    elif (territory_name == Territory.CHINA.name):
        territory_name += " "
    elif (territory_name == Territory.EGITO.name):
        territory_name += " "
    elif (territory_name == Territory.INDIA.name):
        territory_name += " "
    elif (territory_name == Territory.JAPAO.name):
        territory_name += " "
    elif (territory_name == Territory.CONGO.name):
        territory_name += " "
    elif (territory_name == Territory.SUDAO.name):
        territory_name += " "
    elif (territory_name == Territory.PERU.name):
        territory_name += "  "
    res += ("| {0}  |".format(territory_name))

    res += (" _ " * underlines_times)
    res += (" " * spaces)

    return res

def print_player_army(army_quant, player_enum, spaces=3):
    color = Fore.BLACK
    reset = Style.RESET_ALL
    if(player_enum == Player.AZUL):
        color = Fore.BLUE

    army_quant = str(army_quant).zfill(3)
    #get player name and truncate to 3 characters
    player_name = str(player_enum.name)[:3]
    if (player_enum == Player.VERDE):
        player_name = "VRD"
        color = Fore.GREEN
    elif (player_enum == Player.VERMELHO):
        player_name = "VRM"
        color = Fore.RED

    army_quant = str(army_quant).zfill(3)
    #get player name and truncate to 3 characters
    player_name = str(player_enum.name)[:3]
    sys.stdout.write(f"| {0}{1}{2}-{3} |".format(color, player_name, reset, army_quant))
    sys.stdout.write(" " * spaces)

def str_player_army(army_quant, player_enum, spaces=3):
    color = Fore.WHITE
    reset = Style.RESET_ALL

    res = ""
    army_quant = str(army_quant).zfill(3)
    #get player name and truncate to 3 characters
    player_name = str(player_enum.name)[:3]



    if (player_enum == Player.VERDE):
        player_name = "VRD"
        color = Fore.GREEN
    elif (player_enum == Player.VERMELHO):
        player_name = "VRM"
        color = Fore.RED
    elif(player_enum == Player.AZUL):
        color = Fore.BLUE
    elif(player_enum == Player.ROXO):
        color = Fore.MAGENTA
    elif(player_enum == Player.AMARELO):
        color = Fore.YELLOW
    elif(player_enum == Player.CINZA):
        color = Fore.LIGHTBLACK_EX
    

    res += ("| {0}{1}{2}-{3} |".format(color, player_name, reset, army_quant))
    res += (" " * spaces)
    return res

def get_str_map(game_state_matrix=None):
    colorama_init()
    map = ""
    player_army_list = []
    #Alaska
    if(game_state_matrix is not None):
        #convert game_state_matrix to territory_state_matrix, which is the first 42 columns of all lines
        territory_state_matrix = []
        for line in game_state_matrix:
            territory_state_matrix.append(line[0:42])

        #check if any column has more than 1 value > 0
        for column in range(0, len(territory_state_matrix[0])):
            count = 0
            for row in range(0, len(territory_state_matrix)):
                if(territory_state_matrix[row][column] > 0):
                    #print('coluna {0} linha {1} adicionando {2}'.format(column, row, game_state_matrix[row][column]))
                    player_army_list.append((Player(row), territory_state_matrix[row][column]))
                    count += 1
                
            if(count > 1):
                raise Exception("Invalid matrix - more than 1 value > 0 in column {0}".format(column))

        map += "\n\n\n"

        map += str_territory(Territory.ALASKA, 1, 0)
        map += str_territory(Territory.MACKENZIE, 1, 0)
        map += str_territory(Territory.GROELANDIA, 0, 15)
        map += str_territory(Territory.ISLANDIA, 0, 50)
        map += str_territory(Territory.SIBERIA,1,0)
        map += str_territory(Territory.VLADIVOSTOK,0,0)
        map += "\n"
        map += str_player_army(player_army_list[Territory.ALASKA.value[0]][1], player_army_list[Territory.ALASKA.value[0]][0])
        map += str_player_army(player_army_list[Territory.MACKENZIE.value[0]][1], player_army_list[Territory.MACKENZIE.value[0]][0])
        map += str_player_army(player_army_list[Territory.GROELANDIA.value[0]][1], player_army_list[Territory.GROELANDIA.value[0]][0], 15)
        map += str_player_army(player_army_list[Territory.ISLANDIA.value[0]][1], player_army_list[Territory.ISLANDIA.value[0]][0], 50)
        map += str_player_army(player_army_list[Territory.SIBERIA.value[0]][1], player_army_list[Territory.SIBERIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.VLADIVOSTOK.value[0]][1], player_army_list[Territory.VLADIVOSTOK.value[0]][0])
        map += "\n\n"


        #Second line
        map += str_territory(Territory.VANCOUVER, 1, 0)
        map += str_territory(Territory.OTTAWA, 1, 0)
        map += str_territory(Territory.LABRADOR, 0, 15)
        map += str_territory(Territory.INGLATERRA, 1, 0)
        map += str_territory(Territory.SUECIA, 1, 0)
        map += str_territory(Territory.MOSCOU, 1, 0)
        map += str_territory(Territory.OMSK, 1, 0)
        map += str_territory(Territory.DUDINKA, 1, 0)
        map += str_territory(Territory.TCHITA, 0, 0)
        map += "\n"
        map += str_player_army(player_army_list[Territory.VANCOUVER.value[0]][1], player_army_list[Territory.VANCOUVER.value[0]][0])
        map += str_player_army(player_army_list[Territory.OTTAWA.value[0]][1], player_army_list[Territory.OTTAWA.value[0]][0])
        map += str_player_army(player_army_list[Territory.LABRADOR.value[0]][1], player_army_list[Territory.LABRADOR.value[0]][0], 15)
        map += str_player_army(player_army_list[Territory.INGLATERRA.value[0]][1], player_army_list[Territory.INGLATERRA.value[0]][0])
        map += str_player_army(player_army_list[Territory.SUECIA.value[0]][1], player_army_list[Territory.SUECIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.MOSCOU.value[0]][1], player_army_list[Territory.MOSCOU.value[0]][0])
        map += str_player_army(player_army_list[Territory.OMSK.value[0]][1], player_army_list[Territory.OMSK.value[0]][0])
        map += str_player_army(player_army_list[Territory.DUDINKA.value[0]][1], player_army_list[Territory.DUDINKA.value[0]][0])
        map += str_player_army(player_army_list[Territory.TCHITA.value[0]][1], player_army_list[Territory.TCHITA.value[0]][0])
        map += "\n"
        map += "\n"
        #Third line
        map += str_territory(Territory.CALIFORNIA, 1, 0)
        map += str_territory(Territory.NEW_YORK, 0, 30)
        map += str_territory(Territory.FRANCA, 1, 0)
        map += str_territory(Territory.ALEMANHA, 1, 0)
        map += str_territory(Territory.POLONIA, 1, 0)
        map += str_territory(Territory.ARAL, 1, 0)
        map += str_territory(Territory.MONGOLIA, 1, 0)
        map += str_territory(Territory.CHINA, 1, 0)
        map += str_territory(Territory.JAPAO, 0, 0)
        map += "\n"
        map += str_player_army(player_army_list[Territory.CALIFORNIA.value[0]][1], player_army_list[Territory.CALIFORNIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.NEW_YORK.value[0]][1], player_army_list[Territory.NEW_YORK.value[0]][0], 30)
        map += str_player_army(player_army_list[Territory.FRANCA.value[0]][1], player_army_list[Territory.FRANCA.value[0]][0])
        map += str_player_army(player_army_list[Territory.ALEMANHA.value[0]][1], player_army_list[Territory.ALEMANHA.value[0]][0])
        map += str_player_army(player_army_list[Territory.POLONIA.value[0]][1], player_army_list[Territory.POLONIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.ARAL.value[0]][1], player_army_list[Territory.ARAL.value[0]][0])
        map += str_player_army(player_army_list[Territory.MONGOLIA.value[0]][1], player_army_list[Territory.MONGOLIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.CHINA.value[0]][1], player_army_list[Territory.CHINA.value[0]][0])
        map += str_player_army(player_army_list[Territory.JAPAO.value[0]][1], player_army_list[Territory.JAPAO.value[0]][0])
        map += "\n"
        map += "\n"
        map += str_territory(Territory.MEXICO, 0, 45)
        map += str_territory(Territory.ARGELIA, 1, 0)
        map += str_territory(Territory.EGITO, 0, 15)
        map += str_territory(Territory.ORIENTE_MEDIO, 1, 0)
        map += str_territory(Territory.INDIA, 1, 0)
        map += str_territory(Territory.VIETNA, 0, 0)
        map += "\n"
        map += str_player_army(player_army_list[Territory.MEXICO.value[0]][1], player_army_list[Territory.MEXICO.value[0]][0], 45)
        map += str_player_army(player_army_list[Territory.ARGELIA.value[0]][1], player_army_list[Territory.ARGELIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.EGITO.value[0]][1], player_army_list[Territory.EGITO.value[0]][0], 15)
        map += str_player_army(player_army_list[Territory.ORIENTE_MEDIO.value[0]][1], player_army_list[Territory.ORIENTE_MEDIO.value[0]][0])
        map += str_player_army(player_army_list[Territory.INDIA.value[0]][1], player_army_list[Territory.INDIA.value[0]][0])
        map += str_player_army(player_army_list[Territory.VIETNA.value[0]][1], player_army_list[Territory.VIETNA.value[0]][0])
        map += "\n"
        map += "\n"
        map += str_territory(Territory.VENEZUELA, 0, 45)
        map += str_territory(Territory.CONGO, 1,0)
        map += str_territory(Territory.SUDAO, 0, 30)
        map += str_territory(Territory.SUMATRA, 1, 0)
        map += str_territory(Territory.BORNEU, 1, 0) 
        map += str_territory(Territory.NOVA_GUINE, 0, 0)
        map += "\n"
        map += str_player_army(player_army_list[Territory.VENEZUELA.value[0]][1], player_army_list[Territory.VENEZUELA.value[0]][0], 45)
        map += str_player_army(player_army_list[Territory.CONGO.value[0]][1], player_army_list[Territory.CONGO.value[0]][0])
        map += str_player_army(player_army_list[Territory.SUDAO.value[0]][1], player_army_list[Territory.SUDAO.value[0]][0], 30)
        map += str_player_army(player_army_list[Territory.SUMATRA.value[0]][1], player_army_list[Territory.SUMATRA.value[0]][0])
        map += str_player_army(player_army_list[Territory.BORNEU.value[0]][1], player_army_list[Territory.BORNEU.value[0]][0])
        map += str_player_army(player_army_list[Territory.NOVA_GUINE.value[0]][1], player_army_list[Territory.NOVA_GUINE.value[0]][0])

        map += "\n"
        map += "\n"
        map += str_territory(Territory.PERU, 1, 0)
        map += str_territory(Territory.BRASIL, 0, 33)
        map += str_territory(Territory.AFRICA_DO_SUL, 1, 0)
        map += str_territory(Territory.MADAGASCAR, 0, 45)
        map += str_territory(Territory.AUSTRALIA, 0, 0)
        map += "\n"
        map += str_player_army(player_army_list[Territory.PERU.value[0]][1], player_army_list[Territory.PERU.value[0]][0])
        map += str_player_army(player_army_list[Territory.BRASIL.value[0]][1], player_army_list[Territory.BRASIL.value[0]][0], 33)
        map += str_player_army(player_army_list[Territory.AFRICA_DO_SUL.value[0]][1], player_army_list[Territory.AFRICA_DO_SUL.value[0]][0])
        map += str_player_army(player_army_list[Territory.MADAGASCAR.value[0]][1], player_army_list[Territory.MADAGASCAR.value[0]][0], 45)
        map += str_player_army(player_army_list[Territory.AUSTRALIA.value[0]][1], player_army_list[Territory.AUSTRALIA.value[0]][0])
        map += "\n"
        map += "\n"
        map += str_territory(Territory.ARGENTINA)
        map += "\n"
        map += str_player_army(player_army_list[Territory.ARGENTINA.value[0]][1], player_army_list[Territory.ARGENTINA.value[0]][0])
        map += "\n"
        map += "\n"

    else:
        map += 'Nada inserido'

    return map

def print_map(game_state_matrix=None):
    colorama_init()
    random_possible_players = [Player.AZUL, Player.AMARELO, Player.VERDE, Player.VERMELHO, Player.ROXO, Player.CINZA]
    player_army_list = []
    #Alaska
    if(game_state_matrix is not None):
        #convert game_state_matrix to territory_state_matrix, which is the first 42 columns of all lines
        territory_state_matrix = []
        for line in game_state_matrix:
            territory_state_matrix.append(line[0:42])

        #check if any column has more than 1 value > 0
        for column in range(0, len(territory_state_matrix[0])):
            count = 0
            for row in range(0, len(territory_state_matrix)):
                if(territory_state_matrix[row][column] > 0):
                    #print('coluna {0} linha {1} adicionando {2}'.format(column, row, game_state_matrix[row][column]))
                    player_army_list.append((Player(row), territory_state_matrix[row][column]))
                    count += 1
            if(count > 1):
                raise Exception("Invalid matrix - more than 1 value > 0 in column {0}".format(column))
    
        #First line
        print()
        print()
        print()
        print()
        print_territory(Territory.ALASKA, 1, 0)
        print_territory(Territory.MACKENZIE, 1, 0)
        print_territory(Territory.GROELANDIA, 0, 15)
        print_territory(Territory.ISLANDIA, 0, 50)
        print_territory(Territory.SIBERIA,1,0)
        print_territory(Territory.VLADIVOSTOK,0,0)
        print()
        print_player_army(player_army_list[Territory.ALASKA.value[0]][1], player_army_list[Territory.ALASKA.value[0]][0])
        print_player_army(player_army_list[Territory.MACKENZIE.value[0]][1], player_army_list[Territory.MACKENZIE.value[0]][0])
        print_player_army(player_army_list[Territory.GROELANDIA.value[0]][1], player_army_list[Territory.GROELANDIA.value[0]][0], 15)
        print_player_army(player_army_list[Territory.ISLANDIA.value[0]][1], player_army_list[Territory.ISLANDIA.value[0]][0], 50)
        print_player_army(player_army_list[Territory.SIBERIA.value[0]][1], player_army_list[Territory.SIBERIA.value[0]][0])
        print_player_army(player_army_list[Territory.VLADIVOSTOK.value[0]][1], player_army_list[Territory.VLADIVOSTOK.value[0]][0])
        print()
        print()


        #Second line
        print_territory(Territory.VANCOUVER, 1, 0)
        print_territory(Territory.OTTAWA, 1, 0)
        print_territory(Territory.LABRADOR, 0, 15)
        print_territory(Territory.INGLATERRA, 1, 0)
        print_territory(Territory.SUECIA, 1, 0)
        print_territory(Territory.MOSCOU, 1, 0)
        print_territory(Territory.OMSK, 1, 0)
        print_territory(Territory.DUDINKA, 1, 0)
        print_territory(Territory.TCHITA, 0, 0)
        print()
        print_player_army(player_army_list[Territory.VANCOUVER.value[0]][1], player_army_list[Territory.VANCOUVER.value[0]][0])
        print_player_army(player_army_list[Territory.OTTAWA.value[0]][1], player_army_list[Territory.OTTAWA.value[0]][0])
        print_player_army(player_army_list[Territory.LABRADOR.value[0]][1], player_army_list[Territory.LABRADOR.value[0]][0], 15)
        print_player_army(player_army_list[Territory.INGLATERRA.value[0]][1], player_army_list[Territory.INGLATERRA.value[0]][0])
        print_player_army(player_army_list[Territory.SUECIA.value[0]][1], player_army_list[Territory.SUECIA.value[0]][0])
        print_player_army(player_army_list[Territory.MOSCOU.value[0]][1], player_army_list[Territory.MOSCOU.value[0]][0])
        print_player_army(player_army_list[Territory.OMSK.value[0]][1], player_army_list[Territory.OMSK.value[0]][0])
        print_player_army(player_army_list[Territory.DUDINKA.value[0]][1], player_army_list[Territory.DUDINKA.value[0]][0])
        print_player_army(player_army_list[Territory.TCHITA.value[0]][1], player_army_list[Territory.TCHITA.value[0]][0])
        print()
        print()
        #Third line
        print_territory(Territory.CALIFORNIA, 1, 0)
        print_territory(Territory.NEW_YORK, 0, 30)
        print_territory(Territory.FRANCA, 1, 0)
        print_territory(Territory.ALEMANHA, 1, 0)
        print_territory(Territory.POLONIA, 1, 0)
        print_territory(Territory.ARAL, 1, 0)
        print_territory(Territory.MONGOLIA, 1, 0)
        print_territory(Territory.CHINA, 1, 0)
        print_territory(Territory.JAPAO, 0, 0)
        print()
        print_player_army(player_army_list[Territory.CALIFORNIA.value[0]][1], player_army_list[Territory.CALIFORNIA.value[0]][0])
        print_player_army(player_army_list[Territory.NEW_YORK.value[0]][1], player_army_list[Territory.NEW_YORK.value[0]][0], 30)
        print_player_army(player_army_list[Territory.FRANCA.value[0]][1], player_army_list[Territory.FRANCA.value[0]][0])
        print_player_army(player_army_list[Territory.ALEMANHA.value[0]][1], player_army_list[Territory.ALEMANHA.value[0]][0])
        print_player_army(player_army_list[Territory.POLONIA.value[0]][1], player_army_list[Territory.POLONIA.value[0]][0])
        print_player_army(player_army_list[Territory.ARAL.value[0]][1], player_army_list[Territory.ARAL.value[0]][0])
        print_player_army(player_army_list[Territory.MONGOLIA.value[0]][1], player_army_list[Territory.MONGOLIA.value[0]][0])
        print_player_army(player_army_list[Territory.CHINA.value[0]][1], player_army_list[Territory.CHINA.value[0]][0])
        print_player_army(player_army_list[Territory.JAPAO.value[0]][1], player_army_list[Territory.JAPAO.value[0]][0])
        print()
        print()
        print_territory(Territory.MEXICO, 0, 45)
        print_territory(Territory.ARGELIA, 1, 0)
        print_territory(Territory.EGITO, 0, 15)
        print_territory(Territory.ORIENTE_MEDIO, 1, 0)
        print_territory(Territory.INDIA, 1, 0)
        print_territory(Territory.VIETNA, 0, 0)
        print()
        print_player_army(player_army_list[Territory.MEXICO.value[0]][1], player_army_list[Territory.MEXICO.value[0]][0], 45)
        print_player_army(player_army_list[Territory.ARGELIA.value[0]][1], player_army_list[Territory.ARGELIA.value[0]][0])
        print_player_army(player_army_list[Territory.EGITO.value[0]][1], player_army_list[Territory.EGITO.value[0]][0], 15)
        print_player_army(player_army_list[Territory.ORIENTE_MEDIO.value[0]][1], player_army_list[Territory.ORIENTE_MEDIO.value[0]][0])
        print_player_army(player_army_list[Territory.INDIA.value[0]][1], player_army_list[Territory.INDIA.value[0]][0])
        print_player_army(player_army_list[Territory.VIETNA.value[0]][1], player_army_list[Territory.VIETNA.value[0]][0])
        print()
        print()
        print_territory(Territory.VENEZUELA, 0, 45)
        print_territory(Territory.CONGO, 1,0)
        print_territory(Territory.SUDAO, 0, 30)
        print_territory(Territory.SUMATRA, 1, 0)
        print_territory(Territory.BORNEU, 1, 0) 
        print_territory(Territory.NOVA_GUINE, 0, 0)
        print()
        print_player_army(player_army_list[Territory.VENEZUELA.value[0]][1], player_army_list[Territory.VENEZUELA.value[0]][0], 45)
        print_player_army(player_army_list[Territory.CONGO.value[0]][1], player_army_list[Territory.CONGO.value[0]][0])
        print_player_army(player_army_list[Territory.SUDAO.value[0]][1], player_army_list[Territory.SUDAO.value[0]][0], 30)
        print_player_army(player_army_list[Territory.SUMATRA.value[0]][1], player_army_list[Territory.SUMATRA.value[0]][0])
        print_player_army(player_army_list[Territory.BORNEU.value[0]][1], player_army_list[Territory.BORNEU.value[0]][0])
        print_player_army(player_army_list[Territory.NOVA_GUINE.value[0]][1], player_army_list[Territory.NOVA_GUINE.value[0]][0])

        print()
        print()
        print_territory(Territory.PERU, 1, 0)
        print_territory(Territory.BRASIL, 0, 33)
        print_territory(Territory.AFRICA_DO_SUL, 1, 0)
        print_territory(Territory.MADAGASCAR, 0, 45)
        print_territory(Territory.AUSTRALIA, 0, 0)
        print()
        print_player_army(player_army_list[Territory.PERU.value[0]][1], player_army_list[Territory.PERU.value[0]][0])
        print_player_army(player_army_list[Territory.BRASIL.value[0]][1], player_army_list[Territory.BRASIL.value[0]][0], 33)
        print_player_army(player_army_list[Territory.AFRICA_DO_SUL.value[0]][1], player_army_list[Territory.AFRICA_DO_SUL.value[0]][0])
        print_player_army(player_army_list[Territory.MADAGASCAR.value[0]][1], player_army_list[Territory.MADAGASCAR.value[0]][0], 45)
        print_player_army(player_army_list[Territory.AUSTRALIA.value[0]][1], player_army_list[Territory.AUSTRALIA.value[0]][0])
        print()
        print()
        print_territory(Territory.ARGENTINA)
        print()
        print_player_army(player_army_list[Territory.ARGENTINA.value[0]][1], player_army_list[Territory.ARGENTINA.value[0]][0])
        print()
        print()
    else:
        print('Nada inserido')


territory_matrix_example = [(0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 11, 0, 0, 14, 0, 16, 0, 18, 0, 0, 21, 0, 23, 0, 0, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 36, 0, 0, 0, 0, 0, 42),
                       (0, 0, 0, 4, 0, 0, 7, 0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 0, 27, 0, 29, 0, 0, 0, 0, 34, 0, 0, 0, 37, 0, 40, 0, 0),
                       (0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 5, 0, 0, 0, 0, 10, 0, 0, 13, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 0, 0, 0, 0, 0, 39, 0, 41, 0),
                       (1, 2, 3, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 28, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 20, 0, 0, 22, 0, 25, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 38, 0, 0, 0, 0, 0)
                       ]

