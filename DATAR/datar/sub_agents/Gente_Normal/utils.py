from pathlib import Path

def obtener_path_instrucciones():
    """
    Obtiene el path absoluto de la carpeta 'instrucciones'.
    """
    path_agentes = Path(__file__).parent
    return path_agentes / "instrucciones"

def leer_instrucciones(archivo: str = "ins_defecto.txt"):
    """
    Lee el contenido de un archivo de instrucciones 
    ubicado en la carpeta 'instrucciones'.

    Args:
        archivo (str): Nombre del archivo de instrucciones. 
        Por defecto es 'ins_defecto.txt'.
        
    Returns:
        str: Contenido del archivo de instrucciones.
    """

    path_archivo = obtener_path_instrucciones() / archivo

    with open(path_archivo, "r") as a:
        instrucciones = a.read()
 
    return instrucciones