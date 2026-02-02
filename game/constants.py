# Game Constants

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)

# Room colors
ROOM_FLOOR = (60, 60, 80)
ROOM_BORDER = (100, 100, 120)
HALLWAY_COLOR = (45, 45, 60)

# Player colors (for AI bots)
PLAYER_COLORS = [
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (128, 0, 128),    # Purple
    (0, 255, 255),    # Cyan
    (255, 192, 203),  # Pink
    (255, 255, 255),  # White
    (139, 69, 19),    # Brown
]

# Room dimensions
ROOM_WIDTH = 200
ROOM_HEIGHT = 150
HALLWAY_WIDTH = 40

# Player
PLAYER_RADIUS = 15
PLAYER_SPEED = 3

# Vision
VISION_RADIUS_CREWMATE = 150  # Crewmate vision radius in pixels
VISION_RADIUS_IMPOSTOR = 180  # Impostors see slightly further
FOG_COLOR = (10, 10, 15)      # Color for fog of war
