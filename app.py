import os
import sqlite3
import shutil
import getpass
from colorama import init, Fore, Style
import time
import sys

# Inicializar colorama
init()

# Obtener la ruta del directorio donde se encuentra el archivo .py del programa
program_dir = os.path.dirname(os.path.abspath(__file__))

# Función para crear la base de datos si no existe
def create_database():
    conn = sqlite3.connect(os.path.join(program_dir, 'locked_folders.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locked_folders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 folder_path TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Función para mostrar el logo
def print_logo():
    logo = """
""" + Fore.BLUE + """
 █████╗ ██╗  ██╗██╗███╗   ██╗██╗   ██╗███████╗    ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗
██╔══██╗██║ ██╔╝██║████╗  ██║██║   ██║██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝
███████║█████╔╝ ██║██╔██╗ ██║██║   ██║███████╗    ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   
██╔══██║██╔═██╗ ██║██║╚██╗██║██║   ██║╚════██║    ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   
██║  ██║██║  ██╗██║██║ ╚████║╚██████╔╝███████║    ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝   
""" + Style.RESET_ALL + Fore.YELLOW + """
                                                                                                            
    """ + Style.RESET_ALL
    print(logo)

# Función para mostrar el texto "Bloko"
def print_bloko():
    print(Fore.GREEN + "Bloko" + Style.RESET_ALL)

# Función para bloquear una carpeta
def lock_folder():
    print_logo()
    print_bloko()
    print(Fore.CYAN + "Bloqueando carpeta..." + Style.RESET_ALL)
    time.sleep(1)  # Simular proceso de bloqueo

    folder_path = input("Ingrese la ruta de la carpeta a bloquear: ")
    password = getpass.getpass("Ingrese una contraseña para bloquear la carpeta: ")

    # Verificar si la carpeta existe
    if os.path.exists(folder_path):
        # Mover la carpeta al directorio del programa
        try:
            shutil.move(folder_path, program_dir)
        except Exception as e:
            print(Fore.RED + f"Error al bloquear la carpeta: {str(e)}" + Style.RESET_ALL)
            return

        # Guardar la información en la base de datos
        conn = sqlite3.connect(os.path.join(program_dir, 'locked_folders.db'))
        c = conn.cursor()
        c.execute("INSERT INTO locked_folders (folder_path, password) VALUES (?, ?)", (folder_path, password))
        conn.commit()
        conn.close()
        print(Fore.GREEN + "Carpeta bloqueada exitosamente." + Style.RESET_ALL)
    else:
        print(Fore.RED + "La carpeta especificada no existe." + Style.RESET_ALL)

# Función para desbloquear una carpeta

def unlock_folder():
    print(Fore.CYAN + "Desbloqueando carpeta..." + Style.RESET_ALL)
    time.sleep(1)  # Simular proceso de desbloqueo

    conn = sqlite3.connect(os.path.join(program_dir, 'locked_folders.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM locked_folders")
    folders = c.fetchall()
    conn.close()

    if len(folders) == 0:
        print(Fore.YELLOW + "No hay carpetas bloqueadas." + Style.RESET_ALL)
        return

    print("Carpetas bloqueadas:")
    for folder in folders:
        print(f"{folder[0]}. {folder[1]}")

    folder_id = input("Ingrese el número de la carpeta que desea desbloquear: ")

    conn = sqlite3.connect(os.path.join(program_dir, 'locked_folders.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM locked_folders WHERE id=?", (folder_id,))
    folder_info = c.fetchone()
    conn.close()

    if folder_info:

        attempts_left = 3  # Numero de intentos máximo
        wait_time = 100 # Tiempo de espera inicial en segundos

        while attempts_left > 0:
            password = getpass.getpass("Ingrese la contraseña para desbloquear la carpeta: ")
            if password == folder_info[2]:
                # Obtener la ruta de destino en el escritorio
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                folder_name = os.path.basename(folder_info[1])
                destination_path = os.path.join(desktop_path, folder_name)

                # Mover la carpeta al escritorio
                try:
                    shutil.move(os.path.join(program_dir, folder_name), destination_path)
                    print(Fore.GREEN + "Carpeta desbloqueada exitosamente." + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.RED + f"Error al desbloquear la carpeta: {str(e)}" + Style.RESET_ALL)
                return
            else:
                attempts_left -= 1
                if attempts_left > 0:
                    print(Fore.RED + f"Contraseña Incorrecta. Intentos restantes: {attempts_left}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Numero de intentos superado. Alarma activada." + Style.RESET_ALL)
                    # Implementar alarma
                    remaining_time = wait_time
                    while remaining_time > 0:
                        print(Fore.YELLOW + f"El programa está bloqueado. Tiempo restante: {remaining_time} segundos." + Style.RESET_ALL)
                        time.sleep(1)
                        remaining_time -= 1
                       # Duplicar el tiempo de espera para el siguiente bloqueo
                    print("Alarma desactivada. Puede intentarlo nuevamente.")
            
if __name__ == "__main__":
    create_database()

    while True:
        print("\n1. Bloquear carpeta")
        print("2. Desbloquear carpeta")
        print("3. Salir")

        choice = input("Seleccione una opción: ")

        if choice == "1":
            lock_folder()
        elif choice == "2":
            unlock_folder()
        elif choice == "3":
            print(Fore.MAGENTA + "Saliendo del programa..." + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Opción no válida." + Style.RESET_ALL)