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
      - mfa_secret     -> secreto TOTP cifrado para Google Authenticator
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
            password_hash TEXT NOT NULL,
            mfa_secret TEXT
        )
    """)

    # Migracion para bases creadas con versiones anteriores del proyecto.
    columnas = {fila[1] for fila in cursor.execute("PRAGMA table_info(usuarios)")}
    if "mfa_secret" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN mfa_secret TEXT")
    conexion.commit()
    conexion.close()


def insertar_usuario(nombre, correo, rol, ip_camara_cifrada, password_hash, mfa_secret_cifrado=None):
    """
    Inserta un usuario nuevo en la base de datos.
    Recibe el password_hash YA calculado (ver security.py) y la
    ip_camara YA cifrada (ver security.py): este modulo solo guarda,
    no cifra ni hashea nada.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, rol, ip_camara, password_hash, mfa_secret)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, correo, rol, ip_camara_cifrada, password_hash, mfa_secret_cifrado))
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
        SELECT id, nombre, correo, rol, ip_camara, password_hash, mfa_secret
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
    cursor.execute("SELECT id, nombre, correo, rol, ip_camara, password_hash, mfa_secret FROM usuarios")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def usuario_existe(nombre):
    """Regresa True si ya existe un usuario con ese nombre."""
    return obtener_usuario_por_nombre(nombre) is not None


def actualizar_mfa_secret(nombre, mfa_secret_cifrado):
    """Guarda el secreto MFA cifrado de un usuario existente."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE usuarios SET mfa_secret = ? WHERE nombre = ?",
        (mfa_secret_cifrado, nombre),
    )
    conexion.commit()
    conexion.close()
