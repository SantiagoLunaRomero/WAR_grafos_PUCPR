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
            success, message = tablero.reforzar_pais(pais_a_reforzar.nombre, self.tropas_por_turno, self)
            print(message)


    def atacar(self, tablero):
        print("fase de ataque mision compleja")
        
        puede_atacar = True
        attack_counter = 0  # Contador para llevar un registro del número de ataques
        MAX_ATTACKS = 20  # Límite para el número de ataques en un turno

        while puede_atacar and attack_counter < MAX_ATTACKS:
            attack_counter += 1  # Incrementar el contador de ataques

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
                tablero.batalla(pais_origen, pais_objetivo, self)
                puede_atacar = any(pais.tropas > 1 for pais in self.paises)
            else:
                puede_atacar = False

    def mover_tropas(self, tablero):
        # Identificar países en las fronteras con otros jugadores
        paises_frontera = [pais for pais in self.paises if any(tablero.paises[vecino].jugador != self for vecino in pais.vecinos)]

        if not paises_frontera:
            return  # No hay países en las fronteras para mover tropas

        # Seleccionar el país de origen (el que tiene más tropas y al menos tiene más de una tropa)
        pais_origen = max([pais for pais in paises_frontera if pais.tropas > 1], key=lambda pais: pais.tropas, default=None)

        if not pais_origen:
            return  # No hay un país de origen válido con más de una tropa

        # Seleccionar el país destino (el vecino propio con menos tropas)
        paises_vecinos_propios = [tablero.paises[nombre] for nombre in pais_origen.vecinos if tablero.paises[nombre].jugador == self]
        pais_destino = min(paises_vecinos_propios, key=lambda pais: pais.tropas, default=None)

        if not pais_destino:
            return  # No hay vecinos propios para mover tropas

        # Calcular las tropas a mover, dejando al menos una tropa en el país de origen
        tropas_disponibles = pais_origen.tropas_disponibles_para_mover()
        tropas_a_mover = min(pais_origen.tropas - 1, tropas_disponibles)

        if tropas_a_mover > 0:
            tablero.mover_tropas(pais_origen.nombre, pais_destino.nombre, tropas_a_mover)


