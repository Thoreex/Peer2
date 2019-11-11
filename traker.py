import Pyro4
import json
import os
import math
from getpass import getpass
from builtins import str
import threading
#from datetime import datetim


listaNodos = {}

@Pyro4.expose
class GreetingMaker(object):
    def get_fortune(self,name):
        return "Hello, {0}. Here is your fortune message:\n" \
               "Behold the warranty -- the bold print giveth and the fine print taketh away.".format(name)
  
    def conectar(self, cadena):#los servidores/cleintes se conectan
        open('C:\\Users\\francisco\\Documents\\python_proyect\\nodoConexiones.txt', 'w').close()
        nuevoNodo = json.loads(cadena)
        listaNodos[nuevoNodo['nombre']] = nuevoNodo
        f = open('C:\\Users\\francisco\\Documents\\python_proyect\\nodoConexiones.txt','a')
        f.write((json.dumps(listaNodos)))
        f.close()
        #print(listaNodos)
        return "se ha conectado con exito"

    def nuevoArchivo(self, nombreNodo, nombreArchivo, infoArchivo):#los clientes/nodos actualizan la lista de archivos dipsonibles
        archivoNuevo =  json.loads(infoArchivo)
        tamano = int(archivoNuevo['tamanno'])
        archivoNuevo['trozos'] = int(math.ceil(tamano/500000))
        listaNodos[nombreNodo]['archivos'][nombreArchivo] = archivoNuevo      
        f = open('C:\\Users\\francisco\\Documents\\python_proyect\\nodoConexiones.txt','a')
        f.write((json.dumps(listaNodos)))
        f.close()  
        #print(listaNodos)
        return "se ha conectado con exito"

    def listaDirectorio(self):#devuleve la lista el directorio de Clientes/Servidores
        return json.dumps(listaNodos)
 

def cicloTraker(daemon):#iniciar servisor pyro
    daemon.requestLoop()


def actulizarListaNodos():
    for nodo in listaNodos:
        uri = nodo['uri']
    trackerProxy = Pyro4.Proxy(uri)
    resp = trackerProxy.pingpong()


def main():  #inicio de progrma
    control = False
    controlMenu = 0
    loginSeguro = False
    while controlMenu != 5:
        print( 67 * "-")
        print('digite 1 para iniciar Traker ')
        print('digite 2 para ver estadisticas ')
        print('iniciar ping pong 3')
        select = input('selecione  ')
        print( 67 * "-")

        if select == '1' :
            while control != True:
                f = open("C:\\Users\\francisco\\Documents\\python_proyect\\config.txt", "r")
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
                else:
                    print('Error de autentificación, Intente de Nuevo')   

            if loginSeguro:
                trakerDaemon = Pyro4.Daemon(host=Pyro4.socketutil.getIpAddress(''),port=22222)               # make a Pyro daemon
                uri = trakerDaemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
                print("Ready. Object uri =", uri)      # print the uri so we can use it in the client later
                #daemon.requestLoop() 
                trakerHilo = threading.Thread(target=cicloTraker, args=(trakerDaemon,))
                trakerHilo.start()


            
            if select == '3':
                #funcion para actualizar lso nodos
                actulizarListaNodos()


if __name__== "__main__":
    main()
  