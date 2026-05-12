# server.py
import socket
import selectors

# Selector global: va a vigilar todos los sockets a la vez
sel = selectors.DefaultSelector()

# Lista de clientes conectados
clientes = []

def broadcast(mensaje, emisor):
    """Envía el mensaje a todos los clientes excepto al que lo mandó."""
    for cliente in clientes[:]:  # se recorre la lista de clientes conectados
        if cliente != emisor:
            try:
                cliente.sendall(mensaje)
            except Exception:
                desconectar(cliente)


def desconectar(cliente):
    """Cierra un socket y lo saca de todo."""
    if cliente in clientes:
        clientes.remove(cliente)
    try:
        sel.unregister(cliente)
        cliente.close()
    except Exception:
        pass
    print("[servidor] Cliente desconectado.")


def aceptar_conexion(servidor_sock):
    """Acepta un cliente nuevo y lo registra en el selector."""
    cliente_sock, addr = servidor_sock.accept()
    cliente_sock.setblocking(False)
    sel.register(cliente_sock, selectors.EVENT_READ, recibir_mensaje)
    clientes.append(cliente_sock)
    print(f"[servidor] Nuevo cliente: {addr}")
    bienvenida = b"Conectado al chat. Bienvenido.\n"
    cliente_sock.sendall(bienvenida)


def recibir_mensaje(cliente_sock):
    """Lee el mensaje de un cliente y hace broadcast."""
    try:
        datos = cliente_sock.recv(1024) # se recibe el mensaje del cliente
        if datos: # si tiene contenido
            print(f"[chat] {datos.decode().strip()}")
            broadcast(datos, cliente_sock)
        else: # si está vacío
            # datos vacíos = el cliente cerró la conexión
            desconectar(cliente_sock)
    except Exception:
        desconectar(cliente_sock)

def iniciar_servidor(host="0.0.0.0", port=9999):
    servidor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # direcciones IPv4 y protocolo TCP.
    servidor_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # nivel al que se aplica, opción activada - reutilizar el puerto.
    servidor_sock.bind((host, port)) # une la dirección al puerto
    servidor_sock.listen() # modo escucha para recibir conexiones
    servidor_sock.setblocking(False) # # No bloqueante
    sel.register(servidor_sock, selectors.EVENT_READ, aceptar_conexion)
    print(f"[servidor] Escuchando en {host}:{port}")


    while True: # loop infinito - permite manejar multiples clientes sin bloqueos
        eventos = sel.select(timeout=None) 
        for key, mask in eventos:
            callback = key.data # identifica que función ejecutar
            callback(key.fileobj) # la llama

if __name__ == "__main__":
    iniciar_servidor()