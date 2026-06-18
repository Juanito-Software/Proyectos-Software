ESTADOS = ["triste", "normal", "feliz"]
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

tamagotchi = Tamagotchi()
tamagotchi.mostrar_guia()

while True:
    comando = input("Ingresa un comando: ")

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

print("Gracias por jugar.")