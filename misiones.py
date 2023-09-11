class Mision:
    def __init__(self, descripcion, condicion):
        self.descripcion = descripcion
        self.condicion = condicion

    def esta_completa(self, jugador, tablero):
        return self.condicion(jugador, tablero)
    def get_descripcion(self):
        return self.descripcion

def ha_conquistado_continente(continente, jugador, tablero):
    paises_del_continente = [pais for pais in tablero.paises.values() if pais.continente == continente]
    return all(pais.jugador == jugador for pais in paises_del_continente)

def mision_conquistar_europa_oceania_tercero(jugador, tablero):
    # Verificar conquista completa de Europa y Oceanía
    conquista_europa = ha_conquistado_continente('Europa', jugador, tablero)
    conquista_oceania = ha_conquistado_continente('Oceanía', jugador, tablero)
    
    # Lista de continentes sin Europa y Oceanía para verificar la conquista de un tercer continente
    otros_continentes = ['América del Norte', 'América del Sur', 'Asia', 'África']
    conquista_tercer_continente = any(ha_conquistado_continente(continente, jugador, tablero) for continente in otros_continentes)
    
    return conquista_europa and conquista_oceania and conquista_tercer_continente

def mision_conquistar_asia_america_sul(jugador, tablero):
    return all(pais.jugador == jugador for pais in tablero.paises.values() if pais.continente in ['Asia', 'América del Sur'])
def mision_conquistar_18_territorios_dos_ejercitos(jugador, tablero):
    territorios_conquistados = [pais for pais in tablero.paises.values() if pais.jugador == jugador and pais.tropas >= 2]
    return len(territorios_conquistados) >= 18
def mision_conquistar_asia_africa(jugador, tablero):
    return all(pais.jugador == jugador for pais in tablero.paises.values() if pais.continente in ['Asia', 'África'])
def mision_conquistar_america_norte_africa(jugador, tablero):
    return all(pais.jugador == jugador for pais in tablero.paises.values() if pais.continente in ['América del Norte', 'África'])
def mision_conquistar_24_territorios(jugador, tablero):
    return len([pais for pais in tablero.paises.values() if pais.jugador == jugador]) >= 24
def mision_conquistar_america_norte_oceania(jugador, tablero):
    return all(pais.jugador == jugador for pais in tablero.paises.values() if pais.continente in ['América del Norte', 'Oceanía'])
def mision_destruir_ejercitos_color(jugador, tablero, color):
    return all(pais.jugador.color != color for pais in tablero.paises.values())

misiones = [
    Mision("Conquistar na totalidade a Europa, a Oceanía e mais um terceiro", mision_conquistar_europa_oceania_tercero),
    Mision("Conquistar na totalidade a Asia e a América del Sur", mision_conquistar_asia_america_sul),
    Mision("Conquistar 18 TERRITÓRIOS e ocupar cada um deles com pelo menos dois exércitos", mision_conquistar_18_territorios_dos_ejercitos),
    Mision("Conquistar na totalidade a Asia e a África", mision_conquistar_asia_africa),
    Mision("Conquistar na totalidade a América del Norte e a África", mision_conquistar_america_norte_africa),
    Mision("Conquistar 24 TERRITÓRIOS à sua escolha", mision_conquistar_24_territorios),
    Mision("Conquistar na totalidade a América del Norte e a Oceanía", mision_conquistar_america_norte_oceania),
    Mision("Destruir totalmente OS EXÉRCITOS blue", lambda jugador, tablero: mision_destruir_ejercitos_color(jugador, tablero, 'blue')),
    Mision("Destruir totalmente OS EXÉRCITOS yellow", lambda jugador, tablero: mision_destruir_ejercitos_color(jugador, tablero, 'yellow')),
    Mision("Destruir totalmente OS EXÉRCITOS red", lambda jugador, tablero: mision_destruir_ejercitos_color(jugador, tablero, 'red')),
    Mision("Destruir totalmente OS EXÉRCITOS black", lambda jugador, tablero: mision_destruir_ejercitos_color(jugador, tablero, 'black')),
    Mision("Destruir totalmente OS EXÉRCITOS purple", lambda jugador, tablero: mision_destruir_ejercitos_color(jugador, tablero, 'purple')),
    Mision("Destruir totalmente OS EXÉRCITOS green", lambda jugador, tablero: mision_destruir_ejercitos_color(jugador, tablero, 'green'))
]
descripcion_a_indice = {mision.descripcion: i for i, mision in enumerate(misiones)}



def mision_conquistar_europa_oceania_tercero_a(jugador, tablero):
    continentes_conquistados = [pais.continente for pais in tablero.paises.values() if pais.jugador == jugador]
    return continentes_conquistados.count('Europa') == 5 and continentes_conquistados.count('Oceanía') == 4 and len(set(continentes_conquistados)) >= 3
