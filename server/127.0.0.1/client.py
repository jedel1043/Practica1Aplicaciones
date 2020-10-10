from os.path import relpath
import socket
import sys
import os
from typing import overload

HOST = socket.gethostname()
PORT = 50007
BUFFER_SIZE = 4096

def sendfile(filepath, relpath):
    # abre un nuevo socket para conectarse con el servidor
    # socket.AF_INET = IPv4 socket
    # socket.SOCK_STREAM habilita enviar información particionada
    #   en arreglos de tamaño BUFFER_SIZE
    # "with" cierra el socket al salir de su contexto
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # abre el archivo con ruta especificada en el argumento de entrada 1
        # "with" cierra el archivo al salir de su contexto
        with open(filepath, 'rb') as f:
            pathlen = len(relpath)
            filelen = os.path.getsize(f.name)

            print("Getting ready to send file \"" + filepath
                + "\" of", filelen, "bytes")

            # se envían 2 bytes (16 bits) de tamaño de ruta del archivo;
            # la longitud de ruta no deberá superar los 2^16 - 1 bytes (65536 bytes)
            s.sendall(pathlen.to_bytes(2, byteorder="big"))

            # sendall() no acepta str como argumento, solamente arreglos de bytes,
            # por lo que la cadena "rel_path" se convierte a bytes
            # utilizando la codificación de python por defecto (UTF-8)
            print(relpath)
            s.sendall(relpath.encode())

            # se envían 4 bytes (32 bits) de tamaño del archivo;
            # el archivo a enviar no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
            s.sendall(filelen.to_bytes(4, byteorder="big"))

            # Envía bytes hasta alcanzar el final del archivo (EOF)
            byte_counter = 0
            while byte_counter < filelen:
                data = f.read(BUFFER_SIZE)
                byte_counter += len(data)

                deliv = s.send(data)

                # si "l" se envía incompleto, intenta enviar los bytes restantes
                # para evitar perder información
                while (deliv < len(data)):
                    rem = s.send(data[deliv:])
                    deliv += rem

                print("Sent", len(data),
                    "bytes (" + str(byte_counter * 100 // filelen) + "% completed)")
            print("Sent file \"" + filepath + "\" to server")
            print()
    

for arg in sys.argv[1:]:
    if os.path.isdir(arg):
        directory = os.path.realpath(arg)
        dirname = os.path.basename(directory)
        for root, dirs, files in os.walk(directory):
            for f in files:
                filepath = os.path.join(root, f)
                newpath = os.path.join(
                    dirname, os.path.relpath(filepath, start=directory))
                sendfile(filepath, newpath)
    elif os.path.isfile(arg):
        sendfile(arg, os.path.basename(arg))
    else:
        print("path not found")
