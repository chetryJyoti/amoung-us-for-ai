# Among Us AI - Development Log

A phase-by-phase record of what was built.

---

## Phase 1: Game Map Foundation
**Status:** Complete

### What We Built
- Basic pygame application running at 60 FPS (1280x720)
- Minimal test map with 5 rooms connected by hallways
- Collision detection system
- Rendering system for rooms, hallways, and players

### Map Layout
```
        [Navigation]
             |
[Electrical]--[Cafeteria]--[MedBay]
             |
        [Storage]
```

### Files Created
| File | Purpose |
|------|---------|
| `main.py` | Entry point, game loop, test player with keyboard control |
| `game/constants.py` | Screen size, colors, player radius, speeds |
| `game/map.py` | Room, Hallway, GameMap classes |
| `game/renderer.py` | Drawing functions for map and entities |
| `game/__init__.py` | Package exports |

### Key Classes & Methods
- `Room` - dataclass with name, position, size, connections
- `Hallway` - connects two rooms with polygon points
- `GameMap.is_walkable(x, y)` - collision detection
- `GameMap.get_room_at(x, y)` - returns current room name
- `Renderer.draw_map()` - renders rooms and hallways
- `Renderer.draw_player()` - renders colored circle with ID label

### Technical Notes
- Using `pygame-ce` (Community Edition) for Python 3.14 compatibility
- Standard `pygame` has font module issues with Python 3.14

---

## Phase 2: Player Entities & Movement
**Status:** Complete

### What We Built
- `Player` class with id, position, color, provider label, alive status
- `PlayerManager` to spawn and manage multiple players
- Movement system with directional movement and collision detection
- 6 players spawning in Cafeteria with spread-out positions
- Player 1 is keyboard-controlled, others wait for AI (Phase 5)

### Files Created/Modified
| File | Changes |
|------|---------|
| `game/player.py` | NEW - Player, PlayerManager, Direction classes |
| `game/__init__.py` | Added player exports |
| `main.py` | Updated to use PlayerManager |

### Key Classes & Methods
- `Player` - dataclass with id, x, y, color, provider, alive, speed
- `Player.move(direction, game_map)` - move in a direction with collision check
- `Player.move_towards(x, y, game_map)` - move towards a point (for AI)
- `Player.distance_to(other)` - calculate distance to another player
- `PlayerManager.spawn_players(count, providers)` - spawn players in Cafeteria
- `PlayerManager.get_nearby_players(player, radius)` - find players within range
- `PlayerManager.get_players_in_room(room_name)` - find players in a room
- `Direction` - enum for UP, DOWN, LEFT, RIGHT, NONE

### Visual Result
```
[Cafeteria]
  1-You   2-GPT    3-Claude
  4-Gemini 5-GPT   6-Claude
```

---

## Phase 3: Game State & Roles
**Status:** Complete

### What We Built
- `GameState` class managing game phases and role assignments
- `Role` enum: CREWMATE, IMPOSTOR
- `GamePhase` enum: LOBBY, PLAYING, DISCUSSION, VOTING, GAME_OVER
- Random role assignment (1 impostor for 6 players)
- Win condition checking (impostors win / crewmates win)
- Visual role indicator (top-right corner)
- Dead player rendering (faded with X)
- Game over screen with winner announcement
- Restart functionality (R key)

### Files Created/Modified
| File | Changes |
|------|---------|
| `game/state.py` | NEW - GameState, Role, GamePhase, WinReason classes |
| `game/player.py` | Added `role` field to Player |
| `game/renderer.py` | Added role indicator, game over screen, dead player rendering |
| `game/__init__.py` | Added state exports |
| `main.py` | Integrated GameState, added restart and debug kill |

### Key Classes & Methods
- `Role` - enum (CREWMATE, IMPOSTOR)
- `GamePhase` - enum (LOBBY, PLAYING, DISCUSSION, VOTING, GAME_OVER)
- `GameState.start_game()` - assign roles and begin playing
- `GameState.check_win_conditions()` - check if game ended
- `GameState.get_alive_impostors()` / `get_alive_crewmates()` - get living players by role
- `Renderer.draw_role_indicator()` - show "You are: CREWMATE/IMPOSTOR"
- `Renderer.draw_game_over()` - show winner screen

### Win Conditions
- **Impostors win**: When impostors >= crewmates (alive)
- **Crewmates win**: When all impostors are dead

### Test Controls
- `K` - Kill a crewmate (debug, to test win conditions)
- `R` - Restart game with new roles

---

## Phase 4: Visibility System
**Status:** Pending

### Planned
- Players only see nearby players (limited vision)
- Fog of war or vision radius
- This feeds into the AI observation contract

---

## Phase 5: AI Provider Interface
**Status:** Pending

### Planned
- Abstract `AIProvider` base class
- `decide(observation) -> action` interface
- OpenAI, Claude, Gemini adapters
- Rule-based bot for testing
- Non-blocking API calls with timeouts

---

## Phase 6: Discussion & Voting
**Status:** Pending

### Planned
- Discussion phase triggered by body report or emergency button
- Chat system for AI to send messages
- Voting UI and logic
- Ejection based on vote results

---

## Phase 7: Kill Mechanics & Bodies
**Status:** Pending

### Planned
- Impostor kill action (with cooldown)
- Dead bodies on map
- Body reporting system
- Ghost state for dead players

---

## Phase 8: Configuration System
**Status:** Pending

### Planned
- YAML config for player setup
- Assign providers and personalities per player
- Game settings (kill cooldown, vision range, etc.)
- Reproducible seeds for deterministic runs

---

## Dependencies
```
pygame-ce>=2.5.6
pyyaml>=6.0
```

## Running the Game
```bash
cd amoung-us-for-ai
source venv/bin/activate
python main.py
```

**Controls:**
- WASD / Arrow Keys - Move (Player 1)
- K - Kill a crewmate (debug)
- R - Restart game
- ESC - Quit
