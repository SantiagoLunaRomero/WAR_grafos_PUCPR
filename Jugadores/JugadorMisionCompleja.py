from Jugadores.jugador import Jugador

class JugadorMisionCompleja(Jugador):
    def __init__(self, nombre, color, mision):
        super().__init__(nombre, color, mision)
        self.interpretar_mision(mision)

    def interpretar_mision(self, mision):
        self.objetivos = {
            'continentes': [],
            'territorios': 0,
            'tropas_minimas': 0,
            'destruir_color': None
        }

        descripcion = mision.descripcion

        # Interpretar las misiones de conquistar continentes
        if "Conquistar na totalidade" in descripcion:
            continentes = ['América del Norte', 'América del Sur', 'Europa', 'África', 'Asia', 'Oceanía']
            for continente in continentes:
                if continente in descripcion:
                    self.objetivos['continentes'].append(continente)

        # Interpretar la misión de conquistar 18 territorios con al menos dos ejércitos
        if "Conquistar 18 TERRITÓRIOS" in descripcion:
            self.objetivos['territorios'] = 18
            self.objetivos['tropas_minimas'] = 2

        # Interpretar la misión de conquistar 24 territorios a elección
        if "Conquistar 24 TERRITÓRIOS" in descripcion:
            self.objetivos['territorios'] = 24

        # Interpretar las misiones de destruir ejércitos de un color específico
        colores = ['red', 'blue', 'green', 'yellow', 'black', 'purple'] #['Azul', 'Amarillo', 'Vermelho', 'Preto', 'Branco', 'Verde']
        for color in colores:
            if f"Destruir totalmente OS EXÉRCITOS {color}" in descripcion:
                self.objetivos['destruir_color'] = color

    def reforzar(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            # Identificar países en los continentes objetivo que aún no hemos conquistado completamente
            paises_objetivo = [pais for pais in self.paises if pais.continente in self.objetivos['continentes']]
            
            # Reforzar los países más vulnerables en los continentes objetivo
            pais_a_reforzar = min(paises_objetivo, key=lambda pais: pais.tropas, default=None)

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            # Reforzar los países con menos tropas para protegerlos
            pais_a_reforzar = min(self.paises, key=lambda pais: pais.tropas)

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            # Identificar países que son vecinos de ese color
            paises_vecinos_al_color = [pais for pais in self.paises if any(tablero.paises[vecino].jugador.color == self.objetivos['destruir_color'] for vecino in pais.vecinos)]
            
            # Reforzar los países vecinos al color objetivo que tienen menos tropas
            pais_a_reforzar = min(paises_vecinos_al_color, key=lambda pais: pais.tropas, default=None)

        else:
            # Si no hay un objetivo claro (o algo salió mal), simplemente refuerza el país con menos tropas
            pais_a_reforzar = min(self.paises, key=lambda pais: pais.tropas)

        # Aplicar el refuerzo
        if pais_a_reforzar:
            pais_a_reforzar.tropas += self.tropas_por_turno


    def atacar(self, tablero):
        puede_atacar = True
        while puede_atacar:
            # Objetivo: Conquistar continentes específicos
            if self.objetivos['continentes']:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.continente in self.objetivos['continentes'] and pais.jugador != self]

            # Objetivo: Conquistar un cierto número de territorios
            elif self.objetivos['territorios']:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador != self]

            # Objetivo: Destruir un color específico
            elif self.objetivos['destruir_color']:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador.color == self.objetivos['destruir_color']]

            else:
                paises_a_atacar = [pais for pais in tablero.paises.values() if pais.jugador != self]

            # Si no hay países a atacar, termina el turno de ataque
            if not paises_a_atacar:
                return

            # Selecciona el país objetivo para el ataque (el más débil)
            pais_objetivo = min(paises_a_atacar, key=lambda pais: pais.tropas)

            # Selecciona el país de origen para el ataque (el más fuerte entre los vecinos del objetivo)
            paises_origen_posibles = [pais for pais in self.paises if pais.tropas > 1 and pais_objetivo.nombre in pais.vecinos]
            pais_origen = max(paises_origen_posibles, key=lambda pais: pais.tropas, default=None)

            # Ataca el país objetivo si hay un país de origen válido
            if pais_origen:
                tablero.batalla(pais_origen, pais_objetivo)
                puede_atacar = any(pais.tropas > 1 for pais in self.paises)
            else:
                puede_atacar = False


    def mover_tropas(self, tablero):
        # Objetivo: Conquistar continentes específicos
        if self.objetivos['continentes']:
            # Identificar países en las fronteras de los continentes objetivo
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self and tablero.paises[vecino].continente in self.objetivos['continentes'] for vecino in pais.vecinos)]

        # Objetivo: Conquistar un cierto número de territorios
        elif self.objetivos['territorios']:
            # Identificar países en las fronteras con otros jugadores
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

        # Objetivo: Destruir un color específico
        elif self.objetivos['destruir_color']:
            # Identificar países en las fronteras con el color objetivo
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador.color == self.objetivos['destruir_color'] for vecino in pais.vecinos)]

        else:
            # Si no hay un objetivo claro, simplemente identifica países en las fronteras con otros jugadores
            paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

        if paises_frontera:
            # Seleccionar el país de origen (el que tiene más tropas)
            pais_origen = max(paises_frontera, key=lambda pais: pais.tropas)
            
            # Seleccionar el país destino (el vecino con menos tropas)
            pais_destino_nombre = min(pais_origen.vecinos, key=lambda nombre: tablero.paises[nombre].tropas)
            pais_destino = tablero.paises[pais_destino_nombre]

            # Calcular las tropas a mover (dejando al menos una tropa en el país de origen)
            tropas_a_mover = pais_origen.tropas - 1

            if tropas_a_mover > 0:
                pais_origen.tropas -= tropas_a_mover
                pais_destino.tropas += tropas_a_mover