"""
road.py
Draws the scrolling highway: grass, road surface, edge glow and
dashed lane markings. All road art is generated procedurally with
pygame primitives, no external image assets required.
"""

import pygame

from src import settings


class Road:
    def __init__(self):
        self.scroll_y = 0.0
        # Pre-render a static background tile (grass + road base) that we
        # can blit cheaply, then draw dynamic scrolling elements over it.
        self.static_surface = self._build_static_surface()

    def _build_static_surface(self):
        surf = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        surf.fill(settings.COLOR_BG)

        # Grass with a subtle checker pattern for texture.
        tile = 48
        for y in range(0, settings.SCREEN_HEIGHT, tile):
            for x in range(0, settings.SCREEN_WIDTH, tile):
                if (x // tile + y // tile) % 2 == 0:
                    color = settings.COLOR_GRASS_DARK
                else:
                    color = settings.COLOR_GRASS_LIGHT
                pygame.draw.rect(surf, color, (x, y, tile, tile))

        # Road surface.
        pygame.draw.rect(
            surf, settings.COLOR_ROAD,
            (settings.ROAD_LEFT, 0, settings.ROAD_WIDTH, settings.SCREEN_HEIGHT)
        )
        return surf

    def update(self, dt, world_speed):
        self.scroll_y = (self.scroll_y + world_speed * dt) % (
            settings.LANE_LINE_SEGMENT + settings.LANE_LINE_GAP
        )

    def draw(self, surface, world_speed=0.0, shake_offset=(0, 0)):
        ox, oy = shake_offset
        surface.blit(self.static_surface, (ox, oy))

        # Road edge glow (double line for neon feel).
        left = settings.ROAD_LEFT + ox
        right = settings.ROAD_RIGHT + ox
        edge_w = settings.ROAD_EDGE_WIDTH
        self._draw_glow_line(surface, left, right, edge_w, oy)

        # Dashed lane lines between lanes (not on outer edges).
        segment = settings.LANE_LINE_SEGMENT
        gap = settings.LANE_LINE_GAP
        period = segment + gap
        for lane in range(1, settings.LANE_COUNT):
            lane_x = settings.ROAD_LEFT + lane * settings.LANE_WIDTH + ox
            y = -period + self.scroll_y + oy
            while y < settings.SCREEN_HEIGHT:
                rect = pygame.Rect(
                    int(lane_x - settings.LANE_LINE_WIDTH / 2), int(y),
                    settings.LANE_LINE_WIDTH, segment
                )
                pygame.draw.rect(surface, settings.COLOR_LANE_LINE, rect, border_radius=3)
                y += period

    def _draw_glow_line(self, surface, left, right, edge_w, oy):
        glow_color = settings.COLOR_ROAD_EDGE
        for i, alpha_w in enumerate((edge_w + 8, edge_w + 4, edge_w)):
            alpha = 60 if i < 2 else 255
            layer = pygame.Surface((alpha_w, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            layer.fill((*glow_color, alpha))
            surface.blit(layer, (left - alpha_w / 2, oy), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(layer, (right - alpha_w / 2, oy), special_flags=pygame.BLEND_RGBA_ADD)

    def lane_center_x(self, lane_index):
        return settings.ROAD_LEFT + lane_index * settings.LANE_WIDTH + settings.LANE_WIDTH // 2
