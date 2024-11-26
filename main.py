import os
import hashlib
import subprocess
import platform

# En sistemas Windows importamos pywin32 solo si estamos en Windows
if platform.system() == "Windows":
    import win32api
    import win32file

def obtener_discos_windows():
    # Listar todos los volúmenes del sistema
    discos = win32api.GetLogicalDriveStrings()
    discos = discos.split('\x00')[:-1]  # Separa y quita el último elemento vacío
    return discos

def obtener_informacion_disco_windows(disco):
    try:
        # Obtener información del sistema de archivos del disco
        sectores_por_cluster, bytes_por_sector, num_clusters, num_clusters_libres = win32file.GetDiskFreeSpace(disco)

        # Calcular capacidad total y espacio disponible
        capacidad_total = num_clusters * sectores_por_cluster * bytes_por_sector
        capacidad_disponible = num_clusters_libres * sectores_por_cluster * bytes_por_sector
        capacidad_usada = capacidad_total - capacidad_disponible

        print(f"\nInformación del disco {disco}:")
        print(f"Capacidad total: {capacidad_total / (1024 ** 3):.2f} GB")
        print(f"Espacio usado: {capacidad_usada / (1024 ** 3):.2f} GB")
        print(f"Espacio disponible: {capacidad_disponible / (1024 ** 3):.2f} GB")

        # Concatenar datos para hashear
        datos = f"{capacidad_total}{capacidad_usada}{capacidad_disponible}"
        sha1_hash = hashlib.sha1(datos.encode()).hexdigest()

        print(f"SHA1 del estado del disco: {sha1_hash}")
    except Exception as e:
        print(f"No se pudo acceder al disco {disco}. Error: {str(e)}")

def obtener_discos_linux():
    # Utilizar el comando lsblk para obtener información sobre los discos físicos
    comando = "lsblk -b -o NAME,SIZE,TYPE -J"
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    # Parsear el resultado en formato JSON
    import json
    datos = json.loads(resultado.stdout)
    return datos['blockdevices']

def mostrar_informacion_disco_linux(discos):
    for i, disco in enumerate(discos):
        if disco['type'] == 'disk':
            print(f"{i + 1}. {disco['name']} - {int(disco['size']) / (1024 ** 3):.2f} GB")

def obtener_informacion_disco_linux(disco):
    print(f"\nInformación del disco {disco['name']}:")
    capacidad_total = int(disco['size'])
    print(f"Capacidad total: {capacidad_total / (1024 ** 3):.2f} GB")

    # En Linux, no podemos obtener exactamente la misma información que en Windows sin permisos elevados,
    # así que asumiremos que todos los bloques están disponibles para un cálculo simple.

    # Concatenar datos para hashear
    datos = f"{capacidad_total}"
    sha1_hash = hashlib.sha1(datos.encode()).hexdigest()
    
    print(f"SHA1 del estado del disco: {sha1_hash}")

while True:
    sistema = platform.system()

    if sistema == "Windows":
        # Obtener todos los discos físicos conectados en Windows
        discos = obtener_discos_windows()

        # Mostrar discos detectados
        print("\nDiscos detectados (Windows):")
        for i, disco in enumerate(discos):
            print(f"{i + 1}. {disco}")

        # Preguntar al usuario cuál disco desea hashear
        try:
            eleccion = int(input(f"\nSeleccione el número del disco que desea hashear (1 - {len(discos)}): ")) - 1

            if 0 <= eleccion < len(discos):
                obtener_informacion_disco_windows(discos[eleccion])
            else:
                print("Número seleccionado no válido. Inténtelo de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número.")

    elif sistema == "Linux":
        # Obtener todos los discos físicos conectados en Linux
        discos = obtener_discos_linux()

        # Mostrar discos detectados
        print("\nDiscos detectados (Linux):")
        mostrar_informacion_disco_linux(discos)

        # Preguntar al usuario cuál disco desea hashear
        try:
            eleccion = int(input(f"\nSeleccione el número del disco que desea hashear (1 - {len(discos)}): ")) - 1

            if 0 <= eleccion < len(discos) and discos[eleccion]['type'] == 'disk':
                obtener_informacion_disco_linux(discos[eleccion])
            else:
                print("Número seleccionado no válido. Inténtelo de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número.")

    else:
        print("Sistema operativo no soportado por este script.")
        break

    # Preguntar si desea continuar
    continuar = input("\n¿Desea continuar? (sí/no): ").strip().lower()
    if continuar not in ['sí', 'si', 's']:
        print("Saliendo del programa...")
        break
