# Tras pruebas en el main.py, tanto en opencv como en picamera (y en frecuencias forzadas y no forzadas), en ambos los fps se cumplen a la tasa solicitada
# Aunque la latencia en opencv no es horrible, con la picamera se consigue un mejor resultado, casi nulo en retraso

# No es recomendable usar X11 Forwarding ya que por algún motivo hace que el bucle no pueda ser cerrado a muchos fps y introduce la latencia. Usando VNC no aparecen estos problemas (no le veo sentido ya que se comparte una imagen de menor tamaño por un lado frente a otro pero es así so...)

# si lo pensamos, la secuencia aparentemente lógica es: 
#   recoger imagen SPLIT-> cambiar fondo     -> JOIN -> SPLIT -> mostrar imagen procesada 
#                      |-> reconocer manos   ->|             |-> actuar según gesto reconocido

# no obstante, en una primera aproximación experimental, he visto que montarlo de esta forma (la cuál requiere de estar constantemente creando y matando hilos) no obtiene un buen rendimiento (tasa de cierre de bucle <10)
# podemos considerar procesar nuestros algoritmos en un pipeline, para que de esta forma sea más eficiente... metiendo una imagen de latencia, pero teniendo un output_rate mejor quizá...

# también se ha considerado realizar copia de la variable imagen original en lugar de pasar como parámetro directamente esta, ya que se tarda menos en copiar la imagen y justo después cerrar el semaforo que en pasarla como parametro, esperar a que la función devuelva y cerrar semáforo (bloquea otros hilos empeorando el funcionamiento)