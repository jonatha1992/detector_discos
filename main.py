import os
import json
import hashlib
import subprocess
import platform

# En sistemas Windows importamos pywin32 solo si estamos en Windows
if platform.system() == "Windows":
    try:
        import win32api
        import win32file
    except ImportError:
        win32api = None
        win32file = None

def obtener_discos_windows():
    if not win32api:
        print("Módulo pywin32 no disponible.")
        return []
    # Listar todos los volúmenes del sistema
    discos = win32api.GetLogicalDriveStrings()
    discos = discos.split('\x00')[:-1]  # Separa y quita el último elemento vacío
    return discos

def obtener_informacion_disco_windows(disco):
    if not win32file:
        print("Módulo pywin32 no disponible.")
        return None
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

        # Concatenar datos para hashear con SHA-256
        datos = f"{disco}:{capacidad_total}:{capacidad_usada}:{capacidad_disponible}"
        sha256_hash = hashlib.sha256(datos.encode()).hexdigest()

        print(f"SHA256 del estado del volumen: {sha256_hash}")
        return sha256_hash
    except Exception as e:
        print(f"No se pudo acceder al disco {disco}. Error: {str(e)}")
        return None

def obtener_discos_linux():
    # Utilizar el comando lsblk para obtener información sobre los discos físicos
    comando = ["lsblk", "-b", "-o", "NAME,SIZE,TYPE,SERIAL,UUID", "-J"]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        datos = json.loads(resultado.stdout)
        return datos.get('blockdevices', [])
    except FileNotFoundError:
        print("Error: El comando 'lsblk' no está disponible en este sistema.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar lsblk: {e.stderr.strip() if e.stderr else e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error al parsear salida JSON de lsblk: {e}")
        return []

def mostrar_informacion_disco_linux(discos):
    for i, disco in enumerate(discos):
        if disco.get('type') == 'disk':
            size_val = int(disco.get('size', 0))
            print(f"{i + 1}. {disco.get('name', '')} - {size_val / (1024 ** 3):.2f} GB")

def obtener_informacion_disco_linux(disco):
    nombre = disco.get('name', 'desconocido')
    print(f"\nInformación del disco {nombre}:")
    capacidad_total = int(disco.get('size', 0))
    print(f"Capacidad total: {capacidad_total / (1024 ** 3):.2f} GB")

    serial = disco.get('serial') or ''
    uuid = disco.get('uuid') or ''
    datos = f"{nombre}:{capacidad_total}:{serial}:{uuid}"
    sha256_hash = hashlib.sha256(datos.encode()).hexdigest()
    
    print(f"SHA256 de identidad y capacidad del disco: {sha256_hash}")
    return sha256_hash

def main():
    while True:
        sistema = platform.system()

        if sistema == "Windows":
            discos = obtener_discos_windows()
            if not discos:
                print("No se encontraron discos disponibles.")
                break

            print("\nDiscos detectados (Windows):")
            for i, disco in enumerate(discos):
                print(f"{i + 1}. {disco}")

            try:
                eleccion = int(input(f"\nSeleccione el número del disco que desea hashear (1 - {len(discos)}): ")) - 1
                if 0 <= eleccion < len(discos):
                    obtener_informacion_disco_windows(discos[eleccion])
                else:
                    print("Número seleccionado no válido. Inténtelo de nuevo.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número.")

        elif sistema == "Linux":
            discos = obtener_discos_linux()
            if not discos:
                print("No se encontraron discos disponibles.")
                break

            print("\nDiscos detectados (Linux):")
            mostrar_informacion_disco_linux(discos)

            try:
                eleccion = int(input(f"\nSeleccione el número del disco que desea hashear (1 - {len(discos)}): ")) - 1
                if 0 <= eleccion < len(discos) and discos[eleccion].get('type') == 'disk':
                    obtener_informacion_disco_linux(discos[eleccion])
                else:
                    print("Número seleccionado no válido. Inténtelo de nuevo.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número.")

        else:
            print("Sistema operativo no soportado por este script.")
            break

        continuar = input("\n¿Desea continuar? (sí/no): ").strip().lower()
        if continuar not in ['sí', 'si', 's']:
            print("Saliendo del programa...")
            break

if __name__ == "__main__":
    main()
