import pygame
pygame.init()
file = "/Users/scharlesworth/Desktop/IntruderAlert.ogg"
pygame.mixer.init()
pygame.mixer.music.load(file)
pygame.mixer.music.play()
