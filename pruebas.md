# Guia de pruebas obligatorias

Ejecuta `python main.py` para cada prueba. Toma una captura de pantalla de
la consola en cada caso; esas capturas son las evidencias que pide el
proyecto.

1. **Usuario valido**
   Usuario: `admin` / Contrasena: `Admin123!` + codigo 2FA correcto.
   Resultado esperado: "Autenticacion exitosa".

2. **Contrasena incorrecta**
   Usuario: `admin` / Contrasena: `password_mala`.
   Resultado esperado: "Acceso denegado: usuario o contrasena incorrectos."

3. **Codigo 2FA correcto**
   Login valido, y cuando el programa imprima el codigo en consola,
   escribe exactamente ese mismo codigo.
   Resultado esperado: "Codigo de verificacion correcto."

4. **Codigo 2FA incorrecto**
   Login valido, pero escribe un codigo distinto al mostrado (por ejemplo `000000`).
   Resultado esperado: "Acceso denegado: codigo de verificacion incorrecto."

5. **Hash**
   Despues de un login exitoso, el programa imprime automaticamente el
   hash guardado en la base de datos (linea "[Demostracion de hashing]").
   Tambien puedes abrir `usuarios.db` con una herramienta como
   "DB Browser for SQLite" y ver que la columna `password_hash` no
   contiene la contrasena en texto plano.

6. **Cifrado**
   Al llegar al ultimo paso (acceso a camara), el programa imprime la IP
   cifrada guardada en la base de datos y la IP ya descifrada
   (lineas "[Demostracion de cifrado]").

7. **Control de roles**
   Usuario: `consulta1` / Contrasena: `Consulta123!` + codigo 2FA correcto.
   Resultado esperado: pasa el login y el 2FA, pero al llegar al rol,
   el programa responde "Acceso denegado: tu rol no tiene permiso...".

8. **Acceso autorizado**
   Usuario: `admin` u `operador1`, con contrasena y codigo 2FA correctos.
   Resultado esperado: el programa llega hasta "Conectando a la camara IP..."
   y abre la ventana de video.
