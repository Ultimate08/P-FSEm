import os
import pygame

if "XDG_RUNTIME_DIR" not in os.environ:
    os.environ["XDG_RUNTIME_DIR"]="/tmp/root-runtime-dir"
    if not os.path.exists("/tmp/root-runtime-dir"):
        os.makedirs("/tmp/root-runtime-dir")

pygame.init()


pygame.display.init()

info= pygame.display.Info()
ancho=info.current_w
alto = info.current_h

pantalla=pygame.display.set_mode((ancho,alto),pygame.FULLSCREEN)
pygame.display.set_caption("Test de Pygame")

pantalla.fill((0,128,255))
pygame.display.flip()

corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo=False

pygame.quit()
