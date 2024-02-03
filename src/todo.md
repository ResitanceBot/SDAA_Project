1) Alojar funcionalidades de background removal y detección de mano abierta/cerrada al script main.py. (DONE)
2) Normalizar con distancia en horizontal entre 5 y 17 los umbrales de detección (DONE)
* Para el punto 2 se ha considerado finalmente una métrica distinta ya que no era lo suficientemente robusta
3) Interfaz gesto: 4 pegado a 9-10-11... significaría un click. El puntero sería el punto 8.(DONE)
* Experimentalmente cuadra mejor con 5
4) Gesto adicional: cambiar fondo de pantalla cuando se cierra la mano (DONE)
5) Definir cuadricula donde cada zona de píxeles son botones (utilizar marcos exteriores) y preparar 2 interfaces diferentes (botonera y barras de nivel de %, i.e valores analógicos)
5) Ajustar métricas para que no choquen entre sí (cuidado con mano abierta, valor por defecto)
5) UDP server en RPI que envíe comando y UDP client en windows que traduzca a comando de carla
6) Carla actuando en función del comando

Reparto:
-Álvaro: diseñar imágenes de fondo 640x480, UDP server y client
-Sergio: integrar en hilos (comodín de ayuda si el tema de hilos se empieza a complicar), añadir ideas de gestos

Ambos: Traducir posiciones y clicks en comandos. Actuar en Carla

1) Enclavamiento light on/off + background change (idea: pantalla bloqueo)
2) Conectar a Carla Server
3) Mejorar métrica invariente y/o filtro de perspectiva de la mano a la cámara + ajuste de umbrales a nueva idea

----
1) Pantalla de bloqueo con reconocimiento facial
2) Script Windows lanzador para elegir mundo, weather, dia/noche, trafico, control remoto RPI
----
RETOQUES FINALES
1) Quitar las librerias que no se usan o estén repetidas en main / helpers (comprobando que no peta el sistema)