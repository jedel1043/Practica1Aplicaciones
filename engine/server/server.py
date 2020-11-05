import socket
import os
import pathlib
import shutil
import json
from enum import IntEnum


def fs_tree(root):
    for root, dirs, files in os.walk(root):
        dir_content = []
        for dir in dirs:
            go_inside = os.path.join(root, dir)
            dir_content.append(fs_tree(go_inside))
        files_lst = []
        for f in files:
            files_lst.append(f)
        return {'name': os.path.basename(root), 'files': files_lst, 'dirs': dir_content}


os.chdir(os.path.dirname(os.path.realpath(__file__)))

HOST = 'localhost'
PORT = 50007
BUFFER_SIZE = 4096  # buffer óptimo con tamaño pequeño y potencia de 2


class Instruction(IntEnum):
    UPLOAD = 1
    DOWNLOAD = 2
    DELETE = 3
    GET = 4


''' Formato para la recepción de archivos:
    1 byte: longitud del nombre de usuario
    n bytes: nombre de usuario
    1 byte:  instrucción.
        1: subir archivo
        2: bajar archivo
        3: borrar archivo
    2 bytes: número de archivos a recibir
    2 bytes: longitud de la ruta destino (pathlen)
    m bytes: ruta destino
    si instrucción = subir archivo
        4 bytes: longitud del archivo
        l bytes: datos del archivo
'''


# abre un nuevo socket para esperar peticiones de un cliente
# socket.AF_INET = IPv4 socket
# socket.SOCK_STREAM habilita el protocolo TCP
# with cierra automáticamente el socket después de salir
#   de su contexto
print('Starting server on port', PORT)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

            # se recibe 1 byte (8 bits) de tamaño de nombre de usuario;
            # el nombre de usuario no deberá superar los 2^8 - 1 bytes (256 bytes)
            userlen = conn.recv(1)[0]

            # "recv" devuelve un arreglo de bytes que se decodifica a "str"
            # para obtener el nombre de usuario utilizando la codificación
            # por defecto de python (UTF-8)
            username = conn.recv(userlen).decode()

            # se recibe 1 byte (8 bits) con el tipo de instrucción a realizar;
            # 1 = crear archivo
            # 2 = descargar archivo
            # 3 = borrar archivo
            # 4 = obtener archivos
            instr = conn.recv(1)[0]

            if instr == Instruction.GET:
                if not os.path.isdir(username):
                    out = "{}".encode()
                else:
                    tree = fs_tree(username)
                    out = json.dumps(tree).encode()
                filelen = len(out)
                # envía 4 bytes (32 bits) de tamaño del archivo;
                # el archivo a enviar no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
                conn.sendall(filelen.to_bytes(4, byteorder="big"))

                # envía bytes hasta alcanzar el final del archivo (EOF)
                byte_counter = 0
                while byte_counter < filelen:
                    rem = byte_counter + BUFFER_SIZE
                    data = out[byte_counter:rem if rem < filelen else filelen]
                    byte_counter += len(data)
                    delivered = conn.send(data)
                    # si "data" se envía incompleto, intenta enviar los bytes restantes
                    # para evitar perder información
                    while (delivered < len(data)):
                        rem = conn.send(data[delivered:])
                        delivered += rem
                    print("Sent", len(data),
                        "bytes (" + str(byte_counter * 100 // filelen) + "% completed)")
                print("Correcly sent json to client")
                print()
            else:

                # se reciben 2 bytes (16 bits) con el número de archivos;
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
                    relpath = os.path.join(username, relpath)

                    if instr == Instruction.UPLOAD:
                        dirname, basename = os.path.split(relpath)

                        if dirname and not os.path.exists(dirname):
                            pathlib.Path(dirname).mkdir(parents=True)
                            print("Created directory \"" + dirname + "\"")

                        if basename:
                            # se reciben 4 bytes (32 bits) de tamaño del archivo;
                            # el archivo a recibir no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
                            filelen = int.from_bytes(
                                conn.recv(4), byteorder="big")

                            print("Receiving file \"" + relpath +
                                  "\" of", filelen, "bytes")

                            # with cierra automáticamente el archivo después de salir de su contexto
                            with open(relpath, "wb") as f:

                                # escribe bytes en el archivo de salida hasta recibir el
                                # último byte
                                byte_counter = 0
                                while byte_counter < filelen:
                                    temp_data = conn.recv(BUFFER_SIZE if (
                                        rem := filelen - byte_counter) > BUFFER_SIZE else rem)
                                    byte_counter += len(temp_data)
                                    f.write(temp_data)

                                    print("Received", len(temp_data),
                                          "bytes ("
                                          + str(byte_counter * 100 // filelen)
                                          + "% completed)")
                            print("Wrote file \"" + relpath + "\"")
                            print()
                    elif instr == Instruction.DOWNLOAD:
                        if os.path.exists(relpath):
                            with open(relpath, 'rb') as f:
                                filelen = os.path.getsize(f.name)
                                print(
                                    f"Getting ready to send file \"{relpath}\" of {filelen} bytes")

                                # envía 4 bytes (32 bits) de tamaño del archivo;
                                # el archivo a enviar no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
                                conn.sendall(filelen.to_bytes(
                                    4, byteorder="big"))

                                # envía bytes hasta alcanzar el final del archivo (EOF)
                                byte_counter = 0
                                while byte_counter < filelen:
                                    data = f.read(BUFFER_SIZE)
                                    byte_counter += len(data)

                                    delivered = conn.send(data)

                                    # si "data" se envía incompleto, intenta enviar los bytes restantes
                                    # para evitar perder información
                                    while (delivered < len(data)):
                                        rem = conn.send(data[delivered:])
                                        delivered += rem

                                    print("Sent", len(data),
                                          "bytes (" + str(byte_counter * 100 // filelen) + "% completed)")
                                print("Correcly sent file \"" +
                                      relpath + "\" to client")
                                print()
                        else:
                            print(f"File \"{relpath}\" not found in server")
                            # envía 0s para indicar que el archivo no existe
                            s.sendall(bytes([0, 0, 0, 0]))

                    elif instr == Instruction.DELETE:
                        if os.path.exists(relpath):
                            if os.path.isdir(relpath):
                                print(
                                    f"Getting ready to delete directory \"{relpath}\"")

                                shutil.rmtree(relpath)

                                print("Correcly removed path \"" +
                                      relpath + "\" from server")
                                print()
                            else:
                                print(
                                    f"Getting ready to delete file \"{relpath}\"")

                                os.remove(relpath)

                                print("Correcly removed file \"" +
                                      relpath + "\" from server")
                                print()

                        else:
                            print(f"Path \"{relpath}\" not found in server")
                    else:
                        print(
                            f"Unknown instruction {instr} sent by client {addr}")
