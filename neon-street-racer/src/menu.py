"""
menu.py
Menu screens: main menu, instructions, pause overlay and game over screen.
Handles simple keyboard-driven selection (Up/Down + Enter) with a subtle
animated neon backdrop, procedurally generated (no external assets).
"""

import math
import random
import pygame

from src import settings


class AnimatedBackdrop:
    """A slow-drifting field of neon dots used behind menu screens."""

    def __init__(self, count=60):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                "x": random.uniform(0, settings.SCREEN_WIDTH),
                "y": random.uniform(0, settings.SCREEN_HEIGHT),
                "speed": random.uniform(30, 140),
                "size": random.uniform(1.5, 3.5),
                "color": random.choice(settings.ENEMY_COLORS + [settings.COLOR_PLAYER]),
            })

    def update(self, dt):
        for s in self.stars:
            s["y"] += s["speed"] * dt
            if s["y"] > settings.SCREEN_HEIGHT + 5:
                s["y"] = -5
                s["x"] = random.uniform(0, settings.SCREEN_WIDTH)

    def draw(self, surface):
        surface.fill(settings.COLOR_BG)
        for s in self.stars:
            glow = pygame.Surface((int(s["size"] * 6), int(s["size"] * 6)), pygame.SRCALPHA)
            gc = glow.get_width() / 2
            pygame.draw.circle(glow, (*s["color"], 90), (gc, gc), s["size"] * 2.2)
            surface.blit(glow, (s["x"] - gc, s["y"] - gc), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.circle(surface, s["color"], (s["x"], s["y"]), s["size"])


class Menu:
    def __init__(self, hud):
        self.hud = hud
        self.backdrop = AnimatedBackdrop()
        self.title_font = pygame.font.SysFont("consolas,couriernew,monospace", 64, bold=True)
        self.option_font = pygame.font.SysFont("consolas,couriernew,monospace", 32, bold=True)
        self.body_font = pygame.font.SysFont("consolas,couriernew,monospace", 22)
        self.small_font = pygame.font.SysFont("consolas,couriernew,monospace", 18)
        self.pulse = 0.0

    def update(self, dt):
        self.backdrop.update(dt)
        self.pulse += dt

    # ------------------------------------------------------------------
    # Shared option-list rendering with a highlighted selection.
    # ------------------------------------------------------------------
    def _draw_options(self, surface, options, selected_index, start_y, spacing=56):
        rects = []
        for i, option in enumerate(options):
            y = start_y + i * spacing
            is_selected = i == selected_index
            color = settings.COLOR_PLAYER if is_selected else settings.COLOR_WHITE
            scale = 1.0 + (0.06 * math.sin(self.pulse * 6)) if is_selected else 1.0

            text_surf = self.option_font.render(option, True, color)
            if scale != 1.0:
                w, h = text_surf.get_size()
                text_surf = pygame.transform.smoothscale(text_surf, (int(w * scale), int(h * scale)))
            rect = text_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, y))

            if is_selected:
                arrow_l = self.option_font.render(">", True, settings.COLOR_UI_ACCENT)
                arrow_r = self.option_font.render("<", True, settings.COLOR_UI_ACCENT)
                surface.blit(arrow_l, (rect.left - 40, rect.top))
                surface.blit(arrow_r, (rect.right + 12, rect.top))

            surface.blit(text_surf, rect)
            rects.append(rect)
        return rects

    def draw_main_menu(self, surface, selected_index, high_score):
        self.backdrop.draw(surface)

        title = "NEON STREET RACER"
        title_surf = self.title_font.render(title, True, settings.COLOR_PLAYER)
        glow_surf = self.title_font.render(title, True, settings.COLOR_UI_ACCENT)
        rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 170))
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            g = glow_surf.copy()
            g.set_alpha(70)
            surface.blit(g, (rect.x + dx, rect.y + dy), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(title_surf, rect)

        subtitle = self.body_font.render("A NEON ARCADE HIGHWAY RACER", True, settings.COLOR_GREY)
        surface.blit(subtitle, subtitle.get_rect(center=(settings.SCREEN_WIDTH // 2, 220)))

        hs = self.small_font.render(f"HIGH SCORE: {int(high_score):06d}", True, settings.COLOR_WHITE)
        surface.blit(hs, hs.get_rect(center=(settings.SCREEN_WIDTH // 2, 260)))

        options = ["START GAME", "INSTRUCTIONS", "QUIT"]
        self._draw_options(surface, options, selected_index, start_y=400)

        footer = self.small_font.render("USE UP/DOWN AND ENTER", True, settings.COLOR_GREY)
        surface.blit(footer, footer.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 40)))

    def draw_instructions(self, surface):
        self.backdrop.draw(surface)
        self.hud.draw_center_title(surface, "INSTRUCTIONS", 90)

        lines = [
            ("CONTROLS", settings.COLOR_PLAYER),
            ("W / UP        Accelerate", settings.COLOR_WHITE),
            ("S / DOWN      Brake / Reverse", settings.COLOR_WHITE),
            ("A / LEFT      Steer Left", settings.COLOR_WHITE),
            ("D / RIGHT     Steer Right", settings.COLOR_WHITE),
            ("SPACE         Nitro Boost", settings.COLOR_WHITE),
            ("ESC           Pause", settings.COLOR_WHITE),
            ("R             Restart after Game Over", settings.COLOR_WHITE),
            ("", settings.COLOR_WHITE),
            ("OBJECTIVE", settings.COLOR_PLAYER),
            ("Survive the highway, dodge traffic, and rack", settings.COLOR_WHITE),
            ("up distance and score. You have 3 lives -- a", settings.COLOR_WHITE),
            ("collision costs one and grants brief invulnerability.", settings.COLOR_WHITE),
            ("", settings.COLOR_WHITE),
            ("NITRO", settings.COLOR_PLAYER),
            ("Hold SPACE to burn nitro for a burst of speed.", settings.COLOR_WHITE),
            ("The meter drains while active and slowly refills.", settings.COLOR_WHITE),
            ("", settings.COLOR_WHITE),
            ("POWER-UPS", settings.COLOR_PLAYER),
            ("BOOST  - temporary top speed increase", settings.COLOR_BOOST),
            ("SHIELD - temporary collision immunity", settings.COLOR_SHIELD),
            ("REPAIR - restores one lost life", settings.COLOR_REPAIR),
        ]

        y = 150
        for text, color in lines:
            if text:
                surf = self.body_font.render(text, True, color)
                surface.blit(surf, surf.get_rect(midleft=(settings.SCREEN_WIDTH // 2 - 260, y)))
            y += 24

        footer = self.small_font.render("PRESS ESC OR ENTER TO RETURN", True, settings.COLOR_GREY)
        surface.blit(footer, footer.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 40)))

    def draw_pause(self, surface, game_surface, selected_index):
        surface.blit(game_surface, (0, 0))
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.hud.draw_center_title(surface, "PAUSED", 220)
        options = ["RESUME", "RESTART", "MAIN MENU"]
        self._draw_options(surface, options, selected_index, start_y=360)

    def draw_game_over(self, surface, selected_index, score, high_score, distance, new_high_score):
        self.backdrop.draw(surface)
        self.hud.draw_center_title(surface, "GAME OVER", 130, color=settings.COLOR_UI_ACCENT, glow=settings.COLOR_UI_ACCENT)

        if new_high_score:
            tag = self.body_font.render("NEW HIGH SCORE!", True, settings.COLOR_BOOST)
            surface.blit(tag, tag.get_rect(center=(settings.SCREEN_WIDTH // 2, 190)))

        stats = [
            f"FINAL SCORE   {int(score):06d}",
            f"HIGH SCORE    {int(high_score):06d}",
            f"DISTANCE      {int(distance):05d} m",
        ]
        y = 240
        for line in stats:
            surf = self.option_font.render(line, True, settings.COLOR_WHITE)
            surface.blit(surf, surf.get_rect(center=(settings.SCREEN_WIDTH // 2, y)))
            y += 42

        options = ["RESTART", "MAIN MENU", "QUIT"]
        self._draw_options(surface, options, selected_index, start_y=440)

        footer = self.small_font.render("PRESS R TO QUICK-RESTART", True, settings.COLOR_GREY)
        surface.blit(footer, footer.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 40)))
