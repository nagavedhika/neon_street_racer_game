"""
powerup.py
Random power-up pickups that scroll down the road: nitro boost,
shield, and repair (extra life). Includes spawn timing and rendering.
"""

import math
import random
import pygame

from src import settings


_ICON_COLORS = {
    "boost": settings.COLOR_BOOST,
    "shield": settings.COLOR_SHIELD,
    "repair": settings.COLOR_REPAIR,
}


class PowerUp:
    def __init__(self, kind, lane_index, y):
        self.kind = kind
        self.lane_index = lane_index
        self.x = 0
        self.y = y
        self.size = settings.POWERUP_SIZE
        self.pulse = random.uniform(0, 6.28)

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2), int(self.y - self.size / 2),
            self.size, self.size
        )

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.pulse += dt * 4.0

    def is_off_screen(self):
        return self.y - self.size > settings.SCREEN_HEIGHT + 40

    def draw(self, surface, shake_offset=(0, 0)):
        ox, oy = shake_offset
        color = _ICON_COLORS[self.kind]
        cx, cy = self.x + ox, self.y + oy
        pulse_radius = self.size / 2 + math.sin(self.pulse) * 3

        glow = pygame.Surface((int(pulse_radius * 3), int(pulse_radius * 3)), pygame.SRCALPHA)
        gcx, gcy = glow.get_width() / 2, glow.get_height() / 2
        pygame.draw.circle(glow, (*color, 70), (gcx, gcy), pulse_radius * 1.4)
        surface.blit(glow, (cx - gcx, cy - gcy), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.circle(surface, color, (cx, cy), self.size / 2)
        pygame.draw.circle(surface, settings.COLOR_WHITE, (cx, cy), self.size / 2, width=2)

        if self.kind == "boost":
            self._draw_lightning(surface, cx, cy)
        elif self.kind == "shield":
            self._draw_shield_icon(surface, cx, cy)
        elif self.kind == "repair":
            self._draw_plus(surface, cx, cy)

    def _draw_lightning(self, surface, cx, cy):
        s = self.size * 0.28
        points = [
            (cx - s * 0.2, cy - s), (cx + s * 0.5, cy - s * 0.1),
            (cx + s * 0.05, cy - s * 0.1), (cx + s * 0.3, cy + s),
            (cx - s * 0.5, cy + s * 0.1), (cx - s * 0.05, cy + s * 0.1),
        ]
        pygame.draw.polygon(surface, settings.COLOR_BLACK, points)

    def _draw_shield_icon(self, surface, cx, cy):
        s = self.size * 0.3
        points = [
            (cx, cy - s), (cx + s * 0.85, cy - s * 0.4),
            (cx + s * 0.6, cy + s * 0.8), (cx, cy + s),
            (cx - s * 0.6, cy + s * 0.8), (cx - s * 0.85, cy - s * 0.4),
        ]
        pygame.draw.polygon(surface, settings.COLOR_BLACK, points, width=3)

    def _draw_plus(self, surface, cx, cy):
        s = self.size * 0.28
        pygame.draw.rect(surface, settings.COLOR_BLACK, (cx - s * 0.18, cy - s, s * 0.36, s * 2))
        pygame.draw.rect(surface, settings.COLOR_BLACK, (cx - s, cy - s * 0.18, s * 2, s * 0.36))


class PowerUpManager:
    def __init__(self, road):
        self.road = road
        self.powerups = []
        self.spawn_timer = random.uniform(
            settings.POWERUP_SPAWN_INTERVAL_MIN, settings.POWERUP_SPAWN_INTERVAL_MAX
        )

    def reset(self):
        self.powerups.clear()
        self.spawn_timer = random.uniform(
            settings.POWERUP_SPAWN_INTERVAL_MIN, settings.POWERUP_SPAWN_INTERVAL_MAX
        )

    def update(self, dt, world_speed):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_one()
            self.spawn_timer = random.uniform(
                settings.POWERUP_SPAWN_INTERVAL_MIN, settings.POWERUP_SPAWN_INTERVAL_MAX
            )

        for p in self.powerups:
            p.update(dt, world_speed)
        self.powerups = [p for p in self.powerups if not p.is_off_screen()]

    def _spawn_one(self):
        lane = random.randrange(settings.LANE_COUNT)
        kind = random.choice(settings.POWERUP_TYPES)
        powerup = PowerUp(kind, lane, -settings.POWERUP_SIZE)
        powerup.x = self.road.lane_center_x(lane)
        self.powerups.append(powerup)

    def draw(self, surface, shake_offset=(0, 0)):
        for p in self.powerups:
            p.draw(surface, shake_offset)

    def check_pickups(self, player):
        collected = []
        player_rect = player.rect
        remaining = []
        for p in self.powerups:
            if player_rect.colliderect(p.rect):
                collected.append(p)
            else:
                remaining.append(p)
        self.powerups = remaining
        return collected
