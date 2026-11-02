import socket
import json


HOST = "127.0.0.1"
PUERTO = 5000


def mostrar_menu():
    print()
    print("Operaciones disponibles:")
    print("1. Sumar")
    print("2. Restar")
    print("3. Multiplicar")
    print("4. Convertir texto a mayúsculas")
    print("5. Simular tarea lenta")
    print()


def crear_tarea(opcion):
    if opcion == "1":
        return {
            "operacion": "sumar",
            "valores": [10, 20]
        }

    elif opcion == "2":
        return {
            "operacion": "restar",
            "valores": [20, 5]
        }

    elif opcion == "3":
        return {
            "operacion": "multiplicar",
            "valores": [5, 4]
        }

    elif opcion == "4":
        texto = input("Ingrese el texto: ")

        return {
            "operacion": "mayusculas",
            "texto": texto
        }

    elif opcion == "5":
        return {
            "operacion": "esperar",
            "segundos": 5
        }

    else:
        return None


def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PUERTO))

        print("=" * 60)
        print("CLIENTE DE TAREAS DISTRIBUIDAS")
        print("=" * 60)
        print(f"Conectado al servidor {HOST}:{PUERTO}")

        mostrar_menu()

        opcion = input("Seleccione una opción: ").strip()

        tarea = crear_tarea(opcion)

        if tarea is None:
            print("Opción no válida")
            return

        mensaje = json.dumps(tarea)

        cliente.sendall(mensaje.encode())

        print("Tarea enviada al servidor...")
        print("Esperando resultado...")

        respuesta = cliente.recv(4096)

        if not respuesta:
            print("El servidor cerró la conexión sin responder.")
            return

        datos_respuesta = json.loads(respuesta.decode())

        if datos_respuesta.get("estado") == "ok":
            print()
            print(f"Resultado recibido: {datos_respuesta['resultado']}")

        else:
            print()
            print(f"Error: {datos_respuesta.get('mensaje')}")

    except ConnectionRefusedError:
        print("No se pudo conectar al servidor.")
        print("Verifique que servidor.py esté ejecutándose.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cliente.close()


if __name__ == "__main__":
    iniciar_cliente()