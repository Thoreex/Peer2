import Pyro4
import os
import threading
import socket
import uuid
import json
import hashlib
import random
import math

@Pyro4.expose
class Cliente(object):
    # Para pedir archivo, si sabe que lo tiene
    def handshake(self, hashArchivo):
        # Comprobar si tiene el archivo para compartir
        if hashArchivo not in misArchivos:
            print('No tienes el archivo!')
            return None
        
        # Abrir socket
        socketArchivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketArchivo.bind((Pyro4.socketutil.getIpAddress(''), 0))

        # Info del socket
        ipSocket, puertoSocket = socketArchivo.getsockname()
        socketDic = {
            "ip": ipSocket,
            "puerto": puertoSocket
        }
        socketJson = json.dumps(socketDic)
        
        transferenciaHilo = threading.Thread(target=transferencia, args=(socketArchivo, misArchivos, hashArchivo, ))
        transferenciaHilo.start()

        return socketJson
    # Para que el tracker compruebe el estado del cliente
    def pingPong(self):
        return True

def transferencia(socketArchivo, misArchivos, hashArchivo):
    # Abrir archivo
    streamArchivo = open(misArchivos[hashArchivo]['ruta'], "rb")

    # Escuchar en socket
    socketArchivo.listen()
    connArchivo, _ = socketArchivo.accept()

    tamannoTrozo = math.ceil(misArchivos[hashArchivo]['tamanno'] / misArchivos[hashArchivo]['trozos'])
    while True:
        trozoArchivo = streamArchivo.read(tamannoTrozo)
        if not trozoArchivo:
            break
        connArchivo.sendall(trozoArchivo)
    
    streamArchivo.close()
    connArchivo.close()

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

    # Menu
    loopMenu = True
    while loopMenu:
        # Interfaz menu
        print( 67 * "-")
        print( "1. Listar archivos")
        print( "2. Subir archivo")
        print( "3. Bajar archivo")
        print( "4. Salir")
        print( 67 * "-")

        # Opcion a escoger
        choice = input("Escoge una opcion [1-4]: ")
        
        # Siempre bajar lista de archivos antes de realizar una accion
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

        # Segun opcion escogida
        if choice == '1':
            print(listaArchivos)
        if choice == '2':
            rutaArchivo = input("Ingrese ruta del archivo: ")

            # Informacion del archivo
            tamannoArchivo = os.path.getsize(rutaArchivo)
            nombreArchivo = os.path.basename(rutaArchivo)
            hashArchivo = md5(rutaArchivo)
            
            # No subir el archivo dos veces
            if hashArchivo in misArchivos:
                print('Ya subiste el archivo!')
                pass

            # Enviar informacion del archivo al tracker
            archivoDic = {
                "nombre": nombreArchivo,
                "tamanno": tamannoArchivo
            }
            archivoJson = json.dumps(archivoDic)
            archivoTrozos = trackerProxy.nuevoArchivo(str(clienteNombre), hashArchivo, archivoJson)

            # Guardar en una lista de mis archivos
            archivoLocalDic = {
                "nombre": nombreArchivo,
                "tamanno": tamannoArchivo,
                "ruta": rutaArchivo,
                "trozos": archivoTrozos
            }
            misArchivos[hashArchivo] = archivoLocalDic
        if choice == '3':
            hashArchivo = input("Ingrese hash del archivo: ")

            # Comprobar que no tenga ya ese archivo
            if hashArchivo in misArchivos:
                print('Ya tienes el archivo!')
                pass

            # Comprobar que exista en la lista archivos descargada del tracker
            if hashArchivo not in listaArchivos:
                print('No existe el archivo!')
                pass

            # Inicia handshake
            indiceNodoRandom = random.randrange(0, len(listaArchivos[hashArchivo]['nodos']))
            descargaProxy = Pyro4.Proxy(listaDirectorio[listaArchivos[hashArchivo]['nodos'][indiceNodoRandom]]['uri'])
            respuestaHandshake = descargaProxy.handshake(hashArchivo)

            if not respuestaHandshake:
                print('No se pudo realizar la descarga')
                pass

            # Socket a partir de info retornada
            socketDic = json.loads(respuestaHandshake)

            socketArchivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketArchivo.connect((socketDic['ip'], socketDic['puerto']))

            # Se inicia el archivo
            streamArchivo = open(listaArchivos[hashArchivo]['nombre'],'wb')

            # Se obtiene por socket el archivo
            tamannoTrozo = math.ceil(listaArchivos[hashArchivo]['tamanno'] / listaArchivos[hashArchivo]['trozos'])
            while True:
                trozoArchivo = socketArchivo.recv(tamannoTrozo)
                if not trozoArchivo:
                    break
                streamArchivo.write(trozoArchivo)

            # Se cierra el archivo y socket
            streamArchivo.close()
            socketArchivo.close()
        if choice == '4':
            loopMenu = False

if __name__== "__main__":
    # Variables globales
    listaDirectorio = {}
    listaArchivos = {}
    misArchivos = {}
    
    # Inicio de aplicacion
    main()