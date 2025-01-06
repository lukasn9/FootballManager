import pygame
from data.scenes.Menu import MenuPage
from data.scenes.SaveSelector import SaveSelectorPage
from data.scenes.Dashboard import DashboardPage
from data.scenes.ClubSelectionPage import ClubSelectionPage
from data.scripts.match import MatchSimulationPage

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Football Manager")

def get_page(page_name):
    match page_name:
        case "menu":
            return MenuPage(screen)
        case "save_selector":
            return SaveSelectorPage(screen)
        case "dashboard":
            return DashboardPage(screen)
        case "club_selection":
            return ClubSelectionPage(screen)
        case "match_simulation":
            return MatchSimulationPage(screen)
        case _:
            return MenuPage(screen)

def main():
    clock = pygame.time.Clock()
    current_page_name = "menu"
    current_page = get_page(current_page_name)

    while True:
        events = pygame.event.get()
        next_page_name = current_page.handle_events(events)

        if next_page_name:
            current_page = get_page(next_page_name)
        
        current_page.update()
        current_page.render()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()