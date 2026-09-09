"""
hud.py
On-screen heads-up display during gameplay: score, high score, distance,
lives, and the nitro meter. Also renders the pause overlay and game over
screen contents (layout logic lives in menu.py; this module supplies the
reusable HUD widgets).
"""

import pygame

from src import settings


class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("consolas,couriernew,monospace", 20, bold=True)
        self.font_medium = pygame.font.SysFont("consolas,couriernew,monospace", 28, bold=True)
        self.font_large = pygame.font.SysFont("consolas,couriernew,monospace", 56, bold=True)
        self.clock_font = pygame.font.SysFont("consolas,couriernew,monospace", 16)

    def _draw_text_glow(self, surface, text, font, color, pos, glow_color=None, center=False):
        glow_color = glow_color or color
        base = font.render(text, True, color)
        rect = base.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos

        glow = font.render(text, True, glow_color)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            gsurf = glow.copy()
            gsurf.set_alpha(60)
            surface.blit(gsurf, (rect.x + dx, rect.y + dy), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(base, rect)
        return rect

    def draw_panel(self, surface, rect, alpha=170):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((*settings.COLOR_UI_PANEL, alpha))
        pygame.draw.rect(panel, (*settings.COLOR_UI_ACCENT, 200), panel.get_rect(), width=2, border_radius=10)
        surface.blit(panel, rect.topleft)

    def draw_gameplay_hud(self, surface, score, high_score, distance, lives, nitro, fps=None):
        # Top-left: score / high score / distance panel.
        panel_rect = pygame.Rect(16, 16, 300, 108)
        self.draw_panel(surface, panel_rect)
        self._draw_text_glow(
            surface, f"SCORE  {int(score):06d}", self.font_medium,
            settings.COLOR_WHITE, (panel_rect.x + 14, panel_rect.y + 10),
            glow_color=settings.COLOR_UI_ACCENT
        )
        self._draw_text_glow(
            surface, f"BEST   {int(high_score):06d}", self.font_small,
            settings.COLOR_GREY, (panel_rect.x + 14, panel_rect.y + 46)
        )
        self._draw_text_glow(
            surface, f"DIST   {int(distance):05d}m", self.font_small,
            settings.COLOR_GREY, (panel_rect.x + 14, panel_rect.y + 74)
        )

        # Top-right: lives.
        lives_panel = pygame.Rect(settings.SCREEN_WIDTH - 176, 16, 160, 56)
        self.draw_panel(surface, lives_panel)
        for i in range(settings.PLAYER_START_LIVES):
            cx = lives_panel.x + 30 + i * 46
            cy = lives_panel.y + 28
            color = settings.COLOR_UI_ACCENT if i < lives else (60, 60, 70)
            self._draw_heart(surface, cx, cy, color)

        # Bottom-left: nitro meter.
        meter_rect = pygame.Rect(16, settings.SCREEN_HEIGHT - 56, 260, 26)
        self.draw_panel(surface, meter_rect, alpha=150)
        fill_w = int((meter_rect.width - 8) * (nitro / settings.NITRO_MAX))
        fill_rect = pygame.Rect(meter_rect.x + 4, meter_rect.y + 4, max(0, fill_w), meter_rect.height - 8)
        pygame.draw.rect(surface, settings.COLOR_NITRO, fill_rect, border_radius=6)
        label = self.font_small.render("NITRO", True, settings.COLOR_WHITE)
        surface.blit(label, (meter_rect.x + meter_rect.width + 10, meter_rect.y + 3))

        if fps is not None and settings.SHOW_FPS:
            fps_surf = self.clock_font.render(f"{fps:.0f} FPS", True, settings.COLOR_GREY)
            surface.blit(fps_surf, (settings.SCREEN_WIDTH - 90, settings.SCREEN_HEIGHT - 26))

    def _draw_heart(self, surface, cx, cy, color):
        r = 8
        pygame.draw.circle(surface, color, (cx - r * 0.6, cy - r * 0.3), r)
        pygame.draw.circle(surface, color, (cx + r * 0.6, cy - r * 0.3), r)
        points = [
            (cx - r * 1.5, cy - r * 0.1),
            (cx, cy + r * 1.6),
            (cx + r * 1.5, cy - r * 0.1),
        ]
        pygame.draw.polygon(surface, color, points)

    def draw_center_title(self, surface, text, y, color=None, glow=None):
        color = color or settings.COLOR_WHITE
        glow = glow or settings.COLOR_UI_ACCENT
        return self._draw_text_glow(
            surface, text, self.font_large, color,
            (settings.SCREEN_WIDTH // 2, y), glow_color=glow, center=True
        )

    def draw_center_line(self, surface, text, y, font=None, color=None):
        font = font or self.font_medium
        color = color or settings.COLOR_WHITE
        rect = font.render(text, True, color).get_rect(center=(settings.SCREEN_WIDTH // 2, y))
        surface.blit(font.render(text, True, color), rect)
        return rect
