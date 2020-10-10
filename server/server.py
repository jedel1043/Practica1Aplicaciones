# Echo server program
import socket
import os
import pathlib

HOST = ''
PORT = 50007
BUFFER_SIZE = 4096  # Recommended power of 2 and small buffer

print('Starting server on port', PORT)

# abre un nuevo socket para esperar peticiones de un cliente
# socket.AF_INET = IPv4 socket
# socket.SOCK_STREAM habilita recibir información particionada
#   por arreglos de tamaño BUFFER_SIZE
# with cierra automáticamente el socket después de salir
#   de su contexto
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    while (True):
        # s.accept() espera alguna petición para
        # continuar con la ejecución del programa
        # conn: socket con la conexión entre el cliente
        #       y el servidor
        # addr: dirección ip donde se originó la conexión
        print('Awaiting request')
        conn, addr = s.accept()

        # with cierra la conexión al salir de su contexto
        with conn:
            print('Connected by', addr)

            # se reciven 2 bytes (16 bits) de tamaño de ruta del archivo;
            # la longitud de ruta no deberá superar los 2^16 - 1 bytes (65536 bytes)
            pathlen = int.from_bytes(conn.recv(2), byteorder="big")

            # "recv" devuelve un arreglo de bytes que se decodifica a "str"
            # para obtener el nombre del archivo utilizando la codificación 
            # por defecto de python (UTF-8)
            relpath = conn.recv(pathlen).decode()
            relpath = os.path.join(addr[0], relpath)

            dirname, basename = os.path.split(relpath)
            
            if dirname and not os.path.exists(dirname):
                pathlib.Path(dirname).mkdir(parents=True)
                print("Created directory \"" + dirname + "\"")

            if basename:
                # se reciben 4 bytes (32 bits) de tamaño del archivo;
                # el archivo a recibir no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
                filelen = int.from_bytes(conn.recv(4), byteorder="big")

                print("Receiving file \"" + relpath + "\" of", filelen, "bytes")

                # with cierra automáticamente el archivo después de salir de su contexto
                with open(relpath, "wb") as f:

                    # escribe bytes en el archivo de salida hasta recibir el
                    # último byte
                    byte_counter = 0
                    while byte_counter < filelen:
                        temp_data = conn.recv(BUFFER_SIZE)
                        byte_counter += len(temp_data)
                        f.write(temp_data)

                        print("Received", len(temp_data),
                            "bytes ("
                            + str(byte_counter * 100 // filelen)
                            + "% completed)")
                print("Wrote file \"" + relpath + "\"")
                print()
