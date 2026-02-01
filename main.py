"""
Among Us AI - Main Entry Point
An AI experiment where LLM-powered bots play Among Us

Phase 2: Player entities and movement system
"""

import pygame
import sys

from game.map import GameMap
from game.renderer import Renderer
from game.player import PlayerManager, Direction
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Among Us AI - Phase 2: Players")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize game components
        self.game_map = GameMap()
        self.renderer = Renderer(self.screen)

        # Initialize player manager and spawn players
        self.player_manager = PlayerManager(self.game_map)
        self._spawn_players()

        # Player 1 is keyboard-controlled for testing
        self.controlled_player_id = 1

    def _spawn_players(self):
        """Spawn players with different AI providers"""
        # Mix of providers for testing/demo
        providers = [
            "You",      # Player 1 - keyboard controlled
            "GPT",      # Player 2
            "Claude",   # Player 3
            "Gemini",   # Player 4
            "GPT",      # Player 5
            "Claude",   # Player 6
        ]
        self.player_manager.spawn_players(count=6, providers=providers)

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
        # Handle keyboard input for controlled player
        player = self.player_manager.get_player(self.controlled_player_id)
        if player:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.move(Direction.LEFT, self.game_map)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.move(Direction.RIGHT, self.game_map)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player.move(Direction.UP, self.game_map)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player.move(Direction.DOWN, self.game_map)

        # Update all players (future: AI decisions)
        self.player_manager.update()

    def render(self):
        """Render the game"""
        # Draw map
        self.renderer.draw_map(self.game_map)

        # Draw all players
        for player in self.player_manager.players:
            self.renderer.draw_player(
                int(player.x),
                int(player.y),
                player.color,
                player_id=player.id,
                provider=player.provider,
                radius=player.radius
            )

        # Draw debug info
        controlled = self.player_manager.get_player(self.controlled_player_id)
        current_room = self.game_map.get_room_at(controlled.x, controlled.y) if controlled else "?"

        self.renderer.draw_debug_info({
            "Phase": "2 - Players",
            "Controls": "WASD / Arrow Keys",
            "Players": len(self.player_manager.players),
            "Your Room": current_room or "Hallway",
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
