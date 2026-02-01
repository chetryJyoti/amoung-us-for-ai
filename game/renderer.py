"""
Renderer - Handles all drawing operations
"""

import pygame
from game.map import GameMap
from game.constants import (
    ROOM_FLOOR, ROOM_BORDER, HALLWAY_COLOR,
    WHITE, DARK_GRAY, BLACK, GRAY,
    SCREEN_WIDTH
)


# Colors for roles
IMPOSTOR_COLOR = (255, 50, 50)    # Bright red for impostor indicator
CREWMATE_COLOR = (50, 255, 50)   # Green for crewmate indicator
GHOST_ALPHA = 100                 # Transparency for dead players


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
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)

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
                    provider: str = None, radius: int = 15, alive: bool = True):
        """Draw a player circle with ID label"""
        if alive:
            # Draw living player
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, WHITE, (x, y), radius, 2)

            # Draw player ID
            id_label = self.font_small.render(str(player_id), True, BLACK)
            id_rect = id_label.get_rect(center=(x, y))
            self.screen.blit(id_label, id_rect)
        else:
            # Draw ghost (faded, with X)
            ghost_color = (color[0] // 3, color[1] // 3, color[2] // 3)
            pygame.draw.circle(self.screen, ghost_color, (x, y), radius)
            pygame.draw.circle(self.screen, GRAY, (x, y), radius, 2)

            # Draw X for dead
            x_label = self.font_small.render("X", True, GRAY)
            x_rect = x_label.get_rect(center=(x, y))
            self.screen.blit(x_label, x_rect)

        # Draw provider label below (if provided)
        if provider:
            label_color = WHITE if alive else GRAY
            provider_label = self.font_small.render(provider, True, label_color)
            provider_rect = provider_label.get_rect(center=(x, y + radius + 12))
            self.screen.blit(provider_label, provider_rect)

    def draw_role_indicator(self, role_name: str, is_impostor: bool):
        """Draw the player's role in the top-right corner"""
        color = IMPOSTOR_COLOR if is_impostor else CREWMATE_COLOR
        text = f"You are: {role_name.upper()}"

        # Draw background box
        label = self.font_large.render(text, True, color)
        label_rect = label.get_rect()
        label_rect.topright = (SCREEN_WIDTH - 20, 10)

        # Draw semi-transparent background
        bg_rect = label_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.fill(BLACK)
        bg_surface.set_alpha(180)
        self.screen.blit(bg_surface, bg_rect)

        # Draw text
        self.screen.blit(label, label_rect)

    def draw_game_phase_banner(self, phase: str, extra_info: str = None):
        """Draw a banner showing the current game phase"""
        # Phase text
        phase_text = phase.upper()
        if extra_info:
            phase_text += f" - {extra_info}"

        label = self.font_large.render(phase_text, True, WHITE)
        label_rect = label.get_rect()
        label_rect.midtop = (SCREEN_WIDTH // 2, 10)

        # Draw semi-transparent background
        bg_rect = label_rect.inflate(40, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.fill(BLACK)
        bg_surface.set_alpha(180)
        self.screen.blit(bg_surface, bg_rect)

        # Draw text
        self.screen.blit(label, label_rect)

    def draw_game_over(self, winner: str, reason: str):
        """Draw game over screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, 200))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 260))

        # Winner text
        if winner == "impostor":
            winner_text = "IMPOSTORS WIN!"
            color = IMPOSTOR_COLOR
        else:
            winner_text = "CREWMATES WIN!"
            color = CREWMATE_COLOR

        label = self.font_large.render(winner_text, True, color)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(label, label_rect)

        # Reason text
        reason_label = self.font.render(reason, True, WHITE)
        reason_rect = reason_label.get_rect(center=(SCREEN_WIDTH // 2, 360))
        self.screen.blit(reason_label, reason_rect)

        # Restart hint
        hint_label = self.font_small.render("Press R to restart or ESC to quit", True, GRAY)
        hint_rect = hint_label.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(hint_label, hint_rect)

    def draw_debug_info(self, info: dict):
        """Draw debug information on screen"""
        y_offset = 10
        for key, value in info.items():
            text = self.font_small.render(f"{key}: {value}", True, WHITE)
            self.screen.blit(text, (10, y_offset))
            y_offset += 18
