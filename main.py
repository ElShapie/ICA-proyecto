from getpass import getpass
from logging_config import configurar_logs


RUTA_LOG = configurar_logs()

import database
import security
import camera


# Permisos por rol: que roles SI pueden acceder a la camara
ROLES_CON_ACCESO_A_CAMARA = ["Administrador", "Operador"]


def crear_usuarios_de_prueba():
    """
    Crea la base de datos (si no existe) y la llena con 3 usuarios
    de prueba, uno por cada rol, SOLO si la tabla esta vacia.
    Esto sirve para poder correr las 8 pruebas sin tener que
    registrar usuarios a mano cada vez.
    """
    database.crear_tabla()

    usuarios_prueba = [
        # nombre, correo, rol, password_en_texto_plano, ip_camara
        ("admin", "admin@upy.edu.mx", "Administrador", "Admin123!", "192.168.1.50"),
        ("operador1", "operador1@upy.edu.mx", "Operador", "Operador123!", "192.168.1.51"),
        ("consulta1", "consulta1@upy.edu.mx", "Consulta", "Consulta123!", "192.168.1.52"),
        ("visitante1", "visitante@gmail.com", "Operador", "Visitante1!", "192.168.1.53")
    ]

    for nombre, correo, rol, password_plano, ip_camara in usuarios_prueba:
        if not database.usuario_existe(nombre):
            hash_password = security.hashear_password(password_plano)
            ip_cifrada = security.cifrar_texto(ip_camara)
            secreto_mfa = security.generar_secreto_mfa()
            secreto_mfa_cifrado = security.cifrar_texto(secreto_mfa)
            database.insertar_usuario(
                nombre, correo, rol, ip_cifrada, hash_password, secreto_mfa_cifrado
            )
            print(f"Usuario de prueba creado: {nombre} / {password_plano} (rol: {rol})")

    generar_qr_usuarios()


def generar_qr_usuarios():
    """Crea un QR de Google Authenticator para cada usuario de la base."""
    print("\nCodigos QR para vincular Google Authenticator:")
    for usuario in database.listar_usuarios():
        nombre = usuario[1]
        secreto_cifrado = usuario[6]

        # Completa automaticamente usuarios creados antes de agregar MFA.
        if not secreto_cifrado:
            secreto = security.generar_secreto_mfa()
            secreto_cifrado = security.cifrar_texto(secreto)
            database.actualizar_mfa_secret(nombre, secreto_cifrado)
        else:
            secreto = security.descifrar_texto(secreto_cifrado)

        ruta_qr = security.generar_qr_mfa(nombre, secreto)
        print(f"  {nombre}: {ruta_qr}")


def paso_1_2_autenticacion():
    """
    Modulos 2 y 3: pide usuario y contrasena, y valida contra
    el hash guardado en la base de datos.
    Regresa la tupla del usuario si todo es correcto, o None si no.
    """
    print("=== SISTEMA SEGURO ===")
    nombre_usuario = input("Usuario: ").strip()
    password_ingresada = getpass("Contrasena: ").strip()

    usuario = database.obtener_usuario_por_nombre(nombre_usuario)

    if usuario is None:
        print("\nAcceso denegado: usuario o contrasena incorrectos.")
        return None

    # usuario = (id, nombre, correo, rol, ip_camara_cifrada, password_hash, mfa_secret)
    hash_guardado = usuario[5]

    if not security.verificar_password(password_ingresada, hash_guardado):
        print("\nAcceso denegado: usuario o contrasena incorrectos.")
        return None

    print("\nAutenticacion exitosa (usuario y contrasena correctos).")
    print(f"[Demostracion de hashing] Hash guardado en la base de datos: {hash_guardado}")
    return usuario


def paso_3_dos_factores(usuario):
    """
    Modulo 4: valida el codigo TOTP generado por Google Authenticator.
    Regresa True si el codigo es correcto, False si no.
    """
    secreto_cifrado = usuario[6]
    if not secreto_cifrado:
        print("\nAcceso denegado: el usuario no tiene MFA configurado.")
        return False

    secreto = security.descifrar_texto(secreto_cifrado)
    print("\n--- AUTENTICACION MULTIFACTOR (MFA) ---")
    codigo_ingresado = getpass("Introduce el codigo de Google Authenticator: ").strip()

    if security.validar_codigo_mfa(secreto, codigo_ingresado):
        print("\nCodigo MFA correcto. Segundo factor validado.")
        return True
    else:
        print("\nAcceso denegado: codigo MFA incorrecto.")
        return False


def paso_4_control_de_rol(usuario):
    """
    Modulo 6: revisa si el rol del usuario tiene permiso para
    acceder a la camara.
    """
    rol = usuario[3]
    print(f"\nRol detectado: {rol}")

    if rol in ROLES_CON_ACCESO_A_CAMARA:
        print("Rol autorizado para acceder a la camara.")
        return True
    else:
        print("Acceso denegado: tu rol no tiene permiso para acceder a la camara.")
        return False


def paso_5_acceso_camara(usuario):
    """
    Modulo 7: descifra la IP de la camara guardada en la base de
    datos y abre la conexion/stream.
    """
    ip_cifrada = usuario[4]
    ip_descifrada = security.descifrar_texto(ip_cifrada)

    print(f"\n[Demostracion de cifrado] IP cifrada guardada en BD: {ip_cifrada}")
    print(f"[Demostracion de cifrado] IP descifrada: {ip_descifrada}")

    camera.conectar_camara(ip_descifrada)


def main():
    crear_usuarios_de_prueba()
    print()

    # Paso 1 y 2: usuario + contrasena
    usuario = paso_1_2_autenticacion()
    if usuario is None:
        return  # se detiene el flujo aqui: acceso denegado

    # Paso 3: 2FA
    if not paso_3_dos_factores(usuario):
        return  # se detiene el flujo aqui: acceso denegado

    # Paso 4: rol / permisos
    if not paso_4_control_de_rol(usuario):
        return  # se detiene el flujo aqui: acceso denegado

    # Paso 5: acceso a la camara IP
    paso_5_acceso_camara(usuario)


if __name__ == "__main__":
    main()
