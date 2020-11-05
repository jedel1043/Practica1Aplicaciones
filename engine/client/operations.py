import socket
import os
import pathlib
import sys
from typing import List, Tuple
from enum import IntEnum


class Instruction(IntEnum):
    UPLOAD = 1
    DOWNLOAD = 2
    DELETE = 3
    GET = 4


HOST = 'localhost'
PORT = 50007
BUFFER_SIZE = 4096  # buffer óptimo con tamaño pequeño y potencia de 2

''' Formato para el envío de archivos:
    1 byte: longitud del nombre de usuario
    n bytes: nombre de usuario
    1 byte:  subir archivo (1)
    2 bytes: número de archivos a recibir
    2 bytes: longitud de la ruta destino (pathlen)
    m bytes: ruta destino
    4 bytes: longitud del archivo
    l bytes: datos del archivo
'''

'''
    user: str - nombre de usuario que realiza la petición
    paths:   List[Tuple[rutas de los archivos a enviar, rutas que tendrán los archivos al recibirse en el servidor]]
'''


def upload_files(user: str, paths: List[Tuple[str, str]]):
    # abre un nuevo socket para conectarse con el servidor
    # socket.AF_INET = IPv4 socket
    # socket.SOCK_STREAM habilita el protocolo TCP
    # "with" cierra el socket al salir de su contexto
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # se envía 1 byte (8 bits) de tamaño de nombre de usuario;
        # el nombre de usuario no deberá superar los 2^8 - 1 bytes (256 bytes)
        s.sendall(bytes([len(user)]))

        # "se envía un arreglo de bytes que se decodifica a "str"
        # para obtener el nombre de usuario utilizando la codificación
        # por defecto de python (UTF-8)
        s.sendall(user.encode())

        # se envía 1 byte (8 bits) con el tipo de instrucción a realizar;
        # 1 = crear archivo
        s.sendall(bytes([Instruction.UPLOAD]))

        # se reciben 2 bytes (16 bits) con el número de archivos;
        # el número de archivos no deberá superar los 2^16 - 1 bytes (65536 bytes)
        # print(
        #     f"Sending to server the number of files to send \"{len(paths)}\"")
        s.sendall(len(paths).to_bytes(2, byteorder="big"))

        for filepath, relpath in paths:
            # abre el archivo con ruta "filepath"
            # "with" cierra el archivo al salir de su contexto
            with open(filepath, 'rb') as f:
                pathlen = len(relpath)
                filelen = os.path.getsize(f.name)

                # print("Getting ready to send file \"" + filepath
                #       + "\" of", filelen, "bytes")

                # envía 2 bytes (16 bits) de tamaño de ruta del archivo;
                # la longitud de ruta no deberá superar los 2^16 - 1 bytes (65536 bytes)
                s.sendall(pathlen.to_bytes(2, byteorder="big"))

                # sendall() no acepta str como argumento, solamente arreglos de bytes,
                # por lo que la cadena "relpath" se convierte a bytes
                # utilizando la codificación de python por defecto (UTF-8)
                s.sendall(relpath.encode())

                # envía 4 bytes (32 bits) de tamaño del archivo;
                # el archivo a enviar no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
                s.sendall(filelen.to_bytes(4, byteorder="big"))

                # envía bytes hasta alcanzar el final del archivo (EOF)
                byte_counter = 0
                while byte_counter < filelen:
                    data = f.read(BUFFER_SIZE)
                    byte_counter += len(data)

                    delivered = s.send(data)

                    # si "data" se envía incompleto, intenta enviar los bytes restantes
                    # para evitar perder información
                    while (delivered < len(data)):
                        rem = s.send(data[delivered:])
                        delivered += rem

                #     print("Sent", len(data),
                #           "bytes (" + str(byte_counter * 100 // filelen) + "% completed)")
                # print("Correcly sent file \"" + filepath + "\" to server")
                # print()


''' Formato para la descarga de archivos:
    1 byte:  longitud del nombre de usuario
    n bytes: nombre de usuario
    1 byte:  descargar archivo (2)
    2 bytes: número de archivos o carpetas a descargar
    2 bytes: longitud de la ruta destino (pathlen)
    m bytes: ruta destino
'''

'''
    user: str - nombre de usuario que realiza la petición
    paths:   List[Tuple[rutas de los archivos a borrar]]
'''


def download_files(user: str, paths: List[Tuple[str, str]]):
    # abre un nuevo socket para conectarse con el servidor
    # socket.AF_INET = IPv4 socket
    # socket.SOCK_STREAM habilita el protocolo TCP
    # "with" cierra el socket al salir de su contexto
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # se envía 1 byte (8 bits) de tamaño de nombre de usuario;
        # el nombre de usuario no deberá superar los 2^8 - 1 bytes (256 bytes)
        s.sendall(bytes([len(user)]))

        # se envía un arreglo de bytes que se decodifica a "str"
        # para obtener el nombre de usuario utilizando la codificación
        # por defecto de python (UTF-8)
        s.sendall(user.encode())

        # se envía 1 byte (8 bits) con el tipo de instrucción a realizar;
        s.sendall(bytes([Instruction.DOWNLOAD]))

        # se envían 2 bytes (16 bits) con el número de rutas;
        # el número de rutas no deberá superar los 2^16 - 1 bytes (65536 bytes)
        s.sendall(len(paths).to_bytes(2, byteorder="big"))

        for path in paths:
            pathlen = len(path)

            # envía 2 bytes (16 bits) de tamaño de ruta del archivo;
            # la longitud de ruta no deberá superar los 2^16 - 1 bytes (65536 bytes)
            s.sendall(pathlen.to_bytes(2, byteorder="big"))

            # sendall() no acepta str como argumento, solamente arreglos de bytes,
            # por lo que la cadena "relpath" se convierte a bytes
            # utilizando la codificación de python por defecto (UTF-8)
            s.sendall(path.encode())

            # se reciben 4 bytes (32 bits) de número de archivos;
            # el número de archivos a recibir no deberán superar los 2^32 - 1 bytes (approx. 4 GB)
            filenum = int.from_bytes(s.recv(4), byteorder="big")

            for _ in range(filenum):

                # se reciben 2 bytes (16 bits) de tamaño de ruta del archivo;
                # la longitud de ruta no deberá superar los 2^16 - 1 bytes (65536 bytes)
                pathlen = int.from_bytes(s.recv(2), byteorder="big")

                # "recv" devuelve un arreglo de bytes que se decodifica a "str"
                # para obtener la ruta del archivo utilizando la codificación
                # por defecto de python (UTF-8)
                relpath = s.recv(pathlen).decode()

                dirname, basename = os.path.split(relpath)
                print(dirname)
                print(basename)

                if dirname and not os.path.exists(dirname):
                    pathlib.Path(dirname).mkdir(parents=True)

                if basename:

                    # se reciben 4 bytes (32 bits) de tamaño del archivo;
                    # el archivo a recibir no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
                    filelen = int.from_bytes(s.recv(4), byteorder="big")

                    if filelen > 0:

                        # with cierra automáticamente el archivo después de salir de su contexto
                        with open(relpath, "wb") as f:

                            # escribe bytes en el archivo de salida hasta recibir el
                            # último byte
                            byte_counter = 0
                            while byte_counter < filelen:
                                temp_data = s.recv(BUFFER_SIZE if (
                                    rem := filelen - byte_counter) > BUFFER_SIZE else rem)
                                byte_counter += len(temp_data)
                                f.write(temp_data)
                    else:
                        1


''' Formato para el envío de archivos:
    1 byte: longitud del nombre de usuario
    n bytes: nombre de usuario
    1 byte:  borrar archivo (3)
    2 bytes: número de archivos a borrar
    2 bytes: longitud de la ruta destino (pathlen)
    m bytes: ruta destino
'''

'''
    user: str - nombre de usuario que realiza la petición
    paths:   List[Tuple[rutas de los archivos a borrar]]
'''


def delete_files(user: str, paths: List[Tuple[str, str]]):
    # abre un nuevo socket para conectarse con el servidor
    # socket.AF_INET = IPv4 socket
    # socket.SOCK_STREAM habilita el protocolo TCP
    # "with" cierra el socket al salir de su contexto
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # se envía 1 byte (8 bits) de tamaño de nombre de usuario;
        # el nombre de usuario no deberá superar los 2^8 - 1 bytes (256 bytes)
        s.sendall(bytes([len(user)]))

        # se envía un arreglo de bytes que se decodifica a "str"
        # para obtener el nombre de usuario utilizando la codificación
        # por defecto de python (UTF-8)
        s.sendall(user.encode())

        # se envía 1 byte (8 bits) con el tipo de instrucción a realizar;
        s.sendall(bytes([Instruction.DELETE]))

        # se envían 2 bytes (16 bits) con el número de archivos;
        # el número de archivos no deberá superar los 2^16 - 1 bytes (65536 bytes)
        # print(
        #     f"Sending to the server the number of paths to delete \"{len(paths)}\"")
        s.sendall(len(paths).to_bytes(2, byteorder="big"))

        for path in paths:
            pathlen = len(path)

            # print(f"Getting ready to delete file \"{path}\"")

            # envía 2 bytes (16 bits) de tamaño de ruta del archivo;
            # la longitud de ruta no deberá superar los 2^16 - 1 bytes (65536 bytes)
            s.sendall(pathlen.to_bytes(2, byteorder="big"))

            # sendall() no acepta str como argumento, solamente arreglos de bytes,
            # por lo que la cadena "relpath" se convierte a bytes
            # utilizando la codificación de python por defecto (UTF-8)
            s.sendall(path.encode())

            # print("Correcly deleted file \"" + path + "\" in server")
            # print()


''' Formato para la consulta de archivos:
    1 byte: longitud del nombre de usuario
    n bytes: nombre de usuario
'''

'''
    user: str - nombre de usuario que realiza la petición
'''


def get_files(user: str):
    # abre un nuevo socket para conectarse con el servidor
    # socket.AF_INET = IPv4 socket
    # socket.SOCK_STREAM habilita el protocolo TCP
    # "with" cierra el socket al salir de su contexto
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # se envía 1 byte (8 bits) de tamaño de nombre de usuario;
        # el nombre de usuario no deberá superar los 2^8 - 1 bytes (256 bytes)
        s.sendall(bytes([len(user)]))

        # se envía un arreglo de bytes que se decodifica a "str"
        # para obtener el nombre de usuario utilizando la codificación
        # por defecto de python (UTF-8)
        s.sendall(user.encode())

        # se envía 1 byte (8 bits) con el tipo de instrucción a realizar;
        s.sendall(bytes([Instruction.GET]))

        # se reciben 4 bytes (32 bits) de tamaño del json;
        # el json a recibir no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
        filelen = int.from_bytes(s.recv(4), byteorder="big")

        if filelen > 0:
            byte_counter = 0
            result = bytes([])
            while byte_counter < filelen:
                rem = filelen - byte_counter
                temp_data = s.recv(BUFFER_SIZE if rem > BUFFER_SIZE else rem)
                byte_counter += len(temp_data)
                result += temp_data
            print(result.decode())
        else:
            if filelen == 0:
                sys.stderr.write("error receiving json")
