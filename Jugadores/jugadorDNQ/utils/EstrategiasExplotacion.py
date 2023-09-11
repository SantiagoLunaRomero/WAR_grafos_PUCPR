import numpy as np
class EstrategiasExplotacion:

    @staticmethod
    def reforzar(jugador, tablero,estado_actual,lista_nombres_paises):
        q_values = jugador.reforzamiento_network.predict(estado_actual.reshape(1, -1))
        jugador.debug_print(["Q values : ",q_values])
        pais_reforzado_idx = np.argmax(q_values)
        pais_reforzado = lista_nombres_paises[pais_reforzado_idx]
        exito_refuerzo = tablero.reforzar_pais(pais_reforzado, 1, jugador)
        pais_reforzado = tablero.paises[pais_reforzado]
        jugador.debug_print(["pais reforzado : ",pais_reforzado.get_nombre()])
        return pais_reforzado,pais_reforzado_idx,exito_refuerzo
    
    @staticmethod
    def atacar(jugador,tablero,estado_actual,lista_nombres_paises):
        # Decidir acción usando la red neuronal de ataque
        q_values = jugador.ataque_network.predict(estado_actual.reshape(1, -1))
        
        # Elegir el país origen y destino con base en las Q-values
        pais_origen_idx = np.argmax(q_values[0, :42])
        pais_destino_idx = np.argmax(q_values[0, 42:])

        pais_origen = tablero.paises[lista_nombres_paises[pais_origen_idx]]
        pais_destino = tablero.paises[lista_nombres_paises[pais_destino_idx]]
        
        # Atacar desde el país origen al país destino
        exito_ataque = tablero.batalla(pais_origen, pais_destino, jugador)
        exito_ataque = exito_ataque[0]

        return pais_origen, pais_destino, exito_ataque
    
    @staticmethod
    def mover_tropas(jugador, tablero, estado_actual, lista_nombres_paises):
        # 1. Predice las Q-values usando la red neuronal de movimiento de tropas
        q_values = jugador.mover_tropas_network.predict(estado_actual.reshape(1, -1))
        
        # 2. Elegir el país origen y destino con base en las Q-values
        # (Suponiendo que la primera mitad de las Q-values representan el país origen y la segunda mitad el país destino)
        pais_origen_idx = np.argmax(q_values[0, :42])
        pais_destino_idx = np.argmax(q_values[0, 42:])

        nombre_pais_origen = lista_nombres_paises[pais_origen_idx]
        nombre_pais_destino = lista_nombres_paises[pais_destino_idx]
        
        # 3. Mover tropas desde el país origen al país destino
        # (Necesitarás determinar cuántas tropas quieres mover, esto podría ser un número fijo o basado en alguna estrategia)
        numero_tropas = 1  # Por ahora, solo moveremos 1 tropa. Puedes ajustar este número según lo que consideres mejor.
        
        try:
            tablero.mover_tropas(nombre_pais_origen, nombre_pais_destino, numero_tropas)
            exito_movimiento = True
        except ValueError as e:
            print(e)
            exito_movimiento = False

        return tablero.paises[nombre_pais_origen], tablero.paises[nombre_pais_destino], exito_movimiento
    