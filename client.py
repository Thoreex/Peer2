import Pyro4
import os
import threading
import socket
import uuid
import json
import hashlib
import random

@Pyro4.expose
class Cliente(object):
    def demeFragmento(self, hashArchivo, ipRemoto):
        # Para pedir fragmento, si sabe que lo tiene
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.connect(tuple(ipRemoto))
        # while True:
        #     chunk = data.read(512000)
        #     if not chunk:
        #         break
        #     csock.sendall(chunk)
        return True
    def tomeFragmento(self, idArchivo, inicioFragmento):
        # Para devolver fragmento, iniciar socket
        return True
    def pingPong(self):
        return True

def imprimir_menu():
    print( 67 * "-")
    print( "1. Listar archivos")
    print( "2. Subir archivo")
    print( "3. Bajar archivo")
    print( "4. Salir")
    print( 67 * "-")

def md5(rutaArchivo):
    hash_md5 = hashlib.md5()
    with open(rutaArchivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def cicloCliente(daemon):
    daemon.requestLoop()

def main():
    # Inicia tracker
    trackerUri = input("Tracker URI: ").strip()
    trackerProxy = Pyro4.Proxy(trackerUri)

    # Inicia cliente
    clienteDaemon = Pyro4.Daemon(host=Pyro4.socketutil.getIpAddress(''))
    clienteUri = clienteDaemon.register(Cliente)
    print("Cliente URI: ", clienteUri)

    # Inicia ciclo de pyro del cliente
    clienteHilo = threading.Thread(target=cicloCliente, args=(clienteDaemon, ))
    clienteHilo.start()

    # Conectarse al tracker
    clienteNombre = uuid.uuid1()
    clienteDic = {
        "nombre": str(clienteNombre),
        "uri": str(clienteUri),
        "archivos": {}
        }
    clienteJson = json.dumps(clienteDic)

    trackerProxy.conectar(clienteJson)
    
    # Variables
    loop = True
    listaArchivos = {}
    misArchivos = {}

    # Menu
    while loop:
        imprimir_menu()
        choice = input("Escoge una opcion [1-4]: ")
        
        if choice == '1':
            listaDirectorio = json.loads(trackerProxy.listaDirectorio())
            for keyNodo in listaDirectorio.keys():
                for keyArchivo, valueArchivo in listaDirectorio[keyNodo]['archivos'].items():
                    if keyArchivo not in listaArchivos:
                        listaArchivos[keyArchivo] = valueArchivo
                        listaArchivos[keyArchivo]['nodos'] = [
                            keyNodo
                        ]
                    else:
                        listaArchivos[keyArchivo]['nodos'].append(keyNodo)
            print(listaArchivos)
        if choice == '2':
            rutaArchivo = input("Ingrese ruta del archivo: ")
            tamannoArchivo = os.path.getsize(rutaArchivo)
            nombreArchivo = os.path.basename(rutaArchivo)
            md5Archivo = md5(rutaArchivo)
            
            if md5Archivo in misArchivos:
                print('Ya subiste el archivo!')
                pass

            archivoDic = {
                "nombre": nombreArchivo,
                "tamanno": tamannoArchivo
            }
            
            archivoJson = json.dumps(archivoDic)

            trackerProxy.nuevoArchivo(str(clienteNombre), md5Archivo, archivoJson)

            misArchivos[md5Archivo] = archivoJson
        if choice == '3':
            archivoDescargar = input("Ingrese hash del archivo: ")
            if archivoDescargar in listaArchivos:
                indiceNodoRandom = random.randrange(0, len(listaArchivos[archivoDescargar]['nodos']))
                listaArchivos[archivoDescargar]['nodos'][indiceNodoRandom]
        if choice == '4':
            loop = False

if __name__== "__main__":
    main()