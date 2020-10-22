import socket
import os
import pathlib

# info del servidor
HOST = ''
PORT = 50007
BUFFER_SIZE = 4096  # buffer óptimo con tamaño pequeño y potencia de 2


''' Formato para la recepción de archivos:
    2 bytes: número de archivos a recibir
    2 bytes: longitud de la ruta destino (pathlen)
    n bytes: ruta destino
    4 bytes: longitud del archivo
    m bytes: datos del archivo
'''

# abre un nuevo socket para esperar peticiones de un cliente
# socket.AF_INET = IPv4 socket
# socket.SOCK_STREAM habilita el protocolo TCP
# with cierra automáticamente el socket después de salir
#   de su contexto
print('Starting server on port', PORT)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    # recibe infinitamente peticiones hasta forzar el cierre
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

            # se reciben 2 bytes (16 bits) con el número de archivos a recibir;
            # el número de archivos no deberá superar los 2^16 - 1 bytes (65536 bytes)
            filen = int.from_bytes(conn.recv(2), byteorder="big")

            for unused in range(filen):

                # se reciben 2 bytes (16 bits) de tamaño de ruta del archivo;
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
                            temp_data = conn.recv(BUFFER_SIZE if (rem := filelen - byte_counter) > BUFFER_SIZE else rem)
                            byte_counter += len(temp_data)
                            f.write(temp_data)

                            print("Received", len(temp_data),
                                "bytes ("
                                + str(byte_counter * 100 // filelen)
                                + "% completed)")
                    print("Wrote file \"" + relpath + "\"")
                    print()
