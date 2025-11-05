import turtle
import random

# Screen setup
screen = turtle.Screen()
screen.setup(width=600, height=400)
screen.bgcolor("white")
screen.tracer(0) # Turn off screen updates for smoother animation

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.penup()

# Colors for wind and nature (light blues, greens)
wind_colors = ["#ADD8E6", "#87CEEB", "#6495ED", "#B0C4DE", "#AFEEEE"] # Light blues for wind
water_color = "#E0FFFF" # A very light, almost white blue for water base
ripple_colors = ["#B0E0E6", "#ADD8E6", "#87CEEB"] # Lighter blues for ripples

# Draw a calm "water" body (abstracted as a large, soft ellipse)
t.goto(-200, -100)
t.pendown()
t.fillcolor(water_color)
t.begin_fill()
t.setheading(45)
for _ in range(2):
    t.circle(200, 90)
    t.circle(100, 90)
t.end_fill()
t.penup()

# Draw subtle wind lines and ripples
t.pensize(1)
num_lines = 50
for _ in range(num_lines):
    t.pencolor(random.choice(wind_colors))
    start_x = random.randint(-280, 280)
    start_y = random.randint(-180, 180)
    t.goto(start_x, start_y)
    t.pendown()
    t.setheading(random.randint(0, 360))
    length = random.randint(20, 100)
    angle_change = random.randint(-30, 30)
    for _ in range(5): # Create wavy lines
        t.forward(length / 5)
        t.right(angle_change)
    t.penup()

# Add a few subtle "ripple" like curves on the "water"
t.pensize(0.5)
for _ in range(30):
    t.pencolor(random.choice(ripple_colors))
    start_x = random.randint(-150, 150)
    start_y = random.randint(-80, 80)
    t.goto(start_x, start_y)
    t.pendown()
    t.setheading(random.randint(0, 360))
    radius = random.randint(10, 40)
    t.circle(radius, random.randint(45, 180))
    t.penup()


screen.update()
screen.mainloop()