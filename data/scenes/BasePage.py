import pygame

class BasePage:
    def __init__(self, screen):
        self.screen = screen

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def render(self):
        pass