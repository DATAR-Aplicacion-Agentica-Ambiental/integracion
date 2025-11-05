#Primer resultado
import tkinter as tk

def dibujar_figura():
    # Limpiamos el lienzo antes de dibujar
    canvas.delete("all")

    # Tomamos el texto ingresado
    texto = entrada.get()

    # Validamos que se haya ingresado algo
    if len(texto) == 0:
        return

    # Tomamos SOLO el primer carácter
    caracter = texto[0]

    # Obtenemos su código ASCII
    codigo_ascii = ord(caracter)

    # Escalamos el tamaño para que no sea demasiado grande
    lado = codigo_ascii % 200 + 20   # lado mínimo 20 px, máximo aprox 220 px

    # Calculamos las coordenadas para centrar la figura
    x1 = (300 - lado) / 2
    y1 = (300 - lado) / 2
    x2 = x1 + lado
    y2 = y1 + lado

    # Dibujamos un cuadrado basado en el valor ASCII
    canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3)

    # Mostramos el valor ASCII en el lienzo
    canvas.create_text(150, 280, text=f"ASCII de '{caracter}': {codigo_ascii}", font=("Arial", 12))


# ---------------- INTERFAZ ---------------- #

# Ventana principal
ventana = tk.Tk()
ventana.title("Generador de Formas con ASCII")
ventana.geometry("400x450")

# Etiqueta
label = tk.Label(ventana, text="Ingresa un carácter:", font=("Arial", 12))
label.pack(pady=10)

# Entrada de texto
entrada = tk.Entry(ventana, font=("Arial", 14), justify="center")
entrada.pack(pady=5)

# Botón para generar figura
boton = tk.Button(ventana, text="Generar Figura", font=("Arial", 12), command=dibujar_figura)
boton.pack(pady=10)

# Canvas donde se dibuja la figura
canvas = tk.Canvas(ventana, width=300, height=300, bg="white")
canvas.pack(pady=10)

# Mantener ventana abierta
ventana.mainloop()
