import turtle

def draw_wetland_life():
    screen = turtle.Screen()
    screen.title("Humedal - dibujo con turtle")
    screen.setup(width=600, height=400)
    screen.bgcolor("lightblue")  # cielo / ambiente húmedo

    # Opcional: desactivar animación para dibujar más rápido y luego actualizar
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()     # ocultamos el cursor mientras dibujamos la base
    t.speed(0)
    t.penup()
    t.goto(-280, -150)
    t.pendown()

    # Dibujar la base de agua
    t.color("darkblue")
    t.begin_fill()
    for _ in range(2):
        t.forward(560)
        t.right(90)
        t.forward(50)
        t.right(90)
    t.end_fill()

    # Dibujar juncos o cañas (vida vegetal del humedal)
    t.showturtle()
    t.pensize(4)
    colors = ["forestgreen", "darkgreen", "olivedrab"]
    positions = [(-150, -100), (-50, -100), (50, -100), (150, -100)]
    heights = [180, 150, 170, 190]

    for i, pos in enumerate(positions):
        t.penup()
        t.goto(pos[0], pos[1])   # pasar por separado es más explícito
        t.pendown()
        t.setheading(90)  # mirar hacia arriba
        t.color(colors[i % len(colors)])
        t.forward(heights[i])
        # pequeñas hojas o detalles en la punta
        t.right(45)
        t.forward(10)
        t.backward(10)
        t.left(90)
        t.forward(10)
        t.backward(10)
        t.right(45)

    # Dibujar una pequeña ola para el agua
    t.penup()
    t.goto(-250, -120)
    t.pendown()
    t.color("lightskyblue")
    t.pensize(2)
    t.setheading(0)
    for _ in range(5):
        t.circle(20, 90)
        t.circle(-20, 90)

    t.hideturtle()

    # Actualizar la pantalla si usamos screen.tracer(0)
    screen.update()

    # Mantener la ventana abierta: usar mainloop() (más compatible) o exitonclick()
    # Si usas IDLE o ejecutas el archivo, cualquiera de los dos funcionará.
    screen.mainloop()

if __name__ == "__main__":
    draw_wetland_life()
