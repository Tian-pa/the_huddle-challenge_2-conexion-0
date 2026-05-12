# client.py
import socket
import threading
import sys
import time

HOST = "127.0.0.1" # dirección IP del servidor
PORT = 9999
MAX_REINTENTOS = 5


def recibir(sock):
    """Hilo que escucha mensajes del servidor continuamente."""
    while True:
        try:
            datos = sock.recv(1024)
            if datos: # si tiene contenido
                print(f"\r{datos.decode().strip()}\n> ", end="", flush=True)
            else:
                print("\n[cliente] Servidor cerrado.")
                sys.exit()
        except Exception:
            print("\n[cliente] Conexión perdida.")
            sys.exit()


def conectar():
    """Intenta conectarse al servidor con reintentos."""
    intento = 0
    while intento < MAX_REINTENTOS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            print(f"[cliente] Conectado a {HOST}:{PORT}")
            return sock
        except Exception as e:
            intento += 1
            print(f"[cliente] Intento {intento}/{MAX_REINTENTOS} fallido: {e}")
            time.sleep(2)
    print("[cliente] No se pudo conectar. Cerrando.")
    sys.exit()


def iniciar_cliente():
    nombre = input("Tu nombre: ")
    sock = conectar()

    # Hilo separado para recibir mensajes en segundo plano
    hilo = threading.Thread(target=recibir, args=(sock,), daemon=True)
    hilo.start()

    # Loop principal: el usuario escribe y manda mensajes
    while True:
        try:
            texto = input("> ")
            if texto.strip():
                mensaje = f"{nombre}: {texto}".encode()
                sock.sendall(mensaje)
        except (KeyboardInterrupt, EOFError):
            print("\n[cliente] Saliendo...")
            sock.close()
            break


if __name__ == "__main__":
    iniciar_cliente()