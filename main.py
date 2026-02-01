"""
Among Us AI - Main Entry Point
An AI experiment where LLM-powered bots play Among Us

Phase 1: Basic map rendering and structure
"""

import pygame
import sys

from game.map import GameMap
from game.renderer import Renderer
from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    PLAYER_COLORS, PLAYER_RADIUS
)


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Among Us AI - Phase 1: Map Test")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize game components
        self.game_map = GameMap()
        self.renderer = Renderer(self.screen)

        # Test player position (will be replaced with proper Player class in Phase 2)
        spawn = self.game_map.get_spawn_point()
        self.test_player_x = spawn[0]
        self.test_player_y = spawn[1]

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Update game state"""
        # Test: Allow keyboard movement for debugging the map
        keys = pygame.key.get_pressed()
        speed = 5

        new_x = self.test_player_x
        new_y = self.test_player_y

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += speed

        # Only move if new position is walkable
        if self.game_map.is_walkable(new_x, new_y):
            self.test_player_x = new_x
            self.test_player_y = new_y

    def render(self):
        """Render the game"""
        # Draw map
        self.renderer.draw_map(self.game_map)

        # Draw test player
        self.renderer.draw_player(
            self.test_player_x,
            self.test_player_y,
            PLAYER_COLORS[0],  # Red
            player_id=1,
            provider="Test",
            radius=PLAYER_RADIUS
        )

        # Draw debug info
        current_room = self.game_map.get_room_at(
            self.test_player_x, self.test_player_y
        )
        self.renderer.draw_debug_info({
            "Phase": "1 - Map Test",
            "Controls": "WASD / Arrow Keys",
            "Room": current_room or "Hallway",
            "Position": f"({self.test_player_x}, {self.test_player_y})"
        })

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
