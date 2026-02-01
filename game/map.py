"""
Game Map - Defines rooms, hallways, and connections
Minimal test map with 5 rooms for initial development
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
import pygame

from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ROOM_WIDTH, ROOM_HEIGHT, HALLWAY_WIDTH,
    ROOM_FLOOR, ROOM_BORDER, HALLWAY_COLOR, WHITE
)


@dataclass
class Room:
    """Represents a room on the map"""
    name: str
    x: int
    y: int
    width: int
    height: int
    connections: List[str]  # Names of connected rooms

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def contains_point(self, x: int, y: int) -> bool:
        return self.rect.collidepoint(x, y)


@dataclass
class Hallway:
    """Represents a hallway connecting two rooms"""
    room1: str
    room2: str
    points: List[Tuple[int, int]]  # Path points for drawing


class GameMap:
    """
    Minimal test map layout:

            [Navigation]
                 |
    [Electrical]--[Cafeteria]--[MedBay]
                 |
            [Storage]

    Cafeteria is the central spawn point.
    """

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.hallways: List[Hallway] = []
        self._create_map()

    def _create_map(self):
        """Create the minimal test map"""
        # Center point for Cafeteria
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # Cafeteria (center, larger room - spawn point)
        cafeteria_w, cafeteria_h = 250, 180
        self.rooms["Cafeteria"] = Room(
            name="Cafeteria",
            x=center_x - cafeteria_w // 2,
            y=center_y - cafeteria_h // 2,
            width=cafeteria_w,
            height=cafeteria_h,
            connections=["Electrical", "MedBay", "Navigation", "Storage"]
        )

        # Electrical (left)
        self.rooms["Electrical"] = Room(
            name="Electrical",
            x=center_x - cafeteria_w // 2 - ROOM_WIDTH - 80,
            y=center_y - ROOM_HEIGHT // 2,
            width=ROOM_WIDTH,
            height=ROOM_HEIGHT,
            connections=["Cafeteria"]
        )

        # MedBay (right)
        self.rooms["MedBay"] = Room(
            name="MedBay",
            x=center_x + cafeteria_w // 2 + 80,
            y=center_y - ROOM_HEIGHT // 2,
            width=ROOM_WIDTH,
            height=ROOM_HEIGHT,
            connections=["Cafeteria"]
        )

        # Navigation (top)
        self.rooms["Navigation"] = Room(
            name="Navigation",
            x=center_x - ROOM_WIDTH // 2,
            y=center_y - cafeteria_h // 2 - ROOM_HEIGHT - 80,
            width=ROOM_WIDTH,
            height=ROOM_HEIGHT,
            connections=["Cafeteria"]
        )

        # Storage (bottom)
        self.rooms["Storage"] = Room(
            name="Storage",
            x=center_x - ROOM_WIDTH // 2,
            y=center_y + cafeteria_h // 2 + 80,
            width=ROOM_WIDTH,
            height=ROOM_HEIGHT,
            connections=["Cafeteria"]
        )

        # Create hallways
        self._create_hallways()

    def _create_hallways(self):
        """Create hallway connections between rooms"""
        cafeteria = self.rooms["Cafeteria"]

        # Cafeteria <-> Electrical (horizontal)
        electrical = self.rooms["Electrical"]
        self.hallways.append(Hallway(
            room1="Cafeteria",
            room2="Electrical",
            points=[
                (cafeteria.x, cafeteria.center[1] - HALLWAY_WIDTH // 2),
                (electrical.x + electrical.width, cafeteria.center[1] - HALLWAY_WIDTH // 2),
                (electrical.x + electrical.width, cafeteria.center[1] + HALLWAY_WIDTH // 2),
                (cafeteria.x, cafeteria.center[1] + HALLWAY_WIDTH // 2),
            ]
        ))

        # Cafeteria <-> MedBay (horizontal)
        medbay = self.rooms["MedBay"]
        self.hallways.append(Hallway(
            room1="Cafeteria",
            room2="MedBay",
            points=[
                (cafeteria.x + cafeteria.width, cafeteria.center[1] - HALLWAY_WIDTH // 2),
                (medbay.x, cafeteria.center[1] - HALLWAY_WIDTH // 2),
                (medbay.x, cafeteria.center[1] + HALLWAY_WIDTH // 2),
                (cafeteria.x + cafeteria.width, cafeteria.center[1] + HALLWAY_WIDTH // 2),
            ]
        ))

        # Cafeteria <-> Navigation (vertical)
        navigation = self.rooms["Navigation"]
        self.hallways.append(Hallway(
            room1="Cafeteria",
            room2="Navigation",
            points=[
                (cafeteria.center[0] - HALLWAY_WIDTH // 2, cafeteria.y),
                (cafeteria.center[0] - HALLWAY_WIDTH // 2, navigation.y + navigation.height),
                (cafeteria.center[0] + HALLWAY_WIDTH // 2, navigation.y + navigation.height),
                (cafeteria.center[0] + HALLWAY_WIDTH // 2, cafeteria.y),
            ]
        ))

        # Cafeteria <-> Storage (vertical)
        storage = self.rooms["Storage"]
        self.hallways.append(Hallway(
            room1="Cafeteria",
            room2="Storage",
            points=[
                (cafeteria.center[0] - HALLWAY_WIDTH // 2, cafeteria.y + cafeteria.height),
                (cafeteria.center[0] - HALLWAY_WIDTH // 2, storage.y),
                (cafeteria.center[0] + HALLWAY_WIDTH // 2, storage.y),
                (cafeteria.center[0] + HALLWAY_WIDTH // 2, cafeteria.y + cafeteria.height),
            ]
        ))

    def get_room_at(self, x: int, y: int) -> str | None:
        """Get the room name at a given position, or None if in hallway/void"""
        for name, room in self.rooms.items():
            if room.contains_point(x, y):
                return name
        return None

    def get_spawn_point(self) -> Tuple[int, int]:
        """Get the spawn point (center of Cafeteria)"""
        return self.rooms["Cafeteria"].center

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable (inside a room or hallway)"""
        # Check rooms
        for room in self.rooms.values():
            if room.contains_point(x, y):
                return True

        # Check hallways (simplified - rectangular check)
        for hallway in self.hallways:
            points = hallway.points
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return True

        return False
