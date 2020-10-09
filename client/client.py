import socket
import sys
import os

HOST = socket.gethostname()
PORT = 50007
BUFFER_SIZE = 4096

# abre un nuevo socket para conectarse con el servidor
# socket.AF_INET = IPv4 socket
# socket.SOCK_STREAM habilita enviar información particionada
#   en arreglos de tamaño BUFFER_SIZE
# "with" cierra el socket después al salir de su contexto
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # abre el archivo con ruta especificada en el argumento de entrada 1
    # "with" cierra el archivo al salir de su contexto
    # TODO: implementar envío de multiarchivos
    with open(sys.argv[1], 'rb') as f:

        abs_path = os.path.abspath(f.name)
        rel_path = os.path.relpath(abs_path)
        file_len = os.path.getsize(f.name)

        print("Getting ready to send file \"" + rel_path
              + "\" of", file_len, "bytes")

        # sendall() no acepta str como argumento, solamente arreglos de bytes,
        # por lo que la cadena "rel_path" se convierte a bytes
        # utilizando la codificación de python por defecto (UTF-8)
        s.sendall(rel_path.encode())

        # sólo se envían 4 bytes (32 bits) de tamaño del archivo;
        # el archivo a enviar no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
        s.sendall(file_len.to_bytes(4, byteorder="big"))

        # Envía bytes hasta alcanzar el final del archivo (EOF)
        byte_counter = 0
        while byte_counter < file_len:
            data = f.read(BUFFER_SIZE)
            byte_counter += len(data)
            
            deliv = s.send(data)

            # si "l" se envía incompleto, intenta enviar los bytes restantes 
            # para evitar perder información
            while (deliv < len(data)):
                rem = s.send(data[deliv:])
                deliv += rem

            print("Received", len(data),
                  "bytes (" + str(byte_counter * 100 // file_len) + "% completed)")
        print()
        print("Sent file \"" + rel_path + "\" to server")
