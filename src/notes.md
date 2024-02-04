# Tras pruebas en el main.py, tanto en opencv como en picamera (y en frecuencias forzadas y no forzadas), en ambos los fps se cumplen a la tasa solicitada
# Aunque la latencia en opencv no es horrible, con la picamera se consigue un mejor resultado, casi nulo en retraso

# No es recomendable usar X11 Forwarding ya que por algún motivo hace que el bucle no pueda ser cerrado a muchos fps y introduce la latencia. Usando VNC no aparecen estos problemas (no le veo sentido ya que se comparte una imagen de menor tamaño por un lado frente a otro pero es así so...)

# si lo pensamos, la secuencia aparentemente lógica es: 
#   recoger imagen SPLIT-> cambiar fondo     -> JOIN -> SPLIT -> mostrar imagen procesada 
#                      |-> reconocer manos   ->|             |-> actuar según gesto reconocido

# no obstante, en una primera aproximación experimental, he visto que montarlo de esta forma (la cuál requiere de estar constantemente creando y matando hilos) no obtiene un buen rendimiento (tasa de cierre de bucle <10)
# podemos considerar procesar nuestros algoritmos en un pipeline, para que de esta forma sea más eficiente... metiendo una imagen de latencia, pero teniendo un output_rate mejor quizá...

# también se ha considerado realizar copia de la variable imagen original en lugar de pasar como parámetro directamente esta, ya que se tarda menos en copiar la imagen y justo después cerrar el semaforo que en pasarla como parametro, esperar a que la función devuelva y cerrar semáforo (bloquea otros hilos empeorando el funcionamiento)

# Los objetos creados para mediapipe o SelfiSegmentation deben ser creados como globales, ya que sino python no es capar de liberar la memoria que reservan (al ser librerías externas compiladas en C no depende del manager de Python...) y llega un punto donde el programa peta al superar el máximo de memoria que tiene permitido

# para evitar falsas detecciones de click, hay que restringir la orientación de la mano que se permite en la imagen para procesarlo como comando válido. La métrica más robusta que he podido probar es la del área de la palma de la mano normalizada con distancia 5-17 (invariante a rotación y a zoom)

# ---------------------------------------------------------------

# MEJORAS (feedback agl)
# - main.py: meter en una funcion auxiliar (o varias) el procesamiento de la imagen para detectar gestos (lineas 47-87 aprox). Creo que ensucian la claridad del programa que hasta ese punto está muy bien organizado. 

# ASOCIACION DE CLICK CON BOTON: 
# - Función auxiliar (button_selected): RECIBE coordenadas x,y del pointer (int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT)) cuando se detecte gesto de click. DEVUELVE boton asociado a esas coordenadas (realmente su denominación que se enviará como comando. ej 'A1') o None en caso de que el click se haya dado fuera de la zona permitida (marco). Debe comprobarse si las coordenadas del pointer recibidas están dentro del marco de la imagen, en ese caso entonces se asocia con el boton más cercano (en funcion a la distancia minima a su coordenada central), en caso contrario no se asocia a ningun boton, es como si no se hubiera dado el click. 

# ENVÍO DE COMANDOS DE CONTROL:
# - Funcion auxiliar (send_command_UDP): RECIBE el comando a enviar por UDP y lo hace. No devuelve nada. 

# FUNCIONES PLANTEADAS, diccionario para botones creado, constantes añadidas (a falta de pruebas y ajustes). NO AÑADO USO DE FUNCIONES EN PROGRAMA PRINCIPAL



# Face detection: Bounding box 
Haar cascades: Baja precisión y poco robusto, muy ligero computacionalmente
HOG+Linear: Carga computacional media, precisión buena, poca robustez
CNN: Alta carga computacional (requiere de GPU), alta precisión y alta robustez
Seleccionado HOG dada la aplicación en tiempo real
# Face recognition: Person validation
A más imágenes añadidas en el dataset, peor resultados se han conseguido, penalizando los frames conseguidos por segundo al aumentar el número de comparaciones a realizar por cada cara.
