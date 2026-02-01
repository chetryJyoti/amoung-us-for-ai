"""
Renderer - Handles all drawing operations
"""

import pygame
from game.map import GameMap
from game.constants import (
    ROOM_FLOOR, ROOM_BORDER, HALLWAY_COLOR,
    WHITE, DARK_GRAY, BLACK
)


class Renderer:
    """Handles rendering the game map and entities"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = None
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts for labels"""
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.font_small = pygame.font.SysFont('Arial', 12)

    def draw_map(self, game_map: GameMap):
        """Draw the entire map"""
        # Clear screen with dark background
        self.screen.fill(DARK_GRAY)

        # Draw hallways first (under rooms)
        self._draw_hallways(game_map)

        # Draw rooms
        self._draw_rooms(game_map)

    def _draw_hallways(self, game_map: GameMap):
        """Draw all hallways"""
        for hallway in game_map.hallways:
            pygame.draw.polygon(self.screen, HALLWAY_COLOR, hallway.points)
            pygame.draw.polygon(self.screen, ROOM_BORDER, hallway.points, 2)

    def _draw_rooms(self, game_map: GameMap):
        """Draw all rooms with labels"""
        for name, room in game_map.rooms.items():
            # Draw room floor
            pygame.draw.rect(self.screen, ROOM_FLOOR, room.rect)

            # Draw room border
            pygame.draw.rect(self.screen, ROOM_BORDER, room.rect, 3)

            # Draw room name label
            label = self.font.render(name, True, WHITE)
            label_rect = label.get_rect(center=(room.center[0], room.y + 20))
            self.screen.blit(label, label_rect)

    def draw_player(self, x: int, y: int, color: tuple, player_id: int,
                    provider: str = None, radius: int = 15):
        """Draw a player circle with ID label"""
        # Draw player circle
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, WHITE, (x, y), radius, 2)

        # Draw player ID
        id_label = self.font_small.render(str(player_id), True, BLACK)
        id_rect = id_label.get_rect(center=(x, y))
        self.screen.blit(id_label, id_rect)

        # Draw provider label below (if provided)
        if provider:
            provider_label = self.font_small.render(provider, True, WHITE)
            provider_rect = provider_label.get_rect(center=(x, y + radius + 12))
            self.screen.blit(provider_label, provider_rect)

    def draw_debug_info(self, info: dict):
        """Draw debug information on screen"""
        y_offset = 10
        for key, value in info.items():
            text = self.font_small.render(f"{key}: {value}", True, WHITE)
            self.screen.blit(text, (10, y_offset))
            y_offset += 18
