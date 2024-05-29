import os
import pygame
import subprocess
import time
from gpiozero import Button
from shutil import copyfile

# Inicializar Pygame
pygame.init()

#Inicializar Pygame mixer
pygame.mixer.init()

# Obtener dimensiones de la pantalla para modo de pantalla completa
info = pygame.display.Info()
ancho = info.current_w
alto = info.current_h

# Inicializar la pantalla de Pygame en modo de pantalla completa
pantalla = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)

pygame.display.set_caption("Consola de Videojuegos Retro")

# Cargar la imagen estática
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(directorio_actual, "logo.png")
imagen_logo = pygame.image.load(ruta_imagen)

# Cargar el sonido
ruta_sonido = os.path.join(directorio_actual, "startup_sound.wav")
pygame.mixer.music.load(ruta_sonido)

# Ruta de Mednafen
ruta_mednafen = "/usr/games/mednafen"

# Función para buscar ROMs en la carpeta 'ROMS' y lanzarlas con el emulador correspondiente
def lanzar_roms_desde_carpeta(ruta_carpeta):
    extensiones_rom = [".gb", ".gba", ".nes", ".smd", ".snes", ".smc", ".md", ".sfc"]
    roms = []
    for filename in os.listdir(ruta_carpeta):
        if any(filename.lower().endswith(ext) for ext in extensiones_rom):
            roms.append(filename)
    return roms

def comprobar_conexion_joystick():
    while pygame.joystick.get_count() == 0:
        esperar_joystick()
        pygame.joystick.init()

def mostrar_lista_roms(roms):
    global bandera
   # fuente = pygame.font.SysFont(None, 36)
    fuente = pygame.font.Font(os.path.join(directorio_actual, "8-bit-hud.ttf"), 18)
    indice_seleccionado = 0
    indice_inicio = 0  # Índice inicial de la lista para mostrar

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    while True:
        try:
            comprobar_conexion_joystick()
            
            pantalla.fill((0, 0, 0))
            # Calcular el índice final de la lista para mostrar
            indice_final = min(indice_inicio + 5, len(roms))
            for i, indice_rom in enumerate(range(indice_inicio, indice_final)):
                color = (255, 255, 255) if indice_rom == indice_seleccionado else (128, 128, 128)
                texto = fuente.render(roms[indice_rom], True, color)
                rect_texto = texto.get_rect(center=(ancho // 2, 200 + i * 50))
                pantalla.blit(texto, rect_texto)
            
            # Mostrar el mensaje en la parte inferior derecha
            mensaje = "A -> seleccionar | B -> atras"
           # fuente_mensaje = pygame.font.SysFont(None, 30)
            fuente_mensaje = pygame.font.Font(os.path.join(directorio_actual, "8-bit-hud.ttf"), 15)
            texto_mensaje = fuente_mensaje.render(mensaje, True, (255, 255, 255))
            rect_mensaje = texto_mensaje.get_rect(bottomright=(ancho - 20, alto - 20))
            pantalla.blit(texto_mensaje, rect_mensaje)

            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if evento.type == pygame.JOYBUTTONDOWN:
                    if evento.button == 0:  # Botón A
                        time.sleep(0.2)
                        return roms[indice_seleccionado]
                    elif evento.button == 1:  # Botón B
                        return None  # Si se presiona B, no se selecciona ROM
                    elif evento.button == 8:  # Botón Xbox
                        pygame.quit()
                        time.sleep(1)
                        reproducir_musica()
                        return None  
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return None

            # Mover el índice seleccionado con el joystick
            if abs(joystick.get_axis(1)) > 0.5:  # Eje Y del joystick
                if joystick.get_axis(1) > 0 and indice_seleccionado < len(roms) - 1:  # Mover hacia abajo
                    indice_seleccionado += 1
                    if indice_seleccionado >= indice_inicio + 5:
                        indice_inicio += 1
                elif joystick.get_axis(1) < 0 and indice_seleccionado > 0:  # Mover hacia arriba
                    indice_seleccionado -= 1
                    if indice_seleccionado < indice_inicio:
                        indice_inicio -= 1

                time.sleep(0.2)  # Pequeño retraso para evitar movimientos demasiado rápidos

        except pygame.error:
            esperar_joystick()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

# Función para manejar la selección del menú
def manejar_seleccion_menu():
    global bandera
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    while True:
        try:
            comprobar_conexion_joystick()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if evento.type == pygame.JOYBUTTONDOWN:
                    if joystick.get_button(0):  # Botón A
                        bandera = True
                        return "ROMS"
                    elif joystick.get_button(1):  # Botón B
                        return "USB"
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return None

            # Asegurarse de que el menú se redibuje
            mostrar_interfaz_usuario()
            
        except pygame.error:
            esperar_joystick()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            mostrar_interfaz_usuario()

# Función para reproducir la animación de inicio durante un tiempo especificado
def reproducir_animacion_inicio():
    # Reproducir el sonido
    pygame.mixer.music.play(loops=-1)

    # Mostrar la imagen estática
    pantalla.blit(imagen_logo, (ancho // 2 - imagen_logo.get_width() // 2, alto // 2 - imagen_logo.get_height() // 2))
    pygame.display.flip()

    # Esperar hasta que el sonido termine
    tiempo_inicio = time.time()
    while pygame.mixer.music.get_busy() and time.time() - tiempo_inicio < 5:
        continue

# Función para mostrar la interfaz de usuario
def mostrar_interfaz_usuario():
    pantalla.fill((0, 0, 0))  # Limpiar la pantalla
    #fuente = pygame.font.SysFont(None, 30)
    fuente = pygame.font.Font(os.path.join(directorio_actual, "8-bit-hud.ttf"), 20)  # Cargar una fuente pixelada

    instrucciones = [
        "Bienvenido a la Consola de",
        " Videojuegos Retro",
        "Presiona los botones",
        "del gamepad para navegar:",
        " ",
        "  - A: Leer ROMs instalados",
        "  - B: Leer ROMs desde USB",
        " ",
        "NOTA:",
        "   - Arriba y Abajo: Seleccionar juego",
        "   - Boton Xbox: Salir del juego",
    ]

    # Calcular la altura total de las instrucciones
    altura_total = sum(fuente.size(linea)[1] for linea in instrucciones)
    # Calcular la posición vertical de la primera línea de instrucciones
    y_offset = (alto - altura_total) // 2

    # Mostrar las instrucciones en la pantalla
    for instruccion in instrucciones:
        texto = fuente.render(instruccion, True, (255, 255, 255))
        rect_texto = texto.get_rect(center=(ancho // 2, y_offset))
        pantalla.blit(texto, rect_texto)
        y_offset += fuente.size(instruccion)[1]  # Aumentar la posición vertical para la siguiente línea

    pygame.display.flip()

# Función para comprobar si hay un joystick conectado
def esperar_joystick():
    fuente = pygame.font.Font(None, 50)
    while True:
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            pantalla.fill((0, 0, 0))  # Limpiar la pantalla
            pygame.display.flip()
            return True
        pantalla.fill((0, 0, 0))
        texto = fuente.render("No se ha detectado un control. Conéctelo para continuar.", True, (255, 0, 0))
        rect_texto = texto.get_rect(center=(ancho // 2, alto // 2))
        pantalla.blit(texto, rect_texto)
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                pygame.quit()
                return False
        time.sleep(1)  # Esperar 1 segundo antes de comprobar de nuevo

def reproducir_musica():
    global musica  # Usar la variable global para controlar la música
    if not musica:
        # Reproducir el sonido
        musica = True
        pygame.mixer.music.play(loops=-1)

def detener_musica():
    global musica  # Usar la variable global para controlar la música
    if musica:
        # Detener el sonido
        musica = False
        pygame.mixer.music.stop()


def montar_usb():
    #Montar la USB si está conectada
    ruta_usb = "/media/usb"
    os.system('sudo mkdir -p /media/usb')
    os.system('sudo mount /dev/sda1 /media/usb')
    if os.path.ismount(ruta_usb):
        return True
    else:
        return False

def mostrar_mensaje(mensaje, tiempo=2):
    #Mostrar un mensaje en la pantalla durante un tiempo específico.
    fuente = pygame.font.SysFont(None, 30)
    #fuente = pygame.font.Font(os.path.join(directorio_actual, "8-bit-hud.ttf"), 20)  # Cargar una fuente pixelada
    texto = fuente.render(mensaje, True, (255, 0, 0))
    rect_texto = texto.get_rect(center=(ancho // 2, alto // 2))
    pantalla.fill((0, 0, 0))
    pantalla.blit(texto, rect_texto)
    pygame.display.flip()
    time.sleep(tiempo)

musica = True

# Bucle principal
def main():
    global musica
    corriendo = True
    while corriendo:
        # Esperar conexión de joystick
        esperar_joystick()
        
        # Mostrar el menú
        mostrar_interfaz_usuario()
        
        # Esperar selección del usuario
        seleccion = manejar_seleccion_menu()
        # Leer ROMs desde la carpeta 'ROMS' o desde USB según la selección del usuario
        if seleccion == "ROMS":
            time.sleep(1)
            roms = lanzar_roms_desde_carpeta(os.path.join(directorio_actual, "ROMS"))
            while True:
                rom_seleccionada = mostrar_lista_roms(roms)
                if rom_seleccionada:
                    # Limpiar la pantalla
                    pantalla.fill((0, 0, 0))
                    pygame.display.flip()
                    detener_musica()
                    proceso_juego = subprocess.Popen([ruta_mednafen, os.path.join(directorio_actual, "ROMS", rom_seleccionada)])
                    while proceso_juego.poll() is None:
                        comprobar_conexion_joystick()
                        time.sleep(1)
                    codigo_salida = proceso_juego.wait()  # Espera a que el proceso termine antes de continuar
                    time.sleep(1)
                    if codigo_salida == 0:
                        reproducir_musica()
                else:
                    break
                    
        elif seleccion == "USB":
            if montar_usb():
                ruta_usb = "/media/usb"
                for filename in os.listdir(ruta_usb):
                    if filename.lower().endswith((".gb", ".gba", ".nes", ".smd", ".snes", ".smc", ".md", ".sfc")):
                        src = os.path.join(ruta_usb, filename)
                        dst = os.path.join(directorio_actual, "ROMS", filename)
                        copyfile(src, dst)
                roms = lanzar_roms_desde_carpeta(os.path.join(directorio_actual, "ROMS"))
                while True:
                    rom_seleccionada = mostrar_lista_roms(roms)
                    if rom_seleccionada:
                        pantalla.fill((0, 0, 0))
                        pygame.display.flip()
                        detener_musica()
                        proceso_juego = subprocess.Popen([ruta_mednafen, os.path.join(directorio_actual, "ROMS", rom_seleccionada)])
                        while proceso_juego.poll() is None:
                            comprobar_conexion_joystick()
                            time.sleep(1)
                        codigo_salida = proceso_juego.wait()
                        time.sleep(1)
                        if codigo_salida == 0:
                            reproducir_musica()
                    else:
                        break
            else:
                mostrar_mensaje("USB no conectada")

        # Limpiar la pantalla
        pantalla.fill((0, 0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    # Reproducir la animación de inicio durante 5 segundos
    reproducir_animacion_inicio()
    main()
    pygame.quit()
