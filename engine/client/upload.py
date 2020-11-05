import sys
import os
from typing import List

from operations import upload_files

# guarda todas las rutas relativas y absolutas
# de los archivos a enviar al servidor
paths = []

# obtenemos todos los argumentos del script
# excepto el nombre del mismo script
for arg in sys.argv[2::]:
    if os.path.isdir(arg):
        directory = os.path.realpath(arg)
        dirname = os.path.basename(directory)

        # se buscan recursivamente todos los archivos dentro del directorio
        for root, _, files in os.walk(directory):
            for f in files:
                # ruta absoluta para acceder al archivo desde el cliente
                filepath = os.path.join(root, f)

                # ruta relativa a partir del directorio a enviar
                newpath = os.path.join(
                    dirname, os.path.relpath(filepath, start=directory))
                paths.append((filepath, newpath))

    # si es un archivo, el servidor no crea una carpeta
    elif os.path.isfile(arg):
        paths.append((arg, os.path.basename(arg)))

    # ignora argumentos de entrada inválidos para
    # procesar todos los archivos posibles
    else:
        1
        # print("path not found")

# realiza el envío de los archivos
upload_files(sys.argv[1], paths)
print("finished")