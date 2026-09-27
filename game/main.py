import pygame
from config import *

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

state = GameState()
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        state.handle_event(e)

    state.update()
    state.draw(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()