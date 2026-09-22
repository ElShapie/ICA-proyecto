"""
Aqui vive toda la logica de seguridad del proyecto:
  1. Hashing de contrasenas (bcrypt)
  2. Generacion y validacion de codigo 2FA (secrets)
  3. Cifrado / descifrado de datos sensibles (Fernet)

Cada funcion hace UNA sola cosa, para que sea facil de explicar
en la presentacion.
"""

import secrets
import bcrypt
from cryptography.fernet import Fernet

# ---------------------------------------------------------
# 1) HASHING DE CONTRASENAS
# ---------------------------------------------------------
# bcrypt ya agrega un "salt" (valor aleatorio) automaticamente,
# por eso dos contrasenas iguales generan hashes distintos.


def hashear_password(password_texto_plano: str) -> str:
    """
    Convierte una contrasena en texto plano a un hash seguro.
    Este es el valor que se guarda en la base de datos, NUNCA
    la contrasena original.
    """
    password_bytes = password_texto_plano.encode("utf-8")
    hash_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Lo guardamos como texto (string) para que quepa en la columna TEXT
    return hash_bytes.decode("utf-8")


def verificar_password(password_texto_plano: str, hash_guardado: str) -> bool:
    """
    Compara la contrasena que el usuario acaba de escribir contra
    el hash que esta guardado en la base de datos.
    NO se descifra el hash: se vuelve a hashear el intento y se compara.
    """
    password_bytes = password_texto_plano.encode("utf-8")
    hash_bytes = hash_guardado.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)


# ---------------------------------------------------------
# 2) AUTENTICACION DE DOS FACTORES (2FA)
# ---------------------------------------------------------
# Usamos "secrets" (no "random") porque esta pensado para cosas
# de seguridad: sus numeros son mas dificiles de predecir.


def generar_codigo_2fa() -> str:
    """Genera un codigo aleatorio de 6 digitos, como texto (para no perder ceros a la izquierda)."""
    numero = secrets.randbelow(1_000_000)  # numero entre 0 y 999999
    return f"{numero:06d}"


def enviar_codigo_simulado(correo_destino: str, codigo: str):
    """
    SIMULA el envio del codigo por correo/SMS.
    En un sistema real, aqui se usaria una libreria como smtplib
    para mandar un correo de verdad, por ejemplo:

        import smtplib
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login("mi_correo@gmail.com", "mi_password_de_app")
        servidor.sendmail("mi_correo@gmail.com", correo_destino, mensaje)

    Para este prototipo, solo lo imprimimos en consola.
    """
    print(f"\n[SIMULACION DE ENVIO] Codigo de verificacion enviado a {correo_destino}: {codigo}\n")


def validar_codigo_2fa(codigo_generado: str, codigo_ingresado: str) -> bool:
    """Compara el codigo que genero el sistema contra el que escribio el usuario."""
    return codigo_generado == codigo_ingresado


# ---------------------------------------------------------
# 3) CIFRADO / DESCIFRADO (Fernet - cifrado simetrico)
# ---------------------------------------------------------
# "Simetrico" significa que se usa LA MISMA llave para cifrar y
# para descifrar. Por eso hay que guardar esa llave en un lugar
# seguro (aqui, en un archivo local llamado secret.key).

ARCHIVO_LLAVE = "secret.key"


def obtener_o_crear_llave() -> bytes:
    """
    Si ya existe un archivo secret.key, lo reutiliza (para poder
    descifrar datos guardados en ejecuciones anteriores).
    Si no existe, genera una llave nueva y la guarda.
    """
    try:
        with open(ARCHIVO_LLAVE, "rb") as archivo:
            return archivo.read()
    except FileNotFoundError:
        llave_nueva = Fernet.generate_key()
        with open(ARCHIVO_LLAVE, "wb") as archivo:
            archivo.write(llave_nueva)
        return llave_nueva


def cifrar_texto(texto_original: str) -> str:
    """Cifra un texto (por ejemplo, una IP de camara) y regresa el resultado como texto."""
    llave = obtener_o_crear_llave()
    f = Fernet(llave)
    texto_cifrado_bytes = f.encrypt(texto_original.encode("utf-8"))
    return texto_cifrado_bytes.decode("utf-8")


def descifrar_texto(texto_cifrado: str) -> str:
    """Descifra un texto que fue cifrado con cifrar_texto()."""
    llave = obtener_o_crear_llave()
    f = Fernet(llave)
    texto_original_bytes = f.decrypt(texto_cifrado.encode("utf-8"))
    return texto_original_bytes.decode("utf-8")
