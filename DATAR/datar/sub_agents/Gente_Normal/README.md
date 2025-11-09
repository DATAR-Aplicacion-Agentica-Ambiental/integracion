# Gente (Re) Interpretativa

#### Hablemos sobre tu entorno y busquemos nuevas maneras de entenderlo, de sentirlo, de interpretarlo.
---

La invitación no es tanto a escribir ni a describir con palabras, es a sentir, a contar la historia de lo que sentimos a través de símbolos.

Aquí encontrarás un (a)gente que interpreta y reinterpreta sus conocimientos sobre el entorno para invitarte a explorar, a conocer, reconocer y a preguntarte sobre tu entorno: 
- ¿dónde has visto un bosque? 
- ¿qué hace que sea un bosque y no otra cosa? 
- ¿qué, o quiénes, viven allí? 
- ¿hay cosas, o gentes, que lo estén amenazando? 
- ¿cómo se ve un bosque joven? 
- ¿cómo se ve un bosque en potencia, un bosque que quizás aún no se ha desarrollado por completo? 
- ¿corre algún peligro?

¡Pero la invitación es con emojis! Cuando los veas, piensa cómo te hace sentir, cómo contarlo sin usar palabras...



### ¿Cómo funciona la Gente (Re) Interpretativa?

Mediante orquestación de agentes de LLM (Large Language Models):

1. Tu interacción la recibe `agente_interpretativa_secuencial`, que ejecutará dos agentes, uno tras otro.

2. El primer agente en ser ejecutado es `agente_bucle`, que a su vez ejecutará dos agentes (como una caja china) en un bucle: en este caso da 2 vueltas. 

3. En cada vuelta, un `agente_paralelizador` se encarga de dirigir tu interacción, en paralelo, a dos agentes (sí, de nuevo): `agente_interprete_emojis` y `agente_interprete_textual`.

4. Cada uno de estos dos últimos agentes genera una respuesta (el de emojis sólo con emojis, el de texto sólo con texto) que luego es recibida por un `agente_fusionador`, que se encarga de interpretar y fusionar las dos respuestas como una sola respuesta armónica y con sentido.

5. Se repiten los pasos 3 y 4 (para dar dos vueltas en el bucle). Y finalmente la última interpretación del `agente_fusionador` es recibida por `agente_re_interpretativa`, la cual se encarga de reinterpretar aquella respuesta y de modificarla para interpelarte de una mejor manera, invitándote a la exploración de tu entorno. Esta es la respuesta que terminas leyendo.  