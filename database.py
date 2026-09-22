"""
Este modulo se encarga de TODO lo relacionado con la base de datos SQLite.
No sabe nada de hashing, 2FA ni camaras: solo guarda y consulta datos.
"""

import sqlite3

DB_NAME = "usuarios.db"


def obtener_conexion():
    """
    Abre (o crea, si no existe) el archivo usuarios.db y devuelve
    una conexion que podemos usar para hacer consultas SQL.
    """
    conexion = sqlite3.connect(DB_NAME)
    return conexion


def crear_tabla():
    """
    Crea la tabla 'usuarios' si todavia no existe.
    Columnas minimas que pide el proyecto:
      - id             -> identificador unico
      - nombre         -> nombre del usuario
      - correo         -> correo (lo usamos para 'simular' el envio del 2FA)
      - rol            -> Administrador / Operador / Consulta
      - ip_camara      -> direccion IP de la camara asignada (se guarda cifrada)
      - password_hash  -> hash de la contrasena (NUNCA la contrasena real)
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            rol TEXT NOT NULL,
            ip_camara TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()


def insertar_usuario(nombre, correo, rol, ip_camara_cifrada, password_hash):
    """
    Inserta un usuario nuevo en la base de datos.
    Recibe el password_hash YA calculado (ver security.py) y la
    ip_camara YA cifrada (ver security.py): este modulo solo guarda,
    no cifra ni hashea nada.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, rol, ip_camara, password_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, correo, rol, ip_camara_cifrada, password_hash))
    conexion.commit()
    conexion.close()


def obtener_usuario_por_nombre(nombre):
    """
    Busca un usuario por su nombre de usuario.
    Devuelve una tupla con todos los datos, o None si no existe.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre, correo, rol, ip_camara, password_hash
        FROM usuarios
        WHERE nombre = ?
    """, (nombre,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado


def listar_usuarios():
    """
    Devuelve todos los usuarios registrados.
    Util para mostrar evidencias (por ejemplo, ver los hashes guardados).
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, correo, rol, ip_camara, password_hash FROM usuarios")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def usuario_existe(nombre):
    """Regresa True si ya existe un usuario con ese nombre."""
    return obtener_usuario_por_nombre(nombre) is not None
