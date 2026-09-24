"""Registro de la salida de cada ejecucion del programa."""

import atexit
import sys
import traceback
from datetime import datetime
from pathlib import Path


class SalidaDuplicada:
    """Escribe simultaneamente en la terminal y en el archivo de log."""

    def __init__(self, terminal, archivo):
        self.terminal = terminal
        self.archivo = archivo

    def write(self, texto):
        self.terminal.write(texto)
        self.archivo.write(texto)
        self.archivo.flush()
        return len(texto)

    def flush(self):
        self.terminal.flush()
        self.archivo.flush()

    def isatty(self):
        return self.terminal.isatty()

    def fileno(self):
        return self.terminal.fileno()

    @property
    def encoding(self):
        return self.terminal.encoding


def configurar_logs(directorio="logs") -> str:
    """Duplica stdout/stderr en un archivo distinto para cada ejecucion."""
    carpeta = Path(directorio)
    if not carpeta.is_absolute():
        carpeta = Path(__file__).resolve().parent / carpeta
    carpeta.mkdir(parents=True, exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    ruta = (carpeta / f"ejecucion_{marca_tiempo}.log").resolve()
    archivo = ruta.open("a", encoding="utf-8", buffering=1)

    stdout_original = sys.stdout
    stderr_original = sys.stderr
    stdout_duplicada = SalidaDuplicada(stdout_original, archivo)
    stderr_duplicada = SalidaDuplicada(stderr_original, archivo)
    sys.stdout = stdout_duplicada
    sys.stderr = stderr_duplicada

    def registrar_excepcion(tipo, valor, traza):
        if issubclass(tipo, KeyboardInterrupt):
            sys.__excepthook__(tipo, valor, traza)
            return
        print("\n[ERROR NO CONTROLADO]", file=sys.stderr)
        traceback.print_exception(tipo, valor, traza, file=sys.stderr)

    sys.excepthook = registrar_excepcion

    def cerrar_log():
        try:
            stdout_duplicada.flush()
            stderr_duplicada.flush()
            if sys.stdout is stdout_duplicada:
                sys.stdout = stdout_original
            if sys.stderr is stderr_duplicada:
                sys.stderr = stderr_original
            archivo.flush()
            archivo.close()
        except Exception:
            pass

    atexit.register(cerrar_log)
    print(f"[LOG] Registro de esta ejecucion: {ruta}")
    return str(ruta)
