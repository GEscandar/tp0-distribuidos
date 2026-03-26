# TP0: Docker + Comunicaciones + Concurrencia

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.


### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).

### Solucion

Se realizaron los siguientes cambios.

- En el generador `generar_compose.py`:
    - Se incorporan volúmenes Docker de tipo [Bind Mounts](https://docs.docker.com/engine/storage/bind-mounts/).
    - Se elimina la variable de entorno para el nivel de logs.
- En el Dockerfile del cliente, se saca el `COPY` del archivo de configuración.
- En el Makefile, se quita `--build` del target `docker-compose-up` para evitar reconstruir imagenes cada vez.