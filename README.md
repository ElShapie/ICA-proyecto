# Proyecto U1 - Sistema Seguro de Gestion de Identidades y Control de Acceso

## Que hace cada archivo

- **database.py** - crea y consulta la base de datos SQLite (`usuarios.db`).
- **security.py** - hashea contrasenas (bcrypt), genera/valida el codigo 2FA, y cifra/descifra datos (Fernet).
- **camera.py** - se conecta a la camara IP y muestra el video.
- **main.py** - une todo: pide usuario y contrasena, pide el codigo 2FA, revisa el rol, y si todo esta bien, abre la camara.

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

La primera vez que se ejecuta, el programa crea automaticamente la base de datos `usuarios.db` y tres usuarios de prueba (uno por cada rol).

## Usuarios de prueba

| Usuario | Contrasena | Rol | Acceso a camara |
|---|---|---|---|
| admin | Admin123! | Administrador | Si |
| operador1 | Operador123! | Operador | Si |
| consulta1 | Consulta123! | Consulta | No |

## Nota sobre la camara

Este proyecto solo debe usarse con una camara IP propia, o una que haya sido
expresamente autorizada para esta actividad. Si no cuentas con una camara IP
para la demostracion, el programa usa automaticamente la webcam de la
computadora como modo de simulacion, para poder mostrar que el flujo de
video funciona igual.

## Pruebas

Ver el archivo `pruebas.md` para el paso a paso de las 8 pruebas que pide
la rubrica del proyecto.
