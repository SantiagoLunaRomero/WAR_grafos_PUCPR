class Jugador:
    def __init__(self, nombre, color, mision):
        self.nombre = nombre
        self.color = color  # Añadimos el atributo color
        self.mision = mision
        self.paises = []
        self.tropas_por_turno = 4

    def reforzar(self, tablero):
        pass

    def atacar(self, tablero):
        pass

    def mover_tropas(self, tablero):
        pass
    def informar_perdida(self,tablero,recompensa=-100):
        # En la clase base, simplemente pasamos.
        pass
    def informar_victoria(self,tablero):
        # En la clase base, simplemente pasamos.
        pass
    def imprimir_paises(self):
      print(f"{self.nombre} posee los siguientes países:")
      for pais in self.paises:
          print(pais.nombre)
    def mostrar_mision(self):
      print(f"La misión de {self.nombre} es: {self.mision.descripcion}")
    def get_mision(self):
      return self.mision.descripcion