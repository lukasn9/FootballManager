import pygame
from .BasePage import BasePage
import json

class MenuPage(BasePage):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 28)
        self.background = pygame.image.load("data/assets/images/launch_bg.png")
        self.background = pygame.transform.scale(
            self.background, (screen.get_width(), screen.get_height())
        )
        self.button_text = "Press any Button to Continue"
        text_surface = self.font.render(self.button_text, True, (255, 255, 255))
        self.button_padding = 30
        self.button_width = text_surface.get_width() + self.button_padding * 2
        self.button_height = text_surface.get_height() + self.button_padding
        self.button_x = (screen.get_width() - self.button_width) // 2
        self.button_y = screen.get_height() - 125
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        with open("data/assets/config.json", "r+") as f:
            data = json.load(f)
            data["current_save"] = None
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def create_button_surface(self, width, height, border_radius):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.rect(surface, (50, 50, 50), (0, 0, width, height), border_radius=border_radius)

        return surface

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return "save_selector"

    def render(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(175)
        self.screen.blit(overlay, (0, 0))

        button_rect = pygame.Rect(self.button_x, self.button_y,
                                self.button_width, self.button_height)
        button_surface = self.create_button_surface(self.button_width, self.button_height, 20)
        self.screen.blit(button_surface, (self.button_x, self.button_y))

        text = self.font.render(self.button_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)

        pygame.display.flip()