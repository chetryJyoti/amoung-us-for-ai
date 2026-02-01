"""
Game State - Manages game phases, roles, and win conditions
"""

from enum import Enum
from typing import List, Optional, Dict
import random


class Role(Enum):
    """Player roles"""
    CREWMATE = "crewmate"
    IMPOSTOR = "impostor"


class GamePhase(Enum):
    """Game phases"""
    LOBBY = "lobby"           # Waiting to start
    PLAYING = "playing"       # Main gameplay - moving, tasks, kills
    DISCUSSION = "discussion" # After body found or emergency meeting
    VOTING = "voting"         # Players voting who to eject
    GAME_OVER = "game_over"   # Game ended


class WinReason(Enum):
    """Reason for game ending"""
    IMPOSTORS_KILLED = "All impostors were ejected"
    CREWMATES_KILLED = "Impostors killed enough crewmates"
    TASKS_COMPLETED = "Crewmates completed all tasks"


class GameState:
    """
    Manages the overall game state including:
    - Current phase
    - Role assignments
    - Win conditions
    - Round tracking
    """

    def __init__(self, player_manager):
        self.player_manager = player_manager
        self.phase = GamePhase.LOBBY
        self.round_number = 0
        self.winner: Optional[Role] = None
        self.win_reason: Optional[WinReason] = None

        # Role assignments (player_id -> Role)
        self.roles: Dict[int, Role] = {}

        # Game settings
        self.impostor_count = 1  # Can be 1 or 2 depending on player count

        # Discussion/voting state
        self.discussion_caller_id: Optional[int] = None
        self.votes: Dict[int, int] = {}  # voter_id -> voted_for_id (0 = skip)

    def start_game(self, impostor_count: int = None):
        """
        Start a new game - assign roles and begin playing phase.

        Args:
            impostor_count: Number of impostors (default: auto based on player count)
        """
        players = self.player_manager.players
        player_count = len(players)

        if player_count < 4:
            raise ValueError("Need at least 4 players to start")

        # Determine impostor count
        if impostor_count is None:
            # 4-6 players: 1 impostor, 7+ players: 2 impostors
            self.impostor_count = 1 if player_count <= 6 else 2
        else:
            self.impostor_count = min(impostor_count, player_count // 3)

        # Assign roles randomly
        self._assign_roles()

        # Start the game
        self.phase = GamePhase.PLAYING
        self.round_number = 1
        self.winner = None
        self.win_reason = None

    def _assign_roles(self):
        """Randomly assign roles to all players"""
        players = self.player_manager.players
        player_ids = [p.id for p in players]

        # Shuffle and pick impostors
        random.shuffle(player_ids)
        impostor_ids = set(player_ids[:self.impostor_count])

        # Assign roles
        self.roles = {}
        for player in players:
            if player.id in impostor_ids:
                self.roles[player.id] = Role.IMPOSTOR
                player.role = Role.IMPOSTOR
            else:
                self.roles[player.id] = Role.CREWMATE
                player.role = Role.CREWMATE

    def get_role(self, player_id: int) -> Optional[Role]:
        """Get the role of a player"""
        return self.roles.get(player_id)

    def is_impostor(self, player_id: int) -> bool:
        """Check if a player is an impostor"""
        return self.roles.get(player_id) == Role.IMPOSTOR

    def get_impostors(self) -> List[int]:
        """Get list of impostor player IDs"""
        return [pid for pid, role in self.roles.items() if role == Role.IMPOSTOR]

    def get_crewmates(self) -> List[int]:
        """Get list of crewmate player IDs"""
        return [pid for pid, role in self.roles.items() if role == Role.CREWMATE]

    def get_alive_impostors(self) -> List[int]:
        """Get list of alive impostor player IDs"""
        return [
            pid for pid in self.get_impostors()
            if self.player_manager.get_player(pid).alive
        ]

    def get_alive_crewmates(self) -> List[int]:
        """Get list of alive crewmate player IDs"""
        return [
            pid for pid in self.get_crewmates()
            if self.player_manager.get_player(pid).alive
        ]

    def check_win_conditions(self) -> bool:
        """
        Check if game has ended. Returns True if game is over.
        Sets self.winner and self.win_reason if game ended.
        """
        if self.phase == GamePhase.GAME_OVER:
            return True

        alive_impostors = len(self.get_alive_impostors())
        alive_crewmates = len(self.get_alive_crewmates())

        # Impostors win if they equal or outnumber crewmates
        if alive_impostors >= alive_crewmates:
            self.winner = Role.IMPOSTOR
            self.win_reason = WinReason.CREWMATES_KILLED
            self.phase = GamePhase.GAME_OVER
            return True

        # Crewmates win if all impostors are dead
        if alive_impostors == 0:
            self.winner = Role.CREWMATE
            self.win_reason = WinReason.IMPOSTORS_KILLED
            self.phase = GamePhase.GAME_OVER
            return True

        return False

    def start_discussion(self, caller_id: int):
        """Start a discussion phase (emergency meeting or body report)"""
        if self.phase != GamePhase.PLAYING:
            return

        self.phase = GamePhase.DISCUSSION
        self.discussion_caller_id = caller_id
        self.votes = {}

    def start_voting(self):
        """Transition from discussion to voting"""
        if self.phase != GamePhase.DISCUSSION:
            return

        self.phase = GamePhase.VOTING
        self.votes = {}

    def cast_vote(self, voter_id: int, target_id: int):
        """
        Cast a vote. target_id = 0 means skip vote.

        Args:
            voter_id: The player casting the vote
            target_id: The player being voted for (0 = skip)
        """
        if self.phase != GamePhase.VOTING:
            return

        voter = self.player_manager.get_player(voter_id)
        if not voter or not voter.alive:
            return

        self.votes[voter_id] = target_id

    def tally_votes(self) -> Optional[int]:
        """
        Tally votes and return the ejected player ID.
        Returns None if skipped or tied.
        """
        if not self.votes:
            return None

        # Count votes
        vote_counts: Dict[int, int] = {}
        for target_id in self.votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

        # Find highest vote count
        max_votes = max(vote_counts.values())

        # Check for tie or skip majority
        top_voted = [pid for pid, count in vote_counts.items() if count == max_votes]

        if len(top_voted) > 1 or (0 in top_voted):
            # Tie or skip wins
            return None

        return top_voted[0]

    def eject_player(self, player_id: int):
        """Eject (kill) a player after voting"""
        player = self.player_manager.get_player(player_id)
        if player:
            player.alive = False

    def end_voting(self) -> Optional[int]:
        """
        End voting phase, eject player if applicable, return to playing.
        Returns the ejected player ID or None.
        """
        ejected_id = self.tally_votes()

        if ejected_id and ejected_id != 0:
            self.eject_player(ejected_id)

        # Check win conditions after ejection
        if not self.check_win_conditions():
            self.phase = GamePhase.PLAYING
            self.round_number += 1

        return ejected_id

    def get_state_summary(self) -> dict:
        """Get a summary of the current game state"""
        return {
            "phase": self.phase.value,
            "round": self.round_number,
            "alive_players": len(self.player_manager.get_alive_players()),
            "alive_impostors": len(self.get_alive_impostors()),
            "alive_crewmates": len(self.get_alive_crewmates()),
            "winner": self.winner.value if self.winner else None,
        }
