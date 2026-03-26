# TP0: Docker + Comunicaciones + Concurrencia

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).`

### Solucion

- Como se que ejercicios futuros pediran la implementacion del manejo concurrente de las conexiones, preferi implementarlo aqui en primera instancia, para solo tener que iterar sobre este diseño en vez de tener que reimplementar todo. Con respecto a las limitaciones del paralelismo en Python debido al Global Interpreter Lock, a partir de la versión 3.13 del lenguaje, gracias al [PEP 703](https://peps.python.org/pep-0703/) existe la posibilidad de deshabilitar el GIL para habilitar el paralelismo con threads; este modo de operación se denomina `free-threaded mode`.
- Se agrega la funcion `exit` en el Server para hacer el cierre de todos los recursos utilizados.
- Se agrega la funcion `sig_handler` en el Server para manejar las signals `SIGINT` y `SIGTERM`. Ante cualquiera de ellas se invoca a `exit`.
- Se agrega el handler para la señal SIGTERM en la función NewClient que construye el objeto Client.
- Se utiliza un flag para detener el bucle principal del cliente.