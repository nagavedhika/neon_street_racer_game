"""
player.py
Player-controlled car: movement physics (acceleration, braking, steering
with inertia), nitro boost, shield/power-up state, collision handling and
procedural rendering of a neon sports car sprite.
"""

import math
import pygame

from src import settings


def build_car_surface(width, height, body_color, glow_color, window_color=(20, 24, 34)):
    """Procedurally builds a small top-down car sprite with a neon glow."""
    pad = 14
    surf = pygame.Surface((width + pad * 2, height + pad * 2), pygame.SRCALPHA)
    cx = surf.get_width() // 2
    cy = surf.get_height() // 2

    body_rect = pygame.Rect(0, 0, width, height)
    body_rect.center = (cx, cy)

    # Soft outer glow (a few translucent expanding rounded rects).
    for i in range(4, 0, -1):
        glow_rect = body_rect.inflate(i * 6, i * 6)
        glow_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*glow_color, 18), glow_rect, border_radius=18)
        surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Car body.
    pygame.draw.rect(surf, body_color, body_rect, border_radius=14)
    pygame.draw.rect(surf, (255, 255, 255), body_rect, width=2, border_radius=14)

    # Windshield / cabin.
    cabin_rect = pygame.Rect(0, 0, width * 0.62, height * 0.32)
    cabin_rect.center = (cx, cy - height * 0.10)
    pygame.draw.rect(surf, window_color, cabin_rect, border_radius=8)

    # Rear window.
    rear_rect = pygame.Rect(0, 0, width * 0.5, height * 0.16)
    rear_rect.center = (cx, cy + height * 0.30)
    pygame.draw.rect(surf, window_color, rear_rect, border_radius=6)

    # Headlights / taillights for orientation.
    light_w = width * 0.16
    light_h = height * 0.06
    for dx in (-1, 1):
        head = pygame.Rect(0, 0, light_w, light_h)
        head.center = (cx + dx * width * 0.28, cy - height * 0.46)
        pygame.draw.rect(surf, (255, 255, 210), head, border_radius=3)

        tail = pygame.Rect(0, 0, light_w, light_h)
        tail.center = (cx + dx * width * 0.28, cy + height * 0.46)
        pygame.draw.rect(surf, (255, 60, 60), tail, border_radius=3)

    # Center racing stripe.
    stripe_rect = pygame.Rect(0, 0, width * 0.14, height * 0.86)
    stripe_rect.center = (cx, cy)
    pygame.draw.rect(surf, (255, 255, 255), stripe_rect, border_radius=6)

    return surf


class Player:
    def __init__(self, road):
        self.road = road
        self.width = settings.CAR_WIDTH
        self.height = settings.CAR_HEIGHT

        self.x = road.lane_center_x(settings.PLAYER_START_X_LANE)
        self.y = settings.SCREEN_HEIGHT - 150
        self.vx = 0.0
        self.speed = settings.PLAYER_MIN_SPEED  # forward world speed

        self.lives = settings.PLAYER_START_LIVES
        self.invulnerable_timer = 0.0
        self.hit_flash_timer = 0.0

        self.nitro = settings.NITRO_MAX
        self.nitro_active = False

        self.shield_timer = 0.0
        self.boost_timer = 0.0

        self.sprite = build_car_surface(
            self.width, self.height, settings.COLOR_PLAYER, settings.COLOR_PLAYER_GLOW
        )
        self.shield_pulse = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height
        )

    @property
    def is_invulnerable(self):
        return self.invulnerable_timer > 0 or self.shield_timer > 0

    def handle_input(self, dt, keys):
        accelerating = keys[pygame.K_w] or keys[pygame.K_UP]
        braking = keys[pygame.K_s] or keys[pygame.K_DOWN]
        steer_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        steer_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        want_nitro = keys[pygame.K_SPACE]

        # --- Forward speed (acceleration / braking / drag) ---
        if accelerating:
            self.speed += settings.PLAYER_ACCEL * dt
        elif braking:
            self.speed -= settings.PLAYER_BRAKE_DECEL * dt
        else:
            # Natural drag pulls speed back toward the minimum cruising speed.
            if self.speed > settings.PLAYER_MIN_SPEED:
                self.speed -= settings.PLAYER_NATURAL_DECEL * dt
            elif self.speed < settings.PLAYER_MIN_SPEED:
                self.speed += settings.PLAYER_NATURAL_DECEL * dt

        max_speed = settings.PLAYER_MAX_SPEED
        if self.boost_timer > 0:
            max_speed *= settings.BOOST_SPEED_MULT

        # --- Nitro ---
        self.nitro_active = False
        if want_nitro and self.nitro > settings.NITRO_MIN_TO_ACTIVATE:
            self.nitro_active = True
            self.nitro = max(0.0, self.nitro - settings.NITRO_DRAIN_RATE * dt)
            max_speed *= settings.NITRO_SPEED_MULT
        else:
            self.nitro = min(settings.NITRO_MAX, self.nitro + settings.NITRO_REGEN_RATE * dt)

        self.speed = max(settings.PLAYER_REVERSE_SPEED, min(max_speed, self.speed))

        # --- Steering with inertia ---
        target_vx = 0.0
        if steer_left and not steer_right:
            target_vx = -settings.PLAYER_STEER_SPEED
        elif steer_right and not steer_left:
            target_vx = settings.PLAYER_STEER_SPEED

        if target_vx != 0.0:
            if self.vx < target_vx:
                self.vx = min(target_vx, self.vx + settings.PLAYER_STEER_ACCEL * dt)
            else:
                self.vx = max(target_vx, self.vx - settings.PLAYER_STEER_ACCEL * dt)
        else:
            if self.vx > 0:
                self.vx = max(0.0, self.vx - settings.PLAYER_STEER_FRICTION * dt)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + settings.PLAYER_STEER_FRICTION * dt)

        self.x += self.vx * dt

        # Clamp to road bounds.
        half_w = self.width / 2
        min_x = settings.ROAD_LEFT + half_w + 6
        max_x = settings.ROAD_RIGHT - half_w - 6
        if self.x < min_x:
            self.x = min_x
            self.vx = 0.0
        elif self.x > max_x:
            self.x = max_x
            self.vx = 0.0

    def update(self, dt):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.shield_timer > 0:
            self.shield_timer -= dt
        if self.boost_timer > 0:
            self.boost_timer -= dt
        self.shield_pulse += dt * 6.0

    def apply_powerup(self, kind):
        if kind == "shield":
            self.shield_timer = settings.SHIELD_DURATION
        elif kind == "boost":
            self.boost_timer = settings.BOOST_DURATION
        elif kind == "repair":
            self.lives = min(settings.PLAYER_START_LIVES, self.lives + 1)

    def take_hit(self):
        """Returns True if the hit actually damaged the player (not invulnerable)."""
        if self.is_invulnerable:
            return False
        self.lives -= 1
        self.invulnerable_timer = settings.PLAYER_INVULNERABLE_TIME
        self.hit_flash_timer = 0.35
        self.speed = max(settings.PLAYER_MIN_SPEED * 0.5, self.speed - 120)
        return True

    def draw(self, surface, shake_offset=(0, 0)):
        ox, oy = shake_offset
        draw_x = self.x + ox
        draw_y = self.y + oy

        # Flicker while invulnerable (but not when a shield is actively up,
        # which gets its own persistent ring instead).
        visible = True
        if self.invulnerable_timer > 0 and self.shield_timer <= 0:
            visible = int(self.invulnerable_timer * 12) % 2 == 0

        if visible:
            rect = self.sprite.get_rect(center=(draw_x, draw_y))
            surface.blit(self.sprite, rect)

        if self.hit_flash_timer > 0:
            flash = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
            alpha = int(180 * (self.hit_flash_timer / 0.35))
            flash.fill((255, 255, 255, alpha))
            rect = self.sprite.get_rect(center=(draw_x, draw_y))
            surface.blit(flash, rect, special_flags=pygame.BLEND_RGBA_ADD)

        if self.shield_timer > 0:
            radius = max(self.width, self.height) * 0.62 + math.sin(self.shield_pulse) * 3
            ring_surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                ring_surf, (*settings.COLOR_SHIELD, 110),
                (radius + 4, radius + 4), radius, width=4
            )
            rect = ring_surf.get_rect(center=(draw_x, draw_y))
            surface.blit(ring_surf, rect, special_flags=pygame.BLEND_RGBA_ADD)

        if self.boost_timer > 0:
            tint = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
            tint.fill((*settings.COLOR_BOOST, 40))
            rect = self.sprite.get_rect(center=(draw_x, draw_y))
            surface.blit(tint, rect, special_flags=pygame.BLEND_RGBA_ADD)

    def speed_factor(self):
        """Normalized 0..1+ speed used for visual effects like speed lines."""
        return max(0.0, self.speed / settings.PLAYER_MAX_SPEED)
