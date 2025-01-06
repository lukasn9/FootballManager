import pygame
import os
from .BasePage import BasePage
import json

class SaveSelectorPage(BasePage):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)

        self.slot_width, self.slot_height = 350, 250
        self.start_x = (screen.get_width() - (3 * self.slot_width + 2 * 70)) // 2
        self.start_y = (screen.get_height() - self.slot_height) // 2 - 50

        self.background = pygame.image.load("data/assets/images/stadium_2.jpg")
        self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))

        self.button_font = pygame.font.Font(pygame.font.get_default_font(), 28)
        self.button_text = "Choose a save file"
        self.button_padding = 30
        text_surface = self.button_font.render(self.button_text, True, (255, 255, 255))
        self.button_width = text_surface.get_width() + self.button_padding * 2
        self.button_height = text_surface.get_height() + self.button_padding
        self.button_x = (screen.get_width() - self.button_width) // 2
        self.button_y = self.start_y + self.slot_height + 225

        self.slots = [
            {"slot": "1", "club_id": "", "season": ""},
            {"slot": "2", "club_id": "", "season": ""},
            {"slot": "3", "club_id": "", "season": ""}
        ]

        self.load_slot_data()

    def load_slot_data(self):
        save_files = ["data/assets/save1.json", "data/assets/save2.json", "data/assets/save3.json"]
        for i, save_file in enumerate(save_files):
            if os.path.exists(save_file):
                with open(save_file, "r") as save:
                    data = json.load(save)
                    self.slots[i]["club_id"] = data.get("club_id", "")
                    self.slots[i]["season"] = data.get("season", 0)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i in range(3):
                    slot_rect = pygame.Rect(self.start_x + i * (self.slot_width + 70), self.start_y, self.slot_width, self.slot_height)
                    if slot_rect.collidepoint(mouse_pos):
                        with open("data/assets/config.json", "r+") as f:
                            data = json.load(f)
                            data["current_save"] = str(i + 1)
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()
                        return "dashboard" if self.slots[i]["club_id"] != "" else "club_selection"

    def create_slot_surface(self, width, height):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (50, 50, 50), (0, 0, width, height), border_radius=20)
        return surface

    def render_slot(self, slot_data, slot_x, slot_y):
        slot_surface = self.create_slot_surface(self.slot_width, self.slot_height)

        if slot_data["club_id"] != "":
            background_path = f"data/assets/images/clubs/backgrounds/background_{slot_data['club_id']}.png"
            if os.path.exists(background_path):
                background_img = pygame.image.load(background_path)
                background_img = pygame.transform.scale(background_img, (self.slot_width, self.slot_height - 50))

                mask_surface = pygame.Surface((self.slot_width, self.slot_height - 50), pygame.SRCALPHA)
                pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, self.slot_width, self.slot_height - 50), border_radius=20)

                background_img.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

                overlay = pygame.Surface((self.slot_width, self.slot_height - 50), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                background_img.blit(overlay, (0, 0))

                slot_surface.blit(background_img, (0, 0))

            logo_path = f"data/assets/images/clubs/logos/logo_{slot_data['club_id']}.png"
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (100, 100))
                slot_surface.blit(logo, (self.slot_width // 2 - 50, self.slot_height // 2 - 80))

            season_text = f"Season {slot_data['season']}"
            text_surface = self.font.render(season_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.slot_width // 2, self.slot_height - 30))
            slot_surface.blit(text_surface, text_rect)
        else:
            empty_text = "Empty"
            text_surface = self.font.render(empty_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.slot_width // 2, self.slot_height // 2))
            slot_surface.blit(text_surface, text_rect)

        self.screen.blit(slot_surface, (slot_x, slot_y))

    def render(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        for i in range(3):
            slot_x = self.start_x + i * (self.slot_width + 70)
            self.render_slot(self.slots[i], slot_x, self.start_y)

        button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        pygame.draw.rect(self.screen, (50, 50, 50), button_rect, border_radius=20)
        text = self.button_font.render(self.button_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)

        pygame.display.flip()
