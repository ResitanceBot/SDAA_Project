Estructura del sistema dividida en varios ficheros:

- src/main.py: Programa principal 
- src/helpers.py: Definición de funciones
- src/constants.py: Definición de constantes

- src/udp_com/udp_receiver_basic_example.py: Programa básico recepción de mensajes UDP (sistema a controlar)

- src/face_recognition/facial_req_picam.py: Script de testeo del modelo 
- src/face_recognition/headshots_picam.py: Script para la toma de imágenes para construcción de dataset
- src/face_recognition/train_model.py: Script para entrenamiento 
- src/face_recognition/encodings.pickle: Modelo generado para el reconocimiento facial

Para ejecutar el sistema debe lanzarse el fichero main.py (habilitar la funcionalidad completa de la interfaz de control por reconocimiento de imagen) y udp_receiver_basic_example.py (recibir mensajes enviados por UDP)

Gestos disponibles para interacción con panel de control:
  - CLICK: Dedo índice como puntero y pulgar para selección (llevar pulgar a base del dedo índice). Resto de dedos cerrados
  - BLOQUEAR PANTALLA: Puño completo cerrado
