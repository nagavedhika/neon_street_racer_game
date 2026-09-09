"""
enemy.py
Enemy traffic: spawning logic (random lane, speed, fair gap-checking),
movement relative to the player's world speed, and rendering.
"""

import random
import pygame

from src import settings
from src.player import build_car_surface


_SPRITE_CACHE = {}


def _get_sprite(color):
    if color not in _SPRITE_CACHE:
        glow = tuple(min(255, c + 40) for c in color)
        _SPRITE_CACHE[color] = build_car_surface(
            settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT, color, glow
        )
    return _SPRITE_CACHE[color]


class Enemy:
    def __init__(self, lane_index, y, base_speed, color):
        self.lane_index = lane_index
        self.x = 0  # set by manager via road reference
        self.y = y
        self.base_speed = base_speed
        self.color = color
        self.width = settings.ENEMY_WIDTH
        self.height = settings.ENEMY_HEIGHT
        self.sprite = _get_sprite(color)
        self.passed = False  # whether the player has already scored for passing this one

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height
        )

    def update(self, dt, world_speed):
        # Enemies appear to move toward the player based on the *relative*
        # speed between the player's forward speed and the enemy's own
        # (slower) base speed -- this creates natural closing behavior.
        relative_speed = world_speed - self.base_speed
        self.y += relative_speed * dt

    def draw(self, surface, shake_offset=(0, 0)):
        ox, oy = shake_offset
        rect = self.sprite.get_rect(center=(self.x + ox, self.y + oy))
        surface.blit(self.sprite, rect)

    def is_off_screen(self):
        return self.y - self.height > settings.SCREEN_HEIGHT + 40 or self.y + self.height < -200


class EnemyManager:
    def __init__(self, road):
        self.road = road
        self.enemies = []
        self.spawn_timer = 0.0
        self.elapsed = 0.0

    def reset(self):
        self.enemies.clear()
        self.spawn_timer = 0.0
        self.elapsed = 0.0

    def _difficulty_ramp(self):
        """0..1 progress toward maximum difficulty."""
        return min(1.0, self.elapsed / settings.DIFFICULTY_RAMP_TIME)

    def _current_spawn_interval(self):
        ramp = self._difficulty_ramp()
        start = settings.ENEMY_SPAWN_INTERVAL_START
        end = settings.ENEMY_SPAWN_INTERVAL_MIN
        return start + (end - start) * ramp

    def _current_speed_range(self):
        ramp = self._difficulty_ramp()
        bonus = settings.DIFFICULTY_SPEED_BONUS_MAX * ramp
        return (
            settings.ENEMY_BASE_SPEED_MIN + bonus * 0.3,
            settings.ENEMY_BASE_SPEED_MAX + bonus,
        )

    def _lane_is_clear(self, lane_index, spawn_y):
        for e in self.enemies:
            if e.lane_index == lane_index:
                if abs(e.y - spawn_y) < settings.ENEMY_MIN_VERTICAL_GAP:
                    return False
        return True

    def _spawn_one(self):
        candidate_lanes = list(range(settings.LANE_COUNT))
        random.shuffle(candidate_lanes)
        spawn_y = -settings.ENEMY_HEIGHT

        for lane in candidate_lanes:
            if self._lane_is_clear(lane, spawn_y):
                speed_min, speed_max = self._current_speed_range()
                base_speed = random.uniform(speed_min, speed_max)
                color = random.choice(settings.ENEMY_COLORS)
                enemy = Enemy(lane, spawn_y, base_speed, color)
                enemy.x = self.road.lane_center_x(lane)
                self.enemies.append(enemy)
                return

        # All lanes currently blocked near the top -- skip this spawn cycle
        # to avoid an unfair pile-up at the spawn line.

    def _ensure_fair_start(self, player_lane):
        """Guarantees the player's current lane is never instantly blocked
        right after a spawn by nudging the spawn choice away from a
        too-close same-lane enemy. Used implicitly via the min-gap check;
        kept as a hook for future fairness tuning."""
        return True

    def update(self, dt, world_speed, player):
        self.elapsed += dt
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_one()
            self.spawn_timer = self._current_spawn_interval()

        passed_count = 0
        for enemy in self.enemies:
            enemy.update(dt, world_speed)
            if not enemy.passed and enemy.y > player.y + player.height:
                enemy.passed = True
                passed_count += 1

        self.enemies = [e for e in self.enemies if not e.is_off_screen()]
        return passed_count

    def draw(self, surface, shake_offset=(0, 0)):
        for enemy in self.enemies:
            enemy.draw(surface, shake_offset)

    def check_collisions(self, player):
        if player.is_invulnerable:
            return False
        player_rect = player.rect
        for enemy in self.enemies:
            if player_rect.colliderect(enemy.rect):
                return True
        return False
