"""
settings.py
Central configuration for Neon Street Racer.
All tunable constants live here so gameplay can be balanced in one place.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
DATA_DIR = os.path.join(BASE_DIR, "data")
HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscore.json")

# ---------------------------------------------------------------------------
# Window / display
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Neon Street Racer"
SHOW_FPS = False  # set True for debugging

# ---------------------------------------------------------------------------
# Colors (neon / arcade palette)
# ---------------------------------------------------------------------------
COLOR_BG = (8, 8, 18)
COLOR_ROAD = (24, 22, 38)
COLOR_ROAD_EDGE = (255, 42, 109)
COLOR_LANE_LINE = (0, 229, 255)
COLOR_GRASS_DARK = (10, 30, 20)
COLOR_GRASS_LIGHT = (14, 40, 26)

COLOR_PLAYER = (0, 229, 255)
COLOR_PLAYER_GLOW = (0, 180, 255)

ENEMY_COLORS = [
    (255, 42, 109),   # neon pink/red
    (255, 176, 0),    # neon amber
    (162, 0, 255),    # neon purple
    (57, 255, 20),    # neon green
    (255, 255, 0),    # neon yellow
]

COLOR_WHITE = (240, 240, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (120, 120, 140)
COLOR_SHIELD = (0, 229, 255)
COLOR_BOOST = (255, 176, 0)
COLOR_REPAIR = (57, 255, 20)
COLOR_UI_PANEL = (18, 16, 30)
COLOR_UI_ACCENT = (255, 42, 109)
COLOR_NITRO = (255, 105, 0)

# ---------------------------------------------------------------------------
# Road geometry
# ---------------------------------------------------------------------------
LANE_COUNT = 4
ROAD_WIDTH = 760
ROAD_LEFT = (SCREEN_WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
ROAD_EDGE_WIDTH = 10
LANE_LINE_WIDTH = 6
LANE_LINE_SEGMENT = 40
LANE_LINE_GAP = 30

# ---------------------------------------------------------------------------
# Player car
# ---------------------------------------------------------------------------
CAR_WIDTH = 54
CAR_HEIGHT = 96

PLAYER_START_X_LANE = 1  # zero-indexed lane the player starts in (0..LANE_COUNT-1)
PLAYER_MAX_SPEED = 620.0          # px/sec forward (visual world speed)
PLAYER_MIN_SPEED = 90.0           # px/sec minimum forward speed (idle creep)
PLAYER_REVERSE_SPEED = -140.0     # px/sec while braking hard / reversing
PLAYER_ACCEL = 420.0              # px/sec^2 while accelerating
PLAYER_BRAKE_DECEL = 620.0        # px/sec^2 while braking
PLAYER_NATURAL_DECEL = 160.0      # px/sec^2 natural drag when no input
PLAYER_STEER_SPEED = 560.0        # px/sec horizontal movement speed
PLAYER_STEER_ACCEL = 3200.0       # px/sec^2 horizontal acceleration (inertia)
PLAYER_STEER_FRICTION = 2600.0    # px/sec^2 horizontal friction when no steering input

NITRO_MAX = 100.0
NITRO_DRAIN_RATE = 42.0     # per second while active
NITRO_REGEN_RATE = 12.0     # per second while inactive
NITRO_SPEED_MULT = 1.65
NITRO_MIN_TO_ACTIVATE = 8.0

PLAYER_START_LIVES = 3
PLAYER_INVULNERABLE_TIME = 1.6   # seconds of invulnerability after a hit
PLAYER_COLLISION_KNOCKBACK = 140.0

# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------
ENEMY_WIDTH = 54
ENEMY_HEIGHT = 96
ENEMY_BASE_SPEED_MIN = 160.0     # relative closing speed baseline
ENEMY_BASE_SPEED_MAX = 260.0
ENEMY_SPAWN_INTERVAL_START = 1.35   # seconds between spawns at start
ENEMY_SPAWN_INTERVAL_MIN = 0.45     # fastest spawn interval at max difficulty
ENEMY_MIN_VERTICAL_GAP = 210.0      # minimum vertical gap between enemies in same lane
DIFFICULTY_RAMP_TIME = 90.0         # seconds to reach max difficulty ramp
DIFFICULTY_SPEED_BONUS_MAX = 220.0  # extra speed added at full ramp

# ---------------------------------------------------------------------------
# Power-ups
# ---------------------------------------------------------------------------
POWERUP_SIZE = 40
POWERUP_SPAWN_INTERVAL_MIN = 5.0
POWERUP_SPAWN_INTERVAL_MAX = 10.0
POWERUP_TYPES = ("boost", "shield", "repair")
SHIELD_DURATION = 6.0
BOOST_DURATION = 4.0
BOOST_SPEED_MULT = 1.4

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
SCORE_PER_METER = 1.0          # score per unit distance travelled
SCORE_PASS_BONUS = 25          # bonus score for passing an enemy car
DISTANCE_PER_SCORE_UNIT = 0.1  # how "distance" (meters) maps to world scroll px

# ---------------------------------------------------------------------------
# Particles
# ---------------------------------------------------------------------------
MAX_PARTICLES = 400

# ---------------------------------------------------------------------------
# Game states
# ---------------------------------------------------------------------------
STATE_MAIN_MENU = "main_menu"
STATE_INSTRUCTIONS = "instructions"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_QUIT = "quit"
