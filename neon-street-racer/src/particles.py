"""
particles.py
A lightweight particle system used for speed lines, nitro flame trails,
collision sparks and power-up sparkles. Designed to be cheap to update
and draw so it stays smooth even on modest hardware.
"""

import random
import pygame

from src import settings


class Particle:
    __slots__ = (
        "x", "y", "vx", "vy", "life", "max_life", "size", "color", "shrink", "gravity"
    )

    def __init__(self, x, y, vx, vy, life, size, color, shrink=True, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.shrink = shrink
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        t = max(0.0, self.life / self.max_life)
        alpha = int(255 * t)
        size = self.size * (t if self.shrink else 1.0)
        if size < 0.5:
            return
        radius = max(1, int(size))
        temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        color = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(temp, color, (radius, radius), radius)
        surface.blit(temp, (self.x - radius, self.y - radius), special_flags=pygame.BLEND_RGBA_ADD)


class ParticleSystem:
    """Manages a pool of particles with a soft cap to avoid unbounded growth."""

    def __init__(self, max_particles=settings.MAX_PARTICLES):
        self.particles = []
        self.max_particles = max_particles

    def _add(self, particle):
        if len(self.particles) >= self.max_particles:
            # Drop the oldest particle to make room.
            self.particles.pop(0)
        self.particles.append(particle)

    def emit_speed_lines(self, x, y, speed_factor):
        """Streaks that fly past the player to sell a sense of speed."""
        if speed_factor < 0.35:
            return
        if random.random() < speed_factor * 0.6:
            side = random.choice([-1, 1])
            px = x + side * random.uniform(140, 320)
            py = y - random.uniform(200, 320)
            vy = 900 + speed_factor * 700
            self._add(Particle(
                px, py, 0, vy, life=0.35, size=random.uniform(2, 4),
                color=(200, 230, 255), shrink=True
            ))

    def emit_nitro_flame(self, x, y):
        for _ in range(2):
            vx = random.uniform(-40, 40)
            vy = random.uniform(220, 420)
            color = random.choice([
                (255, 140, 0), (255, 200, 40), (255, 60, 0)
            ])
            self._add(Particle(
                x + random.uniform(-8, 8), y, vx, vy,
                life=random.uniform(0.25, 0.5),
                size=random.uniform(4, 9),
                color=color, shrink=True
            ))

    def emit_collision(self, x, y):
        for _ in range(28):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(80, 380)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            color = random.choice([
                (255, 220, 60), (255, 120, 30), (255, 250, 220)
            ])
            self._add(Particle(
                x, y, vx, vy, life=random.uniform(0.3, 0.7),
                size=random.uniform(3, 7), color=color, shrink=True, gravity=200
            ))

    def emit_powerup_sparkle(self, x, y, color):
        for _ in range(10):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(20, 90)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            self._add(Particle(
                x, y, vx, vy, life=random.uniform(0.4, 0.9),
                size=random.uniform(2, 5), color=color, shrink=True
            ))

    def emit_pickup_burst(self, x, y, color):
        for _ in range(22):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(60, 260)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            self._add(Particle(
                x, y, vx, vy, life=random.uniform(0.35, 0.75),
                size=random.uniform(3, 6), color=color, shrink=True
            ))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()
