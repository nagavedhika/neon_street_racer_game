"""
game.py
Top-level Game class: owns the pygame window, the state machine
(main menu / instructions / playing / paused / game over), and wires
together the road, player, enemies, power-ups, particles, HUD, menus
and audio into a single cohesive game loop.
"""

import random
import asyncio

import pygame

from src import settings
from src import highscore
from src.road import Road
from src.player import Player
from src.enemy import EnemyManager
from src.powerup import PowerUpManager
from src.particles import ParticleSystem
from src.hud import HUD
from src.menu import Menu
from src.audio import AudioEngine


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE
        )
        # We always render to a fixed-size internal surface and scale it to
        # the actual window size, so the game "scales reasonably" when the
        # window is resized without needing to rebuild any game logic.
        self.render_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.audio = AudioEngine()
        self.hud = HUD()
        self.menu = Menu(self.hud)

        self.high_score = highscore.load_high_score()

        self.state = settings.STATE_MAIN_MENU
        self.main_menu_index = 0
        self.pause_index = 0
        self.game_over_index = 0
        self.previous_state_for_instructions = settings.STATE_MAIN_MENU

        self.running = True

        self._init_gameplay_objects()

        # Cached last-rendered gameplay frame, used as the backdrop for the
        # pause overlay so the world appears frozen behind the menu.
        self._pause_backdrop = None

    # ------------------------------------------------------------------
    # Setup / reset
    # ------------------------------------------------------------------
    def _init_gameplay_objects(self):
        self.road = Road()
        self.player = Player(self.road)
        self.enemies = EnemyManager(self.road)
        self.powerups = PowerUpManager(self.road)
        self.particles = ParticleSystem()

        self.score = 0.0
        self.distance = 0.0
        self.shake_timer = 0.0
        self.shake_magnitude = 0.0
        self.new_high_score_flag = False

    def start_new_game(self):
        self._init_gameplay_objects()
        self.state = settings.STATE_PLAYING
        self.audio.set_engine_playing(True)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    async def run(self):
        # The loop is async (and yields with `await asyncio.sleep(0)` every
        # frame) so this exact same code can run either as a normal desktop
        # app (via `asyncio.run(game.run())`) or compiled to WebAssembly
        # with pygbag, which requires the main loop to cooperatively yield
        # back to the browser's event loop each frame.
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            dt = min(dt, 0.05)  # clamp to avoid huge steps if the window stalls

            self._handle_events()
            self._update(dt)
            self._draw()

            await asyncio.sleep(0)

        self._shutdown()

    def _shutdown(self):
        highscore.save_high_score(self.high_score)
        pygame.quit()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key):
        if self.state == settings.STATE_MAIN_MENU:
            self._handle_main_menu_key(key)
        elif self.state == settings.STATE_INSTRUCTIONS:
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.audio.play("menu_select")
                self.state = self.previous_state_for_instructions
        elif self.state == settings.STATE_PLAYING:
            if key == pygame.K_ESCAPE:
                self.audio.play("menu_select")
                self.state = settings.STATE_PAUSED
                self.pause_index = 0
                self.audio.set_engine_playing(False)
        elif self.state == settings.STATE_PAUSED:
            self._handle_pause_key(key)
        elif self.state == settings.STATE_GAME_OVER:
            self._handle_game_over_key(key)

    def _handle_main_menu_key(self, key):
        options_count = 3
        if key in (pygame.K_UP, pygame.K_w):
            self.main_menu_index = (self.main_menu_index - 1) % options_count
            self.audio.play("menu_select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.main_menu_index = (self.main_menu_index + 1) % options_count
            self.audio.play("menu_select")
        elif key == pygame.K_RETURN:
            self.audio.play("menu_select")
            if self.main_menu_index == 0:
                self.start_new_game()
            elif self.main_menu_index == 1:
                self.previous_state_for_instructions = settings.STATE_MAIN_MENU
                self.state = settings.STATE_INSTRUCTIONS
            elif self.main_menu_index == 2:
                self.running = False

    def _handle_pause_key(self, key):
        options_count = 3
        if key in (pygame.K_UP, pygame.K_w):
            self.pause_index = (self.pause_index - 1) % options_count
            self.audio.play("menu_select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.pause_index = (self.pause_index + 1) % options_count
            self.audio.play("menu_select")
        elif key == pygame.K_RETURN:
            self.audio.play("menu_select")
            if self.pause_index == 0:
                self.state = settings.STATE_PLAYING
                self.audio.set_engine_playing(True)
            elif self.pause_index == 1:
                self.start_new_game()
            elif self.pause_index == 2:
                self.state = settings.STATE_MAIN_MENU
                self.main_menu_index = 0

    def _handle_game_over_key(self, key):
        options_count = 3
        if key in (pygame.K_UP, pygame.K_w):
            self.game_over_index = (self.game_over_index - 1) % options_count
            self.audio.play("menu_select")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.game_over_index = (self.game_over_index + 1) % options_count
            self.audio.play("menu_select")
        elif key == pygame.K_r:
            self.audio.play("menu_select")
            self.start_new_game()
        elif key == pygame.K_RETURN:
            self.audio.play("menu_select")
            if self.game_over_index == 0:
                self.start_new_game()
            elif self.game_over_index == 1:
                self.state = settings.STATE_MAIN_MENU
                self.main_menu_index = 0
            elif self.game_over_index == 2:
                self.running = False

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def _update(self, dt):
        if self.state == settings.STATE_MAIN_MENU:
            self.menu.update(dt)
        elif self.state == settings.STATE_INSTRUCTIONS:
            self.menu.update(dt)
        elif self.state == settings.STATE_PLAYING:
            self._update_gameplay(dt)
        elif self.state == settings.STATE_GAME_OVER:
            self.menu.update(dt)

    def _update_gameplay(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(dt, keys)
        self.player.update(dt)

        world_speed = self.player.speed

        self.road.update(dt, world_speed)
        passed_count = self.enemies.update(dt, world_speed, self.player)
        self.powerups.update(dt, world_speed)
        self.particles.update(dt)

        # Scoring: distance-based + bonus for passing enemies.
        self.distance += max(0.0, world_speed) * dt * settings.DISTANCE_PER_SCORE_UNIT
        self.score += max(0.0, world_speed) * dt * settings.DISTANCE_PER_SCORE_UNIT * settings.SCORE_PER_METER
        if passed_count:
            self.score += passed_count * settings.SCORE_PASS_BONUS
            for _ in range(passed_count):
                self.particles.emit_powerup_sparkle(self.player.x, self.player.y - 60, settings.COLOR_WHITE)

        # Speed line / nitro particle effects.
        self.particles.emit_speed_lines(self.player.x, self.player.y, self.player.speed_factor())
        if self.player.nitro_active:
            self.audio.play("nitro") if random.random() < 0.02 else None
            self.particles.emit_nitro_flame(
                self.player.x - self.player.width * 0.22, self.player.y + self.player.height * 0.45
            )
            self.particles.emit_nitro_flame(
                self.player.x + self.player.width * 0.22, self.player.y + self.player.height * 0.45
            )

        # Power-up pickups.
        collected = self.powerups.check_pickups(self.player)
        for p in collected:
            self.player.apply_powerup(p.kind)
            self.audio.play("powerup")
            color = {
                "boost": settings.COLOR_BOOST,
                "shield": settings.COLOR_SHIELD,
                "repair": settings.COLOR_REPAIR,
            }[p.kind]
            self.particles.emit_pickup_burst(p.x, p.y, color)

        # Collisions.
        if self.enemies.check_collisions(self.player):
            damaged = self.player.take_hit()
            if damaged:
                self.audio.play("collision")
                self.particles.emit_collision(self.player.x, self.player.y)
                self.shake_timer = 0.35
                self.shake_magnitude = 10.0
                if self.player.lives <= 0:
                    self._trigger_game_over()

        if self.shake_timer > 0:
            self.shake_timer -= dt

        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score_flag = True

    def _trigger_game_over(self):
        self.audio.set_engine_playing(False)
        self.audio.play("game_over")
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score_flag = True
        highscore.save_high_score(self.high_score)
        self.state = settings.STATE_GAME_OVER
        self.game_over_index = 0

    def _current_shake_offset(self):
        if self.shake_timer <= 0:
            return (0, 0)
        magnitude = self.shake_magnitude * (self.shake_timer / 0.35)
        return (
            random.uniform(-magnitude, magnitude),
            random.uniform(-magnitude, magnitude),
        )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw(self):
        surf = self.render_surface

        if self.state == settings.STATE_MAIN_MENU:
            self.menu.draw_main_menu(surf, self.main_menu_index, self.high_score)
        elif self.state == settings.STATE_INSTRUCTIONS:
            self.menu.draw_instructions(surf)
        elif self.state == settings.STATE_PLAYING:
            self._draw_gameplay(surf)
        elif self.state == settings.STATE_PAUSED:
            # Draw the frozen gameplay frame then overlay the pause menu.
            gameplay_surf = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            self._draw_gameplay(gameplay_surf, draw_hud=False)
            self.menu.draw_pause(surf, gameplay_surf, self.pause_index)
        elif self.state == settings.STATE_GAME_OVER:
            self.menu.draw_game_over(
                surf, self.game_over_index, self.score, self.high_score,
                self.distance, self.new_high_score_flag
            )

        self._blit_to_window(surf)
        pygame.display.flip()

    def _draw_gameplay(self, surf, draw_hud=True):
        shake = self._current_shake_offset()
        self.road.draw(surf, self.player.speed, shake)
        self.powerups.draw(surf, shake)
        self.enemies.draw(surf, shake)
        self.player.draw(surf, shake)
        self.particles.draw(surf)

        if draw_hud:
            fps = self.clock.get_fps()
            self.hud.draw_gameplay_hud(
                surf, self.score, self.high_score, self.distance,
                self.player.lives, self.player.nitro, fps
            )

    def _blit_to_window(self, surf):
        window_size = self.screen.get_size()
        if window_size == (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT):
            self.screen.blit(surf, (0, 0))
            return

        # Scale while preserving aspect ratio, letterboxing as needed.
        target_w, target_h = window_size
        src_ratio = settings.SCREEN_WIDTH / settings.SCREEN_HEIGHT
        target_ratio = target_w / max(1, target_h)

        if target_ratio > src_ratio:
            new_h = target_h
            new_w = int(new_h * src_ratio)
        else:
            new_w = target_w
            new_h = int(new_w / src_ratio)

        scaled = pygame.transform.smoothscale(surf, (max(1, new_w), max(1, new_h)))
        self.screen.fill(settings.COLOR_BLACK)
        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        self.screen.blit(scaled, (x, y))
