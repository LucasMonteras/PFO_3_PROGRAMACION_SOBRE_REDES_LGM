import socket
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor


HOST = "127.0.0.1"
PUERTO = 5000
MAX_WORKERS = 4


def procesar_tarea(tarea):
    operacion = tarea.get("operacion")
    valores = tarea.get("valores", [])

    if operacion == "sumar":
        return sum(valores)

    elif operacion == "restar":
        if len(valores) != 2:
            return "La operación restar requiere exactamente 2 valores"
        return valores[0] - valores[1]

    elif operacion == "multiplicar":
        resultado = 1

        for valor in valores:
            resultado *= valor

        return resultado

    elif operacion == "mayusculas":
        texto = tarea.get("texto", "")
        return texto.upper()

    elif operacion == "esperar":
        segundos = tarea.get("segundos", 5)

        time.sleep(segundos)

        return f"Tarea completada después de {segundos} segundos"

    else:
        return "Operación no válida"


def atender_cliente(cliente, direccion):
    nombre_hilo = threading.current_thread().name

    print(f"[{nombre_hilo}] Cliente conectado desde {direccion}")

    try:
        datos = cliente.recv(4096)

        if not datos:
            print(f"[{nombre_hilo}] Cliente {direccion} no envió datos")
            return

        mensaje = datos.decode()

        tarea = json.loads(mensaje)

        print(f"[{nombre_hilo}] Tarea recibida de {direccion}: {tarea}")

        resultado = procesar_tarea(tarea)

        respuesta = {
            "estado": "ok",
            "resultado": resultado
        }

        cliente.sendall(json.dumps(respuesta).encode())

        print(f"[{nombre_hilo}] Resultado enviado a {direccion}: {resultado}")

    except json.JSONDecodeError:
        respuesta = {
            "estado": "error",
            "mensaje": "JSON inválido"
        }

        cliente.sendall(json.dumps(respuesta).encode())

    except Exception as e:
        print(f"[{nombre_hilo}] Error con {direccion}: {e}")

        try:
            respuesta = {
                "estado": "error",
                "mensaje": str(e)
            }

            cliente.sendall(json.dumps(respuesta).encode())

        except Exception:
            pass

    finally:
        cliente.close()

        print(f"[{nombre_hilo}] Cliente {direccion} desconectado")
        print("-" * 60)


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PUERTO))
    servidor.listen()

    print("=" * 60)
    print("SERVIDOR DE TAREAS DISTRIBUIDAS")
    print("=" * 60)
    print(f"Servidor escuchando en {HOST}:{PUERTO}")
    print(f"Pool de workers iniciado: {MAX_WORKERS} hilos")
    print("Esperando conexiones...")
    print("=" * 60)

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:

            while True:
                cliente, direccion = servidor.accept()

                pool.submit(
                    atender_cliente,
                    cliente,
                    direccion
                )

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar_servidor()