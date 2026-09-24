"""
Aqui vive toda la logica de seguridad del proyecto:
  1. Hashing de contrasenas (bcrypt)
  2. Generacion y validacion de codigos TOTP para Google Authenticator
  3. Cifrado / descifrado de datos sensibles (Fernet)
  4. Generacion de codigos QR para vincular la aplicacion
"""

from pathlib import Path
import bcrypt
import pyotp
import qrcode
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
# 2) AUTENTICACION MULTIFACTOR TOTP
# ---------------------------------------------------------
EMISOR_MFA = "ICA Proyecto"


def generar_secreto_mfa() -> str:
    """Genera un secreto Base32 compatible con aplicaciones TOTP."""
    return pyotp.random_base32()


def crear_uri_mfa(nombre_usuario: str, secreto: str) -> str:
    """Crea la URI otpauth que Google Authenticator guarda al escanear el QR."""
    return pyotp.TOTP(secreto).provisioning_uri(
        name=nombre_usuario,
        issuer_name=EMISOR_MFA,
    )


def generar_qr_mfa(nombre_usuario: str, secreto: str, directorio="qr_mfa") -> str:
    """Genera el PNG de vinculacion y devuelve su ruta absoluta."""
    carpeta = Path(directorio)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre_usuario}_google_authenticator.png"
    imagen = qrcode.make(crear_uri_mfa(nombre_usuario, secreto))
    imagen.save(ruta)
    return str(ruta.resolve())


def validar_codigo_mfa(secreto: str, codigo_ingresado: str) -> bool:
    """Valida el TOTP actual, tolerando un intervalo de 30 segundos adyacente."""
    if not codigo_ingresado.isdigit() or len(codigo_ingresado) != 6:
        return False
    return pyotp.TOTP(secreto).verify(codigo_ingresado, valid_window=1)


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
