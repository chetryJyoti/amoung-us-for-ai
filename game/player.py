"""
Player - Player entity and management
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import random

from game.constants import PLAYER_COLORS, PLAYER_SPEED, PLAYER_RADIUS


class Direction(Enum):
    """Movement directions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


@dataclass
class Player:
    """Represents a player in the game"""
    id: int
    x: float
    y: float
    color: Tuple[int, int, int]
    provider: str = "Bot"  # e.g., "GPT", "Claude", "Gemini", "Rule"
    alive: bool = True
    speed: float = PLAYER_SPEED
    radius: int = PLAYER_RADIUS
    role: any = None  # Set by GameState (Role.CREWMATE or Role.IMPOSTOR)

    def move(self, direction: Direction, game_map) -> bool:
        """
        Move player in a direction if the destination is walkable.
        Returns True if movement occurred.
        """
        if not self.alive:
            return False

        new_x, new_y = self.x, self.y

        if direction == Direction.UP:
            new_y -= self.speed
        elif direction == Direction.DOWN:
            new_y += self.speed
        elif direction == Direction.LEFT:
            new_x -= self.speed
        elif direction == Direction.RIGHT:
            new_x += self.speed
        else:
            return False

        # Check if new position is walkable
        if game_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False

    def move_towards(self, target_x: float, target_y: float, game_map) -> bool:
        """
        Move towards a target position (for AI pathfinding).
        Returns True if movement occurred.
        """
        if not self.alive:
            return False

        dx = target_x - self.x
        dy = target_y - self.y

        # Normalize and apply speed
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < self.speed:
            return False  # Already at target

        new_x = self.x + (dx / distance) * self.speed
        new_y = self.y + (dy / distance) * self.speed

        if game_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False

    def get_position(self) -> Tuple[float, float]:
        """Get current position"""
        return (self.x, self.y)

    def distance_to(self, other: 'Player') -> float:
        """Calculate distance to another player"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def distance_to_point(self, x: float, y: float) -> float:
        """Calculate distance to a point"""
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5


class PlayerManager:
    """Manages all players in the game"""

    def __init__(self, game_map):
        self.game_map = game_map
        self.players: List[Player] = []

    def spawn_players(self, count: int, providers: List[str] = None):
        """
        Spawn players in the Cafeteria with spread-out positions.

        Args:
            count: Number of players to spawn (max 10)
            providers: List of provider names (e.g., ["GPT", "Claude", "Gemini"])
                      If None, defaults to "Bot" for all
        """
        count = min(count, 10)  # Max 10 players (colors limit)

        if providers is None:
            providers = ["Bot"] * count

        # Extend providers list if needed
        while len(providers) < count:
            providers.append("Bot")

        # Get spawn area (Cafeteria)
        cafeteria = self.game_map.rooms["Cafeteria"]
        center_x, center_y = cafeteria.center

        # Calculate spawn positions in a grid pattern
        spawn_positions = self._calculate_spawn_positions(
            center_x, center_y, count, spread=40
        )

        # Create players
        for i in range(count):
            x, y = spawn_positions[i]
            player = Player(
                id=i + 1,
                x=x,
                y=y,
                color=PLAYER_COLORS[i],
                provider=providers[i]
            )
            self.players.append(player)

    def _calculate_spawn_positions(
        self, center_x: float, center_y: float, count: int, spread: int
    ) -> List[Tuple[float, float]]:
        """Calculate spread-out spawn positions around a center point"""
        positions = []

        # Arrange in rows
        cols = 4
        rows = (count + cols - 1) // cols

        start_x = center_x - (min(count, cols) - 1) * spread / 2
        start_y = center_y - (rows - 1) * spread / 2

        for i in range(count):
            row = i // cols
            col = i % cols
            x = start_x + col * spread
            y = start_y + row * spread
            positions.append((x, y))

        return positions

    def get_player(self, player_id: int) -> Optional[Player]:
        """Get player by ID"""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_alive_players(self) -> List[Player]:
        """Get all alive players"""
        return [p for p in self.players if p.alive]

    def get_players_in_room(self, room_name: str) -> List[Player]:
        """Get all players in a specific room"""
        result = []
        for player in self.players:
            current_room = self.game_map.get_room_at(player.x, player.y)
            if current_room == room_name:
                result.append(player)
        return result

    def get_nearby_players(self, player: Player, radius: float) -> List[Player]:
        """Get all players within a certain radius of a player"""
        nearby = []
        for other in self.players:
            if other.id != player.id and other.alive:
                if player.distance_to(other) <= radius:
                    nearby.append(other)
        return nearby

    def check_player_collision(self, player: Player, new_x: float, new_y: float) -> bool:
        """Check if moving to new position would collide with another player"""
        for other in self.players:
            if other.id != player.id and other.alive:
                dist = ((new_x - other.x) ** 2 + (new_y - other.y) ** 2) ** 0.5
                if dist < player.radius + other.radius:
                    return True
        return False

    def update(self):
        """Update all players (called each frame)"""
        # Future: AI decision ticks, animations, etc.
        pass
