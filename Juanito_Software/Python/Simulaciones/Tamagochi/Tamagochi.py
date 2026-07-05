# Copyright (C) 2025 JuanitoSoftware
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.

import random
from time import sleep

personajes = {}
colores = ['rojo', 'azul', 'amarillo', 'verde', 'naranja']
estados_animo = ['triste', 'contento', 'dormido', 'hambriento', 'sano']
acciones = ['comer', 'dormir', 'jugar', 'sentarse', 'caminar', 'correr']

def mostrar_guia():
    print("Bienvenido al Tamagotchi por comandos")
    print("Puedes crear un personaje, alimentarlo, hacerlo jugar y ver cómo cambia su estado")
    print("Tu Tamagotchi crecerá con el tiempo y tendrá diferentes estados de ánimo según tus acciones")
    print("Acciones disponibles: comer, dormir, jugar, sentarse, caminar, correr\n")

def menu():
    print("1. Crear nuevo personaje")
    print("2. Elegir personaje existente")
    print("3. Ver personajes")
    print("4. Eliminar personaje")
    print("5. Salir")
    return input("Selecciona una opción: ")

def crear_personaje():
    nombre = input("Nombre del personaje: ")
    edad = 0
    color = random.choice(colores)
    estado_animo = random.choice(estados_animo)
    energia = random.randint(40, 60)
    hambre = random.randint(40, 60)
    felicidad = random.randint(40, 60)
    personajes[nombre] = {
        'nombre': nombre,
        'edad': edad,
        'color': color,
        'estado_animo': estado_animo,
        'energia': energia,
        'hambre': hambre,
        'felicidad': felicidad
    }
    print(f"{nombre} ha sido creado con éxito\n")

def eliminar_personaje():
    if not personajes:
        print("No hay personajes para eliminar\n")
        return
    ver_personajes()
    nombre = input("Escribe el nombre del personaje a eliminar: ")
    if nombre in personajes:
        del personajes[nombre]
        print(f"{nombre} ha sido eliminado exitosamente\n")
    else:
        print("Personaje no encontrado\n")

def eliminar_personaje_por_nombre(nombre):
    if not personajes:
        print("No hay personajes para eliminar\n")
        return
    if nombre in personajes:
        del personajes[nombre]
        print(f"{nombre} ha Muerto R.I.P\n")
    else:
        print("Personaje no encontrado\n")


def ver_personajes():
    if not personajes:
        print("No hay personajes creados\n")
    else:
        for nombre, p in personajes.items():
            print(f"{nombre} (Edad: {p['edad']} - Estado: {p['estado_animo']} - Energía: {p['energia']} - Hambre: {p['hambre']} - Felicidad: {p['felicidad']})")
        print()

def elegir_personaje():
    if not personajes:
        print("No hay personajes creados\n")
        return None
    ver_personajes()
    nombre = input("Escribe el nombre del personaje: ")
    if nombre in personajes:
        return personajes[nombre]
    print("Personaje no encontrado\n")
    return None

def actualizar_estado(personaje):
    if personaje['hambre'] >= 100:
        print("Tu personaje ha muerto de hambre\n")
        eliminar_personaje_por_nombre(personaje['nombre'])
        main()
    if personaje['energia'] <= 0:
        print("Tu personaje ha muerto de agotamiento\n")
        eliminar_personaje_por_nombre(personaje['nombre'])
        main()
    if personaje['felicidad'] <= 0:
        print("Tu personaje se ha suicidado de tristeza\n")
        eliminar_personaje_por_nombre(personaje['nombre'])
        main()
    if personaje['hambre'] > 80:
        personaje['estado_animo'] = 'hambriento'
    elif personaje['energia'] < 30:
        personaje['estado_animo'] = 'dormido'
    elif personaje['felicidad'] < 30:
        personaje['estado_animo'] = 'triste'
    elif personaje['felicidad'] > 70:
        personaje['estado_animo'] = 'contento'
    else:
        personaje['estado_animo'] = 'sano'

def aplicar_accion(personaje, accion):
    if accion == 'comer':
        personaje['hambre'] = max(0, personaje['hambre'] - 20)
        personaje['energia'] = min(100, personaje['energia'] + 10)
        personaje['felicidad'] = min(100, personaje['felicidad'] + 5)
    elif accion == 'dormir':
        personaje['energia'] = min(100, personaje['energia'] + 30)
        personaje['hambre'] = min(100, personaje['hambre'] + 10)
        personaje['felicidad'] = max(0, personaje['felicidad'] - 5)
    elif accion == 'jugar':
        personaje['energia'] = max(0, personaje['energia'] - 15)
        personaje['hambre'] = min(100, personaje['hambre'] + 10)
        personaje['felicidad'] = min(100, personaje['felicidad'] + 20)
    elif accion == 'sentarse':
        personaje['energia'] = min(100, personaje['energia'] + 5)
        personaje['hambre'] = min(100, personaje['hambre'] + 5)
        personaje['felicidad'] = min(100, personaje['felicidad'] - 10)
    elif accion == 'caminar':
        personaje['energia'] = max(0, personaje['energia'] - 5)
        personaje['hambre'] = min(100, personaje['hambre'] + 5)
        personaje['felicidad'] = min(100, personaje['felicidad'] + 5)
    elif accion == 'correr':
        personaje['energia'] = max(0, personaje['energia'] - 20)
        personaje['hambre'] = min(100, personaje['hambre'] + 20)
        personaje['felicidad'] = min(100, personaje['felicidad'] + 15)
    actualizar_estado(personaje)
    personaje['edad'] += 1

def mostrar_estado(personaje):
    print(f"Nombre: {personaje['nombre']}")
    print(f"Edad: {personaje['edad']}")
    print(f"Color: {personaje['color']}")
    print(f"Estado de ánimo: {personaje['estado_animo']}")
    print(f"Energía: {personaje['energia']}")
    print(f"Hambre: {personaje['hambre']}")
    print(f"Felicidad: {personaje['felicidad']}\n")

def acciones_menu():
    print("Acciones disponibles:")
    for accion in acciones:
        print(f"- {accion}")
    return input("Selecciona una acción: ")

def main():
    mostrar_guia()
    while True:
        opcion = menu()
        if opcion == '1':
            crear_personaje()
        elif opcion == '2':
            personaje = elegir_personaje()
            if personaje:
                while True:
                    mostrar_estado(personaje)
                    accion = acciones_menu()
                    if accion not in acciones:
                        print("Acción no válida\n")
                        continue
                    aplicar_accion(personaje, accion)
                    sleep(2)
                    if personaje['estado_animo'] == 'muerto':
                        print(f"{personaje['nombre']} ha muerto. No puedes realizar más acciones con él.\n")
                        break
                    mostrar_estado(personaje)
                    continuar = input("¿Quieres realizar otra acción con este personaje? (s/n): ")
                    if continuar.lower() != 's':
                        break
        elif opcion == '3':
            ver_personajes()
        elif opcion == '4':
            eliminar_personaje()
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción inválida\n")

if __name__ == '__main__':
    main()
