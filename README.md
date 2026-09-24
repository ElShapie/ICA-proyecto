# Proyecto U1 - Sistema Seguro de Gestion de Identidades y Control de Acceso

## Que hace cada archivo

- **database.py** - crea y consulta la base de datos SQLite (`usuarios.db`).
- **security.py** - hashea contrasenas, genera/valida MFA TOTP, crea los QR y cifra/descifra datos.
- **camera.py** - se conecta a la camara IP y muestra el video.
- **main.py** - une todo: pide usuario y contrasena, valida el codigo MFA, revisa el rol, y si todo esta bien, abre la camara.

## Instalacion

1. Instala Python 3.10 o superior.
2. Dentro de esta carpeta, instala las dependencias:

```bash
pip install -r requirements.txt
```

## Como ejecutar

```bash
python main.py
```

La primera vez que se ejecuta, el programa crea automaticamente la base de datos `usuarios.db`, cuatro usuarios de prueba y un QR por usuario dentro de `qr_mfa/`.

## Vincular Google Authenticator

1. Ejecuta `python main.py` una vez para generar los QR.
2. Abre Google Authenticator y selecciona **Escanear un codigo QR**.
3. Escanea el PNG correspondiente al usuario dentro de `qr_mfa/`.
4. Inicia sesion e introduce el codigo de seis digitos mostrado por la app.

Los QR contienen el secreto MFA y no deben compartirse. Elimina sus archivos cuando termines de vincular los dispositivos; la carpeta esta excluida de Git.

## Logs de ejecucion

Cada vez que se inicia `main.py` se crea automaticamente un archivo dentro de
`logs/ejecucion_FECHA_HORA.log`. El archivo contiene la salida del programa,
los errores y las excepciones no controladas de esa sesion. Las contrasenas y
los codigos MFA se solicitan de forma oculta y no se escriben en el log. La
carpeta `logs/` esta excluida de Git.

## Usuarios de prueba

| Usuario | Contrasena | Rol | Acceso a camara |
|---|---|---|---|
| admin | Admin123! | Administrador | Si |
| operador1 | Operador123! | Operador | Si |
| consulta1 | Consulta123! | Consulta | No |
| visitante1 | Visitante1! | Operador | Si |

## Nota sobre la camara

Este proyecto solo debe usarse con una camara IP propia, o una que haya sido
expresamente autorizada para esta actividad. La URL configurada en
`URL_CAMARA_CONFIGURADA`, dentro de `camera.py`, tiene prioridad sobre la IP
guardada en la base. Debe apuntar al flujo de video que acepta OpenCV, no solo
a la pagina web de administracion de la camara. Si se deja vacia, el programa
utiliza la direccion cifrada correspondiente al usuario.

Para la camara IP Webcam configurada actualmente, el flujo MJPEG es:

```text
http://172.16.10.224:8080/video
```

La direccion base sin `/video` devuelve una pagina HTML y no puede abrirse
como transmision con OpenCV.

## Pruebas

Ver el archivo `pruebas.md` para el paso a paso de las 8 pruebas que pide
la rubrica del proyecto.
