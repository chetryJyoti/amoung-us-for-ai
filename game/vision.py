"""
Vision System - Handles visibility, fog of war, and observations for AI
"""

from typing import List, Dict, Any, Optional
from game.constants import VISION_RADIUS_CREWMATE, VISION_RADIUS_IMPOSTOR


class VisionSystem:
    """
    Manages what each player can see.
    This is critical for the AI - they only receive observations
    of what they would realistically see, not global state.
    """

    def __init__(self, game_map, player_manager, game_state):
        self.game_map = game_map
        self.player_manager = player_manager
        self.game_state = game_state

    def get_vision_radius(self, player) -> float:
        """Get the vision radius for a player based on their role"""
        if player.role and player.role.value == "impostor":
            return VISION_RADIUS_IMPOSTOR
        return VISION_RADIUS_CREWMATE

    def get_visible_players(self, player) -> List:
        """
        Get all players visible to a given player.
        A player is visible if within vision radius.
        Dead players (ghosts) can see everyone.
        """
        if not player.alive:
            # Dead players can see everyone
            return [p for p in self.player_manager.players if p.id != player.id]

        vision_radius = self.get_vision_radius(player)
        visible = []

        for other in self.player_manager.players:
            if other.id == player.id:
                continue

            # Check if within vision radius
            distance = player.distance_to(other)
            if distance <= vision_radius:
                visible.append(other)

        return visible

    def get_visible_player_ids(self, player) -> List[int]:
        """Get IDs of visible players"""
        return [p.id for p in self.get_visible_players(player)]

    def is_player_visible(self, observer, target) -> bool:
        """Check if target player is visible to observer"""
        if not observer.alive:
            return True  # Ghosts see everyone

        distance = observer.distance_to(target)
        return distance <= self.get_vision_radius(observer)

    def get_observation(self, player) -> Dict[str, Any]:
        """
        Build the observation dictionary for a player.
        This is what gets sent to the AI provider.

        Matches the observation contract from requirements:
        {
            "self": { "id", "role", "alive" },
            "location": "room_name",
            "visible_players": [ids],
            "recent_events": [...],
            "chat_history": [...],
            "phase": "playing"
        }
        """
        current_room = self.game_map.get_room_at(player.x, player.y)
        visible_players = self.get_visible_players(player)

        # Build visible player info (limited info - just what you can see)
        visible_info = []
        for vp in visible_players:
            info = {
                "id": vp.id,
                "alive": vp.alive,
                "color": vp.color,
                "provider": vp.provider,
            }
            # You can see where visible players are
            vp_room = self.game_map.get_room_at(vp.x, vp.y)
            info["location"] = vp_room or "Hallway"

            # Impostors can see other impostors' roles
            if player.role and player.role.value == "impostor":
                if vp.role and vp.role.value == "impostor":
                    info["role"] = "impostor"

            visible_info.append(info)

        observation = {
            "self": {
                "id": player.id,
                "role": player.role.value if player.role else None,
                "alive": player.alive,
                "position": {"x": player.x, "y": player.y},
            },
            "location": current_room or "Hallway",
            "visible_players": visible_info,
            "visible_player_ids": [vp.id for vp in visible_players],
            "phase": self.game_state.phase.value,
            "round": self.game_state.round_number,
            # These will be populated by the game engine
            "recent_events": [],
            "chat_history": [],
        }

        # Add impostor-specific info
        if player.role and player.role.value == "impostor":
            # Impostors know who the other impostors are
            observation["fellow_impostors"] = [
                pid for pid in self.game_state.get_impostors()
                if pid != player.id
            ]

        return observation

    def get_observation_for_ai(self, player) -> Dict[str, Any]:
        """
        Get a simplified observation suitable for AI prompt.
        Removes some technical details, keeps what's relevant for decision-making.
        """
        obs = self.get_observation(player)

        # Simplify for AI consumption
        ai_obs = {
            "you": {
                "id": obs["self"]["id"],
                "role": obs["self"]["role"],
                "alive": obs["self"]["alive"],
                "current_room": obs["location"],
            },
            "visible_players": [
                {
                    "id": vp["id"],
                    "location": vp["location"],
                    "alive": vp["alive"],
                }
                for vp in obs["visible_players"]
            ],
            "game_phase": obs["phase"],
            "round": obs["round"],
        }

        if "fellow_impostors" in obs:
            ai_obs["fellow_impostors"] = obs["fellow_impostors"]

        return ai_obs


class FogOfWar:
    """
    Handles the visual fog of war effect.
    Areas outside the player's vision are darkened.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def create_fog_surface(self, player_x: int, player_y: int,
                           vision_radius: float, fog_color: tuple) -> 'pygame.Surface':
        """
        Create a fog surface with a circular hole for vision.
        Returns a surface that can be blitted over the game.
        """
        import pygame

        # Create a surface for the fog
        fog = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        fog.fill((*fog_color, 200))  # Semi-transparent fog

        # Create a gradient circle for vision (soft edges)
        # We'll punch a hole in the fog where the player can see
        for r in range(int(vision_radius), 0, -5):
            alpha = int(200 * (1 - (r / vision_radius) ** 0.5))
            pygame.draw.circle(
                fog,
                (*fog_color, alpha),
                (player_x, player_y),
                r
            )

        # Clear center completely (full vision)
        pygame.draw.circle(
            fog,
            (0, 0, 0, 0),  # Fully transparent
            (player_x, player_y),
            int(vision_radius * 0.7)
        )

        return fog

    def create_simple_fog(self, player_x: int, player_y: int,
                          vision_radius: float, fog_color: tuple) -> 'pygame.Surface':
        """
        Create a simple fog with hard-edged circular vision.
        More performant than gradient fog.
        """
        import pygame

        # Create fog surface
        fog = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        fog.fill((*fog_color, 180))  # Semi-transparent fog

        # Cut out circle for vision
        pygame.draw.circle(
            fog,
            (0, 0, 0, 0),  # Fully transparent
            (player_x, player_y),
            int(vision_radius)
        )

        return fog
