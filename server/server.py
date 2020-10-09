# Echo server program
import socket

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
    print('Awaiting file')

    # s.accept() espera alguna petición para
    # continuar con la ejecución del programa
    # conn: socket con la conexión entre el cliente
    #       y el servidor
    # addr: dirección ip donde se originó la conexión
    conn, addr = s.accept()

    # with cierra la conexión al salir de su contexto
    with conn:
        print('Connected by', addr)

        # "recv" devuelve un arreglo de bytes que tenemos que convertir a str
        # para poder obtener el nombre del archivo, por lo que se decodifica
        # utilizando la codificación por defecto de python (UTF-8)
        rel_path = conn.recv(BUFFER_SIZE).decode()

        # sólo se reciben 4 bytes (32 bits) de tamaño del archivo;
        # el archivo a recibir no deberá superar los 2^32 - 1 bytes (approx. 4 GB)
        file_size = int.from_bytes(conn.recv(4), byteorder="big")

        print("Receiving file \"" + rel_path + "\" of", file_size, "bytes")

        # with cierra automáticamente el archivo después de salir de su contexto
        with open(rel_path, "wb") as f:

            # escribe bytes en el archivo de salida hasta recibir el
            # último byte
            byte_counter = 0
            while byte_counter < file_size:
                temp_data = conn.recv(BUFFER_SIZE)
                byte_counter += len(temp_data)
                f.write(temp_data)
                
                print("Received", len(temp_data),
                      "bytes ("
                      + str(byte_counter * 100 // file_size)
                      + "% completed)")
        print()
        print("Wrote file \"" + rel_path + "\" to pwd")
