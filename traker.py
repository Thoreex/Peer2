import Pyro4
import json
import os
import math
from getpass import getpass
from builtins import str
import threading
import time
#from datetime import datetim


listaNodos = {}
primerNodo = False

@Pyro4.expose
class GreetingMaker(object):
    def get_fortune(self,name):
        return "Hello, {0}. Here is your fortune message:\n" \
               "Behold the warranty -- the bold print giveth and the fine print taketh away.".format(name)
  
    def conectar(self, cadena):#los servidores/cleintes se conectan
        open('nodoConexiones.json', 'w').close()
        nuevoNodo = json.loads(cadena)
        listaNodos[nuevoNodo['nombre']] = nuevoNodo
        f = open('nodoConexiones.json','a')
        f.write((json.dumps(listaNodos)))
        f.close()
        #print(listaNodos)
        return "se ha conectado con exito"

    def nuevoArchivo(self, nombreNodo, nombreArchivo, infoArchivo):#los clientes/nodos actualizan la lista de archivos dipsonibles
        archivoNuevo =  json.loads(infoArchivo)
        tamano = int(archivoNuevo['tamanno'])
        archivoNuevo['trozos'] = int(math.ceil(tamano/500000))
        listaNodos[nombreNodo]['archivos'][nombreArchivo] = archivoNuevo 
        open('nodoConexiones.json', 'w').close()     
        f = open('nodoConexiones.json','a')
        f.write((json.dumps(listaNodos)))
        f.close()  
        #print(listaNodos)
        return archivoNuevo['trozos']

    def listaDirectorio(self):#devuleve la lista el directorio de Clientes/Servidores
        return json.dumps(listaNodos)
 

def cicloTraker(daemon):#iniciar servisor pyro
    daemon.requestLoop()


def actulizarListaNodos():
    while True:
        time.sleep(5)
        f = open('nodoConexiones.json','r')
        nodosAux = f.read()
        f.close() 
        if nodosAux != '""' and nodosAux and nodosAux != '':
            nodosAux = json.loads(nodosAux)
            for nodo in list(nodosAux):
                uri = nodosAux[nodo]['uri']
                try: 
                    trackerProxy = Pyro4.Proxy(uri)
                    resp = trackerProxy.pingPong()
                    #print(resp)
                except:
                    nodoData = nodosAux
                    nodoData.pop(nodo)
                    open('nodoConexiones.json', 'w').close()
                    f = open('nodoConexiones.json','a')
                    f.write((json.dumps(nodoData)))
                    f.close()  

def main():  #inicio de progrma
    control = False
    controlMenu = 0
    loginSeguro = False
    while controlMenu != 5:
        print( 67 * "-")
        print('digite 1 para iniciar Traker ')
        print('digite 2 para ver estadisticas ')
        select = input('selecione  ')
        print( 67 * "-")

        if select == '1' :
            while control != True:
                f = open("config.json", "r")
                data = f.read()
                datos = json.loads(data)
                print( 67 * "-")
                userName = input('Digite el noombre de usuario:  ')
                passWord = getpass('Digite la contraseña:  ')
                print( 67 * "-")
                if userName == datos['usuario'] and passWord == datos['pass']:
                    control = True
                    loginSeguro = True
                    print('Exito Login Seguro')  
                    trakerDaemon = Pyro4.Daemon(host=Pyro4.socketutil.getIpAddress(''),port=22222)               # make a Pyro daemon
                    uri = trakerDaemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
                    print("Ready. Object uri =", uri)      # print the uri so we can use it in the client later
                    #daemon.requestLoop() 
                    trakerHilo = threading.Thread(target=cicloTraker, args=(trakerDaemon,))
                    trakerHilo.start()
                    actualizarHilo = threading.Thread(target=actulizarListaNodos, args=())
                    actualizarHilo.start() 
                else:
                    print('Error de autentificación, Intente de Nuevo')    

        if select == '2':
            print( 67 * "-")
            f = open('nodoConexiones.json','r')
            nodosAux = f.read()
            f.close()
            nodosAux = json.loads(nodosAux)
            print('Numero de Nodos Conectados')
            numNodos = 0
            for nodo in list(nodosAux):
                print('Nombre de Nodo:  ' + nodo)
                for arc in list(nodosAux[nodo]['archivos']):
                     print('Nombre de Archivo disponible:  ' + arc)
                numNodos += 1
                print( 67 * "-")
            print('Numero de Nodos Conectados: ' + str(numNodos))



if __name__== "__main__":
    main()
  