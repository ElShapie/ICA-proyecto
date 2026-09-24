import cv2


# URL configurada por el usuario. Puede ser HTTP, HTTPS o RTSP.
URL_CAMARA_CONFIGURADA = "http://172.16.10.224:8080/video"


def _normalizar_url_camara(direccion: str) -> str:
    """Conserva URLs completas y convierte una IP simple en una URL RTSP."""
    direccion = direccion.strip()
    if direccion.startswith(("http://", "https://", "rtsp://", "rtmp://")):
        return direccion
    return f"rtsp://{direccion}:554/stream1"


def conectar_camara(ip_camara: str):
    # La URL configurada tiene prioridad. Si se deja vacia, se usa la direccion
    # cifrada que llega desde la base de datos.
    direccion = URL_CAMARA_CONFIGURADA or ip_camara
    url_stream = _normalizar_url_camara(direccion)

    print(f"\nConectando a la camara IP en: {url_stream} ...")
    captura = cv2.VideoCapture(url_stream, cv2.CAP_FFMPEG)

    if not captura.isOpened():
        print("No se pudo abrir la transmision de la camara IP.")
        print("Verifica que la URL sea el endpoint de video y que la camara sea accesible.")
        captura.release()
        return

    print("Conexion exitosa. Presiona 'q' en la ventana de video para salir.\n")

    try:
        while True:
            exito, frame = captura.read()
            if not exito:
                print("Se perdio la senal de la camara.")
                break

            cv2.imshow("Camara IP - Acceso autorizado", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        captura.release()
        cv2.destroyAllWindows()
