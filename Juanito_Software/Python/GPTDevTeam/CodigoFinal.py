# Importa las funciones necesarias
import sys

# Define una lista de estados posibles
ESTADOS = ["triste", "normal", "feliz"]

# Define la energía inicial
ENERGIA_INICIAL = 100

class Tamagotchi:
    def __init__(self):
        self.estado_actual = "normal"
        self.energia_actual = ENERGIA_INICIAL

    def mostrar_guia(self):
        print("Guía de Uso:")
        print("Para alimentar al Tamagotchi, escribe 'comer'.")
        print("Para recargar la energía, escribe 'cargar'.")
        print("Para ver el estado de ánimo actual, escribe 'estado'.")
        print("Para salir, escribe 'salir'.")

    def alimentar(self):
        self.energia_actual += 20
        if self.energia_actual > 100:
            self.energia_actual = 100

    def cargar(self):
        self.energia_actual = ENERGIA_INICIAL

    def estado(self):
        print("El estado de ánimo actual es:", self.estado_actual)

# Crea un Tamagotchi
tamagotchi = Tamagotchi()

# Muestra la guía de uso
tamagotchi.mostrar_guia()

# Bucle principal del juego
while True:
    # Solicita al usuario un comando
    comando = input("Ingresa un comando: ")

    # Procesa el comando
    if comando == "comer":
        tamagotchi.alimentar()
    elif comando == "cargar":
        tamagotchi.cargar()
    elif comando == "estado":
        tamagotchi.estado()
    elif comando == "salir":
        break
    else:
        print("Comando inválido.")

# Muestra un mensaje de agradecimiento
print("Gracias por jugar.")