"""
Among Us AI - Main Entry Point
An AI experiment where LLM-powered bots play Among Us

Phase 3: Game state and role assignment
"""

import pygame
import sys

from game.map import GameMap
from game.renderer import Renderer
from game.player import PlayerManager, Direction
from game.state import GameState, GamePhase, Role
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Among Us AI - Phase 3: Roles")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize game components
        self.game_map = GameMap()
        self.renderer = Renderer(self.screen)

        # Initialize player manager and spawn players
        self.player_manager = PlayerManager(self.game_map)
        self._spawn_players()

        # Initialize game state
        self.game_state = GameState(self.player_manager)

        # Start the game immediately (auto-assign roles)
        self.game_state.start_game()

        # Player 1 is keyboard-controlled for testing
        self.controlled_player_id = 1

    def _spawn_players(self):
        """Spawn players with different AI providers"""
        providers = [
            "You",      # Player 1 - keyboard controlled
            "GPT",      # Player 2
            "Claude",   # Player 3
            "Gemini",   # Player 4
            "GPT",      # Player 5
            "Claude",   # Player 6
        ]
        self.player_manager.spawn_players(count=6, providers=providers)

    def _restart_game(self):
        """Restart the game with new roles"""
        # Reset all players
        for player in self.player_manager.players:
            player.alive = True
            player.role = None

        # Respawn at cafeteria
        cafeteria = self.game_map.rooms["Cafeteria"]
        positions = self.player_manager._calculate_spawn_positions(
            cafeteria.center[0], cafeteria.center[1],
            len(self.player_manager.players), spread=40
        )
        for i, player in enumerate(self.player_manager.players):
            player.x, player.y = positions[i]

        # Create new game state and start
        self.game_state = GameState(self.player_manager)
        self.game_state.start_game()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Restart game
                    self._restart_game()
                elif event.key == pygame.K_k:
                    # Debug: Kill a random crewmate (test win conditions)
                    if self.game_state.phase == GamePhase.PLAYING:
                        alive_crewmates = self.game_state.get_alive_crewmates()
                        if alive_crewmates:
                            target_id = alive_crewmates[0]
                            target = self.player_manager.get_player(target_id)
                            if target:
                                target.alive = False
                                self.game_state.check_win_conditions()

    def update(self):
        """Update game state"""
        # Only allow movement during playing phase
        if self.game_state.phase != GamePhase.PLAYING:
            return

        # Handle keyboard input for controlled player
        player = self.player_manager.get_player(self.controlled_player_id)
        if player and player.alive:
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
                radius=player.radius,
                alive=player.alive
            )

        # Draw game phase banner
        self.renderer.draw_game_phase_banner(
            self.game_state.phase.value,
            f"Round {self.game_state.round_number}" if self.game_state.phase == GamePhase.PLAYING else None
        )

        # Draw role indicator for controlled player
        controlled = self.player_manager.get_player(self.controlled_player_id)
        if controlled and controlled.role:
            self.renderer.draw_role_indicator(
                controlled.role.value,
                controlled.role == Role.IMPOSTOR
            )

        # Draw game over screen if game ended
        if self.game_state.phase == GamePhase.GAME_OVER:
            self.renderer.draw_game_over(
                self.game_state.winner.value,
                self.game_state.win_reason.value
            )

        # Draw debug info
        state_summary = self.game_state.get_state_summary()
        current_room = self.game_map.get_room_at(controlled.x, controlled.y) if controlled else "?"

        self.renderer.draw_debug_info({
            "Phase": "3 - Roles",
            "Controls": "WASD=Move, K=Kill(test), R=Restart",
            "Your Room": current_room or "Hallway",
            "Alive": f"{state_summary['alive_crewmates']}C / {state_summary['alive_impostors']}I",
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
