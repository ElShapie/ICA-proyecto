import cv2

def conectar_camara(ip_camara: str):
   
    print(f"\nConectando a la camara IP en: {ip_camara} ...")

    # --- Intento de conexion "real" a una camara IP ---
    # Descomenta y ajusta esta linea si tienes una camara IP real:
    # url_stream = f"rtsp://usuario:password@{ip_camara}:554/stream1"
    # captura = cv2.VideoCapture(url_stream)

    captura = cv2.VideoCapture(ip_camara)

    if not captura.isOpened():
        print("No se pudo conectar a la camara IP indicada.")
        print("Usando la webcam local como MODO SIMULADO para la demostracion...")
        captura = cv2.VideoCapture(0)

    if not captura.isOpened():
        print("No se encontro ninguna camara disponible (ni IP ni webcam local).")
        return

    print("Conexion exitosa. Presiona 'q' en la ventana de video para salir.\n")

    while True:
        exito, frame = captura.read()
        if not exito:
            print("Se perdio la senal de la camara.")
            break

        cv2.imshow("Camara IP - Acceso autorizado", frame)

        # Si el usuario presiona 'q', se cierra la ventana
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    captura.release()
    cv2.destroyAllWindows()
