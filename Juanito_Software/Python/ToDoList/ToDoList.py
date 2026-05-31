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

import json
import os

# Archivo donde se guardarán las tareas
FILE = "tasks.json"

# Cargar tareas desde el archivo
def load_tasks():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

# Guardar tareas en el archivo
def save_tasks(tasks):
    with open(FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# Mostrar todas las tareas
def show_tasks(tasks):
    if not tasks:
        print("\nNo hay tareas pendientes.\n")
        return
    print("\nTareas:")
    for i, task in enumerate(tasks, 1):
        status = "✔" if task["done"] else "✖"
        print(f"{i}. [{status}] {task['task']}")
    print()

# Añadir tarea
def add_task(tasks):
    task_name = input("Escribe la tarea: ").strip()
    if task_name:
        tasks.append({"task": task_name, "done": False})
        save_tasks(tasks)
        print("Tarea añadida!\n")

# Marcar tarea como completada
def complete_task(tasks):
    show_tasks(tasks)
    if not tasks:
        return
    try:
        num = int(input("Número de la tarea completada: "))
        if 1 <= num <= len(tasks):
            tasks[num - 1]["done"] = True
            save_tasks(tasks)
            print("Tarea marcada como completada!\n")
        else:
            print("Número inválido.\n")
    except ValueError:
        print("Por favor, introduce un número válido.\n")

# Eliminar tarea
def delete_task(tasks):
    show_tasks(tasks)
    if not tasks:
        return
    try:
        num = int(input("Número de la tarea a eliminar: "))
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            save_tasks(tasks)
            print(f"Tarea '{removed['task']}' eliminada!\n")
        else:
            print("Número inválido.\n")
    except ValueError:
        print("Por favor, introduce un número válido.\n")

# Menú principal
def main():
    tasks = load_tasks()
    while True:
        print("=== TO-DO LIST ===")
        print("1. Ver tareas")
        print("2. Añadir tarea")
        print("3. Completar tarea")
        print("4. Eliminar tarea")
        print("5. Salir")
        choice = input("Elige una opción: ").strip()
        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida, intenta otra vez.\n")

if __name__ == "__main__":
    main()