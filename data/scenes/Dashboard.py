import pygame
from datetime import datetime
import csv
from .BasePage import BasePage
from ..scripts.gen_schedule import schedule
import json
from colorthief import ColorThief
import random
from ..scripts.match import MatchSimulationPage

class DashboardPage(BasePage):
    def __init__(self, screen):
        super().__init__(screen)

        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 16)

        self.squad = []
        self.schedule = []

        self.save_file = ""
        self.money = 0
        self.club_id = 0
        self.season = ""
        self.date = ""

        with open("data/assets/config.json", "r") as f:
            data = json.load(f)
            self.save_file = f"data/assets/save{data['current_save']}.json"
            self.save_num = data["current_save"]

        self.get_save_data()
        self.get_club_data()
        self.get_schedule()

        self.background = pygame.image.load(f"data/assets/images/clubs/backgrounds/background_{self.club_id}.png")
        self.background = pygame.transform.scale(
            self.background, (screen.get_width(), screen.get_height())
        )

        self.color_thief = ColorThief(f"data/assets/images/clubs/logos/logo_{self.club_id}.png")
        self.dominant_color = self.color_thief.get_color(quality=1)

        self.club_logo = pygame.image.load(f"data/assets/images/clubs/logos/logo_{self.club_id}.png")
        self.club_logo = pygame.transform.scale(self.club_logo, (50, 50))

        self.opponent_logo = pygame.image.load("data/assets/images/clubs/logos/logo_11.png")
        self.opponent_logo = pygame.transform.scale(self.opponent_logo, (50, 50))

        self.icons = {
            "training": pygame.image.load("data/assets/icons/training_icon.png"),
            "players": pygame.image.load("data/assets/icons/players_icon.png"),
            "settings": pygame.image.load("data/assets/icons/settings_icon.png")
        }

        self.buttons = self.setup_navigation_buttons()
        self.load_squad_from_csv(f"data/assets/save{self.save_num}_players.csv")
        self.generate_numbers()

        # Define the "Advance to Next Match" button
        self.advance_match_button = pygame.Rect(50, 150, 400, 200)

    def generate_numbers(self):
        numbers = list(range(1, 100))

        random.shuffle(numbers)

        assigned_numbers = set(player["number"] for player in self.squad if "number" in player)

        available_numbers = [num for num in numbers if num not in assigned_numbers]

        for player in self.squad:
            if "number" in player:
                continue

            if available_numbers:
                player["number"] = available_numbers.pop(0)

    def get_save_data(self):
        with open(self.save_file, "r") as f:
            data = json.load(f)
            self.money = data["money"]
            self.club_id = data["club_id"]

            if data.get("season", "") == "":
                self.season = "24/25"
                data["season"] = self.season
                with open(self.save_file, "w") as f:
                    json.dump(data, f, indent=4)
            else:
                self.season = data["season"]

            if data.get("date", "") == "":
                self.date = datetime.strptime("2024-08-17", "%Y-%m-%d")
                data["date"] = self.date.strftime("%Y-%m-%d")
                with open(self.save_file, "w") as f:
                    json.dump(data, f, indent=4)
            else:
                self.date = data["date"]

    def get_schedule(self):
        try:
            with open(f"data/assets/save{self.save_num}_schedule.json", "r") as f:
                self.schedule = json.load(f)
        except FileNotFoundError:
            schedule(self.club_id, self.club_data["league_code"], self.save_num)
            self.get_schedule()

    def load_squad_from_csv(self, file_path):
        with open(file_path, "r", encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            self.squad = []
            for row in reader:
                if self.club_id == row["current_club_id"]:
                    self.squad.append({
                        "id": row["player_id"],
                        "name": row["name"],
                        "position": row["position"],
                        "overall": row["overall"],
                        "OVR": row["OVR"]
                    })

    def get_club_data(self):
        with open("data/assets/clubs.csv", "r", encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["club_id"] == self.club_id:
                    self.club_data = row

    def format_money(self, money):
        if money >= 1000000:
            return f"{money // 1000000}m"
        else:
            return f"{money // 1000}k"

    def setup_navigation_buttons(self):
        buttons = {
            "dashboard": pygame.Rect(20, self.screen.get_height() - 50, 120, 40),
            "squad": pygame.Rect(150, self.screen.get_height() - 50, 120, 40),
            "training": pygame.Rect(280, self.screen.get_height() - 50, 120, 40),
            "transfer": pygame.Rect(410, self.screen.get_height() - 50, 120, 40),
            "finances": pygame.Rect(540, self.screen.get_height() - 50, 120, 40),
            "leagues": pygame.Rect(670, self.screen.get_height() - 50, 120, 40)
        }
        return buttons

    def render_match_preview(self):
        preview_surface = pygame.Surface((400, 200), pygame.SRCALPHA)
        pygame.draw.rect(preview_surface, (40, 40, 40, 255), (0, 0, 400, 200), border_radius=10)

        title = self.font.render("Advance to Next Match", True, (255, 255, 255))
        preview_surface.blit(title, (20, 20))

        preview_surface.blit(self.club_logo, (50, 75))
        preview_surface.blit(self.opponent_logo, (300, 75))

        vs_text = self.font.render("vs.", True, (255, 255, 255))
        preview_surface.blit(vs_text, (180, 90))

        self.screen.blit(preview_surface, (50, 150))

    def render_squad_section(self):
        player_height = 40
        padding = 0
        title_height = 70
        total_height = 11 * player_height + padding + title_height

        squad_surface = pygame.Surface((400, total_height), pygame.SRCALPHA)
        pygame.draw.rect(squad_surface, (40, 40, 40, 255), (0, 0, 400, total_height), border_radius=10)

        title = self.font.render("Squad", True, (255, 255, 255))
        squad_surface.blit(title, (20, 20))

        y_pos = title_height
        for player in self.squad:
            jersey = pygame.Surface((30, 30))
            jersey.fill((self.dominant_color[0], self.dominant_color[1], self.dominant_color[2]))
            number = self.small_font.render(str(player["number"]), True, (255, 255, 255))
            jersey.blit(number, (8, 8))

            player_ovr = player["OVR"]

            if player["position"] == "GK":
                jersey.fill((0, 0, 0))

            if player["OVR"] == "":
                player_ovr = player["overall"]


            squad_surface.blit(jersey, (20, y_pos))
            name = self.small_font.render(f"{player['name']} (OVR {player_ovr})", True, (255, 255, 255))
            squad_surface.blit(name, (60, y_pos + 5))

            y_pos += player_height

        self.screen.blit(squad_surface, (500, 150))


    def render_upcoming_matches(self):
        matches_surface = pygame.Surface((300, 600), pygame.SRCALPHA)
        pygame.draw.rect(matches_surface, (40, 40, 40, 255), (0, 0, 300, 600), border_radius=10)

        title = self.font.render("Upcoming Matches", True, (255, 255, 255))
        matches_surface.blit(title, (20, 20))

        y_pos = 70
        for match in self.schedule:
            home_logo = pygame.image.load(f"data/assets/images/clubs/logos/logo_{match['home']}.png")
            away_logo = pygame.image.load(f"data/assets/images/clubs/logos/logo_{match['away']}.png")
            home_logo = pygame.transform.scale(home_logo, (40, 40))
            away_logo = pygame.transform.scale(away_logo, (40, 40))

            vs_text = self.font.render("vs.", True, (255, 255, 255))

            matches_surface.blit(home_logo, (20, y_pos))
            matches_surface.blit(vs_text, (135, y_pos + 10))
            matches_surface.blit(away_logo, (240, y_pos))

            y_pos += 50

        self.screen.blit(matches_surface, (950, 150))

    def render_training_and_players(self):
        buttons_surface = pygame.Surface((400, 100), pygame.SRCALPHA)

        training_button = pygame.Rect(20, 10, 180, 80)
        players_button = pygame.Rect(210, 10, 180, 80)

        pygame.draw.rect(buttons_surface, (40, 40, 40, 255), training_button, border_radius=10)
        pygame.draw.rect(buttons_surface, (40, 40, 40, 255), players_button, border_radius=10)

        training_icon = pygame.transform.scale(self.icons["training"], (50, 50))
        players_icon = pygame.transform.scale(self.icons["players"], (50, 50))

        buttons_surface.blit(training_icon, (50, 25))
        buttons_surface.blit(players_icon, (240, 25))

        self.screen.blit(buttons_surface, (50, 360))

    def render(self):
        self.screen.blit(self.background, (0, 0))

        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        self.render_match_preview()
        self.render_squad_section()
        self.render_upcoming_matches()
        self.render_training_and_players()

        for name, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=10)
            text = self.small_font.render(name.title(), True, (255, 255, 255))
            self.screen.blit(text, (rect.x + 10, rect.y + 10))

        info_background = pygame.Surface((200, 80), pygame.SRCALPHA)
        pygame.draw.rect(info_background, (40, 40, 40, 255), (0, 0, 200, 80), border_radius=10)
        self.screen.blit(info_background, (20, 20))

        self.screen.blit(self.club_logo, (30, 30))

        date = str(self.date).split(" ")[0]
        yy, mm, dd = str(date).split("-")
        date_text = self.font.render(f"{dd}.{mm}. {yy}", True, (255, 255, 255))
        self.screen.blit(date_text, (90, 30))

        money_text = self.font.render(f"€{self.format_money(self.money)}", True, (0, 255, 0))
        self.screen.blit(money_text, (90, 60))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.advance_match_button.collidepoint(mouse_pos):
                    return "match_simulation"
                for name, rect in self.buttons.items():
                    if rect.collidepoint(mouse_pos):
                        return name
        return None