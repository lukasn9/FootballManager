import pygame
import json
import csv
import random
from ..scenes.BasePage import BasePage
from datetime import datetime, timedelta

class MatchSimulationPage(BasePage):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 28)
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 20)

        self.background = pygame.image.load("data/assets/images/stadium_2.jpg")
        self.background = pygame.transform.scale(
            self.background, (screen.get_width(), screen.get_height())
        )

        self.is_paused = False
        self.speed_multiplier = 1.0
        self.skip_to_end = False

        self.icons = {
            "pause": pygame.image.load("data/assets/icons/pause.png"),
            "play": pygame.image.load("data/assets/icons/play.png"),
            "slow": pygame.image.load("data/assets/icons/slow.png"),
            "normal": pygame.image.load("data/assets/icons/normal.png"),
            "fast": pygame.image.load("data/assets/icons/fast.png"),
            "skip": pygame.image.load("data/assets/icons/skip.png"),
            "advance": pygame.image.load("data/assets/icons/skip.png")
        }

        for key in self.icons:
            self.icons[key] = pygame.transform.scale(self.icons[key], (24, 24))

        self.home_score = 0
        self.away_score = 0
        self.home_possession = 50
        self.home_shots = 0
        self.away_shots = 0
        self.home_shots_on_target = 0
        self.away_shots_on_target = 0
        self.home_xg = 0
        self.away_xg = 0

        self.commentary_lines = []
        self.max_commentary_lines = 14
        self.commentary_data = self.load_commentary_data()

        self.match_start_time = datetime.now()
        self.current_minute = 0
        self.is_match_running = True

        self.events_per_match = random.randint(20, 30)
        self.events_timeline = self.generate_events_timeline()
        self.current_event_index = 0

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.setup_control_buttons()
        self.load_match_data()

    def load_match_data(self):
        with open('data/assets/config.json', 'r') as file:
            config = json.load(file)
            self.save_num = config['current_save']

        with open(f"data/assets/save{self.save_num}_schedule.json", 'r+') as file:
            self.match_data = json.load(file)
            data = self.match_data
            if data:
                data.pop(0)
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
            self.match_data = self.match_data[0]

        with open(f"data/assets/save{self.save_num}.json", 'r+') as file:
            data = json.load(file)
            data["date"] = self.match_data["date"]
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

        with open("data/assets/clubs.csv", "r", encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if self.match_data["home"] == row["club_id"]:
                    self.home_team = row["club_name"]
                if self.match_data["away"] == row["club_id"]:
                    self.away_team = row["club_name"]

    def load_commentary_data(self):
        with open('data/assets/commentary.json', 'r') as file:
            return json.load(file)
            
    def generate_events_timeline(self):
        events = []
        for _ in range(self.events_per_match):
            minute = random.randint(1, 90)
            team = "home" if random.random() < 0.5 else "away"
            event_type = random.choices(
                ["attack", "shot", "shot_on_target", "goal"],
                weights=[0.4, 0.3, 0.2, 0.1]
            )[0]
            events.append({"minute": minute, "team": team, "type": event_type})
        return sorted(events, key=lambda x: x["minute"])

    def create_stats_surface(self, width, height):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (50, 50, 50, 200), (0, 0, width, height), border_radius=10)
        return surface
        
    def update_match_state(self):
        if not self.is_match_running:
            return

        self.current_minute = int((datetime.now() - self.match_start_time).total_seconds() / 2)

        if self.current_minute >= 90:
            self.current_minute = 90
            self.is_match_running = False
            return

        while (self.current_event_index < len(self.events_timeline) and 
               self.events_timeline[self.current_event_index]["minute"] <= self.current_minute):
            event = self.events_timeline[self.current_event_index]
            self.process_event(event)
            self.current_event_index += 1

    def process_event(self, event):
        team = event["team"]
        event_type = event["type"]
        
        if team == "home":
            self.home_possession += random.uniform(-2, 2)
            if event_type in ["shot", "shot_on_target", "goal"]:
                self.home_shots += 1
                self.home_xg += random.uniform(0.1, 0.3)
                if event_type in ["shot_on_target", "goal"]:
                    self.home_shots_on_target += 1
                    if event_type == "goal":
                        self.home_score += 1
                        self.home_xg += random.uniform(0.3, 0.5)
        else:
            if event_type in ["shot", "shot_on_target", "goal"]:
                self.away_shots += 1
                self.away_xg += random.uniform(0.1, 0.3)
                if event_type in ["shot_on_target", "goal"]:
                    self.away_shots_on_target += 1
                    if event_type == "goal":
                        self.away_score += 1
                        self.away_xg += random.uniform(0.3, 0.5)

        commentary_text = random.choice(self.commentary_data[event_type][team])
        self.commentary_lines.append(f"{self.current_minute}' - {commentary_text}")
        if len(self.commentary_lines) > self.max_commentary_lines:
            self.commentary_lines.pop(0)

    def setup_control_buttons(self):
        button_size = 50
        button_padding = 20
        total_width = (button_size * 6) + (button_padding * 5)
        start_x = (self.screen_width - total_width) // 2
        button_y = self.screen_height - 100
        
        self.buttons = {
            "pause": {
                "rect": pygame.Rect(start_x, button_y, button_size, button_size),
                "icon": "pause",
                "alt_icon": "play",
            },
            "slow": {
                "rect": pygame.Rect(start_x + (button_size + button_padding), button_y, button_size, button_size),
                "icon": "slow",
            },
            "normal": {
                "rect": pygame.Rect(start_x + (button_size + button_padding) * 2, button_y, button_size, button_size),
                "icon": "normal",
            },
            "fast": {
                "rect": pygame.Rect(start_x + (button_size + button_padding) * 3, button_y, button_size, button_size),
                "icon": "fast",
            },
            "skip": {
                "rect": pygame.Rect(start_x + (button_size + button_padding) * 4, button_y, button_size, button_size),
                "icon": "skip",
            },
            "advance": {
                "rect": pygame.Rect(start_x + (button_size + button_padding) * 5, button_y, button_size, button_size),
                "icon": "advance",
            }
        }

    def create_button_surface(self, size, border_radius=10, is_active=False):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (50, 50, 50, 255) if is_active else (70, 70, 70, 255)

        pygame.draw.rect(surface, color, (0, 0, size, size), border_radius=border_radius)

        return surface

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "dashboard"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_button_clicks(mouse_pos)

    def handle_button_clicks(self, mouse_pos):
        for button_key, button_data in self.buttons.items():
            if button_data["rect"].collidepoint(mouse_pos):
                if button_key == "pause":
                    self.is_paused = not self.is_paused
                elif button_key == "slow":
                    self.speed_multiplier = 0.5
                elif button_key == "normal":
                    self.speed_multiplier = 1.0
                elif button_key == "fast":
                    self.speed_multiplier = 2.0
                elif button_key == "skip":
                    self.speed_multiplier = 75.0
                elif button_key == "advance":
                    return "dashboard"

    def update_match_state(self):
        if self.current_minute >= 90:
            self.is_paused = True
            self.is_match_running = False
        if self.is_paused and not self.skip_to_end:
            return

        if self.skip_to_end:
            self.match_start_time = datetime.now() - timedelta(seconds=180)
            while self.current_minute < 90:
                self.current_minute += 1
                while (self.current_event_index < len(self.events_timeline) and
                    self.events_timeline[self.current_event_index]["minute"] <= self.current_minute):
                    self.process_event(self.events_timeline[self.current_event_index])
                    self.current_event_index += 1
                self.render()
            self.is_match_running = False
            self.skip_to_end = False
            return

        time_delta = (datetime.now() - self.match_start_time).total_seconds()
        self.current_minute = int(time_delta * self.speed_multiplier / 2)

        if self.current_minute >= 90:
            self.is_match_running = False
            return

        while (self.current_event_index < len(self.events_timeline) and 
               self.events_timeline[self.current_event_index]["minute"] <= self.current_minute):
            self.process_event(self.events_timeline[self.current_event_index])
            self.current_event_index += 1

    def render(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        self.update_match_state()

        score_surface = self.create_stats_surface(700, 100)
        score_text = self.font.render(f"{self.home_team} {self.home_score} - {self.away_score} {self.away_team}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(350, 50))
        score_surface.blit(score_text, score_rect)
        self.screen.blit(score_surface, (self.screen_width // 2 - 350, 20))

        stats_surface = self.create_stats_surface(300, 250)
        stats_texts = [
            f"Possession: {int(self.home_possession)}% - {100 - int(self.home_possession)}%",
            f"Shots: {self.home_shots} - {self.away_shots}",
            f"On Target: {self.home_shots_on_target} - {self.away_shots_on_target}",
            f"xG: {self.home_xg:.2f} - {self.away_xg:.2f}",
            f"Time: {self.current_minute}'"
        ]
        
        for i, text in enumerate(stats_texts):
            stat_text = self.small_font.render(text, True, (255, 255, 255))
            stats_surface.blit(stat_text, (20, 20 + i * 40))
        self.screen.blit(stats_surface, (20, 20))

        commentary_surface = self.create_stats_surface(600, 450)
        for i, line in enumerate(self.commentary_lines):
            comment_text = self.small_font.render(line, True, (255, 255, 255))
            commentary_surface.blit(comment_text, (20, 20 + i * 30))
        self.screen.blit(commentary_surface, (self.screen_width // 2 - 300, self.screen_height - 600))

        mouse_pos = pygame.mouse.get_pos()

        for button_key, button_data in self.buttons.items():
            is_active = (
                (button_key == "pause" and self.is_paused) or
                (button_key == "slow" and self.speed_multiplier == 0.5) or
                (button_key == "normal" and self.speed_multiplier == 1.0) or
                (button_key == "fast" and self.speed_multiplier == 2.0) or
                (button_key == "skip" and self.speed_multiplier == 75.0)
            )

            button_surface = self.create_button_surface(
                button_data["rect"].width,
                is_active=is_active
            )
            self.screen.blit(button_surface, button_data["rect"])

            icon_key = button_data["alt_icon"] if button_key == "pause" and self.is_paused else button_data["icon"]
            icon = self.icons[icon_key]
            icon_x = button_data["rect"].centerx - icon.get_width() // 2
            icon_y = button_data["rect"].centery - icon.get_height() // 2
            self.screen.blit(icon, (icon_x, icon_y))

        pygame.display.flip()
