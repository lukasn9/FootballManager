import pygame
import os
import csv
import json
from .BasePage import BasePage


class ClubSelectionPage(BasePage):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 28)

        self.background = pygame.image.load("data/assets/images/stadium_4.jpg")
        self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))

        self.leagues = self.load_leagues("data/assets/leagues.csv")
        self.clubs = self.load_clubs("data/assets/clubs.csv")

        self.current_league_index = 0
        self.current_club_index = 0

        self.config_path = "data/assets/config.json"
        self.save_path = None
        self.load_current_save()

        self.update_filtered_clubs()

        self.league_left_arrow = pygame.Rect(200, 100, 50, 50)
        self.league_right_arrow = pygame.Rect(self.screen.get_width() - 250, 100, 50, 50)
        self.club_left_arrow = pygame.Rect(200, self.screen.get_height() // 2 - 25, 50, 50)
        self.club_right_arrow = pygame.Rect(self.screen.get_width() - 250, self.screen.get_height() // 2 - 25, 50, 50)

    def load_current_save(self):
        with open(self.config_path, 'r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)
            save_num = config_data.get("current_save", 1)
            self.save_path = f"data/assets/save{save_num}.json"

    def load_leagues(self, filepath):
        leagues = []
        with open(filepath, mode="r", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                leagues.append(row)
        return leagues

    def load_clubs(self, filepath):
        clubs = []
        with open(filepath, mode="r", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                clubs.append(row)
        return clubs

    def update_filtered_clubs(self):
        league_code = self.leagues[self.current_league_index]["league_code"]
        self.filtered_clubs = [club for club in self.clubs if club["league_code"] == league_code]
        self.current_club_index = min(self.current_club_index, len(self.filtered_clubs) - 1)
        self.update_save_file()

    def update_save_file(self):
        if not self.save_path or not os.path.exists(self.save_path):
            return

        current_club = self.filtered_clubs[self.current_club_index]

        with open("data/assets/clubs.csv", 'r+', encoding='utf-8') as inp:
            reader = csv.reader(inp)

            for row in reader:
                if row[0] == current_club["club_id"]:
                    money = int(row[5])
                    break

        updated_data = {"club_id": current_club["club_id"], "money": current_club.get("initial_money", money)}

        with open(self.save_path, 'r+', encoding='utf-8') as save_file:
            save_data = json.load(save_file)
            save_data.update(updated_data)
            save_file.seek(0)
            json.dump(save_data, save_file, indent=4)
            save_file.truncate()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.league_left_arrow.collidepoint(mouse_pos):
                    self.current_league_index = (self.current_league_index - 1) % len(self.leagues)
                    self.update_filtered_clubs()
                elif self.league_right_arrow.collidepoint(mouse_pos):
                    self.current_league_index = (self.current_league_index + 1) % len(self.leagues)
                    self.update_filtered_clubs()
                elif self.club_left_arrow.collidepoint(mouse_pos):
                    self.current_club_index = (self.current_club_index - 1) % len(self.filtered_clubs)
                    self.update_save_file()
                elif self.club_right_arrow.collidepoint(mouse_pos):
                    self.current_club_index = (self.current_club_index + 1) % len(self.filtered_clubs)
                    self.update_save_file()
                elif self.start_button.collidepoint(mouse_pos):
                    return "dashboard"

    def render_arrows(self):
        pygame.draw.polygon(self.screen, (255, 255, 255), [
            (self.league_left_arrow.x + 10, self.league_left_arrow.y + 25),
            (self.league_left_arrow.x + 40, self.league_left_arrow.y + 10),
            (self.league_left_arrow.x + 40, self.league_left_arrow.y + 40)
        ])

        pygame.draw.polygon(self.screen, (255, 255, 255), [
            (self.league_right_arrow.x + 40, self.league_right_arrow.y + 25),
            (self.league_right_arrow.x + 10, self.league_right_arrow.y + 10),
            (self.league_right_arrow.x + 10, self.league_right_arrow.y + 40)
        ])

        pygame.draw.polygon(self.screen, (255, 255, 255), [
            (self.club_left_arrow.x + 10, self.club_left_arrow.y + 25),
            (self.club_left_arrow.x + 40, self.club_left_arrow.y + 10),
            (self.club_left_arrow.x + 40, self.club_left_arrow.y + 40)
        ])

        pygame.draw.polygon(self.screen, (255, 255, 255), [
            (self.club_right_arrow.x + 40, self.club_right_arrow.y + 25),
            (self.club_right_arrow.x + 10, self.club_right_arrow.y + 10),
            (self.club_right_arrow.x + 10, self.club_right_arrow.y + 40)
        ])

    def get_club_logo(self, club_id):
        logo_path = f"data/assets/images/clubs/logos/logo_{club_id}.png"
        if os.path.exists(logo_path):
            try:
                return pygame.image.load(logo_path)
            except pygame.error as e:
                return self.get_default_logo()
        else:
            return self.get_default_logo()

    def get_default_logo(self):
        placeholder_path = "data/assets/images/clubs/logos/logo_11.png"
        if os.path.exists(placeholder_path):
            try:
                return pygame.image.load(placeholder_path)
            except pygame.error as e:
                pass
        return pygame.Surface((200, 200))

    def render(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))

        league = self.leagues[self.current_league_index]
        league_text = self.font.render(f"{league['league_name']} ({league['country_name']})", True, (255, 255, 255))
        text_y = self.league_left_arrow.y + (self.league_left_arrow.height // 2) - (league_text.get_height() // 2)
        self.screen.blit(league_text, (self.screen.get_width() // 2 - league_text.get_width() // 2, text_y))

        current_club = self.filtered_clubs[self.current_club_index]
        club_logo = self.get_club_logo(current_club["club_id"])
        if club_logo:
            club_logo = pygame.transform.scale(club_logo, (200, 200))
            self.screen.blit(club_logo, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 150))

        club_text = self.font.render(current_club["club_name"], True, (255, 255, 255))
        stadium_text = self.small_font.render(
            f"Stadium: {current_club['stadium_name']} ({current_club['stadium_capacity']})", True, (255, 255, 255)
        )
        budget_text = self.small_font.render(
            f"Starting Budget: {int(current_club['budget']) / 1000000}m", True, (255, 255, 255)
        )

        self.screen.blit(club_text, (self.screen.get_width() // 2 - club_text.get_width() // 2, self.screen.get_height() // 2 + 70))
        self.screen.blit(stadium_text, (self.screen.get_width() // 2 - stadium_text.get_width() // 2, self.screen.get_height() // 2 + 110))
        self.screen.blit(budget_text, (self.screen.get_width() // 2 - budget_text.get_width() // 2, self.screen.get_height() // 2 + 150))

        self.render_arrows()

        self.start_button = pygame.Rect(self.screen.get_width() // 2 - 150, self.screen.get_height() - 100, 300, 50)
        pygame.draw.rect(self.screen, (50, 50, 50), self.start_button, border_radius=10)
        button_text = self.small_font.render("Start Game", True, (255, 255, 255))
        self.screen.blit(button_text, button_text.get_rect(center=self.start_button.center))