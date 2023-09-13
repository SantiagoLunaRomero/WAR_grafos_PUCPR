# app/models/board.py
import random
from enum import Enum     
#http://www.gametrack.com.br/jogos/war/instrucoes/tabelas.asp

class Board:
    def __init__(self):
        # Initialize the board components
        self.empty = None
        self.adj_territory_dict = {}

        self.setup()
        
    def get_adjacent_Territory(self, enum_territory):
        return (self.adj_territory_dict[enum_territory])
    
    def get_territory_continent(self, enum_territory):
        for continent in Continents:
            if enum_territory in continent.territory_list:
                return continent
        return None


    def setup(self):
        self.adj_territory_dict = {

            #America do Sul +2 VERIFIED
            Territory.BRASIL : [Territory.ARGENTINA, Territory.VENEZUELA, Territory.PERU, Territory.ARGELIA], #Verified
            Territory.ARGENTINA : [Territory.PERU, Territory.BRASIL], #Verified
            Territory.VENEZUELA : [Territory.BRASIL, Territory.PERU, Territory.MEXICO],#Verified
            Territory.PERU : [Territory.ARGENTINA, Territory.BRASIL, Territory.VENEZUELA], #Verified

            #America do Norte +5 VERIFIED
            Territory.MEXICO : [Territory.VENEZUELA, Territory.NEW_YORK, Territory.CALIFORNIA], #Verified
            Territory.NEW_YORK : [Territory.MEXICO, Territory.CALIFORNIA, Territory.OTTAWA, Territory.LABRADOR],#Verified
            Territory.CALIFORNIA : [Territory.MEXICO, Territory.NEW_YORK, Territory.OTTAWA, Territory.VANCOUVER],#Verified
            Territory.OTTAWA : [Territory.NEW_YORK, Territory.CALIFORNIA, Territory.VANCOUVER, Territory.LABRADOR, Territory.MACKENZIE], #Verified
            Territory.VANCOUVER : [Territory.MACKENZIE, Territory.ALASKA, Territory.OTTAWA, Territory.CALIFORNIA], #Verified
            Territory.LABRADOR : [Territory.OTTAWA, Territory.NEW_YORK, Territory.GROELANDIA],#Verified
            Territory.MACKENZIE : [Territory.ALASKA, Territory.VANCOUVER, Territory.GROELANDIA, Territory.OTTAWA], #Verified
            Territory.ALASKA : [Territory.MACKENZIE, Territory.VANCOUVER, Territory.VLADIVOSTOK], #Verified
            Territory.GROELANDIA : [Territory.LABRADOR, Territory. MACKENZIE, Territory.ISLANDIA], #Verified

            #Europa +5 VERIFIED
            Territory.ISLANDIA : [Territory.GROELANDIA, Territory.INGLATERRA],#Verified
            Territory.INGLATERRA : [Territory.ISLANDIA, Territory.SUECIA, Territory.FRANCA, Territory.ALEMANHA], #Verified
            Territory.ALEMANHA : [Territory.INGLATERRA, Territory.FRANCA, Territory.POLONIA], #Verified
            Territory.SUECIA : [Territory.INGLATERRA, Territory.MOSCOU], #Verified
            Territory.FRANCA : [Territory.INGLATERRA, Territory.ALEMANHA, Territory.POLONIA, Territory.ARGELIA, Territory.EGITO], #Verified
            Territory.POLONIA : [Territory.ALEMANHA, Territory.FRANCA, Territory.MOSCOU, Territory.ORIENTE_MEDIO, Territory.EGITO],#Verified
            Territory.MOSCOU : [Territory.SUECIA, Territory.POLONIA, Territory.OMSK, Territory.ARAL, Territory.ORIENTE_MEDIO], #Verified

            #África +3 VERIFIED
            Territory.ARGELIA : [Territory.BRASIL, Territory.FRANCA, Territory.EGITO, Territory.SUDAO,
                                Territory.CONGO], #Verified
            Territory.AFRICA_DO_SUL : [Territory.CONGO, Territory.SUDAO, Territory.MADAGASCAR], #Verified
            Territory.MADAGASCAR : [Territory.SUDAO, Territory.AFRICA_DO_SUL],#Verified
            Territory.CONGO : [Territory.ARGELIA, Territory.SUDAO, Territory.AFRICA_DO_SUL], #Verified
            Territory.EGITO : [Territory.ARGELIA, Territory.FRANCA, Territory.POLONIA, Territory.SUDAO,
                                Territory.ORIENTE_MEDIO],#Verified
            Territory.SUDAO : [Territory.ARGELIA, Territory.EGITO, Territory.MADAGASCAR, Territory.AFRICA_DO_SUL, Territory.CONGO],#Verified
           

            #Asia +7 VERIFIED

            Territory.CHINA : [Territory.MONGOLIA, Territory.ARAL, Territory.INDIA, Territory.VIETNA, Territory.VLADIVOSTOK, 
                               Territory.JAPAO, Territory.TCHITA, Territory.OMSK], #Verified
            Territory.ARAL : [Territory.MOSCOU, Territory.ORIENTE_MEDIO, Territory.OMSK, Territory.CHINA, Territory.INDIA],#Verified
            Territory.OMSK : [Territory.MOSCOU, Territory.DUDINKA, Territory.MONGOLIA, Territory.CHINA, Territory.ARAL], #Verified
            Territory.ORIENTE_MEDIO : [Territory.EGITO, Territory.MOSCOU, Territory.ARAL, Territory.INDIA, Territory.POLONIA], #Verified
            Territory.DUDINKA : [Territory.OMSK, Territory.SIBERIA, Territory.TCHITA, Territory.MONGOLIA], #Verified
            Territory.SIBERIA : [Territory.DUDINKA, Territory.TCHITA, Territory.VLADIVOSTOK], #Verified
            Territory.TCHITA : [Territory.SIBERIA, Territory.DUDINKA, Territory.VLADIVOSTOK, Territory.CHINA, 
                                Territory.MONGOLIA], #Verified
            Territory.MONGOLIA : [Territory.OMSK, Territory.DUDINKA, Territory.TCHITA, Territory.CHINA], #Verified
            Territory.VLADIVOSTOK : [Territory.SIBERIA, Territory.TCHITA, Territory.JAPAO, Territory.ALASKA, Territory.CHINA], #Verified
            Territory.INDIA : [Territory.CHINA, Territory.ORIENTE_MEDIO, Territory.ARAL, Territory.VIETNA, Territory.SUMATRA], #Verified
            Territory.JAPAO : [Territory.VLADIVOSTOK, Territory.CHINA],#Verified
            Territory.VIETNA : [Territory.INDIA, Territory.CHINA, Territory.BORNEU], #Verified

            #Oceania +2 VERIFIED
            Territory.BORNEU :  [Territory.VIETNA, Territory.NOVA_GUINE, Territory.AUSTRALIA], #Verified
            Territory.AUSTRALIA : [Territory.SUMATRA, Territory.BORNEU, Territory.NOVA_GUINE], #Verified
            Territory.SUMATRA : [Territory.INDIA, Territory.AUSTRALIA],#Verified
            Territory.NOVA_GUINE : [Territory.BORNEU, Territory.AUSTRALIA]#Verified
            
        }




class Territory(Enum):
    # América do Sul +2
    BRASIL = (0, "Brasil")
    ARGENTINA = (1, "Argentina")
    VENEZUELA = (2, "Venezuela")
    PERU = (3, "Peru")

    #America do Norte +5
    MEXICO = (4, "Mexico")
    NEW_YORK = (5, "New York")
    CALIFORNIA = (6, "California")
    OTTAWA = (7, "Ottawa")
    VANCOUVER = (8, "Vancouver")
    MACKENZIE = (9, "Mackenzie")
    ALASKA = (10, "Alaska")
    LABRADOR = (11, "Labrador")
    GROELANDIA = (12, "Groelandia")

    #Europa +5
    ISLANDIA = (13, "Islandia")
    INGLATERRA = (14, "Inglaterra")
    SUECIA = (15, "Suecia")
    ALEMANHA = (16, "Alemanha")
    FRANCA = (17, "Franca")
    POLONIA = (18, "Polonia")
    MOSCOU = (19, "Moscou")

    #África +3
    ARGELIA = (20, "Argelia")
    EGITO = (21, "Egito")
    CONGO = (22, "Congo")
    SUDAO = (23, "Sudao")
    MADAGASCAR = (24, "Madagascar")
    AFRICA_DO_SUL = (25, "Africa do Sul")

    #Asia +7
    ORIENTE_MEDIO = (26, "Oriente Medio")
    ARAL = (27, "Aral")
    OMSK = (28, "Omsk")
    DUDINKA = (29, "Dudinka")
    SIBERIA = (30, "Siberia")
    TCHITA = (31, "Tchita")
    MONGOLIA = (32, "Mongolia")
    VLADIVOSTOK = (33, "Vladivostok")
    CHINA = (34, "China")
    INDIA = (35, "India")
    JAPAO = (36, "Japao")
    VIETNA = (37, "Vietna")

    #Oceania +2
    BORNEU = (38, "Borneu")
    SUMATRA = (39, "Sumatra")
    NOVA_GUINE = (40, "Nova Guine")
    AUSTRALIA = (41, "Australia")

    def get_territory_by_index(index):
        for territory in Territory:
            if territory.value[0] == index:
                return territory
        return None

class Continents(Enum):
    AMERICA_DO_SUL = (0, "America Do Sul", 2, [Territory.BRASIL, Territory.ARGENTINA, Territory.PERU, Territory.VENEZUELA])
    
    AMERICA_DO_NORTE = (1, "America Do Norte", 5, [Territory.MEXICO, Territory.OTTAWA, Territory.CALIFORNIA, Territory.NEW_YORK,
                                                   Territory.VANCOUVER, Territory.MACKENZIE, Territory.ALASKA, Territory.LABRADOR,
                                                   Territory.GROELANDIA])
    
    EUROPA = (2, "Europa", 5, [Territory.ISLANDIA, Territory.INGLATERRA, Territory.SUECIA, Territory.ALEMANHA, Territory.FRANCA,
                               Territory.POLONIA, Territory.MOSCOU])
    
    AFRICA = (3, "Africa", 3, [Territory.ARGELIA, Territory.EGITO, Territory.CONGO, Territory.SUDAO, Territory.MADAGASCAR, Territory.AFRICA_DO_SUL])
    
    ASIA = (4, "Asia", 7, [Territory.ORIENTE_MEDIO, Territory.ARAL, Territory.OMSK, Territory.DUDINKA, Territory.SIBERIA, Territory.TCHITA,
            Territory.MONGOLIA, Territory.VLADIVOSTOK, Territory.CHINA, Territory.INDIA, Territory.JAPAO, Territory.VIETNA])
    
    OCEANIA = (5, "Oceania", 2, [Territory.BORNEU, Territory.SUMATRA, Territory.NOVA_GUINE, Territory.AUSTRALIA])

    def __init__(self, index, name, extra_soldiers, territory_list):
        self.name_str = name
        self.index = index
        self.extra_soldiers = extra_soldiers
        self.territory_list = territory_list

    def __str__(self):
        return self._name_
    
