import turtle

# Inicializar la ventana de Turtle
screen = turtle.Screen()
screen.setup(width=800, height=600)
screen.bgcolor("lightgray")
screen.tracer(0) # Desactivar actualizaciones automáticas para un dibujo más rápido

t = turtle.Turtle()
t.speed(0) # Velocidad máxima
t.penup()

# Color del agua y el suelo
WATER_COLOR = "#0077be"  # Azul profundo para el agua
LAND_COLOR = "#5a8c5a"   # Verde musgo para el suelo húmedo
VEGETATION_COLOR = "#336633" # Verde oscuro para la vegetación
SKY_COLOR = "#87ceeb"    # Azul cielo para el horizonte
SUN_COLOR = "#ffd700"    # Amarillo para el sol o la luz

# --- Dibujar el cielo y el horizonte (Perspectiva macro, Google Earth) ---
t.goto(-400, 300)
t.pendown()
t.color(SKY_COLOR)
t.begin_fill()
for _ in range(2):
    t.forward(800)
    t.right(90)
    t.forward(200)
    t.right(90)
t.end_fill()
t.penup()

# --- Dibujar la base del humedal (el "cuerpo" del humedal) ---
t.goto(-400, 100)
t.pendown()
t.color(LAND_COLOR)
t.begin_fill()
t.goto(400, 100)
t.goto(400, -300)
t.goto(-400, -300)
t.goto(-400, 100)
t.end_fill()
t.penup()

# --- Dibujar el agua como el "pulso" o el "corazón" del humedal ---
# Representa el movimiento y la vida acuática
t.goto(-350, 80)
t.pendown()
t.color(WATER_COLOR)
t.begin_fill()
t.setheading(0)
t.forward(700)
t.right(90)
t.forward(350)
t.right(90)
t.forward(700)
t.right(90)
t.forward(350)
t.end_fill()
t.penup()

# --- Dibujar elementos de vegetación (representando la vida y la biodiversidad) ---
# Simboliza la "respiración" y la resiliencia del humedal
t.color(VEGETATION_COLOR)
t.pensize(2)

def draw_reed(x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.setheading(90)
    t.forward(40)
    t.left(30)
    t.forward(10)
    t.backward(10)
    t.right(60)
    t.forward(10)
    t.backward(10)
    t.setheading(90)
    t.penup()

# Algunas cañas en la orilla del agua
for i in range(-300, 300, 70):
    draw_reed(i, 80)
    draw_reed(i + 20, 80)
    draw_reed(i + 40, 80)
    draw_reed(i, -200) # También en el fondo


# --- Dibujar un símbolo de "contemplación y protección" ---
# Representa la mano que cuida, la conexión humana y el respeto
t.color("black")
t.pensize(3)

# Dibujar un ojo estilizado o un símbolo de mirada atenta
t.penup()
t.goto(0, 200)
t.pendown()
t.circle(20) # El iris
t.penup()
t.goto(-30, 200)
t.pendown()
t.setheading(0)
t.circle(30, extent=180) # El párpado superior
t.penup()
t.goto(30, 200)
t.pendown()
t.setheading(180)
t.circle(30, extent=180) # El párpado inferior
t.penup()

t.goto(0, 180)
t.pendown()
t.write("Contemplación y Protección", align="center", font=("Arial", 14, "bold"))
t.penup()

# Finalizar dibujo
t.hideturtle()
screen.update() # Actualizar la pantalla una vez al final
screen.mainloop()